const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
const ts = require("typescript");
const code = ts.transpileModule(fs.readFileSync(path.join(__dirname, "../src/services/api.ts"), "utf8"), {
  compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2017 },
}).outputText;
function fixture(options = {}) {
  let session = { access_token: "old-token", user: { id: "user-a" } };
  let refreshes = 0, signouts = 0, requests = 0;
  const auth = {
    getSession: async () => ({ data: { session }, error: options.sessionError ?? null }),
    refreshSession: async () => {
      refreshes++;
      await new Promise((resolve) => setImmediate(resolve));
      if (options.refreshThrows) throw new Error("Disconnected");
      if (options.refreshError) return { data: { session: null }, error: options.refreshError };
      session = options.invalid ? null : { ...session, access_token: "fresh-token" };
      return { data: { session }, error: null };
    },
    signOut: async () => { signouts++; session = null; return { error: null }; },
  };
  const output = { exports: {} };
  vm.runInNewContext(code, {
    module: output, exports: output.exports, Error, Promise,
    require: (name) => name.includes("supabase") ? { getSupabaseBrowserClient: () => ({ auth }) } : { config: { apiUrl: "http://example.test" } },
    fetch: async (_url, init) => {
      requests++;
      if (options.switchAccount) session = { access_token: "other-token", user: { id: "user-b" } };
      const rejected = options.rejectAll || init.headers.Authorization === "Bearer old-token";
      return { status: rejected ? 401 : 200, ok: !rejected, json: async () => ({ id: "user-a" }) };
    },
  });
  return { api: output.exports, counts: () => ({ refreshes, signouts, requests }), current: () => session };
}
let passed = 0;
async function check(name, run) { await run(); passed++; console.log(`PASS: ${name}`); }
(async () => {
  await check("rejected stale token recovers and retries without signing out", async () => {
    const test = fixture();
    const me = await test.api.authenticatedGet("/api/auth/me");
    assert.equal(me.id, "user-a"); assert.deepEqual(test.counts(), { refreshes: 1, signouts: 0, requests: 2 });
  });
  await check("concurrent 401 responses share one refresh", async () => {
    const test = fixture();
    await Promise.all([test.api.authenticatedGet("/one"), test.api.authenticatedGet("/two")]);
    assert.equal(test.counts().refreshes, 1); assert.equal(test.counts().signouts, 0);
  });
  await check("temporary refresh failure preserves stored session", async () => {
    const test = fixture({ refreshError: { name: "AuthRetryableFetchError", status: 503 } });
    await assert.rejects(() => test.api.authenticatedGet("/me"), (error) => error.status === 503);
    assert(test.current()); assert.equal(test.counts().signouts, 0);
  });
  await check("genuinely rejected refreshed session signs out", async () => {
    const test = fixture({ rejectAll: true });
    await assert.rejects(() => test.api.authenticatedGet("/me"), (error) => error.status === 401);
    assert.equal(test.current(), null); assert.equal(test.counts().signouts, 1);
  });
  await check("an old request cannot sign out a newly signed-in account", async () => {
    const test = fixture({ switchAccount: true });
    await assert.rejects(() => test.api.authenticatedGet("/me"), (error) => error.status === 401);
    assert.equal(test.current().user.id, "user-b"); assert.equal(test.counts().signouts, 0);
  });
  await check("temporary session restore error is not treated as invalid credentials", async () => {
    const test = fixture({ sessionError: { name: "AuthRetryableFetchError", status: 503 } });
    await assert.rejects(() => test.api.authenticatedGet("/me"), (error) => error.status === 503);
    assert.equal(test.counts().signouts, 0);
  });
  await check("thrown refresh failure is retryable and preserves session", async () => {
    const test = fixture({ refreshThrows: true });
    await assert.rejects(() => test.api.authenticatedGet("/me"), (error) => error.status === 503);
    assert(test.current()); assert.equal(test.counts().signouts, 0);
  });
  await check("invalid refresh credentials clear the rejected session", async () => {
    const test = fixture({ refreshError: { status: 400 } });
    await assert.rejects(() => test.api.authenticatedGet("/me"), (error) => error.status === 401);
    assert.equal(test.current(), null); assert.equal(test.counts().signouts, 1);
  });
  console.log(`PASS: ${passed} authenticated API recovery checks`);
})().catch((error) => { console.error(error); process.exitCode = 1; });
