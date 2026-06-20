import { getRuns } from "./api.js";

const PER_PAGE = 20;

const tableBody = document.getElementById("run-list-body");
const loadError = document.getElementById("load-error");
const searchInput = document.getElementById("search-input");
const statusFilter = document.getElementById("status-filter");
const sortSelect = document.getElementById("sort-select");
const exportBtn = document.getElementById("export-btn");
const prevPageBtn = document.getElementById("prev-page-btn");
const nextPageBtn = document.getElementById("next-page-btn");
const paginationInfo = document.getElementById("pagination-info");

const COLUMNS = 8;

let currentItems = [];
let total = 0;
let page = 1;

function escapeHtml(value) {
  const div = document.createElement("div");
  div.textContent = value ?? "";
  return div.innerHTML;
}

function formatRelativeTime(dateStr) {
  if (!dateStr) return "—";
  const date = new Date(dateStr);
  const diffSec = Math.floor((Date.now() - date.getTime()) / 1000);
  if (diffSec < 60) return "just now";
  const diffMin = Math.floor(diffSec / 60);
  if (diffMin < 60) return `${diffMin}m ago`;
  const diffHr = Math.floor(diffMin / 60);
  if (diffHr < 24) return `${diffHr}h ago`;
  const diffDay = Math.floor(diffHr / 24);
  if (diffDay < 30) return `${diffDay}d ago`;
  return date.toLocaleDateString();
}

function scoreBarFillClass(ratio) {
  if (ratio >= 0.7) return "score-bar__fill--high";
  if (ratio >= 0.45) return "score-bar__fill--mid";
  return "score-bar__fill--low";
}

function personaCell(item) {
  if (!item.persona_name) return '<span class="muted">—</span>';
  const assumedPill = item.persona_assumed ? ' <span class="badge badge--neutral">Assumed</span>' : "";
  return `${escapeHtml(item.persona_name)}${assumedPill}`;
}

function groundednessCell(item) {
  if (item.groundedness_pct === null || item.groundedness_pct === undefined) {
    return '<span class="muted">—</span>';
  }
  const ratio = item.groundedness_pct / 100;
  const fillClass = scoreBarFillClass(ratio);
  const fraction =
    item.groundedness_total !== null && item.groundedness_total !== undefined
      ? ` · ${item.groundedness_grounded ?? 0}/${item.groundedness_total}`
      : "";
  return `<span class="score-bar">
    <span class="score-bar__track"><span class="score-bar__fill ${fillClass}" style="width:${Math.round(ratio * 100)}%"></span></span>
    <span class="score-bar__value">${item.groundedness_pct}%${fraction}</span>
  </span>`;
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

function rowAccentClass(status) {
  return status === "insufficient_signal" || status === "failed" ? " row--danger-accent" : "";
}

function matchesSearch(item, query) {
  if (!query) return true;
  const haystack = `${item.prospect_name || ""} ${item.company || ""}`.toLowerCase();
  return haystack.includes(query);
}

function getDisplayRows() {
  const query = searchInput.value.trim().toLowerCase();
  return currentItems.filter((item) => matchesSearch(item, query));
}

function renderTable() {
  const rows = getDisplayRows();

  if (!rows.length) {
    tableBody.innerHTML = `<tr class="table-empty-row"><td colspan="${COLUMNS}">No runs match your filters.</td></tr>`;
    return;
  }

  tableBody.innerHTML = rows
    .map((item) => {
      return `<tr data-run-id="${item.id}" class="clickable-row${rowAccentClass(item.status)}">
        <td>${escapeHtml(item.prospect_name || "—")}</td>
        <td>${escapeHtml(item.title || "—")}</td>
        <td>${escapeHtml(item.company || "—")}</td>
        <td>${personaCell(item)}</td>
        <td>${statusBadge(item)}</td>
        <td>${groundednessCell(item)}</td>
        <td>${item.personalization_depth ?? "—"}</td>
        <td>${escapeHtml(formatRelativeTime(item.created_at))}</td>
      </tr>`;
    })
    .join("");

  tableBody.querySelectorAll("tr.clickable-row").forEach((row) => {
    row.addEventListener("click", () => {
      window.location.href = `run.html?id=${row.dataset.runId}`;
    });
  });
}

function renderPagination() {
  const start = total === 0 ? 0 : (page - 1) * PER_PAGE + 1;
  const end = Math.min(page * PER_PAGE, total);
  paginationInfo.textContent = total === 0 ? "0 runs" : `Showing ${start}–${end} of ${total} runs`;
  prevPageBtn.disabled = page <= 1;
  nextPageBtn.disabled = end >= total;
}

async function loadRuns() {
  tableBody.innerHTML = `<tr class="table-loading-row"><td colspan="${COLUMNS}">Loading runs…</td></tr>`;
  loadError.hidden = true;

  const params = { page, per_page: PER_PAGE, sort: sortSelect.value };
  if (statusFilter.value) {
    params.status = statusFilter.value;
  }

  try {
    const result = await getRuns(params);
    currentItems = result.items;
    total = result.total;
    page = result.page;
    renderTable();
    renderPagination();
  } catch (error) {
    loadError.hidden = false;
    loadError.textContent = `Could not load runs: ${error.message}`;
    tableBody.innerHTML = "";
    paginationInfo.textContent = "";
  }
}

function exportCsv() {
  const rows = getDisplayRows();
  const header = [
    "Prospect",
    "Title",
    "Company",
    "Persona",
    "Persona Assumed",
    "Status",
    "Groundedness %",
    "Groundedness Grounded",
    "Groundedness Total",
    "Personalization Depth",
    "Updated",
  ];
  const csvRows = rows.map((item) =>
    [
      item.prospect_name || "",
      item.title || "",
      item.company || "",
      item.persona_name || "",
      item.persona_assumed ? "yes" : "no",
      item.status || "",
      item.groundedness_pct ?? "",
      item.groundedness_grounded ?? "",
      item.groundedness_total ?? "",
      item.personalization_depth ?? "",
      item.created_at || "",
    ]
      .map((value) => `"${String(value).replace(/"/g, '""')}"`)
      .join(",")
  );

  const csv = [header.join(","), ...csvRows].join("\n");
  const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = "run-list-export.csv";
  link.click();
  URL.revokeObjectURL(url);
}

searchInput.addEventListener("input", renderTable);
statusFilter.addEventListener("change", () => {
  page = 1;
  loadRuns();
});
sortSelect.addEventListener("change", () => {
  page = 1;
  loadRuns();
});
exportBtn.addEventListener("click", exportCsv);
prevPageBtn.addEventListener("click", () => {
  if (page > 1) {
    page -= 1;
    loadRuns();
  }
});
nextPageBtn.addEventListener("click", () => {
  if (page * PER_PAGE < total) {
    page += 1;
    loadRuns();
  }
});

loadRuns();
