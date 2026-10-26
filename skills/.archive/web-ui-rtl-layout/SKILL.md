---
name: web-ui-rtl-layout
description: "Use when adapting a WebUI for RTL. Fix flex layouts."
tags: [css, frontend, rtl, layout, formatting]
---

# Web UI RTL Layouts

## Workflow

1. Implement RTL logic using a document-level class or attribute (e.g., `<html class="chat-content-rtl">`).
2. Do **not** blindly mirror everything. Certain structural flows, like the left/right dichotomy of chat interfaces, usually need careful individual adjustment, not blanket `direction: rtl`.
3. In chatbots, User bubbles align left in RTL, and Assistant bubbles align right.
4. Target explicit selectors like `.msg-row[data-role="user"]` using `align-self: flex-start` or `justify-content: flex-start` to push bubbles to the appropriate side.

## UI Theming Preferences

When the user requests a dark theme or a ChatGPT-style appearance:
1. They generally prefer neutral dark grays (e.g., `#212121` background, `#2F2F2F` bubbles) rather than tinted colors (like yellow, navy, or gold).
2. For RTL interfaces, ensure the font is set correctly (e.g., `Vazirmatn` for Persian) across the main UI variables (`--font-ui`).
3. Ensure chat bubbles (both user and assistant) properly implement these neutral background variables. Assistant bubbles might need `background: transparent !important; border: none !important;` to blend properly with the main background, while User bubbles should use the `--user-bubble-bg`.

When switching `direction: rtl` on a flex container, it visually swaps `flex-start` and `flex-end`. If a user bubble was styled with `align-self: flex-end`, turning on RTL makes it appear on the left.
Instead of trying to override `text-align: right` universally, explicitly target the layout rules.

For example, to fix user bubbles shifting to the wrong side in an RTL chat view, use:

```css
.chat-content-rtl .msg-row[data-role="user"] { align-self: flex-start; }
```

This ensures that the flex item explicitly pulls to the visual "start" (which is now the right side of the screen) while maintaining proper structure.