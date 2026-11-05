# DevTalks Frontend

Next.js App Router frontend for the DevTalks developer community. The interface
uses the real FastAPI API; it does not substitute sample records for backend
responses.

## Run locally

To run the entire application, including backend, PostgreSQL, and Redis, use
the root [Docker Compose instructions](../README.md).

1. Start PostgreSQL, Redis, and the backend using the instructions in
   [backend/README.md](../backend/README.md).
2. Copy `.env.example` to `.env.local`. `BACKEND_API_URL` is used only by the
   Next.js server-side API proxy (default `http://localhost:8000`).
3. Install dependencies and start Next.js:

   ```powershell
   npm install
   npm run dev
   ```

Open `http://localhost:3000`. Access and refresh tokens are held in
`sessionStorage` for the active browser tab. The API client refreshes an
expired access token through the backend's `/auth/refresh` endpoint.

## Implemented screens and actions

- Feed sorting and pagination, post/category search, developer search.
- Registration, login, refresh, logout, and profile editing.
- Uploading, replacing, and removing the current user's avatar.
- Creating, editing, and deleting posts; tags and categories.
- Voting, bookmarks, comment threads, replies, and deleting your own comments.
- Responsive navigation and persistent light/dark theme.

Followers, notifications, direct messages, media uploads, and password reset
are not shown as working features because the backend does not expose those
APIs yet.
