/**
 * Control plane view-model. Preview is never a receipt.
 */
export function renderExecutionCard({ verified = false, body = "" } = {}) {
  if (verified === true) {
    return {
      kind: "RECEIPT",
      state: "VERIFIED",
      label: "Receipt",
      body,
      preview: false,
    };
  }
  return {
    kind: "PREVIEW",
    state: "UNVERIFIED",
    label: "Preview — not a receipt",
    body,
    preview: true,
  };
}

export function controlPlane({ n = 0, contradictions = [], hold = [] } = {}) {
  return {
    mission: { prompt: "Que veux-tu accomplir ?" },
    network: { n, live: false },
    contradictions,
    lock: {
      title: "Human Decision Lock",
      merge: false,
      write: "DENIED",
      requires: "Carl",
    },
    hold,
    preview: true,
    receipt: false,
    epsilon_zero_is_a_lie: true,
  };
}
