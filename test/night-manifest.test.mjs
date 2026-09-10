import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { readFileSync } from "node:fs";

describe("night manifest is a preview, not a receipt", () => {
  it("does not claim merge, LIVE, or fake paths", () => {
    const m = JSON.parse(readFileSync("NIGHT_BUILD_MANIFEST.json", "utf8"));
    assert.equal(m.receipt, false);
    assert.equal(m.live, false);
    assert.equal(m.kind, "PREVIEW");
    assert.equal(m.authority.mode.AI_MERGE, "DENIED");
    assert.equal(m.execution_summary.integrity_checks.auto_merge, false);
    assert.ok(m.deliverables_preview.famille.includes("scripts/provenance.mjs"));
    assert.equal(
      m.deliverables_preview.famille.includes("src/provenance.mjs"),
      false,
    );
    assert.ok(m.execution_summary.tests_measured.famille.fail === 0);
    assert.match(m.next_action, /Carl/);
  });
});
