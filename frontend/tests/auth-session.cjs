// Narrow lifecycle regressions; Supabase/network boundaries use controlled responses.
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
const ts = require("typescript");
const file = path.join(__dirname, "../src/features/auth/session-verification.ts");
assert(fs.existsSync(file), "A shared session verification cache must replace per-page bootstraps");
const output = { exports: {} };
vm.runInNewContext(ts.transpileModule(fs.readFileSync(file, "utf8"), {
  compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2017 },
}).outputText, { module: output, exports: output.exports, AbortController, Error, Promise });
const { SessionVerifier } = output.exports;
const session = (token = "token-a", id = "user-a") => ({ access_token: token, user: { id } });
const user = (id = "user-a") => ({ id, email: null });
const settle = () => new Promise((resolve) => setImmediate(resolve));
const deferred = () => { let resolve, reject; const promise = new Promise((yes, no) => { resolve = yes; reject = no; }); return { promise, resolve, reject }; };
let passed = 0;
async function check(name, run) { await run(); passed++; console.log(`PASS: ${name}`); }
(async () => {
  await check("initial unknown session blocks; logged out bootstrap resolves", async () => {
    const verifier = new SessionVerifier(async () => user(), () => {});
    assert.equal(verifier.state.loading, true);
    verifier.accept(null);
    assert.equal(verifier.state.loading, false);
    assert.equal(verifier.state.user, null);
  });
  await check("first authenticated load waits for backend verification", async () => {
    const request = deferred();
    const verifier = new SessionVerifier(() => request.promise, () => {});
    verifier.accept(session());
    assert.equal(verifier.state.user, null);
    request.resolve(user()); await settle();
    assert.equal(verifier.state.user.id, "user-a");
  });
  await check("focus/SIGNED_IN and page reuse do not repeat auth/me", async () => {
    let calls = 0;
    const verifier = new SessionVerifier(async () => { calls++; return user(); }, () => {});
    verifier.accept(session()); await settle();
    for (let i = 0; i < 10; i++) verifier.accept(session());
    await settle();
    assert.equal(calls, 1);
    assert.equal(verifier.state.user.id, "user-a");
  });
  await check("token refresh keeps authenticated content visible and deduplicates verification", async () => {
    const request = deferred(); let calls = 0;
    const verifier = new SessionVerifier(() => ++calls === 1 ? Promise.resolve(user()) : request.promise, () => {});
    verifier.accept(session()); await settle();
    verifier.accept(session("token-b")); verifier.accept(session("token-b"));
    assert.equal(verifier.state.user.id, "user-a");
    assert.equal(verifier.state.loading, false);
    await settle(); assert.equal(calls, 2);
    request.resolve(user()); await settle();
    assert.equal(verifier.state.error, null);
  });
  await check("temporary background outage retains UI and explicit retry recovers", async () => {
    let fail = false;
    const verifier = new SessionVerifier(async () => { if (fail) throw new Error("offline"); return user(); }, () => {});
    verifier.accept(session()); await settle(); fail = true;
    verifier.accept(session("token-b")); await settle();
    assert.equal(verifier.state.user.id, "user-a"); assert(verifier.state.error);
    fail = false; verifier.retry(); await settle(); assert.equal(verifier.state.error, null);
  });
  await check("sign out cancels stale verification and clears cached user immediately", async () => {
    const request = deferred();
    const verifier = new SessionVerifier(() => request.promise, () => {});
    verifier.accept(session()); await settle(); verifier.accept(null);
    request.resolve(user()); await settle();
    assert.equal(verifier.state.session, null); assert.equal(verifier.state.user, null);
  });
  await check("account switch cannot show cached identity or stale results", async () => {
    const request = deferred();
    const verifier = new SessionVerifier((current) => current.user.id === "user-a" ? request.promise : Promise.resolve(user("user-b")), () => {});
    verifier.accept(session()); await settle(); verifier.accept(session("token-b", "user-b"));
    assert.equal(verifier.state.user, null);
    request.resolve(user()); await settle(); assert.equal(verifier.state.user.id, "user-b");
  });
  await check("backend identity mismatch is never accepted", async () => {
    const verifier = new SessionVerifier(async () => user("different-user"), () => {});
    verifier.accept(session()); await settle();
    assert.equal(verifier.state.user, null); assert(verifier.state.error);
  });
  await check("background identity mismatch removes previously validated content", async () => {
    let calls = 0;
    const verifier = new SessionVerifier(async () => ++calls === 1 ? user() : user("different-user"), () => {});
    verifier.accept(session()); await settle();
    verifier.accept(session("token-b")); await settle();
    assert.equal(verifier.state.user, null); assert(verifier.state.error);
  });
  await check("definitive invalid session clears the authenticated identity", async () => {
    let invalid = false;
    const verifier = new SessionVerifier(async () => { if (invalid) throw { status: 401 }; return user(); }, () => {});
    verifier.accept(session()); await settle(); invalid = true;
    verifier.accept(session("token-b")); await settle();
    assert.equal(verifier.state.session, null); assert.equal(verifier.state.user, null);
  });
  await check("disposing provider aborts verification and prevents late publication", async () => {
    const request = deferred(); let publications = 0;
    const verifier = new SessionVerifier(() => request.promise, () => publications++);
    verifier.accept(session()); await settle(); verifier.dispose(); const before = publications;
    request.resolve(user()); await settle(); assert.equal(publications, before);
  });
  console.log(`PASS: ${passed} auth lifecycle regression checks`);
})().catch((error) => { console.error(error); process.exitCode = 1; });
