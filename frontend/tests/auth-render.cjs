// Render the real guard/shell at auth transitions without installing a DOM runner.
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
const React = require("react");
const { renderToStaticMarkup } = require("react-dom/server");
const ts = require("typescript");
const src = path.join(__dirname, "../src");
let state, pathname = "/", redirects = [];
let mobileNavigationProps;
const router = { replace: (path) => redirects.push(path) };
const modules = new Map();
function load(file) {
  if (modules.has(file)) return modules.get(file).exports;
  const output = { exports: {} }; modules.set(file, output);
  const requireLocal = (name) => {
    if (name === "./auth-provider") return { useAuth: () => state };
    if (name === "./supabase") return { getSupabaseBrowserClient: () => { throw Error("Unexpected SDK call during render"); } };
    if (name === "react") return { ...React, useEffect: (effect) => effect() };
    if (name === "react/jsx-runtime") {
      const runtime = require(name);
      const capture = (create) => (type, props, ...args) => {
        if (type === "details" && props.className === "mobile-navigation") mobileNavigationProps = props;
        return create(type, props, ...args);
      };
      return { ...runtime, jsx: capture(runtime.jsx), jsxs: capture(runtime.jsxs) };
    }
    if (name === "next/navigation") return { useRouter: () => router, usePathname: () => pathname };
    if (name === "next/link") return { default: ({ children, ...props }) => React.createElement("a", props, children) };
    if (name.startsWith("@/")) return load(path.join(src, name.slice(2) + ".tsx"));
    return require(name);
  };
  const code = ts.transpileModule(fs.readFileSync(file, "utf8"), {
    compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2017, jsx: ts.JsxEmit.ReactJSX },
  }).outputText;
  vm.runInNewContext(code, { module: output, exports: output.exports, require: requireLocal, Error });
  return output.exports;
}
const { ProtectedApp } = load(path.join(src, "features/auth/protected-dashboard.tsx"));
function render(next) {
  state = { ...next, retry: () => {} }; redirects = [];
  return renderToStaticMarkup(React.createElement(ProtectedApp, null, React.createElement("p", null, "Current page content")));
}
const session = { access_token: "a", user: { id: "user-a" } };
const user = { id: "user-a", email: null };
assert(!render({ loading: true, session: null, user: null, error: null }).includes("Current page content"));
assert(!render({ loading: false, session, user: null, error: null }).includes("app-shell"));
for (const path of ["/", "/subjects", "/study-plan", "/subjects/subject-a/videos", "/", "/subjects", "/study-plan"]) {
  pathname = path;
  const html = render({ loading: false, session, user, error: null });
  assert(html.includes("app-shell") && html.includes("Current page content"));
  assert(!html.includes("auth-bootstrap"));
}
const refreshing = render({ loading: false, session: { ...session, access_token: "b" }, user, error: null });
assert(refreshing.includes("app-shell") && !refreshing.includes("auth-bootstrap"));
const offline = render({ loading: false, session, user, error: "Connection unavailable" });
assert(offline.includes("Current page content") && offline.includes("Retry connection"));
assert(offline.includes('role="group" aria-label="Workspace"'));
let focused = false, prevented = false;
const menu = { open: true, querySelector: () => ({ focus: () => { focused = true; } }) };
mobileNavigationProps.ref.current = menu;
mobileNavigationProps.onKeyDown({ key: "Enter", preventDefault: () => { prevented = true; } });
assert.equal(menu.open, true, "Other keys preserve native navigation behavior");
mobileNavigationProps.onKeyDown({ key: "Escape", preventDefault: () => { prevented = true; } });
assert.equal(menu.open, false, "Escape closes the mobile navigation");
assert(focused && prevented, "Escape restores focus to the navigation disclosure");
assert(!render({ loading: false, session: null, user: null, error: null }).includes("Current page content"));
assert.deepEqual(redirects, ["/login"]);
console.log("PASS: guard renders protected content only after bootstrap, retains shell on refresh/offline, redirects signed-out users");
console.log("PASS: Dashboard/Subjects/Study Plan/Videos guard rendering across repeated route changes");
console.log("PASS: mobile navigation Escape dismissal, focus return and named navigation groups");
