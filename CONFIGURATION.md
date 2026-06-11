# Configuration

Needs Radar uses the same free France Travail API as the
[France Travail MCP](https://github.com/mohamed-amine-ben-mallessa/francetravail-mcp).

## Getting free credentials

1. Create a developer account at **[francetravail.io](https://francetravail.io)**.
2. **"Mes applications"** → create an application.
3. **Subscribe it to the API "Offres d'emploi v2"** (scope `api_offresdemploiv2 o2dsoffre`).
4. Copy the **client ID** and **client secret**.

> ⚠️ Creating the app but not subscribing it to the API gives `invalid_client` on auth,
> even with correct keys. Subscribe first.

## Environment variables

| Variable | Required | Description |
|----------|----------|-------------|
| `FT_CLIENT_ID` | ✅ | Application client ID (starts with `PAR_`) |
| `FT_CLIENT_SECRET` | ✅ | Application client secret |

Set them in your MCP client's `env` block or in a `.env` file (copy `.env.example`).

## Rate limits

4 requests/second per application. The server caches the OAuth token and refreshes it
automatically, so scans don't waste requests re-authenticating.
