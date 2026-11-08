# InHouseTX interface design system

## Source of truth

The editable Figma design is [InHouseTX — PayPal AI Spending Intelligence](https://www.figma.com/design/f4BTFU5wEmutlA2FetAxoI). It contains foundation and component references, desktop product screens, mobile and tablet layouts, and common loading, empty, success, and error states. The repository did not contain a link to a pre-existing Figma file, and the connected Figma tools did not provide file search; this file was created for the redesign.

## Visual language

- Inter-based typography with clear heading, label, and supporting-copy hierarchy.
- Evergreen primary actions and accents, neutral stone backgrounds, white content surfaces, and restrained borders.
- Compact but readable financial tables, cards, labels, and chart summaries.
- Keyboard-visible focus rings, reduced-motion support, touch-friendly mobile navigation, and explicit source/status labels.
- Product data remains currency-separated and synthetic demonstration content is labelled as such.

Core values are defined near the end of `frontend/src/styles.css`: primary evergreen `#145c49`, deep evergreen `#0c493a`, page background `#f5f6f2`, pale green `#e7f1eb`, standard text `#172b25`, and muted text `#738078`. Spacing is based on 4, 8, 12, 16, 24, and 32 px; corner radii are 6, 10, and 14 px.

## Components

The Figma file contains editable Button, Input, navigation item, status badge, and metric card components. The browser implementation uses matching navigation, buttons, metric cards, chart panels, transaction tables, status/source labels, feedback dialog, alert review controls, and mobile bottom navigation.

## Screen inventory

1. Landing page
2. Sign in and registration
3. Spending dashboard
4. Transaction list and filters
5. Transaction detail and categorisation explanation
6. Spending analytics
7. Grounded AI insights
8. Unusual activity review
9. PayPal Sandbox checkout, including an honest unconfigured state
10. Settings and integration status
11. Mobile overview, transactions, and checkout
12. Tablet layout and reusable loading, empty, success, and error state examples

## Behavior and trust

The checkout UI reports a completed payment only after the server returns PayPal-confirmed capture status. Missing Sandbox configuration is shown as a setup state. The account recovery page explains that recovery is not configured rather than presenting a nonfunctional reset form. Category corrections are submitted through the existing feedback API and remain subject to review before retraining. Financial answers continue to use server-side persisted analytics.
