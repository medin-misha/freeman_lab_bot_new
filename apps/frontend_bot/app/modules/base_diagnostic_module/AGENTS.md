# Base Diagnostic Module Agent Context

## Purpose

`app/modules/base_diagnostic_module` is a shared orchestration module for
creating diagnostics from Telegram `Message.document` objects.

It exists so product diagnostic modules can be connected quickly without
re-implementing backend lookup, file upload and diagnostic creation steps.

## What Belongs Here

- reusable backend diagnostic creation flow
- generic validation of `diagnostic_type`
- adaptation between Telegram `Document` and backend file upload
- local read-schemas for backend responses

## What Does Not Belong Here

- product-specific business rules for a concrete diagnostic type
- Telegram UX handlers for a specific flow
- auth/session ownership outside the shared `system` module

## Design Rules

- Reuse the shared `system` backend client instead of creating a second
  process-wide HTTP session.
- Keep the public API small and stable: product modules should usually need
  only `create_diagnostic(...)`.
- Treat backend product endpoints as interchangeable as long as they accept
  `user_id`, `voice_file_id`, and `description`.
- Keep response schemas tolerant to product-specific extra fields.

## Safe Extension Points

- add helper functions for new diagnostic orchestration steps
- add more backend response schemas if future product modules need them
- extend error classes when callers need more precise recovery behavior

## Caution

- `diagnostic_type` must remain a single safe path segment
- backend user lookup is based on `telegram_id == chat_id`
- file upload must stay compatible with backend `POST /api/files/`
