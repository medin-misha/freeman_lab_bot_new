# Base Diagnostic Module

`base_diagnostic_module` is a reusable orchestration layer for creating backend
diagnostics from Telegram documents and a shared FSM foundation for diagnostic
product modules.

## Purpose

It hides the multi-step integration flow required by product diagnostic modules:

1. find backend user by Telegram `chat_id`
2. download `Message.document` from Telegram
3. upload the file to backend `/api/files/`
4. call product endpoint `/api/diagnostic/<type>`

It also exposes a base `StatesGroup` so product modules can share the same
state names for file-first diagnostic flows.

## Public API

The module exposes one main async helper:

- `create_diagnostic(bot, document, chat_id, description, diagnostic_type)`

And one helper for delayed submission from FSM data:

- `create_diagnostic_from_telegram_file(bot, telegram_file_id, filename, content_type, chat_id, description, diagnostic_type)`

And one reusable FSM class:

- `BaseDiagnosticStates`

It returns a unified object with:

- backend Telegram user
- created backend file
- created diagnostic extension object

## Shared FSM States

`BaseDiagnosticStates` defines these states:

- `waiting_for_file`
- `waiting_for_text`
- `sending_to_server`

Two common flows are supported by these names:

1. file arrives together with text:
   `waiting_for_file -> sending_to_server`
2. file arrives without text:
   `waiting_for_file -> waiting_for_text -> sending_to_server`

The base module intentionally does not define a separate `file_received` state.
Product modules should store the received document in `FSMContext` and decide
whether to ask for extra text or submit immediately.

## Boundaries

- The module does not implement product-specific Telegram handlers.
- The module does not implement shared FSM transition handlers.
- The module does not own authentication or backend session lifecycle.
- The module depends on the shared `system` backend client.

## Extension

New product modules such as `default_diagnostic_module` or
`invisible_diagnostic_module` should:

- call `create_diagnostic(...)` instead of duplicating backend transport logic
- inherit `BaseDiagnosticStates` instead of inventing their own base state names
