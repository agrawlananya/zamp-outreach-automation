import { getRunStatus, getRunDetail, retryRun, submitReview } from "./api.js";

const BACKEND_STAGE_LABELS = {
  stage1_intake: "Intake & Normalize",
  stage2_research: "Web Research",
  stage3_role_confirmation: "Role Confirmation",
  stage4_extract_signals: "Extract Signals",
  stage5_validate_signals: "Validate Signals",
  stage6_persona_mapping: "Persona Mapping",
  stage7_pain_mapping: "Pain Mapping",
  stage8_hook_scoring: "Hook Scoring",
  stage9_draft_generation: "Draft Generation",
  stage10_quality_scoring: "Quality Scoring",
  stage11_routing: "Routing",
};

// 11 backend stages grouped into the 8 rows the UI shows (per shared context mapping).
const PIPELINE_GROUPS = [
  { label: "Intake & Parsing", stages: ["stage1_intake", "stage3_role_confirmation"] },
  { label: "Web Research", stages: ["stage2_research"] },
  { label: "Signal Extraction", stages: ["stage4_extract_signals"] },
  { label: "Signal Validation", stages: ["stage5_validate_signals"] },
  { label: "Persona & Pain Mapping", stages: ["stage6_persona_mapping", "stage7_pain_mapping"] },
  { label: "Hook Scoring & Selection", stages: ["stage8_hook_scoring"] },
  { label: "Draft Generation", stages: ["stage9_draft_generation"] },
  { label: "Quality Check & Scoring", stages: ["stage10_quality_scoring", "stage11_routing"] },
];

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
const viewLogsBtn = document.getElementById("view-logs-btn");
const logsPanel = document.getElementById("logs-panel");

let pollTimer = null;

if (viewLogsBtn && logsPanel) {
  viewLogsBtn.addEventListener("click", () => {
    logsPanel.hidden = !logsPanel.hidden;
  });
}

function escapeHtml(value) {
  const div = document.createElement("div");
  div.textContent = value ?? "";
  return div.innerHTML;
}

function formatScore(value) {
  return value === null || value === undefined ? "—" : Number(value).toFixed(2);
}

function formatLatency(ms) {
  if (ms === null || ms === undefined) return "";
  return ms >= 1000 ? `${(ms / 1000).toFixed(1)}s` : `${ms}ms`;
}

function formatTimestamp(value) {
  if (!value) return "—";
  return new Date(value).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" });
}

function getInitials(name) {
  if (!name) return "?";
  const parts = name.trim().split(/\s+/).filter(Boolean);
  if (!parts.length) return "?";
  const first = parts[0][0] || "";
  const last = parts.length > 1 ? parts[parts.length - 1][0] : "";
  return (first + last).toUpperCase();
}

function getDomain(url) {
  if (!url) return null;
  try {
    return new URL(url).hostname.replace(/^www\./, "");
  } catch (e) {
    return null;
  }
}

function safeParseArray(value) {
  if (!value) return [];
  try {
    const parsed = JSON.parse(value);
    return Array.isArray(parsed) ? parsed : [];
  } catch (e) {
    return [];
  }
}

function valenceTag(valence) {
  if (!valence) return "";
  return `<span class="tag tag--${escapeHtml(valence)}">${escapeHtml(valence)}</span>`;
}

function hookScoreCell(s) {
  const raw = formatScore(s.hook_score);
  const hasAdjustment =
    s.adjusted_hook_score !== null && s.adjusted_hook_score !== undefined && s.adjusted_hook_score !== s.hook_score;
  if (!hasAdjustment) {
    return raw;
  }
  const pct = s.hook_score ? Math.round((1 - s.adjusted_hook_score / s.hook_score) * 100) : 0;
  return `${raw} &rarr; ${formatScore(s.adjusted_hook_score)}${pct > 0 ? `<div class="score-adjusted">saturation -${pct}%</div>` : ""}`;
}

function signalStatusCell(s) {
  if (s.valence === "sensitive") {
    return "suppressed: sensitive";
  }
  return s.selected_as_hook ? "Selected" : "Considered — not selected";
}

// ============================================================
// Running state — header, execution pipeline, contextual signals
// ============================================================

function currentGroupIndex(currentStage) {
  const idx = PIPELINE_GROUPS.findIndex((g) => g.stages.includes(currentStage));
  return idx === -1 ? 0 : idx;
}

function renderRunHeader(detail, status) {
  const avatar = document.getElementById("run-avatar");
  const nameEl = document.getElementById("run-name");
  const metaEl = document.getElementById("run-meta");
  const stageCountEl = document.getElementById("run-stage-count");
  if (!avatar || !nameEl || !metaEl || !stageCountEl) return;

  avatar.textContent = getInitials(detail.prospect_name);
  nameEl.textContent = detail.prospect_name || "Prospect";

  const metaParts = [detail.prospect_title, detail.company_name].filter(Boolean);
  if (detail.persona_mapping && detail.persona_mapping.persona_name) {
    const assumed = detail.persona_mapping.is_assumed ? " (assumed)" : "";
    metaParts.push(`${detail.persona_mapping.persona_name}${assumed}`);
  }
  metaEl.textContent = metaParts.length ? metaParts.join(" · ") : "";

  const stageNumber = Math.min(currentGroupIndex(status.current_stage) + 1, PIPELINE_GROUPS.length);
  stageCountEl.textContent = `Stage ${stageNumber} of ${PIPELINE_GROUPS.length}`;
}

function latestAuditByStage(auditLog) {
  const map = new Map();
  (auditLog || []).forEach((entry) => {
    map.set(entry.stage, entry);
  });
  return map;
}

function renderPipelineExpand(detail) {
  const persona = detail.persona_mapping;
  if (!persona) return "";

  const kpis = safeParseArray(persona.kpis);
  const pains = safeParseArray(persona.pains);

  return `<div class="pipeline-expand">
    <h4>Matched Persona</h4>
    <div class="pipeline-expand__row">
      <strong>${escapeHtml(persona.persona_name || "—")}</strong>${persona.is_assumed ? ' <span class="tag">ASSUMED</span>' : ""}
    </div>
    ${
      kpis.length
        ? `<div class="pipeline-expand__row">KPIs<ul class="pipeline-expand__list">${kpis
            .map((k) => `<li>${escapeHtml(k)}</li>`)
            .join("")}</ul></div>`
        : ""
    }
    ${
      pains.length
        ? `<div class="pipeline-expand__row">Pain Points<ul class="pipeline-expand__list">${pains
            .map((p) => `<li>${escapeHtml(p)}</li>`)
            .join("")}</ul></div>`
        : ""
    }
  </div>`;
}

function renderPipeline(detail, status) {
  const container = document.getElementById("pipeline-list");
  if (!container) return;

  const auditByStage = latestAuditByStage(detail.audit_log);
  const activeGroupIndex = currentGroupIndex(status.current_stage);
  const isLive = NON_TERMINAL_STATUSES.has(status.status);

  container.innerHTML = PIPELINE_GROUPS.map((group, index) => {
    const entries = group.stages.map((s) => auditByStage.get(s)).filter(Boolean);
    const isDegraded = entries.some((e) => e.status === "degraded" || e.status === "failed");
    const isActive = !isDegraded && index === activeGroupIndex && isLive;
    const isDone = !isDegraded && !isActive && (index < activeGroupIndex || (index === activeGroupIndex && !isLive));

    let stateClass = "queued";
    let icon = "";
    let meta = "";

    if (isDegraded) {
      stateClass = "degraded";
      icon = "&#9650;";
      meta = "Degraded";
    } else if (isActive) {
      stateClass = "active";
      meta = "Running…";
    } else if (isDone) {
      stateClass = "done";
      icon = "&#10003;";
      const totalLatency = entries.reduce((sum, e) => sum + (e.latency_ms || 0), 0);
      meta = entries.length ? formatLatency(totalLatency) : "";
    }

    const rowClass = `stage-row${isActive ? " stage-row--active" : ""}${stateClass === "queued" ? " stage-row--queued" : ""}`;
    const expandHtml = isActive ? renderPipelineExpand(detail) : "";

    return `<div class="pipeline-group">
      <div class="${rowClass}">
        <span class="stage-row__icon stage-row__icon--${stateClass}">${icon}</span>
        <span class="stage-row__label">${escapeHtml(group.label)}</span>
        <span class="stage-row__meta">${escapeHtml(meta)}</span>
      </div>
      ${expandHtml}
    </div>`;
  }).join("");
}

function renderSignalsPanel(detail) {
  const container = document.getElementById("signals-list");
  if (!container) return;

  const signals = detail.signals || [];

  if (!signals.length) {
    container.innerHTML = `<p class="signals-empty">No signals extracted yet.</p>`;
    return;
  }

  container.innerHTML = signals
    .map((s) => {
      const domain = getDomain(s.source_url);
      const sourceLine = s.source_url
        ? `<span class="snippet__source">${escapeHtml(domain || "")}${domain ? " · " : ""}<a href="${escapeHtml(s.source_url)}" target="_blank" rel="noopener">${escapeHtml(s.source_url)}</a></span>`
        : "";
      const snippet = s.source_snippet ? `<div class="snippet">${escapeHtml(s.source_snippet)}</div>` : "";

      return `<div class="signal-card">
        <div class="signal-card__label">${escapeHtml(s.claim || s.type || "Signal")}</div>
        ${sourceLine}
        ${snippet}
      </div>`;
    })
    .join("");
}

function renderLogsPanel(detail) {
  const body = document.getElementById("logs-body");
  if (!body) return;

  const entries = detail.audit_log || [];

  if (!entries.length) {
    body.innerHTML = `<tr class="table-empty-row"><td colspan="4">No log entries yet.</td></tr>`;
    return;
  }

  body.innerHTML = entries
    .map(
      (e) => `<tr>
        <td>${escapeHtml(BACKEND_STAGE_LABELS[e.stage] || e.stage || "—")}</td>
        <td>${escapeHtml((e.status || "—").toUpperCase())}</td>
        <td>${formatLatency(e.latency_ms)}</td>
        <td>${formatTimestamp(e.created_at)}</td>
      </tr>`
    )
    .join("");
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
    const derivedConsequence = detail.draft && detail.draft.derived_consequence;
    html += `<div class="trail-block">
      <h3>Chosen Hook</h3>
      ${
        derivedConsequence
          ? `<p class="derived-consequence">${escapeHtml(derivedConsequence)}</p>
             <p class="muted raw-claim-context">from: ${escapeHtml(hookSignal.claim)} — used as context, not the hook.</p>`
          : `<p class="claim">${escapeHtml(hookSignal.claim)}</p>`
      }
      <p class="muted">Hook score: <strong>${hookScoreCell(hookSignal)}</strong> · Type: ${escapeHtml(hookSignal.type)} ${valenceTag(hookSignal.valence)}</p>
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
        <tr><th>Claim</th><th>Status</th><th>Valence</th><th>Rel.</th><th>Spec.</th><th>Rec.</th><th>Act.</th><th>Ver.</th><th>Hook</th></tr>
      </thead>
      <tbody>
        ${detail.signals
          .map(
            (s) => `<tr class="${s.selected_as_hook ? "row--selected" : s.valence === "sensitive" ? "row--suppressed" : ""}">
          <td>${escapeHtml(s.claim)}</td>
          <td>${signalStatusCell(s)}</td>
          <td>${valenceTag(s.valence)}</td>
          <td>${formatScore(s.relevance_score)}</td>
          <td>${formatScore(s.specificity_score)}</td>
          <td>${formatScore(s.recency_score)}</td>
          <td>${formatScore(s.actionability_score)}</td>
          <td>${formatScore(s.verifiability_score)}</td>
          <td>${hookScoreCell(s)}</td>
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

function renderAnnotatedBody(detail) {
  const container = document.getElementById("annotated-body");
  if (!container) return;

  let bodySentences = [];
  try {
    bodySentences = detail.draft && detail.draft.body_sentences ? JSON.parse(detail.draft.body_sentences) : [];
  } catch (error) {
    bodySentences = [];
  }

  if (!bodySentences.length) {
    container.hidden = true;
    container.innerHTML = "";
    return;
  }

  const byParagraph = new Map();
  bodySentences.forEach((s) => {
    if (!byParagraph.has(s.paragraph)) byParagraph.set(s.paragraph, []);
    byParagraph.get(s.paragraph).push(s);
  });

  const paragraphsHtml = [...byParagraph.keys()]
    .sort((a, b) => a - b)
    .map((p) => {
      const sentences = byParagraph
        .get(p)
        .map((s) => {
          const isInference = s.type === "inference";
          const cls = isInference ? "sentence--inference" : "sentence--fact";
          const title = isInference ? "inference — not directly sourced" : "fact — sourced from the selected hook signal";
          return `<span class="${cls}" title="${escapeHtml(title)}">${escapeHtml(s.text)}</span>`;
        })
        .join(" ");
      return `<p>${sentences}</p>`;
    })
    .join("");

  container.hidden = false;
  container.innerHTML = `<h3>Fact / Inference Preview</h3>${paragraphsHtml}`;
}

function renderRoleConfirmationNote(detail) {
  const note = document.getElementById("role-confirmation-note");
  if (!note) return;

  const rc = detail.role_confirmation;
  if (!rc || (!rc.title_corrected && !rc.new_in_role)) {
    note.hidden = true;
    note.textContent = "";
    return;
  }

  const parts = [];
  if (rc.title_corrected) {
    parts.push(`Title corrected from "${rc.input_title}" to "${rc.confirmed_title}".`);
  }
  if (rc.new_in_role) {
    parts.push(`New in role (~${rc.tenure_days} days) — hooked on new mandate, not past performance.`);
  }

  note.hidden = false;
  note.textContent = parts.join(" ");
}

function renderFixtureBadge(detail) {
  const badge = document.getElementById("fixture-badge");
  if (!badge) return;
  badge.hidden = !detail.is_fixture;
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

  approveEditsBtn.addEventListener("click", () => {
    if (approveEditsBtn.textContent !== "Confirm Edits") {
      approveEditsBtn.textContent = "Confirm Edits";
      bodyTextarea.focus();
      return;
    }
    recordDecision({ action: "approve_with_edits", edited_body: bodyTextarea.value });
  });

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
  renderRoleConfirmationNote(detail);
  renderDraftPanel(detail);
  renderAnnotatedBody(detail);
  renderReasoningTrail(detail);
  renderFixtureBadge(detail);
  wireActions(detail);
}

async function pollStatus() {
  try {
    const status = await getRunStatus(runId);
    const detail = await getRunDetail(runId);

    renderFixtureBadge(detail);

    if (NON_TERMINAL_STATUSES.has(status.status)) {
      renderRunHeader(detail, status);
      renderPipeline(detail, status);
      renderSignalsPanel(detail);
      renderLogsPanel(detail);
    } else {
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
