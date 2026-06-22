.PHONY: init test test-fast test-resource-intensive test-resource-intensive-dymola test-resources-intensive-dymola test-all

PYTEST := poetry run pytest
PYTEST_ARGS := tests --doctest-modules
PYTEST_EXTRA_ARGS ?=
FAST_TEST_MARKERS := not simulation and not compilation and not dymola
RESOURCE_TEST_MARKERS := (simulation or compilation) and not dymola
DYMOLA_TEST_MARKERS := dymola

init:
	poetry install

# Default to the quick local feedback loop; this excludes Docker workloads.
test: test-fast

test-fast:
	$(PYTEST) $(PYTEST_ARGS) -n auto --dist loadgroup -m '$(FAST_TEST_MARKERS)' $(PYTEST_EXTRA_ARGS)

# One pytest process intentionally keeps Docker simulations and compilations serial.
test-resource-intensive:
	$(PYTEST) $(PYTEST_ARGS) -m '$(RESOURCE_TEST_MARKERS)' $(PYTEST_EXTRA_ARGS)

# Dymola requires a local installation and license, and must run in series.
test-resources-intensive-dymola:
	$(PYTEST) $(PYTEST_ARGS) -m '$(DYMOLA_TEST_MARKERS)' $(PYTEST_EXTRA_ARGS)

# Provide the singular spelling alongside the requested command.
test-resource-intensive-dymola: test-resources-intensive-dymola

# Run the fast suite first, then the resource-intensive suite in series.
test-all: test-fast test-resource-intensive
