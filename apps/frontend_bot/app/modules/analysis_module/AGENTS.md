# Analysis Module Agent Context

## Purpose

`app/modules/analysis_module` owns the Telegram booking flow for analysis
sessions.

## What Belongs Here

- entrypoint handling for `Записаться на Разбор`
- inline buttons for choosing public vs private analysis
- delivery of Google Form links for each analysis type
- scheduling step after the form is completed
- analysis registration creation through backend API

## What Does Not Belong Here

- CRM or admin-side follow-up logic after registration creation
- complex form completion business logic
- unrelated main-menu or diagnostics behavior

## Design Rules

- keep handlers thin and UI-focused
- keep user-facing texts in `messages.json`
- keep callback ids and inline keyboards in `keyboards.py`
- keep backend request orchestration in `service.py`
- do not move this flow into `menu_module`

## Safe Extension Points

- extend post-registration follow-up after backend record creation
- add admin notifications only if backend contract changes
- extend the module with extra analysis formats if the business flow grows
