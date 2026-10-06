// Algorithm fixtures only; no sample topics are inserted or rendered in the app.
const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");
const ts = require("typescript");
const source = fs.readFileSync("src/features/subjects/hierarchy.ts", "utf8");
const compiled = ts.transpileModule(source, { compilerOptions: { module: ts.ModuleKind.CommonJS } });
const context = { exports: {} };
vm.runInNewContext(compiled.outputText, context);
const flattenTopics = context.exports.flattenTopics;
const topic = (id, parent, order) => ({ id, parent_topic_id: parent, display_order: order, title: id, subject_id: "subject", code: null, description: null });
const result = flattenTopics([topic("child", "root", 1), topic("second", null, 2), topic("root", null, 1), topic("deep", "child", 1)]);
assert.equal(JSON.stringify(result.map(({ topic, depth }) => [topic.id, depth])), JSON.stringify([["root", 0], ["child", 1], ["deep", 2], ["second", 0]]));
const malformed = flattenTopics([topic("a", "b", 1), topic("b", "a", 2), topic("orphan", "absent", 3), topic("self", "self", 4)]);
assert.equal(malformed.length, 4);
assert.equal(new Set(malformed.map((row) => row.topic.id)).size, 4);
assert.equal(flattenTopics([]).length, 0);
console.log("Topic hierarchy: ordering, nesting, cycles, missing parents, and empty data passed.");
