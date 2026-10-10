const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
const React = require("react");
const { renderToStaticMarkup } = require("react-dom/server");
const ts = require("typescript");
const src = path.join(__dirname, "../src");
const modules = new Map();
let stateOverrides = null, stateIndex = 0;
const reactShim = { ...React, useState: (initial) => stateOverrides ? [stateOverrides[stateIndex++], () => {}] : React.useState(initial) };
function load(file) {
  if (modules.has(file)) return modules.get(file).exports;
  const output = { exports: {} }; modules.set(file, output);
  const local = (name) => {
    if (name === "react") return reactShim;
    if (name === "@/features/auth/auth-provider") return { useAuth: () => ({ user: { id: "test-owner", email: "reviewer@example.test" } }) };
    if (name === "next/link") return { default: ({ children, ...props }) => React.createElement("a", props, children) };
    if (name === "next/navigation") return { useRouter: () => ({ push: () => {} }) };
    if (name === "@/services/api" || name === "./api") return { ApiError: class extends Error {} };
    if (name.startsWith("@/") || name.startsWith(".")) {
      const base = name.startsWith("@/") ? path.join(src, name.slice(2)) : path.resolve(path.dirname(file), name);
      return load(fs.existsSync(base + ".tsx") ? base + ".tsx" : base + ".ts");
    }
    return require(name);
  };
  const code = ts.transpileModule(fs.readFileSync(file, "utf8"), { compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2017, jsx: ts.JsxEmit.ReactJSX } }).outputText;
  vm.runInNewContext(code, { module: output, exports: output.exports, require: local, Error, Intl, Date, FormData, URLSearchParams });
  return output.exports;
}
const { ResourceListView, ResourceContentView } = load(path.join(src, "features/resources/resource-views.tsx"));
const resource = { id: "resource-id", title: "Real source <notes>", original_filename: "notes.pdf", resource_type: "pdf", mime_type: "application/pdf", processing_status: "ready", subject_code: "FAR", topic_title: "Cash", file_size_bytes: 1024, page_count: 12, row_count: null, created_at: "2026-10-06T23:30:00Z", updated_at: "2026-10-06T23:30:00Z" };
const render = (data, extra = {}) => renderToStaticMarkup(React.createElement(ResourceListView, { data, loading: false, error: null, retry: () => {}, offset: 0, limit: 20, changePage: () => {}, timezone: "Asia/Manila", ...extra }));
assert(render(null, { loading: true }).includes('role="status"'));
assert(render(null, { error: "Unavailable" }).includes('role="alert"'));
assert(!render(null, { error: "Unavailable" }).includes("No resources yet"));
assert(render({ resources: [], total: 0 }).includes("No resources yet"));
const populated = render({ resources: [resource], total: 21 }, { error: "Refresh failed" });
assert(populated.includes('href="/library/resource-id"') && populated.includes("Real source &lt;notes&gt;"));
assert(populated.includes("FAR") && populated.includes("Cash") && populated.includes("12 pages") && populated.includes("Ready"));
assert(populated.includes("Oct 7, 2026"), "Upload date must use configured profile timezone");
assert(populated.includes("Refresh failed") && populated.includes("Next"), "Refresh failures retain loaded resources");
function content(data) { return renderToStaticMarkup(React.createElement(ResourceContentView, { data })); }
assert(content({ resource, sections: [{ id: "section", page_number: 1, section_index: 0, content: "Source <script>alert(1)</script>" }], headers: [], rows: [], total_sections: 12 }).includes("Page 1"));
assert(content({ resource, sections: [{ id: "section", page_number: 1, content: "<script>alert(1)</script>" }], headers: [], rows: [] }).includes("&lt;script&gt;"));
const csv = content({ resource: { ...resource, resource_type: "csv" }, headers: ["Title", "Answer"], rows: [["Revenue", "Income"]], row_count: 75, sections: [] });
assert(csv.includes("<table") && csv.includes("Income") && csv.includes("1 of 75 rows"));
const { uploadFileError } = load(path.join(src, "services/resources.ts"));
assert(uploadFileError({ name: "notes.pdf", size: 4194305 }).includes("4 MiB"));
assert(uploadFileError({ name: "notes.xlsx", size: 10 }).includes("PDF or CSV"));
assert(uploadFileError({ name: "notes.csv", size: 0 }).includes("empty"));
assert.equal(uploadFileError({ name: "notes.PDF", size: 4194304 }), null);
const { ResourceDetail } = load(path.join(src, "features/resources/resource-detail.tsx"));
assert(renderToStaticMarkup(React.createElement(ResourceDetail, { resourceId: "id" })).includes('role="status"'));
function renderDetail(overrides = {}, resourceId = resource.id) {
  const full = { ...resource, updated_at: resource.created_at, error_message: null };
  stateOverrides = [full, null, 0, false, null, null, false, 0, 0, false, null, null, "Asia/Manila", false, 0];
  for (const [index, value] of Object.entries(overrides)) stateOverrides[Number(index)] = value;
  stateIndex = 0;
  try { return renderToStaticMarkup(React.createElement(ResourceDetail, { resourceId })); }
  finally { stateOverrides = null; }
}
const detail = renderDetail({ 4: { data: { resource, sections: [{ id: "s", page_number: 1, section_index: 0, content: "Saved PDF text" }], headers: [], rows: [], total_sections: 12 }, offset: 0 }, 5: "Preview refresh failed", 9: true });
assert(detail.includes("Download original") && detail.includes("Open PDF") && detail.includes("Confirm deletion") && detail.includes("Keep resource"));
assert(detail.includes("Saved PDF text") && detail.includes("Preview refresh failed"), "Preview failures retain loaded sections");
assert(detail.includes("2 minutes") && !detail.includes("storage.example"), "Signed links are requested on demand, not rendered into saved state");
assert(renderDetail({ 0: { ...resource, processing_status: "failed" } }).includes("PDF processing failed"));
assert(renderDetail({ 0: { ...resource, resource_type: "csv" } }).includes("Download original") && !renderDetail({ 0: { ...resource, resource_type: "csv" } }).includes("Open PDF"));
assert(!renderDetail({}, "replacement-id").includes("Real source"), "A reused detail component must not display a previous resource's metadata");
assert(renderDetail({ 0: { ...resource, processing_status: "failed", error_message: "No selectable text was found. OCR is not supported." } }).includes("No selectable text was found. OCR is not supported."));
assert(!renderDetail({ 0: { ...resource, processing_status: "failed", error_message: "Private provider path /secret" } }).includes("/secret"));
const { UploadDialog } = load(path.join(src, "features/resources/upload-dialog.tsx"));
const upload = renderToStaticMarkup(React.createElement(UploadDialog, { subjects: [{ id: "far", code: "FAR", name: "Financial Accounting" }], saved: () => {}, close: () => {} }));
assert(upload.includes("<dialog") && upload.includes('type="file"') && upload.includes("4 MiB") && upload.includes("FAR"));
assert(upload.includes('maxLength="200"') && upload.includes("Topic (optional)"));
const { ResourceLibrary } = load(path.join(src, "features/resources/resource-library.tsx"));
const library = renderToStaticMarkup(React.createElement(ResourceLibrary));
assert(library.includes("All types") && library.includes("All subjects") && library.includes('type="search"') && library.includes('role="status"'));
console.log("PASS: resource states, retained data, timezone, pagination, escaped PDF/CSV previews and upload limits");

const { SettingsPage } = load(path.join(src, "features/settings/settings-page.tsx"));
function settings(states) {
  stateOverrides = states; stateIndex = 0;
  try { return renderToStaticMarkup(React.createElement(SettingsPage)); } finally { stateOverrides = null; }
}
const settingsKnown = settings(["Asia/Taipei", false, 0]);
assert(settingsKnown.includes("reviewer@example.test") && settingsKnown.includes("Asia/Taipei"));
assert(!settingsKnown.includes("<input") && !settingsKnown.includes("<select"), "Read-only Settings must not invent preference controls");
const settingsFallback = settings([null, true, 0]);
assert(settingsFallback.includes("until your profile timezone is available") && settingsFallback.includes("Retry timezone"));
console.log("PASS: read-only Settings account/profile timezone, labeled fallback and retry state");
