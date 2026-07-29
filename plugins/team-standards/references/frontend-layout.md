# Frontend layout — Next.js / Vue

Tier 2 detail for the **Frontend** section of `context/team-standards.md`. Read this when
adding a component or wiring up an API call, or when judging whether existing code is in
the right place.

Anything marked **⚠️ POR DEFINIR** is not settled team convention — ask before assuming it.

## Where a component goes

The decision is about **scope**, not about file type:

- **Used by one route/page** → colocate it with that route, not in a global folder.
- **Used by two or more routes** → promote it to the shared components folder.
- **No logic, purely presentational and reusable** (button, input, badge) → the UI
  primitives folder.

Promote a component when the second consumer appears, not in anticipation of one (YAGNI).
Match the folder names the repo already uses; do not introduce a parallel scheme.

## Components & state

- React: function components + hooks. Vue: Composition API.
- **Keep state local.** Lift it only when a sibling genuinely needs it, and reach for
  Context or a store only when it is shared across unrelated parts of the tree.
- Server data is not application state — it belongs to whatever fetching layer the repo
  uses, not to a global store you keep in sync by hand.
- A component that both fetches and renders complex UI is two things: split the data
  concern into a hook/composable.

## Styling

**Tailwind CSS** is the base styling system. Prefer utility classes in the markup over a
parallel stylesheet. Extract a component (not a CSS class) when a pattern repeats.

Do not introduce a second styling system (CSS modules, styled-components, a UI kit's own
theming) into a repo that already uses Tailwind.

## API calls

**⚠️ POR DEFINIR** — there is no team convention yet for consuming the backend.

Until there is: use the pattern the repo already has, keep fetch/axios calls out of
components (behind a client or service module), and don't add a new data-fetching library
to a repo that already has one.

## Integrating backend changes

When the backend hands over a `frontend-handoff` brief, follow it: it carries the real
contract (routes, schemas, error shapes, auth). If integration reveals the backend is
insufficient, stop and report what the backend must change rather than patching around it
in the frontend — the brief itself asks for this.

## Open questions for the team

- API call convention (above) — decide and remove the ⚠️.
- Folder naming: confirm the canonical names for route-local, shared, and primitive
  components, per framework.
- Form handling and validation: any shared approach, or per-repo?
- Testing expectations for components.
