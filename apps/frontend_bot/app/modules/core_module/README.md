# Core Module

`app/modules/core_module` owns the "Узнать про Ядро" flow in `frontend_bot`.

## Responsibility

The module:

- handles the `Узнать про Ядро` reply button
- sends the informational message about the Core community
- exposes an inline `web_app` button that opens the configured mini app URL

## Configuration

The module relies on the shared `CORE_URL` environment variable exposed through
`app.core.settings`.
