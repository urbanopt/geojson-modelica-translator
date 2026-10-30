# GeoJSON Modelica Translator (GMT)

Project-wide context is in `../AGENTS.md`; shared preferences are in `~/.codex/AGENTS.md`.

- Source lives in `geojson_modelica_translator/`; tests live in `tests/`. GMT translates feature GeoJSON plus system-parameter JSON into Modelica packages. The CLI is `uo_des`.
- Start with `docs/getting_started.md`, `docs/input_file_documentation.md`, and `docs/developer_resources.md` for environment, input, and development details.
- `make test` / `make test-fast` runs the quick suite, excluding simulation, compilation, and Dymola. `make test-resource-intensive` runs non-Dymola simulation/compilation tests serially. `make test-resource-intensive-dymola` requires local Dymola and its license. `make test-all` does not include the Dymola suite.
- Preserve the Makefile's grouped parallel execution for fast tests and serial execution for simulation tests; some tests share filesystem state.
- Model generation and simulation have different prerequisites. Check the required Buildings Library version and `MODELICAPATH`; simulation workflows may require Docker or Dymola. Sibling Buildings Library directories are not interchangeable merely because they exist.
- `pyproject.toml` selects Modelica Builder; its sibling path dependency is commented out. Check the installed dependency before attributing behavior to edits in `../modelica-builder/`.
- Documentation uses MkDocs: `poetry run mkdocs serve` previews it and `poetry run mkdocs build --strict` validates it.
