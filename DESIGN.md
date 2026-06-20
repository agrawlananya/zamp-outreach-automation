---
version: alpha
name: Zamp AI SDR
description: >
  Internal B2B decision-support tool for Zamp's sales team. Produces grounded,
  source-backed outbound email drafts with a full visible reasoning trail.
  Designed for trust, density, and speed — not decoration. Human reviews every
  draft before anything is sent; the reasoning trail is co-equal with the output.

colors:
  # ─── Brand primitives (Zamp Brand Guidelines v1) ───────────────────────────
  # Ink #16171A · Accent #2347E5 · Slate #5B5E66 · Mist #ECEEF3 · Paper #FFFFFF
  # Semantic status overrides (success, warning, danger) are outside the brand
  # palette but retained for functional run-outcome signalling.

  # Interactive accent
  primary:
    value: "#2347E5"
    description: >
      Brand Accent. The sole interactive action color — used exclusively for
      primary buttons, hyperlinks, focus rings, and active-state indicators.
      One accent per view; never diluted or repurposed for decoration.
  primary-hover:
    value: "#1A38C4"
    description: >
      Accent darkened ~10%. Applied on hover and pressed states for primary
      interactive elements. Never used as a standalone fill color.
  primary-subtle:
    value: "#EBF0FD"
    description: >
      Accent at ~8% opacity over Paper. Used for selected-row highlight
      backgrounds, hover states on ghost/text buttons, and focus-area tints.

  # Brand anchors
  secondary:
    value: "#16171A"
    description: >
      Brand Ink. Near-black with a warm undertone. The sidebar background and
      the visual brand anchor of every screen. Communicates authority without
      feeling cold or pure-black.
  tertiary:
    value: "#16A34A"
    description: >
      Forest green. Not in the brand palette; retained as a product-level
      semantic token for the Approve action only. Its uniqueness reinforces the
      gravity of approval. Never used for any other positive or decorative state.

  # Surfaces & backgrounds
  neutral:
    value: "#ECEEF3"
    description: >
      Brand Mist. The page-level background for all screens. Slightly cool;
      reduces eye strain in extended sessions. Never use Paper (#FFFFFF) as a
      page background — surface elevation must be legible through tonal contrast.
  surface:
    value: "#FFFFFF"
    description: >
      Brand Paper. Used only for cards and raised content panels. The primary
      content container surface, set against the Mist page background to
      establish the first tonal elevation step.
  surface-raised:
    value: "#E4E7EF"
    description: >
      Mist darkened slightly (~5%). Used for nested surfaces within cards —
      table header rows, expanded pipeline stage panels, and snippet block
      backgrounds. Establishes the second tonal elevation step without shadows.

  # Borders & dividers
  border:
    value: "#ECEEF3"
    description: >
      Brand Mist. Default 1px border for cards and structural dividers. Tonal
      and low-contrast — defines layout structure without visual weight.
  border-strong:
    value: "#C8CCDA"
    description: >
      Mist darkened for emphasis. Used for input field borders, table row
      separators, and any divider that needs to be legible against surface-raised
      backgrounds.

  # Text
  text-primary:
    value: "#16171A"
    description: >
      Brand Ink. All primary readable content — headings, body copy, labels,
      and data values. Same hex as the sidebar background; creates a consistent
      brand-anchored near-black across contexts.
  text-secondary:
    value: "#5B5E66"
    description: >
      Brand Slate. Supporting text — field labels, captions, metadata rows,
      and secondary data values. Sufficient contrast on both Paper and Mist
      backgrounds for WCAG AA compliance.
  text-muted:
    value: "#9396A0"
    description: >
      Slate lightened ~25%. Placeholder text, disabled-state labels, timestamps,
      and decorative separators. Intentionally low-contrast — never use for
      content the user must read to complete a task.

  # Semantic status colors
  status-success:
    value: "#16A34A"
    description: >
      Semantic success green. Used for the Approve button fill, READY badge
      text, score-bar-high, and completed pipeline stage icons. Also maps to
      tertiary. Never repurposed for non-approval positive states.
  status-success-bg:
    value: "#F0FDF4"
    description: >
      Soft green tint. Background fill for success badges and banners. Always
      paired with status-success text to meet contrast requirements.
  status-warning:
    value: "#D97706"
    description: >
      Semantic warning amber. Used for INSUFFICIENT SIGNAL and NEEDS RESEARCH
      badge text, score-bar-mid, and degraded pipeline stage icons.
  status-warning-bg:
    value: "#FFFBEB"
    description: >
      Soft amber tint. Background fill for warning badges and banners. Always
      paired with status-warning text.
  status-danger:
    value: "#DC2626"
    description: >
      Semantic danger red. Used for FAILED badge text, score-bar-low, the
      Reject button border and text, and error-state input borders. The only
      permitted uses of red in the product.
  status-danger-bg:
    value: "#FEF2F2"
    description: >
      Soft red tint. Background fill for danger badges, banners, and inline
      error messages. Always paired with status-danger text.
  status-info:
    value: "#2347E5"
    description: >
      Brand Accent — mirrors primary. Used for RUNNING badge text and info
      banners. Intentionally the same as primary to maintain a single blue in
      the system.
  status-info-bg:
    value: "#EBF0FD"
    description: >
      Matches primary-subtle. Background fill for info badges and RUNNING status
      banners. Always paired with status-info text.
  status-neutral:
    value: "#5B5E66"
    description: >
      Brand Slate. Used for REVIEWED badge text and neutral/inactive state
      indicators. Communicates completion without a positive or negative valence.
  status-neutral-bg:
    value: "#ECEEF3"
    description: >
      Brand Mist. Background fill for neutral badges. Low visual weight —
      used for states that need labelling but not emphasis.

  # Sidebar
  sidebar-bg:
    value: "#16171A"
    description: >
      Brand Ink. The fixed left sidebar background. Anchors every screen with
      the brand's near-black and creates strong contrast for the navigation
      items rendered over it.
  sidebar-text:
    value: "#9396A0"
    description: >
      Ink lightened for legibility against the dark sidebar background. Used
      for inactive navigation item labels and supporting sidebar metadata.
      Meets WCAG AA on sidebar-bg.
  sidebar-text-active:
    value: "#FFFFFF"
    description: >
      Brand Paper. Active navigation item label color on the dark sidebar.
      Full white over Ink provides maximum contrast and clear active-state
      signalling.
  sidebar-active-bg:
    value: "#2C2D32"
    description: >
      Ink lightened ~10%. Background fill for the active or hovered navigation
      item in the sidebar. Tonal step above sidebar-bg — no border or shadow
      needed to distinguish the active item.

  # Score bars
  score-high:
    value: "#16A34A"
    description: >
      Semantic green (matches status-success). Applied to score bars when the
      hook score is ≥ 0.7. Signals a strong, research-backed signal that is
      likely ready for review.
  score-mid:
    value: "#D97706"
    description: >
      Semantic amber (matches status-warning). Applied to score bars when the
      hook score is between 0.45 and 0.69. Signals a marginal signal — human
      review is especially important at this range.
  score-low:
    value: "#DC2626"
    description: >
      Semantic red (matches status-danger). Applied to score bars when the hook
      score is < 0.45. Signals insufficient signal — the run will route to
      insufficient_signal rather than generating a confident draft.

  # Source snippet blocks
  snippet-bg:
    value: "#E4E7EF"
    description: >
      Matches surface-raised. The background of verbatim source snippet blocks.
      Visually separates quoted, human-authored source text from AI-generated
      prose — a primary trust signal in the product. Never use Paper or Mist
      here; the contrast step must be perceptible.
  snippet-border:
    value: "#C8CCDA"
    description: >
      Matches border-strong. The 1px border on snippet blocks. Reinforces the
      visual boundary between snippet content and surrounding card prose.

typography:
  # ─── Brand spec ─────────────────────────────────────────────────────────────
  # Grotesque sans, weight 500 (headlines) / 400 (body). Inter is used as the
  # grotesque sans throughout — it is a humanist grotesque with strong legibility
  # at the small sizes this product requires.
  # JetBrains Mono is reserved for source snippets and the email draft body only.
  #
  # Product exception: the brand spec says "never ALL CAPS in copy." This product
  # uses uppercase in two non-prose contexts only — badge labels and table column
  # headers — as a metadata legibility signal. This is an intentional override,
  # documented here so it is not mistaken for brand non-compliance.

  display:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: 500
    lineHeight: 1.2
    letterSpacing: -0.02em
    description: >
      Page-level titles and the primary metric value in dashboard cards.
      Tight letter-spacing (-0.02em) gives a compressed, data-terminal feel
      at large sizes. Never used for subheadings or section labels.

  headline-lg:
    fontFamily: Inter
    fontSize: 20px
    fontWeight: 500
    lineHeight: 1.3
    letterSpacing: -0.01em
    description: >
      Card-level headings and modal titles. Slightly looser tracking than
      display. Used when a section needs a strong heading but the display
      size would be too heavy.

  headline-md:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: 500
    lineHeight: 1.4
    description: >
      Section headings within cards — e.g., "Reasoning Trail," "Draft Email,"
      "Signal Hooks." The workhorse heading size for the two-column review
      layout. No letter-spacing adjustment at this size.

  headline-sm:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: 500
    lineHeight: 1.4
    description: >
      Button labels, table column headers, and the active sidebar nav item.
      The minimum size at which weight 500 reads as a heading rather than
      bold body text. Never use for running prose.

  body-lg:
    fontFamily: Inter
    fontSize: 15px
    fontWeight: 400
    lineHeight: 1.6
    description: >
      Primary reading text for the reasoning trail prose and any explanation
      copy that runs longer than two lines. The 1.6 line-height is essential
      for scanning dense signal summaries without losing place.

  body-md:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: 400
    lineHeight: 1.6
    description: >
      Default body text. Used for pipeline stage descriptions, signal source
      labels, form field values, and most supporting prose. The base text size
      for the product.

  body-sm:
    fontFamily: Inter
    fontSize: 13px
    fontWeight: 400
    lineHeight: 1.5
    description: >
      Supporting metadata — timestamps, source domain labels above snippet
      blocks, helper text below form fields, and inline error messages.
      Not for primary reading; information at this size supports, not leads.

  label-md:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: 500
    lineHeight: 1
    letterSpacing: 0.06em
    description: >
      Table column headers and section sub-labels within cards. Uppercase.
      Generous tracking (0.06em) ensures legibility at 12px. Use only for
      structural metadata labels — not for prose or inline emphasis.

  label-sm:
    fontFamily: Inter
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
    fontFamily: "JetBrains Mono, ui-monospace, monospace"
    fontSize: 13px
    fontWeight: 400
    lineHeight: 1.6
    description: >
      Source snippet blocks. The monospace treatment makes it immediately
      obvious that this is verbatim, unedited source material — not AI-generated
      prose. This distinction is a core trust signal in the product. Never use
      mono for AI-generated text outside the email draft body.

  email-body:
    fontFamily: "JetBrains Mono, ui-monospace, monospace"
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

The palette is derived directly from the Zamp Brand Guidelines (v1). Five brand primitives — Ink, Accent, Slate, Mist, Paper — are mapped to all product-level tokens. Semantic status colors (success green, warning amber, danger red) are not in the brand palette and are retained as functional overrides.

- **Primary / Accent (#2347E5):** Brand Accent — used exclusively for primary interactive actions (buttons, links, focus rings, active states). One action color per view, always the same, never diluted.
- **Primary Subtle (#EBF0FD):** Accent at ~8% opacity on Paper — for hover backgrounds on primary elements and selected row highlights.
- **Secondary / Ink (#16171A):** Brand Ink — the sidebar background and brand anchor. Near-black with a warm undertone; communicates authority without feeling cold.
- **Tertiary (#16A34A):** Forest green — approve/success states only. Outside the brand palette; retained for the semantic weight of the approval action. Never used for decoration.
- **Neutral / Mist (#ECEEF3):** Brand Mist — the page background. Slightly cool, reduces eye strain in extended sessions. Never use Paper (#FFFFFF) as a page background.
- **Surface / Paper (#FFFFFF):** Brand Paper — cards and raised content panels only.
- **Text Primary / Ink (#16171A):** Brand Ink — all primary readable content.
- **Text Secondary / Slate (#5B5E66):** Brand Slate — supporting labels, captions, and metadata.
- **Text Muted (#9396A0):** Slate lightened ~25% — placeholder text, disabled states, timestamps.
- **Status colors:** Four semantic colors — Success green (#16A34A), Warning amber (#D97706), Danger red (#DC2626), Info blue (#2347E5) — each with a paired soft background tint for badges and banners.
- **Snippet Background (#E4E7EF):** Darkened Mist for source snippet blocks inside cards. Visually separates AI-generated prose from verbatim human-authored source text — a critical trust signal in this product.

## Typography

The typographic system follows the Zamp brand spec: a **grotesque sans at weight 500 (headlines) and 400 (body)**, with monospace reserved for data, labels, and metrics. **Inter** is used as the grotesque sans throughout; **JetBrains Mono** is reserved exclusively for source snippets and the generated email body.

**One deliberate product exception to brand guidance:** the brand spec says "never ALL CAPS in copy." In this product, uppercase is used in two narrow, non-prose contexts — badge labels and table column headers — where it functions as a metadata legibility signal, not copy. This is an intentional override, not a drift.

- **Display / Headlines:** Inter Medium (weight 500) at varying scales. Tight letter-spacing on large sizes (−0.02em at 24px) for a compressed, professional feel. Never decorative — used only for page titles, card headings, and section labels.
- **Body:** Inter Regular at 14–15px with 1.6 line-height for comfortable scanning of dense reasoning trail content.
- **Labels:** Inter Medium at 11–12px, uppercase, with generous letter spacing (0.06–0.08em). Used for badge text, table column headers, and all status indicators only — never in prose.
- **Monospace (JetBrains Mono):** Used in two specific contexts only:
  1. **Source snippet blocks** — verbatim text extracted from research sources. The monospace treatment makes it immediately obvious that this is quoted, unedited source material, not AI-generated prose.
  2. **Email body text** — the generated draft body is shown in monospace to reinforce that it is an artifact to be reviewed and edited, not the final voice. This is intentional — it subtly signals "this is a draft" without requiring a label.

Never mix font families in the same prose paragraph. The two-font distinction (Inter / JetBrains Mono) maps 1:1 to the semantic distinction: AI context vs. source evidence.

## Layout

The layout follows a **fixed sidebar + scrollable content area** model for all screens.

- **Sidebar (240px, fixed left):** Brand Ink (#16171A). Contains wordmark, navigation, and user identity. At 1024px viewport, collapses to icon-only (48px wide).
- **Top bar (56px, fixed top):** Paper (#FFFFFF) with a 1px bottom border. Page title only. No breadcrumbs, no secondary navigation.
- **Content area:** Mist (#ECEEF3) background, scrollable, max-width 1280px centered with auto horizontal margins.
- **Cards:** White surface, 1px border, 6px radius, 24px internal padding. The standard container for all content units. Cards never nest inside cards.
- **8px grid:** All spacing is a multiple of 8px. The 4px half-step (`xs`) is used only for micro-adjustments within compact components (e.g., icon-to-label gap, badge padding).
- **Two-column layout on the Review screen:** 55% (draft) / 45% (reasoning trail). Both columns are equal in visual weight — no visual hierarchy between them. The reasoning trail column must not look like a footnote panel.
- **Table row height: 40px.** Dense enough to show 15–20 rows without scrolling on a standard laptop.

## Elevation & Depth

Depth is achieved through **tonal layering**, not drop shadows. The three surface levels are:

1. **Page background (#ECEEF3):** The base layer — never used for interactive elements.
2. **Cards (#FFFFFF):** Primary content containers. Defined by a 1px `#ECEEF3` border, not a shadow. Flat, not floating.
3. **Raised surface (#E4E7EF):** Used inside cards for nested elements — source snippet blocks, table header rows, expanded stage detail panels.

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

- **Primary (blue):** Used for the single most important action on a screen — "Start Research," "Confirm & Approve." Maximum one per screen section.
- **Success (green):** Approve action only. Never used elsewhere. Its uniqueness reinforces the gravity of the approval decision.
- **Danger outline (red border, red text):** Reject action only. An outlined destructive button — less visually loud than a filled red, but clearly negative.
- **Secondary (white, grey border):** Supporting actions — "Approve with Edits," "Cancel," "Retry." The default non-primary action style.
- Button text always uses `headline-sm` (14px semibold). Never all-caps on buttons.
- All buttons have a clear disabled state: 40% opacity, no cursor pointer, no hover effect.

**Status badges.** Pill-shaped, uppercase label text, color-matched background tint. Five variants map to five run outcomes:

- `READY` — green
- `INSUFFICIENT SIGNAL` — amber
- `NEEDS RESEARCH` — orange (use amber token, deeper saturation via opacity overlay)
- `FAILED` — red
- `REVIEWED` — neutral grey
- `RUNNING` — blue with a subtle animated pulse on the dot indicator

**Score bars.** Horizontal progress bars (4px tall, full-radius) showing numeric scores. Color is data-driven: green above 0.7, amber 0.45–0.7, red below 0.45. Never show a score bar without its numeric value next to it.

**Source snippet blocks.** A visually distinct component: cool-grey background (#E4E7EF), 1px border (#C8CCDA), monospace font, 12px/14px padding. Every source snippet must be preceded by a domain label + source link in regular body text. The block itself is not clickable — the link above it is.

**Stage step indicator.** Each pipeline stage renders as a row with: a circle status icon (16px) on the left, stage name in `body-md`, and elapsed time or one-line summary on the right. Active stage has a 2px left border in Accent blue (#2347E5). Completed stage has a green checkmark circle. Degraded stage has an amber warning triangle. The row height is 48px when collapsed, expanding to auto-height when expanded to show stage output detail.

**Metric cards.** Five equal-width cards in a horizontal row. Each card: label in `label-md` uppercase, metric value in `display` (24px semibold), and a small context label in `body-sm` muted text. No chart, no trend arrow — just the number, clearly labeled.

**Input fields.** Single border style: 1px solid `#ECEEF3`. On focus: border transitions to `#2347E5`. Label floats above the input. Error state: border turns red, error message appears below in `body-sm` danger color. No filled/background-colored inputs.

## Do's and Don'ts

- **Do** give the reasoning trail equal visual weight to the draft. If the reasoning panel looks secondary, the design has failed its primary purpose.
- **Do** use monospace for source snippets and email draft body. The font distinction is a trust signal, not a stylistic choice.
- **Do** use pill badges for every run status. The rounded shape is reserved for status labels — preserving this uniqueness makes status instantly scannable in tables.
- **Do** use the green Approve button only for approval. Never repurpose its color for other positive actions.
- **Do** design every state: loading, empty, error, degraded, and success. A blank white area or a raw error string is a design failure.
- **Don't** use gradients, glow effects, drop shadows (except floating menus), or animated background elements anywhere.
- **Don't** use more than one primary blue button in a single screen section.
- **Don't** use uppercase text outside of badge labels and table column headers. Prose and button text are always sentence-case.
- **Don't** display a source snippet without its source URL and domain. A snippet without attribution is the exact failure mode the product is built to prevent.
- **Don't** use red for anything other than destructive/error states. Score bars below threshold use red — that is the only other permitted use.
- **Don't** add illustrations, icons, or visual decoration to the reasoning trail panel. It must look like a structured data view, not a feature highlight card.
- **Do** maintain WCAG AA contrast ratios (4.5:1 for normal text, 3:1 for large text) on all text/background combinations.
