const NAV_ITEMS = [
  { key: "dashboard", label: "Dashboard", icon: "D", href: "dashboard.html" },
  { key: "runs", label: "Run List", icon: "R", href: "run-list.html" },
];

function escapeHtml(value) {
  const div = document.createElement("div");
  div.textContent = value ?? "";
  return div.innerHTML;
}

export function renderLayout({ active, title }) {
  const mount = document.getElementById("app-shell");
  if (!mount) return;

  const navHtml = NAV_ITEMS.map((item) => {
    const isActive = item.key === active;
    return `<a href="${item.href}" class="sidebar-nav-item${isActive ? " sidebar-nav-item--active" : ""}">
      <span class="sidebar-nav-item__icon">${item.icon}</span>
      <span class="sidebar-nav-item__label">${escapeHtml(item.label)}</span>
    </a>`;
  }).join("");

  mount.innerHTML = `
    <aside class="sidebar">
      <div class="sidebar__brand">
        <span class="sidebar__mark">Z</span>
        <div class="sidebar__brand-text">
          <div class="sidebar__brand-name">Zamp AI SDR</div>
          <div class="sidebar__eyebrow">Analytical Research</div>
        </div>
      </div>
      <a href="index.html" class="sidebar__primary-action">
        <span class="sidebar__primary-action-icon">+</span>
        <span class="sidebar__primary-action-label">New Research</span>
      </a>
      <div class="sidebar__section-label">Workspace</div>
      <nav class="sidebar__nav">${navHtml}</nav>
    </aside>
    <header class="topbar">
      <h1 class="topbar__title">${escapeHtml(title || "")}</h1>
    </header>
  `;
}
