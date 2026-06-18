import { getMetrics, getRuns } from "./api.js";

const STATUS_BADGE_CLASS = {
  pending: "badge badge--pending",
  running: "badge badge--running",
  ready_for_review: "badge badge--ready",
  insufficient_signal: "badge badge--insufficient",
  needs_human_research: "badge badge--needs-research",
  deprioritized: "badge badge--deprioritized",
  failed: "badge badge--failed",
  reviewed: "badge badge--reviewed",
};

const statusFilter = document.getElementById("status-filter");
const tableBody = document.getElementById("runs-table-body");

let currentRuns = [];
let sortKey = "created_at";
let sortAsc = false;

function escapeHtml(value) {
  const div = document.createElement("div");
  div.textContent = value ?? "";
  return div.innerHTML;
}

function formatPercent(value) {
  return `${Math.round((value || 0) * 100)}%`;
}

function renderMetrics(metrics) {
  document.getElementById("metric-acceptance").textContent = formatPercent(metrics.acceptance_rate);
  document.getElementById("metric-groundedness").textContent = formatPercent(metrics.groundedness_pct);
  document.getElementById("metric-escalation").textContent = formatPercent(metrics.escalation_rate);
  document.getElementById("metric-time").textContent =
    metrics.avg_time_to_draft_ms != null ? `${Math.round(metrics.avg_time_to_draft_ms)} ms` : "—";
  document.getElementById("metric-depth").textContent = (metrics.avg_personalization_depth || 0).toFixed(2);
}

function renderTable() {
  const rows = [...currentRuns].sort((a, b) => {
    const av = a[sortKey];
    const bv = b[sortKey];
    if (av === null || av === undefined) return 1;
    if (bv === null || bv === undefined) return -1;
    if (av < bv) return sortAsc ? -1 : 1;
    if (av > bv) return sortAsc ? 1 : -1;
    return 0;
  });

  tableBody.innerHTML = rows
    .map((run) => {
      const badgeClass = STATUS_BADGE_CLASS[run.status] || "badge";
      const date = run.created_at ? new Date(run.created_at).toLocaleString() : "—";
      const hookScore = run.top_hook_score == null ? "—" : Number(run.top_hook_score).toFixed(2);
      const timeToDraft = run.time_to_draft_ms == null ? "—" : `${run.time_to_draft_ms} ms`;
      return `<tr data-run-id="${run.id}" class="clickable-row">
        <td>${escapeHtml(run.prospect_name || "—")}</td>
        <td>${escapeHtml(run.company || "—")}</td>
        <td><span class="${badgeClass}">${escapeHtml(run.status)}</span></td>
        <td>${hookScore}</td>
        <td>${timeToDraft}</td>
        <td>${escapeHtml(run.human_decision || "—")}</td>
        <td>${escapeHtml(date)}</td>
      </tr>`;
    })
    .join("");

  tableBody.querySelectorAll("tr.clickable-row").forEach((row) => {
    row.addEventListener("click", () => {
      window.location.href = `run.html?id=${row.dataset.runId}`;
    });
  });
}

document.querySelectorAll("#runs-table th[data-sort]").forEach((th) => {
  th.addEventListener("click", () => {
    const key = th.dataset.sort;
    sortAsc = sortKey === key ? !sortAsc : true;
    sortKey = key;
    renderTable();
  });
});

async function loadRuns() {
  const params = { page: 1, per_page: 20 };
  if (statusFilter.value) {
    params.status = statusFilter.value;
  }
  const result = await getRuns(params);
  currentRuns = result.items;
  renderTable();
}

statusFilter.addEventListener("change", loadRuns);

async function init() {
  const [metrics] = await Promise.all([getMetrics(), loadRuns()]);
  renderMetrics(metrics);
}

init();
