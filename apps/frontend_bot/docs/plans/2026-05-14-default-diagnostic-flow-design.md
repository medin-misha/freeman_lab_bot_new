# Default Diagnostic Flow Design

## Goal

Implement the first real FSM-based diagnostic flow in
`apps/frontend_bot/app/modules/default_diagnostic_module`.

The module should guide the user from the preview screen to backend diagnostic
creation using the shared `base_diagnostic_module`.

## Entry Point

When the user sends `Базовая диагностика`, the module should:

1. send the diagnostic preview text together with the PDF instruction
2. attach a reply keyboard with a single `Назад` button
3. move the user into `BaseDiagnosticStates.waiting_for_file`

## Supported Media

The flow should accept these Telegram message types:

- `document`
- `audio`
- `voice`

## Text Source Rules

The diagnostic description should be taken from:

- `caption`, if the media message includes it
- a follow-up text message, if `caption` is missing

## Runtime Flow

### Media With Caption

1. user enters the flow
2. user sends `document`, `audio`, or `voice`
3. if `caption` is present, the bot immediately creates the diagnostic
4. on success, the bot replies that the diagnostic was received
5. on failure, the bot shows the developer contact message

### Media Without Caption

1. user enters the flow
2. user sends `document`, `audio`, or `voice` without `caption`
3. bot stores Telegram file metadata in `FSMContext`
4. bot asks the user to send the text answers
5. bot moves to `BaseDiagnosticStates.waiting_for_text`
6. user sends text
7. bot creates the diagnostic through the base module
8. bot reports success or failure and clears FSM state

## Back Navigation

The module should define a local reply button:

- `Назад`

When the user presses it:

1. clear FSM state
2. send the main menu using the existing `menu_module` delivery helper

## Shared Layer Change

`base_diagnostic_module` should gain one more public helper that creates a
diagnostic from raw Telegram file metadata:

- `telegram_file_id`
- `filename`
- `content_type`

This avoids duplicating Telegram download and backend upload logic in product
modules and supports delayed submission after `FSMContext` persistence.

## Verification

The implementation should be verified with a Python compile check for the
updated frontend modules.
