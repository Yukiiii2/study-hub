// Narrow auth verification using actual frontend modules and existing ignored credentials.
// No browser session/storage, credential logging, or database writes.
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
const assert = require("node:assert/strict");
const root = path.resolve(__dirname, "..");
const frontend = path.join(root, "frontend");
const ts = require(path.join(frontend, "node_modules/typescript"));
const { loadEnvConfig } = require(path.join(frontend, "node_modules/@next/env"));
const publicEnv = { ...loadEnvConfig(frontend, false, undefined, true).combinedEnv };
const privateEnv = { ...loadEnvConfig(path.join(root, "backend"), false, undefined, true).combinedEnv };
const browserEnv = Object.fromEntries(Object.entries(publicEnv).filter(([key]) => key.startsWith("NEXT_PUBLIC_")));
const modules = new Map();
let meRequests = 0;
function load(file) {
  if (modules.has(file)) return modules.get(file).exports;
  const output = { exports: {} }; modules.set(file, output);
  const code = ts.transpileModule(fs.readFileSync(file, "utf8"), {
    compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2017 },
  }).outputText;
  const localRequire = (name) => {
    if (name.startsWith("@/")) return load(path.join(frontend, "src", name.slice(2) + ".ts"));
    if (name.startsWith(".")) return load(path.resolve(path.dirname(file), name + ".ts"));
    return require(path.join(frontend, "node_modules", name));
  };
  const originFetch = (url, options = {}) => {
    if (url.endsWith("/api/auth/me")) meRequests++;
    return fetch(url, { ...options, headers: { ...options.headers, Origin: "http://localhost:3001" } });
  };
  vm.runInNewContext(code, { module: output, exports: output.exports, require: localRequire,
    process: { env: browserEnv }, fetch: originFetch, AbortController, Error, Promise }, { filename: file });
  return output.exports;
}
async function waitFor(check) {
  for (let i = 0; i < 100; i++) {
    if (check()) return;
    await new Promise((resolve) => setTimeout(resolve, 100));
  }
  throw new Error("Auth transition timed out");
}
(async () => {
  assert.equal(browserEnv.NEXT_PUBLIC_API_URL, "http://localhost:8001");
  assert(privateEnv.PHASE2_VERIFY_EMAIL && privateEnv.PHASE2_VERIFY_PASSWORD, "Local verification credentials required");
  const health = await fetch(`${browserEnv.NEXT_PUBLIC_API_URL}/health`);
  assert(health.ok && (await health.json()).status === "ok");
  const preflight = await fetch(`${browserEnv.NEXT_PUBLIC_API_URL}/api/auth/me`, { method: "OPTIONS", headers: {
    Origin: "http://localhost:3001", "Access-Control-Request-Method": "GET", "Access-Control-Request-Headers": "authorization",
  } });
  assert(preflight.ok && preflight.headers.get("access-control-allow-origin") === "http://localhost:3001");
  const auth = load(path.join(frontend, "src/features/auth/supabase.ts")).getSupabaseBrowserClient();
  const api = load(path.join(frontend, "src/services/api.ts"));
  const { SessionVerifier } = load(path.join(frontend, "src/features/auth/session-verification.ts"));
  const verifier = new SessionVerifier((_session, signal) => api.authenticatedGet("/api/auth/me", signal), () => {});
  const { data } = auth.auth.onAuthStateChange((event, session) => verifier.accept(session, event === "USER_UPDATED"));
  try {
    await waitFor(() => !verifier.state.loading);
    assert.equal(verifier.state.session, null);
    await assert.rejects(() => api.authenticatedGet("/api/auth/me"), (error) => error.status === 401);
    const login = await auth.auth.signInWithPassword({ email: privateEnv.PHASE2_VERIFY_EMAIL, password: privateEnv.PHASE2_VERIFY_PASSWORD });
    assert(!login.error && login.data.session, "SDK sign-in failed");
    await waitFor(() => verifier.state.user);
    assert.equal(verifier.state.user.id, login.data.user.id);
    assert.equal(meRequests, 1);
    for (let i = 0; i < 10; i++) verifier.accept((await auth.auth.getSession()).data.session);
    assert.equal(meRequests, 1);
    console.log("PASS: logged-out bootstrap; real sign-in -> auth/me; repeated same-token notifications reuse validation");

    // A fresh verifier models a hard refresh: restored SDK session still needs backend validation.
    const fresh = new SessionVerifier((_session, signal) => api.authenticatedGet("/api/auth/me", signal), () => {});
    fresh.accept((await auth.auth.getSession()).data.session);
    assert.equal(fresh.state.user, null);
    await waitFor(() => fresh.state.user); assert.equal(fresh.state.user.id, login.data.user.id); fresh.dispose();
    console.log("PASS: restored session/hard-bootstrap path validates before showing protected content");

    const refreshed = await auth.auth.refreshSession();
    assert(!refreshed.error && refreshed.data.session, "SDK token refresh failed");
    assert(verifier.state.user && !verifier.state.loading, "Refresh must preserve authenticated UI");
    await waitFor(() => meRequests >= 3 && !verifier.state.error);
    const me = await api.authenticatedGet("/api/auth/me"); assert.equal(me.id, login.data.user.id);
    console.log("PASS: real Supabase token refresh retains verified identity; authenticated bearer request accepted");

    const invalid = await fetch(`${browserEnv.NEXT_PUBLIC_API_URL}/api/auth/me`, {
      headers: { Origin: "http://localhost:3001", Authorization: "Bearer deliberately-invalid-test-token" },
    });
    assert.equal(invalid.status, 401);
    const signedOut = await auth.auth.signOut({ scope: "local" }); assert(!signedOut.error);
    assert.equal(verifier.state.user, null); assert.equal(verifier.state.session, null);
    await assert.rejects(() => api.authenticatedGet("/api/auth/me"), (error) => error.status === 401);
    console.log("PASS: invalid bearer rejected; sign-out clears cached identity; subsequent requests require authentication");
    console.log("PASS: health and authenticated-request CORS on port 8001");
  } finally {
    data.subscription.unsubscribe(); verifier.dispose();
    await auth.auth.signOut({ scope: "local" }); auth.auth.stopAutoRefresh();
  }
})().catch(() => { console.error("Auth verification failed; no credential details printed."); process.exitCode = 1; });
