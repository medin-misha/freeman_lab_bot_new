# Default Diagnostic Module

`default_diagnostic_module` is the Telegram entrypoint for the basic diagnostic
flow.

## Purpose

When a user sends the text `Базовая диагностика` or taps a reply button with
the same label, the module:

- sends the preview text from `messages.json`
- sends the PDF instruction file from the module `files/` directory
- shows a reply button `Назад`
- enters the shared FSM flow from `base_diagnostic_module`

Then it accepts:

- `document`
- `audio`
- `voice`

If the media message contains a `caption`, the module immediately creates the
backend diagnostic through `base_diagnostic_module`.

If the media message has no `caption`, the module asks for a follow-up text
message with the answers and submits the diagnostic after that.

## Configuration

All module-specific paths and static settings live in `config.py`:

- trigger text
- back button text
- diagnostic type constant
- path to the preview PDF
- path to `messages.json`

## Boundaries

- This module handles the user-facing flow and FSM transitions of the basic
  diagnostic.
- It does not own generic backend upload orchestration.
- Backend diagnostic creation is delegated to `base_diagnostic_module`.
