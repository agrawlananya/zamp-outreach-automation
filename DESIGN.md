---
version: alpha
name: Zamp AI SDR
description: >
  Internal B2B decision-support tool for Zamp's sales team. Produces grounded,
  source-backed outbound email drafts with a full visible reasoning trail.
  Designed for trust, density, and speed — not decoration. Human reviews every
  draft before anything is sent; the reasoning trail is co-equal with the output.

colors:
  # ─── Dual-theme palette ────────────────────────────────────────────────────
  # The product ships two themes — DARK (default) and LIGHT — toggled via a
  # [data-theme] attribute on <html> and persisted in localStorage. Token NAMES
  # are identical across themes; only their values change (see frontend/css/
  # tokens.css). Each `value` below is the DARK (default) value; the light-theme
  # counterpart is given as "Light: #xxxxxx" in the description.
  #
  # Accent is indigo: #7c83ff (dark) / #4b44d6 (light) — replacing the former
  # royal-blue brand accent #2347E5. Typeface is IBM Plex Sans / IBM Plex Mono.
  # Semantic status colors (success, warning, danger) sit outside the brand
  # palette but are retained for functional run-outcome signalling.

  # Interactive accent
  primary:
    value: "#7c83ff"
    description: >
      Indigo accent. The sole interactive action color — used exclusively for
      primary buttons, hyperlinks, focus rings, and active-state indicators.
      One accent per view; never diluted or repurposed for decoration.
      Light: #4b44d6.
  primary-hover:
    value: "#aeb3ff"
    description: >
      Accent hover/pressed state for primary interactive elements. In dark mode
      the accent lightens on hover; in light mode it darkens. Never used as a
      standalone fill color. Light: #3a34b8.
  primary-subtle:
    value: "#1c2129"
    description: >
      Low-emphasis accent surface. Used for selected-row highlight backgrounds,
      hover states on ghost/text buttons, and focus-area tints. Light: #edeef1.

  # Brand anchors
  secondary:
    value: "#0c0e12"
    description: >
      Ink. Near-black page anchor in the dark theme and the deepest tonal step.
      In the light theme this resolves to the primary ink text color.
      Light: #16181d.
  tertiary:
    value: "#38c08a"
    description: >
      Approve green. Not in the brand palette; retained as a product-level
      semantic token for the Approve action only. Its uniqueness reinforces the
      gravity of approval. Never used for any other positive or decorative state.
      Light: #1f9d61.

  # Surfaces & backgrounds
  neutral:
    value: "#0c0e12"
    description: >
      Page-level background for all screens. Surface elevation must stay legible
      through tonal contrast against the card surface — never set a card to the
      same value as the page. Light: #f1f2f4.
  surface:
    value: "#161a20"
    description: >
      Card / panel surface. The primary content container, set against the page
      background to establish the first tonal elevation step. Light: #fcfcfd.
  surface-raised:
    value: "#1c2129"
    description: >
      Nested surface within cards — table header rows, expanded pipeline stage
      panels, and snippet block backgrounds. The second tonal elevation step,
      achieved without shadows. Light: #e3e4e8.

  # Borders & dividers
  border:
    value: "#232a33"
    description: >
      Default 1px border for cards and structural dividers. Tonal and
      low-contrast — defines layout structure without visual weight.
      Light: #e2e3e7.
  border-strong:
    value: "#3a4049"
    description: >
      Emphasis border. Used for input field borders, table row separators, and
      any divider that needs to be legible against surface-raised backgrounds.
      Light: #c8ccd2.

  # Text
  text-primary:
    value: "#e9ebf1"
    description: >
      All primary readable content — headings, body copy, labels, and data
      values. The highest-contrast text token in each theme. Light: #16181d.
  text-secondary:
    value: "#c8cdd6"
    description: >
      Supporting text — field labels, captions, metadata rows, and secondary
      data values. Meets WCAG AA on both the page and card surfaces.
      Light: #5c616a.
  text-muted:
    value: "#737b89"
    description: >
      Placeholder text, disabled-state labels, timestamps, and decorative
      separators. Intentionally low-contrast — never use for content the user
      must read to complete a task. Light: #83888f.

  # Semantic status colors
  status-success:
    value: "#38c08a"
    description: >
      Semantic success green. Used for the Approve button fill, READY badge
      text, score-bar-high, and completed pipeline stage icons. Also maps to
      tertiary. Never repurposed for non-approval positive states. Light: #1f9d61.
  status-success-bg:
    value: "#1c2129"
    description: >
      Background fill for success badges and banners. Always paired with
      status-success text to meet contrast requirements. Light: #e7f4ec.
  status-warning:
    value: "#e0a93c"
    description: >
      Semantic warning amber. Used for INSUFFICIENT SIGNAL and NEEDS RESEARCH
      badge text, score-bar-mid, and degraded pipeline stage icons. Light: #b9770a.
  status-warning-bg:
    value: "#1c2129"
    description: >
      Background fill for warning badges and banners. Always paired with
      status-warning text. Light: #fbf1dd.
  status-danger:
    value: "#f06a5d"
    description: >
      Semantic danger red. Used for FAILED badge text, score-bar-low, the
      Reject button border and text, and error-state input borders. The only
      permitted uses of red in the product. Light: #d1453b.
  status-danger-bg:
    value: "#1c2129"
    description: >
      Background fill for danger badges, banners, and inline error messages.
      Always paired with status-danger text. Light: #fdf3f2.
  status-info:
    value: "#7c83ff"
    description: >
      Mirrors primary (indigo accent). Used for RUNNING badge text and info
      banners. Intentionally the same as primary to maintain a single accent in
      the system. Light: #4b44d6.
  status-info-bg:
    value: "#1c2129"
    description: >
      Matches primary-subtle. Background fill for info badges and RUNNING status
      banners. Always paired with status-info text. Light: #edeef1.
  status-neutral:
    value: "#9aa0a8"
    description: >
      Used for REVIEWED badge text and neutral/inactive state indicators.
      Communicates completion without a positive or negative valence.
      Light: #5c616a.
  status-neutral-bg:
    value: "#1c2129"
    description: >
      Background fill for neutral badges. Low visual weight — used for states
      that need labelling but not emphasis. Light: #edeef1.

  # Sidebar — theme-scoped (dark sidebar in dark theme, light sidebar in light)
  sidebar-bg:
    value: "#0e1116"
    description: >
      Fixed left sidebar background. Follows the active theme — a near-black
      panel in dark mode, a near-white panel (with a 1px right divider) in light
      mode. Light: #fcfcfd.
  sidebar-text:
    value: "#9aa0a8"
    description: >
      Inactive navigation item labels and supporting sidebar metadata. Meets
      WCAG AA on sidebar-bg in both themes. Light: #5c616a.
  sidebar-text-active:
    value: "#e9ebf1"
    description: >
      Active navigation item label and brand wordmark color. Maximum contrast
      against sidebar-bg in each theme. Light: #16181d.
  sidebar-active-bg:
    value: "#1c2129"
    description: >
      Background fill for the active or hovered navigation item, and the base of
      the theme-toggle control. One tonal step from sidebar-bg — no border or
      shadow needed to distinguish the active item. Light: #edeef1.

  # Score bars
  score-high:
    value: "#38c08a"
    description: >
      Matches status-success. Applied to score bars when the hook score is
      ≥ 0.7 — a strong, research-backed signal likely ready for review.
      Light: #1f9d61.
  score-mid:
    value: "#e0a93c"
    description: >
      Matches status-warning. Applied to score bars when the hook score is
      between 0.45 and 0.69 — a marginal signal where human review especially
      matters. Light: #b9770a.
  score-low:
    value: "#f06a5d"
    description: >
      Matches status-danger. Applied to score bars when the hook score is
      < 0.45 — insufficient signal; the run routes to insufficient_signal rather
      than generating a confident draft. Light: #d1453b.

  # Source snippet blocks
  snippet-bg:
    value: "#1c2129"
    description: >
      Matches surface-raised. The background of verbatim source snippet blocks.
      Visually separates quoted, human-authored source text from AI-generated
      prose — a primary trust signal in the product. The contrast step against
      the card surface must stay perceptible. Light: #edeef1.
  snippet-border:
    value: "#2a313b"
    description: >
      The 1px border on snippet blocks. Reinforces the visual boundary between
      snippet content and surrounding card prose. Light: #c8ccd2.

typography:
  # ─── Brand spec ─────────────────────────────────────────────────────────────
  # Grotesque sans, weight 500 (headlines) / 400 (body). IBM Plex Sans is used as
  # the grotesque sans throughout — a humanist grotesque with strong legibility
  # at the small sizes this product requires.
  # IBM Plex Mono is reserved for source snippets and the email draft body only.
  #
  # Product exception: the brand spec says "never ALL CAPS in copy." This product
  # uses uppercase in two non-prose contexts only — badge labels and table column
  # headers — as a metadata legibility signal. This is an intentional override,
  # documented here so it is not mistaken for brand non-compliance.

  display:
    fontFamily: IBM Plex Sans
    fontSize: 24px
    fontWeight: 500
    lineHeight: 1.2
    letterSpacing: -0.02em
    description: >
      Page-level titles and the primary metric value in dashboard cards.
      Tight letter-spacing (-0.02em) gives a compressed, data-terminal feel
      at large sizes. Never used for subheadings or section labels.

  headline-lg:
    fontFamily: IBM Plex Sans
    fontSize: 20px
    fontWeight: 500
    lineHeight: 1.3
    letterSpacing: -0.01em
    description: >
      Card-level headings and modal titles. Slightly looser tracking than
      display. Used when a section needs a strong heading but the display
      size would be too heavy.

  headline-md:
    fontFamily: IBM Plex Sans
    fontSize: 16px
    fontWeight: 500
    lineHeight: 1.4
    description: >
      Section headings within cards — e.g., "Reasoning Trail," "Draft Email,"
      "Signal Hooks." The workhorse heading size for the two-column review
      layout. No letter-spacing adjustment at this size.

  headline-sm:
    fontFamily: IBM Plex Sans
    fontSize: 14px
    fontWeight: 500
    lineHeight: 1.4
    description: >
      Button labels, table column headers, and the active sidebar nav item.
      The minimum size at which weight 500 reads as a heading rather than
      bold body text. Never use for running prose.

  body-lg:
    fontFamily: IBM Plex Sans
    fontSize: 15px
    fontWeight: 400
    lineHeight: 1.6
    description: >
      Primary reading text for the reasoning trail prose and any explanation
      copy that runs longer than two lines. The 1.6 line-height is essential
      for scanning dense signal summaries without losing place.

  body-md:
    fontFamily: IBM Plex Sans
    fontSize: 14px
    fontWeight: 400
    lineHeight: 1.6
    description: >
      Default body text. Used for pipeline stage descriptions, signal source
      labels, form field values, and most supporting prose. The base text size
      for the product.

  body-sm:
    fontFamily: IBM Plex Sans
    fontSize: 13px
    fontWeight: 400
    lineHeight: 1.5
    description: >
      Supporting metadata — timestamps, source domain labels above snippet
      blocks, helper text below form fields, and inline error messages.
      Not for primary reading; information at this size supports, not leads.

  label-md:
    fontFamily: IBM Plex Sans
    fontSize: 12px
    fontWeight: 500
    lineHeight: 1
    letterSpacing: 0.06em
    description: >
      Table column headers and section sub-labels within cards. Uppercase.
      Generous tracking (0.06em) ensures legibility at 12px. Use only for
      structural metadata labels — not for prose or inline emphasis.

  label-sm:
    fontFamily: IBM Plex Sans
    fontSize: 11px
    fontWeight: 500
    lineHeight: 1
    letterSpacing: 0.08em
    description: >
      Badge text for all run-status pills and signal-type tags. Uppercase.
      Maximum letter-spacing (0.08em) keeps the all-caps label readable at
      the smallest label size in the system. Never use for anything outside
      pill badges and compact inline tags.

  mono:
    fontFamily: "IBM Plex Mono, ui-monospace, monospace"
    fontSize: 13px
    fontWeight: 400
    lineHeight: 1.6
    description: >
      Source snippet blocks. The monospace treatment makes it immediately
      obvious that this is verbatim, unedited source material — not AI-generated
      prose. This distinction is a core trust signal in the product. Never use
      mono for AI-generated text outside the email draft body.

  email-body:
    fontFamily: "IBM Plex Mono, ui-monospace, monospace"
    fontSize: 14px
    fontWeight: 400
    lineHeight: 1.7
    description: >
      Generated email draft body text. Monospace signals "this is an artifact
      under review" — it subtly communicates draft status without requiring an
      explicit label. Slightly larger and looser than mono to support the longer
      continuous reading required to review a full email draft.

rounded:
  # ─── Corner radius scale ─────────────────────────────────────────────────────
  # Shape language is softly angular — modern enough to feel current, restrained
  # enough to feel like a data tool, not a consumer app.
  # Never use radii above xl (12px) on structural containers.
  # Never mix 0px (sharp) with any rounded value in the same view.

  none:
    value: 0px
    description: >
      Sharp corners. Not used in the standard component set — reserved only
      for explicit overrides where a flush edge is required (e.g., a full-bleed
      table row with no card wrapping).

  sm:
    value: 4px
    description: >
      Micro-rounding for compact inline elements: tags inside table cells,
      inline code spans, and compact badge variants that appear within dense
      data rows. Distinguishable from sharp but with minimal visual softness.

  md:
    value: 6px
    description: >
      The default interactive-element radius. Applied to all buttons, text
      inputs, select menus, and dropdown panels. Consistent across every
      interactive control to create a unified tactile feel.

  lg:
    value: 8px
    description: >
      Card and modal container radius. The primary structural container shape.
      Soft enough to feel modern; angular enough to read as a data container
      rather than a consumer card.

  xl:
    value: 12px
    description: >
      Larger contextual panels — info banners, status alert boxes, empty-state
      containers, and onboarding callouts. The maximum radius permitted on
      structural containers. Do not exceed this on any layout-level element.

  full:
    value: 9999px
    description: >
      Pill badges only. The fully rounded pill shape is reserved exclusively
      for run-status badges and signal-type tags. Its distinctiveness from all
      other rounded values makes status scannable at a glance in dense tables.
      Never apply to buttons, cards, or inputs.

spacing:
  # ─── 8px grid ────────────────────────────────────────────────────────────────
  # All spacing values are multiples of 8px. The 4px half-step (xs) is permitted
  # only for micro-adjustments within compact components. Never use ad-hoc values
  # outside this scale.

  xs:
    value: 4px
    description: >
      Half-step. Used only for micro-adjustments within compact components —
      icon-to-label gaps, badge internal padding, and tight inline separators.
      Not for layout spacing between components.

  sm:
    value: 8px
    description: >
      Base grid unit. Used for tight spacing between related inline elements —
      e.g., the gap between a score bar and its numeric label, or between a
      status dot and badge text.

  md:
    value: 16px
    description: >
      Standard internal component spacing. Used for padding within table cells,
      spacing between a label and its input, and gaps between stacked inline
      elements within a card section.

  lg:
    value: 24px
    description: >
      Section-level spacing. The gap between distinct sections within a card,
      and the vertical rhythm between stacked cards on a page. Also the standard
      card padding (see card-padding).

  xl:
    value: 32px
    description: >
      Large section breaks. Used between major page sections — e.g., the gap
      between the metrics row and the prospect table on the dashboard, or
      between the top bar and the first content card.

  2xl:
    value: 48px
    description: >
      Extra-large page-level spacing. Used for top and bottom page padding on
      content-heavy screens, and for vertical spacing around empty states and
      onboarding elements.

  3xl:
    value: 64px
    description: >
      Maximum spacing unit. Used sparingly — only for the outer vertical margin
      on full-page empty states and the top padding on the login/onboarding
      screen. Never used within card layouts.

  sidebar-width:
    value: 240px
    description: >
      Fixed width of the left navigation sidebar at standard viewport (≥ 1024px).
      Collapses to 48px (icon-only) at viewports below 1024px. All content-area
      width calculations must account for this offset.

  topbar-height:
    value: 56px
    description: >
      Fixed height of the top bar. Present on every screen. All scrollable
      content areas must be offset by this value to avoid content appearing
      behind the top bar.

  card-padding:
    value: 24px
    description: >
      Internal padding applied uniformly to all card components (top, right,
      bottom, left). Matches spacing.lg to keep the spacing scale internally
      consistent. Never reduce card padding for density — use table rows
      instead of cards when vertical space is constrained.

  row-height:
    value: 40px
    description: >
      Fixed height for table rows throughout the product. Dense enough to
      display 15–20 rows on a standard laptop without scrolling. Applies to
      the prospect queue table, signal hooks table, and any other tabular layout.

  gutter:
    value: 24px
    description: >
      The horizontal gap between the two columns on the Review screen (draft
      column / reasoning trail column) and between cards in multi-column grid
      layouts. Consistent with card-padding to maintain rhythmic visual spacing.

  max-content:
    value: 1280px
    description: >
      Maximum width of the scrollable content area, centered with auto horizontal
      margins. Prevents line lengths from becoming unreadable on wide displays
      and keeps the two-column review layout proportional.

components:
  # ─── Buttons ────────────────────────────────────────────────────────────────

  button-primary:
    description: >
      The single most important action on a screen — "Start Research,"
      "Confirm & Approve," "Retry." Maximum one primary button per screen
      section. Brand Accent fill with Paper text. Disabled state: 40% opacity,
      no pointer, no hover.
    backgroundColor: "{colors.primary}"
    textColor: "{colors.surface}"
    typography: "{typography.headline-sm}"
    rounded: "{rounded.md}"
    padding: "10px 18px"

  button-primary-hover:
    description: >
      Hover and pressed state for button-primary. Darkened Accent fill.
      Applied via :hover and :active pseudo-classes — not a standalone component.
    backgroundColor: "{colors.primary-hover}"

  button-secondary:
    description: >
      Supporting actions that appear alongside a primary or success button —
      "Approve with Edits," "Cancel," "Export," "View Source." Paper background
      with a strong border. Never the most prominent action on screen.
    backgroundColor: "{colors.surface}"
    textColor: "{colors.text-primary}"
    typography: "{typography.headline-sm}"
    rounded: "{rounded.md}"
    padding: "10px 18px"
    borderColor: "{colors.border-strong}"

  button-success:
    description: >
      The Approve action only. Forest green fill with Paper text. This button
      variant is reserved exclusively for run approval — its color is never
      repurposed for other positive actions. Its uniqueness reinforces the
      gravity of the approval decision in the review workflow.
    backgroundColor: "{colors.status-success}"
    textColor: "{colors.surface}"
    typography: "{typography.headline-sm}"
    rounded: "{rounded.md}"
    padding: "10px 18px"

  button-danger:
    description: >
      The Reject action only. Outlined destructive button — danger-colored
      border and label text over a Paper background. Less visually loud than
      a filled red button; clearly negative without dominating the screen.
      Never used for non-destructive actions.
    backgroundColor: "{colors.surface}"
    textColor: "{colors.status-danger}"
    typography: "{typography.headline-sm}"
    rounded: "{rounded.md}"
    padding: "10px 18px"
    borderColor: "{colors.status-danger}"

  # ─── Inputs ─────────────────────────────────────────────────────────────────

  input:
    description: >
      Standard text input for the prospect intake form (name, title, company).
      Paper background, Ink text, Mist border at rest. No filled or tinted
      background variants — all inputs are white-on-border.
    backgroundColor: "{colors.surface}"
    textColor: "{colors.text-primary}"
    typography: "{typography.body-md}"
    rounded: "{rounded.md}"
    padding: "10px 14px"
    borderColor: "{colors.border}"

  input-focus:
    description: >
      Focus state for all input fields. Border transitions to Brand Accent to
      signal keyboard focus clearly. No background tint change — the border
      alone carries the focus signal.
    borderColor: "{colors.primary}"

  # ─── Badges ─────────────────────────────────────────────────────────────────
  # All badges are pill-shaped (rounded.full), uppercase label-sm text, with
  # a color-matched soft background tint. The pill shape is reserved exclusively
  # for status badges — do not apply rounded.full to any other component.

  badge-success:
    description: >
      READY status. Indicates a run with a strong signal (hook score ≥ 0.45),
      a generated draft, and a passing groundedness check. The most positive
      state in the run lifecycle — green fill reflects approval-readiness.
    backgroundColor: "{colors.status-success-bg}"
    textColor: "{colors.status-success}"
    typography: "{typography.label-sm}"
    rounded: "{rounded.full}"
    padding: "3px 10px"

  badge-warning:
    description: >
      INSUFFICIENT SIGNAL status. Indicates a run where the top hook score
      fell below 0.45. An honest fallback state — no fabricated draft is shown.
      Amber signals the user to either enrich the prospect data or deprioritize.
    backgroundColor: "{colors.status-warning-bg}"
    textColor: "{colors.status-warning}"
    typography: "{typography.label-sm}"
    rounded: "{rounded.full}"
    padding: "3px 10px"

  badge-danger:
    description: >
      FAILED status. An unrecoverable pipeline error after retries. Red signals
      that no output was produced and no action can be taken on this run without
      manual intervention or a retry trigger.
    backgroundColor: "{colors.status-danger-bg}"
    textColor: "{colors.status-danger}"
    typography: "{typography.label-sm}"
    rounded: "{rounded.full}"
    padding: "3px 10px"

  badge-info:
    description: >
      RUNNING status. Indicates an active in-progress pipeline run. Brand Accent
      text on a subtle Accent tint. The dot indicator within this badge should
      carry a subtle CSS pulse animation to reinforce the live state — the only
      animation permitted in the product.
    backgroundColor: "{colors.status-info-bg}"
    textColor: "{colors.status-info}"
    typography: "{typography.label-sm}"
    rounded: "{rounded.full}"
    padding: "3px 10px"

  badge-neutral:
    description: >
      REVIEWED status. Indicates a run that has been actioned by a human
      (approved, approved with edits, or rejected). Slate text on Mist
      background — low visual weight signals a terminal, non-urgent state.
    backgroundColor: "{colors.status-neutral-bg}"
    textColor: "{colors.status-neutral}"
    typography: "{typography.label-sm}"
    rounded: "{rounded.full}"
    padding: "3px 10px"

  # ─── Cards ──────────────────────────────────────────────────────────────────

  card:
    description: >
      The standard content container. Paper background, 1px Mist border, 8px
      radius, 24px internal padding. Used for every major content unit — the
      prospect intake form, the review columns, the dashboard metric row, and
      the pipeline stage panel. Cards never nest inside other cards.
    backgroundColor: "{colors.surface}"
    rounded: "{rounded.lg}"
    padding: "{spacing.card-padding}"
    borderColor: "{colors.border}"

  # ─── Source snippet block ────────────────────────────────────────────────────

  snippet-block:
    description: >
      Verbatim source text extracted during research. The raised surface
      background and monospace font distinguish quoted source material from
      AI-generated prose — a core trust signal in the product. Every snippet
      block must be preceded by a domain label and source URL in body-sm text.
      The block itself is not clickable; the link above it is. Never show a
      snippet without attribution.
    backgroundColor: "{colors.snippet-bg}"
    textColor: "{colors.text-secondary}"
    typography: "{typography.mono}"
    rounded: "{rounded.md}"
    padding: "12px 14px"
    borderColor: "{colors.snippet-border}"

  # ─── Score bars ─────────────────────────────────────────────────────────────

  score-bar-high:
    description: >
      Hook score ≥ 0.7. Green fill signals a strong, research-backed signal.
      Always rendered alongside the numeric score value — never show the bar
      alone without the number.
    backgroundColor: "{colors.score-high}"
    height: 4px
    rounded: "{rounded.full}"

  score-bar-mid:
    description: >
      Hook score 0.45–0.69. Amber fill signals a marginal signal — the draft
      may be generated but human scrutiny of the reasoning trail is especially
      important at this range.
    backgroundColor: "{colors.score-mid}"
    height: 4px
    rounded: "{rounded.full}"

  score-bar-low:
    description: >
      Hook score < 0.45. Red fill signals insufficient signal — the run will
      route to insufficient_signal status and no confident draft will be shown.
      Red here is a data-driven indicator, not a destructive action color; it
      is the only context outside error/danger states where red is permitted.
    backgroundColor: "{colors.score-low}"
    height: 4px
    rounded: "{rounded.full}"

  # ─── Sidebar navigation ─────────────────────────────────────────────────────

  sidebar-nav-item:
    description: >
      Inactive navigation item in the fixed left sidebar. Slate-equivalent text
      over the Ink background. Padding provides a comfortable tap/click target.
      On hover, background transitions to sidebar-active-bg without text color
      change.
    textColor: "{colors.sidebar-text}"
    typography: "{typography.body-md}"
    padding: "10px 16px"
    rounded: "{rounded.md}"

  sidebar-nav-item-active:
    description: >
      Active navigation item. Ink-lightened background fill with Paper text —
      maximum contrast to clearly indicate the current screen. Typography steps
      up to headline-sm (weight 500) to reinforce active state without relying
      on color alone.
    backgroundColor: "{colors.sidebar-active-bg}"
    textColor: "{colors.sidebar-text-active}"
    typography: "{typography.headline-sm}"
---

# Zamp AI SDR — Design System

## Overview

Zamp AI SDR is an internal B2B decision-support tool for a sales team. The visual language is rooted in **Institutional Precision** — the aesthetic of a high-quality financial data terminal crossed with a modern internal tool. Think Linear, Retool, or a Bloomberg terminal redesigned for clarity.

The product's core value is trust. Every design decision must reinforce that the data shown is real, sourced, and verified — never fabricated. This means the UI earns credibility through restraint and density, not through flashy AI aesthetics (no glowing gradients, no animated blobs, no "AI sparkle" iconography).

The tool has a non-technical primary user: an SDR or AE who reviews AI-generated email drafts. They need to feel confident that every claim in the email is backed by evidence — and the UI must make that evidence effortless to see and verify. The reasoning trail is not a sidebar footnote; it is co-equal with the output.

**Primary design goals, in order:**

1. Trust — the interface communicates that the AI's work is traceable and verifiable
2. Speed — a user can review and approve a draft in under 60 seconds
3. Clarity — every element has an obvious purpose; nothing is decorative
4. Density — fits meaningful data without feeling cramped; 8px grid, generous card padding

## Colors

The product ships **two themes — Dark (default) and Light** — built on a single set of token names whose values swap per theme (see the Theming section). The accent is **indigo** (`#7c83ff` dark / `#4b44d6` light), replacing the former royal-blue brand accent. Semantic status colors (success green, warning amber, danger red) sit outside the brand palette and are retained as functional overrides in both themes.

The bullets below describe each token by role; values are listed as **dark / light**.

- **Primary / Accent (#7c83ff / #4b44d6):** Indigo accent — used exclusively for primary interactive actions (buttons, links, focus rings, active states). One action color per view, never diluted.
- **Primary Subtle (#1c2129 / #edeef1):** Low-emphasis accent surface — hover backgrounds on primary elements and selected row highlights.
- **Tertiary / Approve (#38c08a / #1f9d61):** Approve-green — approve/success states only. Retained for the semantic weight of the approval action; never used for decoration.
- **Page background (#0c0e12 / #f1f2f4):** The base layer for all screens. Card surfaces sit one tonal step above; never set a card to the page value.
- **Surface / Card (#161a20 / #fcfcfd):** Cards and raised content panels only.
- **Surface Raised (#1c2129 / #e3e4e8):** Nested surfaces inside cards — table headers, expanded stage panels, snippet blocks.
- **Text Primary (#e9ebf1 / #16181d):** All primary readable content.
- **Text Secondary (#c8cdd6 / #5c616a):** Supporting labels, captions, and metadata.
- **Text Muted (#737b89 / #83888f):** Placeholder text, disabled states, timestamps.
- **Status colors:** Four semantic roles — Success (#38c08a / #1f9d61), Warning (#e0a93c / #b9770a), Danger (#f06a5d / #d1453b), Info = accent (#7c83ff / #4b44d6). In the dark theme all status *background* tints collapse to the raised surface (#1c2129) and the status text color carries the meaning; in the light theme each has a soft colored tint (e.g. success #e7f4ec, warning #fbf1dd, danger #fdf3f2).
- **Snippet Background (#1c2129 / #edeef1):** A distinct surface for verbatim source snippet blocks inside cards. Visually separates AI-generated prose from human-authored source text — a critical trust signal in this product.

## Theming

The interface supports a **Dark** theme (default) and a **Light** theme. Both are defined as token sets in [`frontend/css/tokens.css`](frontend/css/tokens.css): theme-agnostic tokens (radii, spacing, layout dimensions, font families) live in `:root`, and each theme overrides the color tokens under `:root[data-theme="dark"]` and `:root[data-theme="light"]`.

- **Switching:** the active theme is set via a `data-theme` attribute on the `<html>` element. A toggle in the sidebar footer flips it and persists the choice to `localStorage` under the key `theme`. A tiny inline script in each page's `<head>` applies the stored theme before first paint, so there is no flash of the wrong theme on load.
- **Default:** Dark. If no preference is stored (or storage is unavailable), the app renders the dark theme.
- **Same names, different values:** because both themes share token names, all component CSS is written once against the tokens — no theme-specific component rules are needed. The only theme-aware exceptions are the per-theme token values themselves.
- **Sidebar follows the theme:** the sidebar is a dark panel in the dark theme and a near-white panel (with a 1px right divider) in the light theme — there is no dark sidebar on a light page.

| Token | Dark (default) | Light |
|---|---|---|
| Page background | `#0c0e12` | `#f1f2f4` |
| Card surface | `#161a20` | `#fcfcfd` |
| Raised surface / snippet | `#1c2129` | `#e3e4e8` / `#edeef1` |
| Border / border-strong | `#232a33` / `#3a4049` | `#e2e3e7` / `#c8ccd2` |
| Accent / hover / subtle | `#7c83ff` / `#aeb3ff` / `#1c2129` | `#4b44d6` / `#3a34b8` / `#edeef1` |
| Text primary / secondary / muted | `#e9ebf1` / `#c8cdd6` / `#737b89` | `#16181d` / `#5c616a` / `#83888f` |
| Success / Warning / Danger | `#38c08a` / `#e0a93c` / `#f06a5d` | `#1f9d61` / `#b9770a` / `#d1453b` |
| Sidebar bg / active / text-active | `#0e1116` / `#1c2129` / `#e9ebf1` | `#fcfcfd` / `#edeef1` / `#16181d` |

Maintain WCAG AA contrast in **both** themes when introducing or adjusting tokens.

## Typography

The typographic system follows the Zamp brand spec: a **grotesque sans at weight 500 (headlines) and 400 (body)**, with monospace reserved for data, labels, and metrics. **IBM Plex Sans** is used as the grotesque sans throughout; **IBM Plex Mono** is reserved exclusively for source snippets and the generated email body.

**One deliberate product exception to brand guidance:** the brand spec says "never ALL CAPS in copy." In this product, uppercase is used in two narrow, non-prose contexts — badge labels and table column headers — where it functions as a metadata legibility signal, not copy. This is an intentional override, not a drift.

- **Display / Headlines:** IBM Plex Sans Medium (weight 500) at varying scales. Tight letter-spacing on large sizes (−0.02em at 24px) for a compressed, professional feel. Never decorative — used only for page titles, card headings, and section labels.
- **Body:** IBM Plex Sans Regular at 14–15px with 1.6 line-height for comfortable scanning of dense reasoning trail content.
- **Labels:** IBM Plex Sans Medium at 11–12px, uppercase, with generous letter spacing (0.06–0.08em). Used for badge text, table column headers, and all status indicators only — never in prose.
- **Monospace (IBM Plex Mono):** Used in two specific contexts only:
  1. **Source snippet blocks** — verbatim text extracted from research sources. The monospace treatment makes it immediately obvious that this is quoted, unedited source material, not AI-generated prose.
  2. **Email body text** — the generated draft body is shown in monospace to reinforce that it is an artifact to be reviewed and edited, not the final voice. This is intentional — it subtly signals "this is a draft" without requiring a label.

Never mix font families in the same prose paragraph. The two-font distinction (IBM Plex Sans / IBM Plex Mono) maps 1:1 to the semantic distinction: AI context vs. source evidence.

## Layout

The layout follows a **fixed sidebar + scrollable content area** model for all screens.

- **Sidebar (240px, fixed left):** `sidebar-bg` (#0e1116 dark / #fcfcfd light) with a 1px right divider. Contains wordmark, navigation, and the theme toggle. At 1024px viewport, collapses to icon-only (48px wide).
- **Top bar (56px, fixed top):** Card surface (#161a20 dark / #fcfcfd light) with a 1px bottom border. Page title only. No breadcrumbs, no secondary navigation.
- **Content area:** Page background (#0c0e12 dark / #f1f2f4 light), scrollable, max-width 1280px centered with auto horizontal margins.
- **Cards:** Card surface, 1px border, 8px radius, 24px internal padding. The standard container for all content units. Cards never nest inside cards.
- **8px grid:** All spacing is a multiple of 8px. The 4px half-step (`xs`) is used only for micro-adjustments within compact components (e.g., icon-to-label gap, badge padding).
- **Two-column layout on the Review screen:** 55% (draft) / 45% (reasoning trail). Both columns are equal in visual weight — no visual hierarchy between them. The reasoning trail column must not look like a footnote panel.
- **Table row height: 40px.** Dense enough to show 15–20 rows without scrolling on a standard laptop.

## Elevation & Depth

Depth is achieved through **tonal layering**, not drop shadows. The three surface levels are:

1. **Page background (#0c0e12 dark / #f1f2f4 light):** The base layer — never used for interactive elements.
2. **Cards (#161a20 dark / #fcfcfd light):** Primary content containers. Defined by a 1px border (`border` token), not a shadow. Flat, not floating.
3. **Raised surface (#1c2129 dark / #e3e4e8 light):** Used inside cards for nested elements — source snippet blocks, table header rows, expanded stage detail panels.

The one exception: dropdown menus and tooltips use a single subtle shadow (`0 4px 12px rgba(0,0,0,0.08)`) to float above the card layer. No other component uses shadows.

This keeps the interface feeling data-terminal precise, not app-store soft.

## Shapes

The shape language is **softly angular** — enough corner rounding to feel modern, not enough to feel consumer.

- **4px (sm):** Micro-rounding for tags, inline code elements, and compact badge variants inside tables.
- **6px (md):** The default for all interactive elements: buttons, text inputs, select menus.
- **8px (lg):** Cards and modal containers.
- **12px (xl):** Larger info panels, status banners, and the empty-state illustration container.
- **9999px (full):** Pill badges only — for status labels and signal-type tags. The fully rounded pill is a strong visual signal that differentiates status labels from all other UI text.

Never mix sharp (0px) corners with soft corners in the same view. Never use corner radii above 12px on structural containers.

## Components

**Buttons.** Three core variants:

- **Primary (indigo):** Used for the single most important action on a screen — "Start Research," "Confirm & Approve." Maximum one per screen section.
- **Success (green):** Approve action only. Never used elsewhere. Its uniqueness reinforces the gravity of the approval decision.
- **Danger outline (red border, red text):** Reject action only. An outlined destructive button — less visually loud than a filled red, but clearly negative.
- **Secondary (card surface, strong border):** Supporting actions — "Approve with Edits," "Cancel," "Retry." The default non-primary action style.
- Button text always uses `headline-sm` (14px semibold). Never all-caps on buttons.
- All buttons have a clear disabled state: 40% opacity, no cursor pointer, no hover effect.

**Status badges.** Pill-shaped, uppercase label text, color-matched background tint. Five variants map to five run outcomes:

- `READY` — green
- `INSUFFICIENT SIGNAL` — amber
- `NEEDS RESEARCH` — orange (use amber token, deeper saturation via opacity overlay)
- `FAILED` — red
- `REVIEWED` — neutral grey
- `RUNNING` — indigo accent with a subtle animated pulse on the dot indicator

**Score bars.** Horizontal progress bars (4px tall, full-radius) showing numeric scores. Color is data-driven: green above 0.7, amber 0.45–0.7, red below 0.45. Never show a score bar without its numeric value next to it.

**Source snippet blocks.** A visually distinct component: raised `snippet-bg` surface (#1c2129 dark / #edeef1 light), 1px `snippet-border` (#2a313b dark / #c8ccd2 light), monospace font, 12px/14px padding. Every source snippet must be preceded by a domain label + source link in regular body text. The block itself is not clickable — the link above it is.

**Stage step indicator.** Each pipeline stage renders as a row with: a circle status icon (16px) on the left, stage name in `body-md`, and elapsed time or one-line summary on the right. Active stage has a 2px left border in the indigo accent (#7c83ff dark / #4b44d6 light). Completed stage has a green checkmark circle. Degraded stage has an amber warning triangle. The row height is 48px when collapsed, expanding to auto-height when expanded to show stage output detail.

**Metric cards.** Five equal-width cards in a horizontal row. Each card: label in `label-md` uppercase, metric value in `display` (24px semibold), and a small context label in `body-sm` muted text. No chart, no trend arrow — just the number, clearly labeled.

**Input fields.** Single border style: 1px solid `border` token. On focus: border transitions to the indigo accent with a soft accent focus ring. Label floats above the input. Error state: border turns red, error message appears below in `body-sm` danger color. No filled/background-colored inputs.

## Do's and Don'ts

- **Do** give the reasoning trail equal visual weight to the draft. If the reasoning panel looks secondary, the design has failed its primary purpose.
- **Do** use monospace for source snippets and email draft body. The font distinction is a trust signal, not a stylistic choice.
- **Do** use pill badges for every run status. The rounded shape is reserved for status labels — preserving this uniqueness makes status instantly scannable in tables.
- **Do** use the green Approve button only for approval. Never repurpose its color for other positive actions.
- **Do** design every state: loading, empty, error, degraded, and success. A blank white area or a raw error string is a design failure.
- **Don't** use gradients, glow effects, drop shadows (except floating menus), or animated background elements anywhere.
- **Don't** use more than one primary (indigo) button in a single screen section.
- **Don't** use uppercase text outside of badge labels and table column headers. Prose and button text are always sentence-case.
- **Don't** display a source snippet without its source URL and domain. A snippet without attribution is the exact failure mode the product is built to prevent.
- **Don't** use red for anything other than destructive/error states. Score bars below threshold use red — that is the only other permitted use.
- **Don't** add illustrations, icons, or visual decoration to the reasoning trail panel. It must look like a structured data view, not a feature highlight card.
- **Do** maintain WCAG AA contrast ratios (4.5:1 for normal text, 3:1 for large text) on all text/background combinations.
