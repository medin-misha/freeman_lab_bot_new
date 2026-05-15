# Default Diagnostic Module

Product module for the free default diagnostic flow.

Responsibilities:

- accept a simplified product request from the bot;
- create a generic `DiagnosticRun` with `diagnostic_code="default"`;
- store a module-specific extension record in `DefaultDiagnostic`.
