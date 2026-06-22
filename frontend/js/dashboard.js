import { getMetrics, getRuns, deleteRun } from "./api.js";

const RECENT_RUNS_COUNT = 6;
const COLUMNS = 6;

const metricsError = document.getElementById("metrics-error");
const recentRunsError = document.getElementById("recent-runs-error");
const recentRunsBody = document.getElementById("recent-runs-body");

function escapeHtml(value) {
  const div = document.createElement("div");
  div.textContent = value ?? "";
  return div.innerHTML;
}

function formatPercent(value) {
  return `${Math.round((value || 0) * 100)}%`;
}

function statusBadge(item) {
  const status = item.status;
  let label = (status || "").replace(/_/g, " ").toUpperCase();
  let cls = "badge--neutral";
  let dot = "";

  switch (status) {
    case "ready_for_review":
      label = "READY";
      cls = "badge--success";
      break;
    case "running":
      label = "RUNNING";
      cls = "badge--info";
      dot = '<span class="badge__dot"></span>';
      break;
    case "insufficient_signal":
      label = "INSUFFICIENT SIGNAL";
      cls = "badge--warning";
      break;
    case "needs_human_research":
      label = "NEEDS RESEARCH";
      cls = "badge--warning";
      break;
    case "failed":
      label = "FAILED";
      cls = "badge--danger";
      break;
    case "deprioritized":
      label = "DEPRIORITIZED";
      cls = "badge--neutral";
      break;
    case "pending":
      label = "PENDING";
      cls = "badge--neutral";
      break;
    case "reviewed":
      if (item.human_decision === "approve" || item.human_decision === "approve_with_edits") {
        label = "APPROVED";
        cls = "badge--success";
      } else if (item.human_decision === "reject") {
        label = "REJECTED";
        cls = "badge--danger";
      } else {
        label = "REVIEWED";
        cls = "badge--neutral";
      }
      break;
  }

  return `<span class="badge ${cls}">${dot}${escapeHtml(label)}</span>`;
}

function renderMetrics(metrics) {
  document.getElementById("metric-acceptance").textContent = formatPercent(metrics.acceptance_rate);
  document.getElementById("metric-groundedness").textContent = formatPercent(metrics.groundedness_pct);
  document.getElementById("metric-escalation").textContent = formatPercent(metrics.escalation_rate);
  document.getElementById("metric-time").textContent =
    metrics.avg_time_to_draft_ms != null ? `${(metrics.avg_time_to_draft_ms / 1000).toFixed(1)}s` : "—";
  document.getElementById("metric-depth").textContent =
    metrics.avg_personalization_depth != null ? `${metrics.avg_personalization_depth.toFixed(1)}/2` : "—";

  document.getElementById("metric-acceptance-sub").textContent =
    metrics.reviewed_count != null ? `${metrics.accepted_count} of ${metrics.reviewed_count} reviewed` : "";
  document.getElementById("metric-groundedness-sub").textContent =
    metrics.groundedness_drafts_total != null
      ? `${metrics.groundedness_drafts_pass}/${metrics.groundedness_drafts_total} drafts grounded`
      : "";
  document.getElementById("metric-escalation-sub").textContent =
    metrics.completed_count != null ? `${metrics.escalated_count} of ${metrics.completed_count} runs` : "";
}

function signalCell(item) {
  if (!item.signal_type) return '<span class="muted">—</span>';
  const domain = item.signal_source_domain ? ` · ${escapeHtml(item.signal_source_domain)}` : "";
  return `${escapeHtml(item.signal_type)}${domain}`;
}

function confidenceCell(item) {
  if (item.top_hook_score == null) return '<span class="muted">—</span>';
  return `${Math.round(item.top_hook_score * 100)}%`;
}

function renderRecentRuns(items) {
  if (!items.length) {
    recentRunsBody.innerHTML = `<tr class="table-empty-row"><td colspan="${COLUMNS}">No runs yet.</td></tr>`;
    return;
  }

  recentRunsBody.innerHTML = items
    .map(
      (item) => `<tr data-run-id="${item.id}" class="clickable-row">
        <td>${escapeHtml(item.prospect_name || "—")}</td>
        <td>${escapeHtml(item.company || "—")}</td>
        <td>${statusBadge(item)}</td>
        <td>${signalCell(item)}</td>
        <td>${confidenceCell(item)}</td>
        <td><button type="button" class="btn btn--danger btn--small delete-run-btn" data-run-id="${item.id}">Delete</button></td>
      </tr>`
    )
    .join("");

  recentRunsBody.querySelectorAll("tr.clickable-row").forEach((row) => {
    row.addEventListener("click", () => {
      window.location.href = `run.html?id=${row.dataset.runId}`;
    });
  });

  recentRunsBody.querySelectorAll(".delete-run-btn").forEach((btn) => {
    btn.addEventListener("click", async (event) => {
      event.stopPropagation();
      if (!window.confirm("Delete this research run? This cannot be undone from the UI.")) {
        return;
      }
      btn.disabled = true;
      try {
        await deleteRun(btn.dataset.runId);
        await loadRecentRuns();
      } catch (error) {
        recentRunsError.hidden = false;
        recentRunsError.textContent = `Could not delete run: ${error.message}`;
        btn.disabled = false;
      }
    });
  });
}

async function loadMetrics() {
  try {
    const metrics = await getMetrics();
    renderMetrics(metrics);
  } catch (error) {
    metricsError.hidden = false;
    metricsError.textContent = `Could not load metrics: ${error.message}`;
  }
}

async function loadRecentRuns() {
  try {
    const result = await getRuns({ per_page: RECENT_RUNS_COUNT });
    renderRecentRuns(result.items);
  } catch (error) {
    recentRunsError.hidden = false;
    recentRunsError.textContent = `Could not load recent runs: ${error.message}`;
    recentRunsBody.innerHTML = "";
  }
}

loadMetrics();
loadRecentRuns();
