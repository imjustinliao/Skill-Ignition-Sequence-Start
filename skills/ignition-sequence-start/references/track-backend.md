# Track: backend and system architecture

Servers, APIs, data, accounts, background work and integrations. Guide like a staff engineer at a fast startup: boring, managed, cheap to run and easy to change, so the MVP never becomes a rewrite.

## Questions

Ask only those you cannot infer, alongside the drafted direction (`intake.md` › 3).

1. **Who signs in, and how?** Nobody · email or Google sign-in. Default: a managed auth provider.
2. **Is any data sensitive** (payments, health, children's data, anything regulated)?
3. **Budget and preferences**: a monthly budget, existing cloud accounts, a preferred language. Default: free tiers; TypeScript or Python.

Slow or scheduled work (emails, AI calls, imports) and users at launch come from the features and `docs/product.md` › Goals; ask only if they are unclear.

## The draft

`docs/architecture.md` gets: the shape (a small diagram), the stack with a one-line reason per choice, the data model (main entities and who can access what), auth, hosting with expected monthly cost, the accounts the owner will need, what starts as a mock, and the scaling path. The message summarizes it in plain words.

One yes covers the architecture. Two things always get their own line in that message, so the yes is informed: anything that costs money, and any personal data shared with a third party. Pros may want to weigh in on the data model, auth and hosting separately; offer it.

## Defaults: boring, managed, one of each

- A modular monolith with clear module boundaries, and one Postgres database.
- **Fastest path**: Supabase (Postgres, auth, storage, row-level security) with the app on Vercel. Firebase for realtime or mobile-first apps.
- **Custom API**: TypeScript (Hono, Fastify or Next.js route handlers) or Python (FastAPI), with Postgres and an ORM with migrations (Drizzle or Prisma; SQLAlchemy with Alembic).
- **Hosting**: Vercel for web and serverless; Render, Railway, Fly.io or Cloud Run for long-running services.
- **Auth**: Supabase Auth, Clerk or Auth.js. Never hand-rolled password storage.
- **Background jobs**: a managed queue (Inngest, Trigger.dev) or a Postgres-backed queue.
- **Observability**: structured logs, error tracking (Sentry), a health endpoint, an uptime check.
- **Not for an MVP** unless the goals demand it: microservices, Kubernetes, several databases, event sourcing, self-hosted infrastructure.

Pricing and free tiers change: check the current pages before recommending, and state the numbers.

## Interfaces and contracts

- The contract comes first: an OpenAPI spec or shared typed schemas (zod, Pydantic), recorded in `docs/architecture.md` › Interfaces or a file it links.
- Generate typed clients from it. Validate every request at the boundary. One error shape everywhere. Version breaking changes.
- **Backend only (frontend elsewhere)**: publish the contract plus a mock server (Prism) or example requests so the frontend team can start. Contract changes go through the owner.

## Scaling path, without rewrites

Indexes → cache hot reads → move slow work to background jobs → read replicas → extract a module only when measurement says so. Keep app servers stateless, every schema change in a migration, and every list paginated.

## Build and verify

- Migrations run cleanly on a fresh database; seed data for development.
- Tests for business logic and **every authorization rule**: a second test user must not see the first user's data.
- Real requests against the running server, including failures (bad input, no auth, wrong user).
- Contract tests on both sides when another team builds against the API.

## Ship

Deploy with environment variables set in the host's settings; health check passing; database backups on; error tracking connected; a known rollback path. Production keys live only in the host.

## Pitfalls

Tables exposed without access rules (row-level security) · secrets in frontend bundles · schema changes without migrations · vendor SDK calls scattered everywhere (wrap each vendor in one module) · premature microservices · unbounded queries · trusting client input.
