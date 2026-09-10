import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { controlPlane, renderExecutionCard } from "../src/ui/control-plane.mjs";

describe("control plane — preview is not a receipt", () => {
  it("isolates UNVERIFIED from VERIFIED and locks merge", () => {
    const preview = renderExecutionCard({ verified: false, body: "draft" });
    const receipt = renderExecutionCard({ verified: true, body: "sealed" });
    assert.equal(preview.kind, "PREVIEW");
    assert.equal(preview.state, "UNVERIFIED");
    assert.equal(receipt.kind, "RECEIPT");
    assert.notEqual(preview.kind, receipt.kind);
    const ui = controlPlane({ n: 6, contradictions: ["a≠b"] });
    assert.equal(ui.lock.merge, false);
    assert.equal(ui.lock.write, "DENIED");
    assert.equal(ui.receipt, false);
    assert.equal(ui.epsilon_zero_is_a_lie, true);
  });
});
