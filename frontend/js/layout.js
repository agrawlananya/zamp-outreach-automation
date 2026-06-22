const NAV_ITEMS = [
  { key: "dashboard", label: "Dashboard", icon: '<i class="ph ph-squares-four"></i>', href: "dashboard.html" },
  { key: "runs", label: "Run List", icon: '<i class="ph ph-list-dashes"></i>', href: "run-list.html" },
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
        <span class="sidebar__primary-action-icon"><i class="ph ph-plus"></i></span>
        <span class="sidebar__primary-action-label">New Research</span>
      </a>
      <div class="sidebar__section-label">Workspace</div>
      <nav class="sidebar__nav">${navHtml}</nav>
      <div class="sidebar__footer">
        <div class="sidebar__section-label">Appearance</div>
        <div class="theme-toggle" role="group" aria-label="Theme">
          <button type="button" class="theme-toggle__btn" data-theme-value="light">
            <span class="theme-toggle__icon" aria-hidden="true"><i class="ph ph-sun"></i></span>
            <span class="theme-toggle__label">Light</span>
          </button>
          <button type="button" class="theme-toggle__btn" data-theme-value="dark">
            <span class="theme-toggle__icon" aria-hidden="true"><i class="ph ph-moon"></i></span>
            <span class="theme-toggle__label">Dark</span>
          </button>
        </div>
      </div>
    </aside>
    <header class="topbar">
      <h1 class="topbar__title">${escapeHtml(title || "")}</h1>
    </header>
  `;

  initThemeToggle(mount);
}

function initThemeToggle(mount) {
  const buttons = mount.querySelectorAll(".theme-toggle__btn");
  if (!buttons.length) return;

  const getTheme = () => document.documentElement.dataset.theme || "dark";

  const sync = () => {
    const current = getTheme();
    buttons.forEach((btn) => {
      const isActive = btn.dataset.themeValue === current;
      btn.classList.toggle("theme-toggle__btn--active", isActive);
      btn.setAttribute("aria-pressed", String(isActive));
    });
  };

  buttons.forEach((btn) => {
    btn.addEventListener("click", () => {
      const next = btn.dataset.themeValue;
      document.documentElement.dataset.theme = next;
      try {
        localStorage.setItem("theme", next);
      } catch (e) {
        /* ignore storage failures — theme still applies for this session */
      }
      sync();
    });
  });

  sync();
}
