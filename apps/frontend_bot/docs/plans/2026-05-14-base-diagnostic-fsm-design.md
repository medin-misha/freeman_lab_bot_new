# Base Diagnostic FSM Design

## Goal

Add a shared FSM foundation to `apps/frontend_bot/app/modules/base_diagnostic_module`
so product diagnostic modules can inherit a common set of state names without
forcing a single handler implementation.

## Scope

This change adds only the base `StatesGroup` structure.

It does not add:

- base Telegram handlers
- shared transition helpers
- shared `FSMContext` persistence helpers
- product-specific diagnostic flow logic

## Supported Scenarios

The shared state model is designed around two common flows.

### File With Text

1. enter `waiting_for_file`
2. receive a file together with user text
3. move to `sending_to_server`
4. create the backend diagnostic

### File Without Text

1. enter `waiting_for_file`
2. receive a file without user text
3. move to `waiting_for_text`
4. receive the follow-up text message
5. move to `sending_to_server`
6. create the backend diagnostic

## Shared States

The base module should expose these reusable states:

- `waiting_for_file`
- `waiting_for_text`
- `sending_to_server`

## Why There Is No `file_received` State

`file_received` is not modeled as a standalone `State`.

Receiving a file is a short-lived event, not a stable user-facing step. Product
modules should store the received document data in `FSMContext` and then decide
whether to:

- continue directly to `sending_to_server`
- or ask for extra text through `waiting_for_text`

## Suggested FSM Data

The base module does not enforce storage keys yet, but product modules are
expected to keep at least:

- Telegram document identifiers or serialized document metadata
- optional user description text

This keeps the shared layer small while preserving flexibility for future
diagnostic modules.

## Public API

`base_diagnostic_module` should export the new base FSM class alongside the
existing `create_diagnostic(...)` helper.

## Verification

The implementation should be verified with a Python compile check for the
updated module package.
