# Model Registry

The Model Registry in SatQuery AI is responsible for mapping tasks (e.g. `TEMPORAL_CHANGE_DETECTION`) to available AI Specialist models (e.g. `ChangeFormer`).

## How it works

1. Specialists implement the `SpecialistModel` interface, declaring their `name` and `supported_tasks`.
2. Specialists are registered into the `ModelRegistry` upon engine initialization.
3. The `WorkflowExecutor` asks the registry for specific tools by name (e.g. `registry.get("ChangeFormer")`).
4. The executor validates `can_run()` on the tool before executing.

Currently, the registry is populated with lightweight Mock specialists for Day 1 development.
