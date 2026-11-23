# Track: frontend and design

For anything people see or touch: websites, web apps, mobile and desktop apps. Guide like a senior product designer and design engineer: few questions, a clear point of view, polish in the details.

## Questions

Ask only those you cannot infer, alongside the drafted direction (`intake.md` › 3).

1. **How should it feel?** Three words, or pick one: calm and minimal (default) · playful · dense and pro · editorial.
2. **Light, dark, or both?** Default: both, following the system setting.
3. *Optional*: brand color, logo, fonts, and apps or sites they like (screenshots or links). References inspire; they are never copied.

Where it runs (web, iOS, Android, desktop) usually came up in setup; if not, it replaces question 2 (default: web, responsive and phone-first). The agent decides the component system, typography and motion; the owner may override.

## The draft

`docs/design.md` gets: the feel in a sentence; layout and navigation model; component system; tokens (color, type, spacing, radius, motion); the key screens and the states each one handles; accessibility commitments. The message summarizes it. If the harness can render, show it: a quick HTML mock or a screenshot of a running prototype beats a description. Save reference images to `references/` with descriptive names and index them in `docs/design.md` › References (patterns several references share come first).

## Principles

- **Clarity.** Content first. One primary action per screen. Hierarchy through size, weight and space, not decoration.
- **Deference.** The interface serves the content: restrained color (one accent), system-quality typography, generous spacing.
- **Consistency.** Follow the platform: Apple's Human Interface Guidelines on Apple devices, Material on Android, web conventions on the web. The same thing looks and behaves the same everywhere.
- **Feedback.** Every action responds at once. Every screen handles empty, loading, error and success.
- **Motion with purpose.** 150–300 ms, ease-out for interface changes, springs for gestures; interruptible; animate transform and opacity only; respect reduced motion.
- **Accessible by default.** Text contrast ≥ 4.5:1, visible focus, full keyboard use, labels and alt text, touch targets ≥ 44 px, dynamic type on mobile.
- **Polish is the product.** Alignment, spacing rhythm, copy that sounds human. Avoid the generic "AI look": default gradients, cards around everything, emoji headings.

## Defaults

| Platform | Default | Why |
|----------|---------|-----|
| Web app | React with Next.js (Vite for a client-only app), Tailwind CSS, shadcn/ui | Components live in the repo and are fully editable; the ecosystem agents know best |
| Landing page or content site | Astro or plain HTML and CSS | Fastest, almost nothing to maintain |
| iOS | SwiftUI with system components | Native feel for free |
| Android | Jetpack Compose, Material 3 | The platform standard |
| Both mobile platforms | Expo (React Native) | One codebase, easy testing on a real phone |

Define tokens once (CSS variables or the platform's equivalent) with semantic names (`--background`, `--primary`); dark mode is a token swap, not a rewrite. CLIs and starters change often: check the official docs for the current setup command before scaffolding.

## Build and verify

- Build screens against `docs/design.md` with realistic content, including worst cases: long names, empty lists, errors, slow networks.
- Check in a browser or simulator at phone and desktop widths, in both themes, keyboard only, clicking through the main flow. Put screenshots in the report. Run Lighthouse or axe on the web when available.
- The console stays free of errors and warnings.
- What only a person can judge (the feel, touch on a real phone) goes to the owner with exactly what to try and what to look for.

## Frontend only (backend elsewhere or later)

Agree the contract in `docs/architecture.md` › Interfaces: endpoints, types, errors, auth. If the backend team already has an API spec, use theirs. Build against a typed client and a mock (MSW on the web, a local mock server elsewhere). Log every backend need under Blockers. Swapping a mock for the real API happens one endpoint at a time, behind the same interface.

## Ship

- **Web**: deploy (Vercel, Netlify or Cloudflare Pages), set environment variables in the host, check the live link on a phone.
- **iOS**: TestFlight (needs a paid Apple Developer account: owner approval). **Android**: Play Console internal testing. **Expo**: EAS Build and Submit.
- README with screenshots or a short GIF of the main flow.

## Pitfalls

Hard-coded colors that break dark mode · missing empty and error states · mixing component systems · animating layout properties · testing only on desktop · mobile-web input zoom and `100vh` bugs · custom controls without keyboard or screen-reader support.
