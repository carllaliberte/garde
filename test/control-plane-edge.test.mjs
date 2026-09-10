import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { controlPlane, renderExecutionCard } from "../src/ui/control-plane.mjs";

describe("control plane edges", () => {
  it("does not promote preview when verified is a string", () => {
    const card = renderExecutionCard({ verified: "true", body: "nope" });
    assert.equal(card.kind, "PREVIEW");
    const empty = controlPlane();
    assert.equal(empty.network.live, false);
    assert.equal(empty.lock.merge, false);
    assert.deepEqual(empty.contradictions, []);
  });
});
