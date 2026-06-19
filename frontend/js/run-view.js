import { getRunStatus, getRunDetail, retryRun, submitReview } from "./api.js";

const STAGE_ORDER = [
  "stage1_intake",
  "stage2_research",
  "stage4_extract_signals",
  "stage5_validate_signals",
  "stage6_persona_mapping",
  "stage7_pain_mapping",
  "stage8_hook_scoring",
  "stage9_draft_generation",
  "stage10_quality_scoring",
  "stage11_routing",
];

const STAGE_LABELS = {
  stage1_intake: "Intake & Normalize",
  stage2_research: "Research Company & Individual",
  stage4_extract_signals: "Extract Signals",
  stage5_validate_signals: "Validate Signals",
  stage6_persona_mapping: "Map Persona",
  stage7_pain_mapping: "Map Pain",
  stage8_hook_scoring: "Score & Select Hook",
  stage9_draft_generation: "Generate Draft",
  stage10_quality_scoring: "Score Draft Quality",
  stage11_routing: "Route Run",
};

const BANNER_CONFIG = {
  insufficient_signal: {
    className: "banner--yellow",
    text: "Low confidence — fallback draft. Manual research recommended.",
  },
  needs_human_research: {
    className: "banner--orange",
    text: (detail) => detail.escalation_reason || "Groundedness check failed. Review carefully before sending.",
  },
  failed: {
    className: "banner--red",
    text: (detail) => `Run failed — ${detail.escalation_reason || "unknown error"}. Use retry button.`,
  },
};

const POLL_INTERVAL_MS = 1500;
const NON_TERMINAL_STATUSES = new Set(["pending", "running"]);

const params = new URLSearchParams(window.location.search);
const runId = params.get("id");

if (!runId) {
  window.location.href = "index.html";
}

const livePhase = document.getElementById("live-phase");
const reviewPhase = document.getElementById("review-phase");
const loadError = document.getElementById("load-error");
const stageList = document.getElementById("stage-list");

let pollTimer = null;

function escapeHtml(value) {
  const div = document.createElement("div");
  div.textContent = value ?? "";
  return div.innerHTML;
}

function formatScore(value) {
  return value === null || value === undefined ? "—" : Number(value).toFixed(2);
}

function renderStageList(currentStage, runStatus, degradedStages) {
  const currentIndex = STAGE_ORDER.indexOf(currentStage);

  stageList.innerHTML = STAGE_ORDER.map((stageName, index) => {
    let stateClass = "stage-item--pending";
    let icon = "○";

    if (degradedStages.has(stageName)) {
      stateClass = "stage-item--degraded";
      icon = "⚠";
    } else if (currentIndex !== -1 && index < currentIndex) {
      stateClass = "stage-item--done";
      icon = "✓";
    } else if (currentIndex !== -1 && index === currentIndex) {
      if (NON_TERMINAL_STATUSES.has(runStatus)) {
        stateClass = "stage-item--running";
        icon = "";
      } else {
        stateClass = "stage-item--done";
        icon = "✓";
      }
    }

    return `<li class="stage-item ${stateClass}"><span class="stage-item__icon">${icon}</span><span class="stage-item__label">${STAGE_LABELS[stageName]}</span></li>`;
  }).join("");
}

function renderStatusBanner(detail) {
  const banner = document.getElementById("status-banner");
  const config = BANNER_CONFIG[detail.status];

  if (!config) {
    banner.hidden = true;
    banner.innerHTML = "";
    return;
  }

  const text = typeof config.text === "function" ? config.text(detail) : config.text;
  banner.hidden = false;
  banner.className = `banner ${config.className}`;

  if (detail.status === "failed") {
    banner.innerHTML = `<span>${escapeHtml(text)}</span><button id="retry-btn" class="btn btn--small">Retry</button><span id="retry-error" class="retry-error"></span>`;
    document.getElementById("retry-btn").addEventListener("click", async (event) => {
      const button = event.currentTarget;
      const retryErrorSpan = document.getElementById("retry-error");
      button.disabled = true;
      retryErrorSpan.textContent = "";
      try {
        const result = await retryRun(detail.id);
        window.location.href = `run.html?id=${result.new_run_id}`;
      } catch (error) {
        retryErrorSpan.textContent = ` Retry failed: ${error.message}`;
        button.disabled = false;
      }
    });
  } else {
    banner.textContent = text;
  }
}

function renderDraftPanel(detail) {
  const subjectInput = document.getElementById("draft-subject");
  const bodyTextarea = document.getElementById("draft-body");
  const isLocked = detail.status === "reviewed" || !detail.draft;

  subjectInput.value = detail.draft ? detail.draft.subject || "" : "";
  bodyTextarea.value = detail.draft ? detail.draft.body || "" : "(No draft was generated for this run.)";
  subjectInput.disabled = isLocked;
  bodyTextarea.disabled = isLocked;

  document.getElementById("approve-btn").disabled = isLocked;
  document.getElementById("approve-edits-btn").disabled = isLocked;
  document.getElementById("reject-btn").disabled = isLocked;

  if (detail.status === "reviewed") {
    const confirmation = document.getElementById("decision-confirmation");
    confirmation.hidden = false;
    confirmation.textContent = "Decision recorded.";
  }
}

function renderReasoningTrail(detail) {
  const container = document.getElementById("reasoning-trail");
  const hookSignal = detail.signals.find((s) => s.selected_as_hook);
  const painBySignalId = new Map(detail.pain_mappings.map((pm) => [pm.signal_id, pm]));

  let html = "";

  if (detail.persona_mapping) {
    const persona = detail.persona_mapping;
    html += `<div class="trail-block">
      <h3>Persona</h3>
      <p>${escapeHtml(persona.persona_name)}${persona.is_assumed ? ' <span class="tag">assumed</span>' : ""}</p>
    </div>`;
  }

  if (hookSignal) {
    const pain = painBySignalId.get(hookSignal.id);
    html += `<div class="trail-block">
      <h3>Chosen Hook</h3>
      <p class="claim">${escapeHtml(hookSignal.claim)}</p>
      <p class="muted">Hook score: <strong>${formatScore(hookSignal.hook_score)}</strong> · Type: ${escapeHtml(hookSignal.type)}</p>
      ${pain ? `<p class="muted">Matched pain: <strong>${escapeHtml(pain.owned_pain)}</strong>${pain.owned_kpi ? ` (KPI: ${escapeHtml(pain.owned_kpi)})` : ""}</p>` : ""}
      ${hookSignal.source_url ? `<p class="source"><a href="${escapeHtml(hookSignal.source_url)}" target="_blank" rel="noopener">${escapeHtml(hookSignal.source_url)}</a></p>` : ""}
      ${hookSignal.source_snippet ? `<blockquote>${escapeHtml(hookSignal.source_snippet)}</blockquote>` : ""}
    </div>`;
  } else {
    html += `<div class="trail-block"><h3>Chosen Hook</h3><p class="muted">No signal met the confidence threshold.</p></div>`;
  }

  html += `<div class="trail-block">
    <h3>All Candidate Signals</h3>
    <table class="scores-table">
      <thead>
        <tr><th>Claim</th><th>Status</th><th>Rel.</th><th>Spec.</th><th>Rec.</th><th>Act.</th><th>Ver.</th><th>Hook</th></tr>
      </thead>
      <tbody>
        ${detail.signals
          .map(
            (s) => `<tr class="${s.selected_as_hook ? "row--selected" : ""}">
          <td>${escapeHtml(s.claim)}</td>
          <td>${s.selected_as_hook ? "Selected" : "Considered — not selected"}</td>
          <td>${formatScore(s.relevance_score)}</td>
          <td>${formatScore(s.specificity_score)}</td>
          <td>${formatScore(s.recency_score)}</td>
          <td>${formatScore(s.actionability_score)}</td>
          <td>${formatScore(s.verifiability_score)}</td>
          <td>${formatScore(s.hook_score)}</td>
        </tr>`
          )
          .join("")}
      </tbody>
    </table>
  </div>`;

  html += `<div class="trail-block">
    <h3>Sources</h3>
    <ul class="sources-list">
      ${detail.signals
        .map(
          (s) => `<li>
        <a href="${escapeHtml(s.source_url || "#")}" target="_blank" rel="noopener">${escapeHtml(s.source_url || "(no source)")}</a>
        ${s.source_snippet ? `<blockquote>${escapeHtml(s.source_snippet)}</blockquote>` : ""}
      </li>`
        )
        .join("")}
    </ul>
  </div>`;

  container.innerHTML = html;
}

function wireActions(detail) {
  const approveBtn = document.getElementById("approve-btn");
  const approveEditsBtn = document.getElementById("approve-edits-btn");
  const rejectBtn = document.getElementById("reject-btn");
  const rejectBox = document.getElementById("reject-reason-box");
  const rejectReasonInput = document.getElementById("reject-reason");
  const confirmation = document.getElementById("decision-confirmation");
  const bodyTextarea = document.getElementById("draft-body");

  if (!detail.draft || detail.status === "reviewed") {
    return;
  }

  function disableAll() {
    approveBtn.disabled = true;
    approveEditsBtn.disabled = true;
    rejectBtn.disabled = true;
    rejectBox.hidden = true;
  }

  async function recordDecision(payload) {
    disableAll();
    try {
      await submitReview(detail.draft.id, payload);
      confirmation.hidden = false;
      confirmation.className = "confirmation";
      confirmation.textContent = "Decision recorded.";
    } catch (error) {
      confirmation.hidden = false;
      confirmation.className = "confirmation confirmation--error";
      confirmation.textContent = `Could not record decision: ${error.message}`;
      approveBtn.disabled = false;
      approveEditsBtn.disabled = false;
      rejectBtn.disabled = false;
    }
  }

  approveBtn.addEventListener("click", () => recordDecision({ action: "approve" }));

  approveEditsBtn.addEventListener("click", () =>
    recordDecision({ action: "approve_with_edits", edited_body: bodyTextarea.value })
  );

  rejectBtn.addEventListener("click", () => {
    if (rejectBox.hidden) {
      rejectBox.hidden = false;
      rejectBtn.textContent = "Confirm Reject";
      rejectReasonInput.focus();
      return;
    }
    recordDecision({ action: "reject", reason: rejectReasonInput.value });
  });
}

function showReviewPhase(detail) {
  livePhase.hidden = true;
  reviewPhase.hidden = false;

  renderStatusBanner(detail);
  renderDraftPanel(detail);
  renderReasoningTrail(detail);
  wireActions(detail);
}

async function pollStatus() {
  try {
    const status = await getRunStatus(runId);
    const detail = await getRunDetail(runId);

    const degradedStages = new Set(
      (detail.audit_log || [])
        .filter((entry) => entry.status === "degraded" || entry.status === "failed")
        .map((entry) => entry.stage)
    );

    renderStageList(status.current_stage, status.status, degradedStages);

    if (!NON_TERMINAL_STATUSES.has(status.status)) {
      if (pollTimer) {
        clearInterval(pollTimer);
        pollTimer = null;
      }
      showReviewPhase(detail);
    }
  } catch (error) {
    if (pollTimer) {
      clearInterval(pollTimer);
      pollTimer = null;
    }
    livePhase.hidden = true;
    loadError.hidden = false;
    loadError.textContent = `Could not load run: ${error.message}`;
  }
}

if (runId) {
  livePhase.hidden = false;
  pollStatus();
  pollTimer = setInterval(pollStatus, POLL_INTERVAL_MS);
}
