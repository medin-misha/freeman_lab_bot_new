# Base Diagnostic Module

`base_diagnostic_module` is a shared backend module that owns the generic lifecycle of a diagnostic run.

It stores only fields common to every diagnostic and exposes:

- the `DiagnosticRun` ORM model;
- lifecycle service methods;
- thin HTTP endpoints under `/api/diagnostics`.

The module is intentionally generic:

- it knows nothing about product-specific scoring;
- it does not store diagnostic-only fields;
- it publishes shared lifecycle events through `rmq_module`.
