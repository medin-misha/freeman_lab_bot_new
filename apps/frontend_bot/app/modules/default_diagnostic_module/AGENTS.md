# Default Diagnostic Module Agent Context

## Purpose

`app/modules/default_diagnostic_module` owns the Telegram entrypoint for the
basic diagnostic product flow.

## What Belongs Here

- text trigger handling for `Базовая диагностика`
- sending the preview PDF and preview message
- product-specific static settings in `config.py`

## What Does Not Belong Here

- shared backend orchestration for diagnostic creation
- generic file upload or Telegram user lookup logic
- unrelated onboarding or menu behavior

## Design Rules

- Keep all file paths and static product settings in `config.py`
- Keep `handlers.py` thin and user-facing
- Keep text templates in `messages.json` and load them via `messages.py`
- Reuse `base_diagnostic_module` when this module later needs to create a
  backend diagnostic

## Safe Extension Points

- add the next-step handler for receiving voice/audio files
- call `base_diagnostic_module.create_diagnostic(...)` from a future flow step
- add more product-specific texts to `messages.json`
