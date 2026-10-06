// Executes the actual frontend SDK/API modules against the local backend.
// Uses only existing ignored verification credentials and cleans up its own task.
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
function load(file) {
  if (modules.has(file)) return modules.get(file).exports;
  const output = { exports: {} }; modules.set(file, output);
  const code = ts.transpileModule(fs.readFileSync(file, "utf8"), { compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2017 } }).outputText;
  const localRequire = (name) => {
    if (name.startsWith("@/")) return load(path.join(frontend, "src", name.slice(2) + ".ts"));
    if (name.startsWith(".")) return load(path.resolve(path.dirname(file), name + ".ts"));
    return require(path.join(frontend, "node_modules", name));
  };
  const originFetch = (url, options = {}) => fetch(url, { ...options, headers: { ...options.headers, Origin: "http://localhost:3001" } });
  vm.runInNewContext(code, { module: output, exports: output.exports, require: localRequire,
    process: { env: browserEnv }, fetch: originFetch, URLSearchParams, AbortController, Error }, { filename: file });
  return output.exports;
}
(async () => {
  assert.equal(browserEnv.NEXT_PUBLIC_API_URL, "http://localhost:8001");
  assert(privateEnv.PHASE2_VERIFY_EMAIL && privateEnv.PHASE2_VERIFY_PASSWORD, "Existing local verification credentials are required");
  const auth = load(path.join(frontend, "src/features/auth/supabase.ts")).getSupabaseBrowserClient();
  const planner = load(path.join(frontend, "src/services/study-plan.ts"));
  const api = load(path.join(frontend, "src/services/api.ts"));
  let task;
  try {
    const login = await auth.auth.signInWithPassword({ email: privateEnv.PHASE2_VERIFY_EMAIL, password: privateEnv.PHASE2_VERIFY_PASSWORD });
    assert(!login.error && login.data.session, "Frontend SDK sign-in failed");
    const me = await api.authenticatedGet("/api/auth/me");
    assert.equal(me.id, login.data.user.id);
    const context = await planner.getPlannerContext();
    assert(context.timezone);
    task = await planner.createTask({ title: "Temporary frontend planner verification", subject_id: null, topic_id: null,
      task_type: "general", estimated_minutes: 15, due_at: null, status: "pending" });
    const updated = await planner.updateTask(task.id, { status: "cancelled" });
    assert.equal(updated.status, "cancelled");
    await planner.deleteTask(task.id); task = undefined;
    console.log("PASS: actual frontend SDK -> bearer API on 8001 -> PostgreSQL GET/POST/PATCH/DELETE/204");
  } finally {
    if (task) await planner.deleteTask(task.id);
    await auth.auth.signOut({ scope: "local" });
    auth.auth.stopAutoRefresh();
  }
  await assert.rejects(() => planner.getPlannerContext(), (error) => error.status === 401);
  console.log("PASS: signed-out frontend requests require authentication");
})().catch(() => { console.error("Frontend planner verification failed; no credential details printed."); process.exitCode = 1; });
