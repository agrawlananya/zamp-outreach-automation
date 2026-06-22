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
    text: (detail) =>
      detail.escalation_reason ||
      "Signal strength was too low to generate a confident draft. Manual research recommended.",
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

const REVIEW_ACTION_LABELS = {
  approve: "Approved",
  approve_with_edits: "Approved with Edits",
  reject: "Rejected",
};

// Stages where a halted/degraded run still shows the pipeline recap (per audit_log).
const DEGRADED_TERMINAL_STATUSES = new Set(["insufficient_signal", "needs_human_research", "failed"]);

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

function formatDateTime(value) {
  if (!value) return "—";
  return new Date(value).toLocaleString([], {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
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

function scoreTier(value) {
  if (value === null || value === undefined) return "low";
  if (value >= 0.7) return "high";
  if (value >= 0.45) return "mid";
  return "low";
}

function renderScoreBar(value) {
  const tier = scoreTier(value);
  const pct = Math.max(0, Math.min(1, value || 0)) * 100;
  return `<span class="score-bar">
    <span class="score-bar__track"><span class="score-bar__fill score-bar__fill--${tier}" style="width:${pct}%"></span></span>
    <span class="score-bar__value">${formatScore(value)}</span>
  </span>`;
}

function hookScoreText(s) {
  const raw = formatScore(s.hook_score);
  const hasAdjustment =
    s.adjusted_hook_score !== null && s.adjusted_hook_score !== undefined && s.adjusted_hook_score !== s.hook_score;
  if (!hasAdjustment) return raw;
  const pct = s.hook_score ? Math.round((1 - s.adjusted_hook_score / s.hook_score) * 100) : 0;
  return `${raw} &rarr; ${formatScore(s.adjusted_hook_score)}${pct > 0 ? `<span class="score-adjusted"> (saturation -${pct}%)</span>` : ""}`;
}

function valenceTag(valence) {
  if (!valence) return "";
  return `<span class="tag tag--${escapeHtml(valence)}">${escapeHtml(valence)}</span>`;
}

function candidateFlag(s) {
  if (s.valence === "sensitive") {
    return { cls: "suppressed", label: "Suppressed — sensitive" };
  }
  if (s.selected_as_hook) {
    return { cls: "selected", label: "&#10003; Selected" };
  }
  if (s.recency_score !== null && s.recency_score !== undefined && s.recency_score < 0.45) {
    return { cls: "low-recency", label: "Low recency" };
  }
  return { cls: "considered", label: "Considered" };
}

function buildCitationIndex(bodySentences) {
  const order = [];
  (bodySentences || []).forEach((s) => {
    if (s.signal_id && !order.includes(s.signal_id)) order.push(s.signal_id);
  });
  return new Map(order.map((id, index) => [id, index + 1]));
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

function renderPipeline(detail, status, containerId = "pipeline-list") {
  const container = document.getElementById(containerId);
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

    return `<div class="pipeline-group">
      <div class="${rowClass}">
        <span class="stage-row__icon stage-row__icon--${stateClass}">${icon}</span>
        <span class="stage-row__label">${escapeHtml(group.label)}</span>
        <span class="stage-row__meta">${escapeHtml(meta)}</span>
      </div>
    </div>`;
  }).join("");
}

function renderPipelineRecap(detail) {
  const card = document.getElementById("pipeline-recap-card");
  if (!card) return;

  if (!DEGRADED_TERMINAL_STATUSES.has(detail.status)) {
    card.hidden = true;
    return;
  }

  card.hidden = false;
  renderPipeline(detail, { status: detail.status, current_stage: detail.current_stage }, "pipeline-recap-list");
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

function copyDraftText(detail) {
  if (!detail.draft) return "";
  const body = detail.review_action && detail.review_action.edited_body ? detail.review_action.edited_body : detail.draft.body || "";
  return `Subject: ${detail.draft.subject || ""}\n\n${body}`;
}

function wireCopyButton(btnId, detail) {
  const btn = document.getElementById(btnId);
  if (!btn) return;
  // Icon buttons flash a title/tooltip; text buttons swap their label.
  const isIcon = btn.classList.contains("icon-btn");
  btn.addEventListener("click", async () => {
    try {
      await navigator.clipboard.writeText(copyDraftText(detail));
      if (isIcon) {
        btn.classList.add("icon-btn--copied");
        const originalTitle = btn.title;
        btn.title = "Copied!";
        setTimeout(() => {
          btn.classList.remove("icon-btn--copied");
          btn.title = originalTitle;
        }, 1500);
      } else {
        const original = btn.textContent;
        btn.textContent = "Copied!";
        setTimeout(() => {
          btn.textContent = original;
        }, 1500);
      }
    } catch (error) {
      if (!isIcon) btn.textContent = "Copy failed";
    }
  });
}

function renderReviewedBanner(detail) {
  const banner = document.getElementById("status-banner");
  const action = detail.review_action ? detail.review_action.action : null;
  const isApproval = action === "approve" || action === "approve_with_edits";

  banner.hidden = false;
  banner.className = `banner ${isApproval ? "banner--green" : "banner--neutral"}`;

  const title = action === "reject" ? "Decision Recorded" : "Approval Confirmed";
  const subtextParts = [REVIEW_ACTION_LABELS[action] || "Reviewed"];
  if (detail.review_action && detail.review_action.reviewed_at) {
    subtextParts.push(formatDateTime(detail.review_action.reviewed_at));
  }
  if (detail.review_action && detail.review_action.reason) {
    subtextParts.push(`Reason: ${detail.review_action.reason}`);
  }

  const copyButtonHtml = detail.draft
    ? `<button id="copy-draft-btn" class="btn btn--secondary btn--small">Copy draft</button>`
    : "";

  banner.innerHTML = `
    <div class="banner__text">
      <div class="banner__title">${escapeHtml(title)}</div>
      <div class="banner__subtext">${escapeHtml(subtextParts.join(" · "))}</div>
    </div>
    ${copyButtonHtml}
  `;

  wireCopyButton("copy-draft-btn", detail);
}

function renderStatusBanner(detail) {
  const banner = document.getElementById("status-banner");

  if (detail.status === "reviewed") {
    renderReviewedBanner(detail);
    return;
  }

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

function parseBodySentences(draft) {
  if (!draft || !draft.body_sentences) return [];
  try {
    const parsed = JSON.parse(draft.body_sentences);
    return Array.isArray(parsed) ? parsed : [];
  } catch (e) {
    return [];
  }
}

function groundednessFromSentences(draft) {
  if (!draft) return { grounded: 0, total: 0, pct: 0 };
  const sentences = parseBodySentences(draft);
  if (!sentences.length) {
    return draft.groundedness_pass ? { grounded: 1, total: 1, pct: 100 } : { grounded: 0, total: 1, pct: 0 };
  }
  const facts = sentences.filter((s) => s.type === "fact");
  const total = facts.length;
  const grounded = facts.filter((s) => s.signal_id).length;
  const pct = total ? Math.round((100 * grounded) / total) : 0;
  return { grounded, total, pct };
}

function groundednessTier(pct, failed) {
  if (failed || pct < 45) return "low";
  return pct < 70 ? "mid" : "high";
}

function renderGroundednessMeter(detail) {
  const meter = document.getElementById("groundedness-meter");
  if (!meter) return;

  if (!detail.draft) {
    meter.hidden = true;
    meter.innerHTML = "";
    return;
  }

  const failed = detail.draft.groundedness_pass === false;
  const { grounded, total, pct } = groundednessFromSentences(detail.draft);
  const tier = groundednessTier(pct, failed);

  const segments =
    total > 0
      ? Array.from(
          { length: total },
          (_, i) =>
            `<span class="groundedness-meter__seg groundedness-meter__seg--${i < grounded ? "fill" : "empty"}"></span>`
        ).join("")
      : `<span class="groundedness-meter__seg groundedness-meter__seg--empty"></span>`;

  let caption;
  if (failed) {
    caption = total
      ? `Groundedness check failed — ${grounded} of ${total} claims traced.`
      : "Groundedness check failed. Review carefully before sending.";
  } else if (total === 0) {
    caption = "No factual claims to trace.";
  } else {
    caption = `All ${grounded} of ${total} claims traced to a verified source.`;
  }

  meter.hidden = false;
  meter.className = `groundedness-meter groundedness-meter--${tier}`;
  meter.innerHTML = `
    <div class="groundedness-meter__top">
      <span class="groundedness-meter__label">Groundedness</span>
      <span class="groundedness-meter__pct">${total === 0 ? "—" : `${pct}%`}</span>
    </div>
    <div class="groundedness-meter__bars">${segments}</div>
    <p class="groundedness-meter__caption">${escapeHtml(caption)}</p>
  `;
}

function renderDraftBody(detail, citationIndex) {
  const container = document.getElementById("draft-body-rendered");

  if (!detail.draft) {
    container.innerHTML = `<p>(No draft was generated for this run.)</p>`;
    return;
  }

  // The approved text of record for "approve_with_edits" — draft.body is never mutated by
  // the review endpoint, only review_actions.edited_body carries what was actually approved.
  const editedBody = detail.status === "reviewed" && detail.review_action ? detail.review_action.edited_body : null;
  if (editedBody) {
    container.innerHTML = editedBody
      .split(/\n{2,}/)
      .map((p) => `<p>${escapeHtml(p)}</p>`)
      .join("");
    return;
  }

  const sentences = parseBodySentences(detail.draft);

  if (!sentences.length) {
    container.innerHTML = (detail.draft.body || "")
      .split(/\n{2,}/)
      .map((p) => `<p>${escapeHtml(p)}</p>`)
      .join("");
    return;
  }

  const byParagraph = new Map();
  sentences.forEach((s) => {
    if (!byParagraph.has(s.paragraph)) byParagraph.set(s.paragraph, []);
    byParagraph.get(s.paragraph).push(s);
  });

  // body_sentences only carries the LLM-written core paragraphs — the greeting and sign-off
  // are assembled deterministically server-side into draft.body, so pull them from there.
  const bodyParagraphs = (detail.draft.body || "").split(/\n{2,}/);
  const greeting = bodyParagraphs[0] || "";
  const signoff = bodyParagraphs[bodyParagraphs.length - 1] || "";

  const coreHtml = [...byParagraph.keys()]
    .sort((a, b) => a - b)
    .map((p) => {
      const inner = byParagraph
        .get(p)
        .map((s) => {
          const isInference = s.type === "inference";
          const cls = isInference ? "sentence--inference" : "sentence--fact";
          const title = isInference ? "inference — not directly sourced" : "fact — sourced from the selected hook signal";
          const n = s.signal_id ? citationIndex.get(s.signal_id) : null;
          const marker = n ? `<a href="#source-S${n}" class="citation">S${n}</a>` : "";
          return `<span class="${cls}" title="${escapeHtml(title)}">${escapeHtml(s.text)}</span>${marker}`;
        })
        .join(" ");
      return `<p>${inner}</p>`;
    })
    .join("");

  container.innerHTML =
    `<p>${escapeHtml(greeting)}</p>` + coreHtml + `<p>${escapeHtml(signoff).replace(/\n/g, "<br>")}</p>`;
}

function renderDraftRecipient(detail) {
  const el = document.getElementById("draft-recipient");
  if (!el) return;
  const parts = [detail.prospect_title, detail.company_name].filter(Boolean).join(", ");
  el.textContent = detail.prospect_name ? `Recipient: ${detail.prospect_name}${parts ? ` · ${parts}` : ""}` : "";
}

function renderDraftPanel(detail, citationIndex) {
  const subjectInput = document.getElementById("draft-subject");
  const bodyTextarea = document.getElementById("draft-body");
  const bodyRendered = document.getElementById("draft-body-rendered");
  const actionsRow = document.getElementById("draft-actions");
  const isReviewed = detail.status === "reviewed";
  const isLocked = isReviewed || !detail.draft;

  subjectInput.value = detail.draft ? detail.draft.subject || "" : "";
  bodyTextarea.value = detail.draft ? detail.draft.body || "" : "";
  subjectInput.disabled = isLocked;

  bodyRendered.hidden = false;
  bodyTextarea.hidden = true;
  renderDraftBody(detail, citationIndex);
  renderDraftRecipient(detail);

  actionsRow.hidden = isReviewed;
  document.getElementById("approve-btn").disabled = isLocked;
  document.getElementById("approve-edits-btn").disabled = isLocked;
  document.getElementById("reject-btn").disabled = isLocked;
  if (isLocked) {
    document.getElementById("approve-edits-btn").textContent = "Approve with Edits";
    document.getElementById("reject-btn").textContent = "Reject";
  }
}

function renderWebResearchCollapsible(detail, citationIndex) {
  const signalById = new Map(detail.signals.map((s) => [s.id, s]));
  const entries = [...citationIndex.entries()].sort((a, b) => a[1] - b[1]);

  const summaryContent = `<span style="display:flex; align-items:center; gap:8px;"><i class="ph ph-check" style="color: var(--success); font-size: 14px; stroke-width: 2px;"></i> Web Research</span>`;

  if (!entries.length) {
    return `<details class="trail-collapsible" open>
      <summary>${summaryContent}</summary>
      <div class="trail-collapsible__body">
        <p class="muted">No sources were cited in this draft.</p>
      </div>
    </details>`;
  }

  const cards = entries
    .map(([signalId, n]) => {
      const s = signalById.get(signalId);
      if (!s) return "";
      const domain = getDomain(s.source_url);
      const sourceLine = s.source_url
        ? `<span class="snippet__source">${escapeHtml(domain || "")}${domain ? " · " : ""}<a href="${escapeHtml(s.source_url)}" target="_blank" rel="noopener">${escapeHtml(s.source_url)}</a></span>`
        : `<span class="snippet__source muted">(no source URL)</span>`;
      const snippet = s.source_snippet ? `<div class="snippet">${escapeHtml(s.source_snippet)}</div>` : "";
      return `<div class="source-card" id="source-S${n}">
        <div><span class="citation-tag">S${n}</span>${sourceLine}</div>
        ${snippet}
      </div>`;
    })
    .join("");

  return `<details class="trail-collapsible" open>
    <summary>${summaryContent}</summary>
    <div class="trail-collapsible__body">
      ${cards}
    </div>
  </details>`;
}

function renderHookScoringCollapsible(detail) {
  const ordered = [...detail.signals].sort((a, b) => {
    if (a.selected_as_hook !== b.selected_as_hook) return a.selected_as_hook ? -1 : 1;
    const sa = a.adjusted_hook_score ?? a.hook_score ?? 0;
    const sb = b.adjusted_hook_score ?? b.hook_score ?? 0;
    return sb - sa;
  });

  const candidates = ordered
    .map((s) => {
      const flag = candidateFlag(s);
      const finalScore = s.adjusted_hook_score ?? s.hook_score ?? 0;
      const isSelected = flag.cls === "selected";
      return `<div class="hook-candidate${isSelected ? " hook-candidate--selected" : ""}">
        <p class="hook-candidate__claim">${escapeHtml(s.claim)}</p>
        <div class="hook-candidate__meta">
          <span class="hook-candidate__flag hook-candidate__flag--${flag.cls}">${flag.label}</span>
          ${valenceTag(s.valence)}
          <div style="margin-left: auto; display: flex; align-items: center; gap: 8px;">
            <span style="font-family:var(--font-mono); font-size:11px; color:var(--text-muted); text-transform:uppercase;">HOOK</span>
            ${renderScoreBar(finalScore)}
          </div>
        </div>
        ${s.adjusted_hook_score !== null && s.adjusted_hook_score !== undefined && s.adjusted_hook_score !== s.hook_score ? `<p class="hook-candidate__adjustment score-adjusted">raw ${hookScoreText(s)}</p>` : ""}
        <div class="hook-candidate__axes">
          <span class="score-tag"><span class="score-tag__label">REL</span><span class="score-tag__value">${formatScore(s.relevance_score)}</span></span>
          <span class="score-tag"><span class="score-tag__label">SPEC</span><span class="score-tag__value">${formatScore(s.specificity_score)}</span></span>
          <span class="score-tag"><span class="score-tag__label">REC</span><span class="score-tag__value">${formatScore(s.recency_score)}</span></span>
          <span class="score-tag"><span class="score-tag__label">ACT</span><span class="score-tag__value">${formatScore(s.actionability_score)}</span></span>
          <span class="score-tag"><span class="score-tag__label">VER</span><span class="score-tag__value">${formatScore(s.verifiability_score)}</span></span>
        </div>
      </div>`;
    })
    .join("");

  const summaryContent = `<span style="display:flex; align-items:center; gap:8px;"><i class="ph ph-check" style="color: var(--success); font-size: 14px; stroke-width: 2px;"></i> Hook Scoring</span>`;

  return `<details class="trail-collapsible" open>
    <summary>${summaryContent}</summary>
    <div class="trail-collapsible__body">
      <p class="muted trail-caption" style="margin-top: 0; margin-bottom: 12px;">5 axes &rarr; REL &middot; SPEC &middot; REC &middot; ACT &middot; VER. HOOK = weighted composite.</p>
      ${candidates}
    </div>
  </details>`;
}

function renderPersonaMatchCollapsible(detail) {
  const persona = detail.persona_mapping;
  if (!persona) return "";

  const goals = safeParseArray(persona.goals);
  const pains = safeParseArray(persona.pains);
  const kpis = safeParseArray(persona.kpis);

  return `<details class="trail-collapsible">
    <summary>Persona Match</summary>
    <div class="trail-collapsible__body">
      <p><strong>${escapeHtml(persona.persona_name || "—")}</strong>${persona.is_assumed ? ' <span class="tag">ASSUMED</span>' : ""}</p>
      ${goals.length ? `<p class="muted">Goals</p><ul class="trail-collapsible__list">${goals.map((g) => `<li>${escapeHtml(g)}</li>`).join("")}</ul>` : ""}
      ${pains.length ? `<p class="muted">Pains</p><ul class="trail-collapsible__list">${pains.map((p) => `<li>${escapeHtml(p)}</li>`).join("")}</ul>` : ""}
      ${kpis.length ? `<p class="muted">KPIs</p><ul class="trail-collapsible__list">${kpis.map((k) => `<li>${escapeHtml(k)}</li>`).join("")}</ul>` : ""}
    </div>
  </details>`;
}

function renderDraftGenerationCollapsible(detail) {
  if (!detail.draft) return "";

  const hookSignal = detail.signals.find((s) => s.selected_as_hook);
  const pain = hookSignal ? detail.pain_mappings.find((pm) => pm.signal_id === hookSignal.id) : null;

  return `<details class="trail-collapsible">
    <summary>Draft Generation</summary>
    <div class="trail-collapsible__body">
      <p class="muted">Framework: hook &rarr; value &rarr; call-to-action (3 paragraphs).</p>
      ${detail.draft.derived_consequence ? `<p><strong>Derived consequence:</strong> ${escapeHtml(detail.draft.derived_consequence)}</p>` : ""}
      ${pain ? `<p><strong>Value prop used:</strong> ${escapeHtml(pain.zamp_value_prop || "—")}${pain.owned_pain ? ` (pain: ${escapeHtml(pain.owned_pain)})` : ""}${pain.owned_kpi ? ` (KPI: ${escapeHtml(pain.owned_kpi)})` : ""}</p>` : ""}
    </div>
  </details>`;
}

function renderGroundednessCheckCollapsible(detail) {
  const signalById = new Map(detail.signals.map((s) => [s.id, s]));
  const sentences = parseBodySentences(detail.draft);
  const grounded = sentences.filter((s) => s.type === "fact" && s.signal_id);

  return `<details class="trail-collapsible">
    <summary>Groundedness Check</summary>
    <div class="trail-collapsible__body">
      ${
        grounded.length
          ? `<ul class="trail-collapsible__list">${grounded
              .map((s) => {
                const signal = signalById.get(s.signal_id);
                const domain = signal ? getDomain(signal.source_url) : null;
                const link = signal && signal.source_url
                  ? `<a href="${escapeHtml(signal.source_url)}" target="_blank" rel="noopener">${escapeHtml(domain || signal.source_url)}</a>`
                  : "(no source)";
                return `<li>${escapeHtml(s.text)} — ${link}</li>`;
              })
              .join("")}</ul>`
          : `<p class="muted">No grounded claims found.</p>`
      }
    </div>
  </details>`;
}

function renderReasoningTrail(detail) {
  const container = document.getElementById("reasoning-trail");
  const citationIndex = buildCitationIndex(parseBodySentences(detail.draft));

  container.innerHTML =
    renderWebResearchCollapsible(detail, citationIndex) +
    renderHookScoringCollapsible(detail) +
    renderPersonaMatchCollapsible(detail) +
    renderDraftGenerationCollapsible(detail) +
    renderGroundednessCheckCollapsible(detail);
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
  const bodyRendered = document.getElementById("draft-body-rendered");

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
      const updated = await getRunDetail(runId);
      showReviewPhase(updated);
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
      bodyRendered.hidden = true;
      bodyTextarea.hidden = false;
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

  const citationIndex = buildCitationIndex(parseBodySentences(detail.draft));

  renderStatusBanner(detail);
  renderRoleConfirmationNote(detail);
  renderPipelineRecap(detail);
  renderDraftPanel(detail, citationIndex);
  renderGroundednessMeter(detail);
  renderReasoningTrail(detail);
  renderFixtureBadge(detail);
  wireActions(detail);
  wireCopyButton("copy-draft-header", detail);
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
