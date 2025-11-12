# Update Dependency Management to PEP 621 - Technical Specification

## 1. Feature Overview
This feature updates the project templates within `hitoshura25-mcp-server-generator` to adopt modern Python packaging standards (PEP 621). The `requirements.txt` file will be eliminated in favor of declaring all project dependencies directly within `pyproject.toml`. This change, inspired by `hitoshura25-pypi-workflow-generator v0.5.0`, simplifies dependency management, provides a single source of truth for project metadata, and aligns generated projects with current best practices.

## 2. Architecture Overview
The core architecture of the generator remains unchanged. The `generator.py` script will continue to use Jinja2 to render project templates from the `hitoshura25_mcp_server_generator/templates/python/` directory.

The key modifications are:
1.  **Dependency Data Flow:** The list of dependencies, currently passed to `requirements.txt.j2`, will be redirected to the `pyproject.toml.j2` template.
2.  **Template Changes:** `pyproject.toml.j2` will be updated to include a `[project.dependencies]` section. The `requirements.txt.j2` template will be removed.
3.  **CI/CD Workflow:** The GitHub workflow templates, which are copied into the generated project, will be modified. The dependency installation step will be changed from `pip install -r requirements.txt` to `pip install .` (or `pip install -e .[dev]`), which uses `pyproject.toml`.

This change affects only the structure and content of the *generated* project, not the generator itself.

## 3. Database Changes
### Schema Modifications
N/A

### Migration Scripts Needed
N/A

## 4. Files to Create
None.

*(Note: `hitoshura25_mcp_server_generator/templates/python/requirements.txt.j2` will be deleted.)*

## 5. Files to Modify
1.  **`hitoshura25_mcp_server_generator/generator.py`**
    *   Remove the logic for rendering `requirements.txt.j2`.
    *   Modify the template rendering context for `pyproject.toml.j2` to include the list of project dependencies.

2.  **`hitoshura25_mcp_server_generator/templates/python/pyproject.toml.j2`**
    *   Add a `[project]` section if it doesn't exist.
    *   Add a `dependencies` key under `[project]` to dynamically list the project dependencies from the Jinja2 context.
    *   Example:
        ```toml
        [project]
        name = "{{ project_name }}"
        version = "0.1.0"
        dependencies = [
          {% for dep in dependencies %}"{{ dep }}",{% endfor %}
        ]
        ```
    *   Add an `[project.optional-dependencies]` table for development dependencies (e.g., `pytest`, `black`).

3.  **`hitoshura25_mcp_server_generator/templates/python/setup.py.j2`**
    *   Remove any logic that reads `requirements.txt` to populate `install_requires`. `setuptools` will automatically use the `[project.dependencies]` from `pyproject.toml`.

4.  **`.github/workflows/_reusable-test-build.yml`**
    *   Locate the step that installs dependencies.
    *   Replace `pip install -r requirements.txt` with `pip install -e .[dev]` (or the equivalent that installs main and test dependencies).

5.  **`.github/workflows/release.yml`**
    *   Locate the build/publish steps.
    *   Ensure dependency installation for the build environment uses the new `pyproject.toml` standard (e.g., `pip install build`). The build process itself (`python -m build`) will correctly use `pyproject.toml`.

6.  **`hitoshura25_mcp_server_generator/templates/python/README.md.j2`**
    *   Update the "Installation" or "Development Setup" sections.
    *   Replace instructions for `pip install -r requirements.txt` with `pip install -e .[dev]`.

7.  **`hitoshura25_mcp_server_generator/templates/python/MANIFEST.in.j2`**
    *   Remove the line that includes `requirements.txt` if it exists.

## 6. Implementation Tasks (Ordered)
1.  Modify `hitoshura25_mcp_server_generator/templates/python/pyproject.toml.j2` to accept and define project dependencies and optional development dependencies.
2.  Delete the `hitoshura25_mcp_server_generator/templates/python/requirements.txt.j2` file.
3.  Update `hitoshura25_mcp_server_generator/generator.py` to stop rendering `requirements.txt.j2` and to pass the dependency list to `pyproject.toml.j2`'s context.
4.  Modify `hitoshura25_mcp_server_generator/templates/python/setup.py.j2` to remove any manual reading of `requirements.txt`.
5.  Update the dependency installation step in `.github/workflows/_reusable-test-build.yml` to use `pip install -e .[dev]`.
6.  Review and update `.github/workflows/release.yml` to ensure the build process is aligned with `pyproject.toml`.
7.  Update documentation templates (`README.md.j2`, `MCP-USAGE.md.j2`, etc.) with the new installation instructions.
8.  Remove any reference to `requirements.txt` from `hitoshura25_mcp_server_generator/templates/python/MANIFEST.in.j2`.
9.  Update `hitoshura25_mcp_server_generator/tests/test_generator.py` to assert that `requirements.txt` is no longer created and that `pyproject.toml` contains the correct dependency data in the generated project.
10. Manually run the generator to create a test project and verify that it can be installed, tested, and built correctly using the new `pyproject.toml`-based workflow.

## 7. Testing Requirements
### Unit Tests
*   **`test_generator.py`**:
    *   Verify that a generated project no longer contains a `requirements.txt` file.
    *   Verify that the generated `pyproject.toml` correctly lists the base dependencies.
    *   Verify that the generated `pyproject.toml` correctly lists development dependencies under `[project.optional-dependencies]`.

### Integration Tests
*   A test that runs the generator to create a temporary project.
*   Within the temporary project's directory, the test should:
    1.  Execute `pip install -e .[dev]`.
    2.  Run the project's test suite (e.g., `pytest`).
    3.  Confirm that both commands execute successfully.

### E2E Tests
*   Execute the `mcp-server-generator` CLI to create a new project in a temporary directory.
*   Initialize a git repository in the new project.
*   Simulate a CI run by executing the key steps from the generated `.github/workflows/test-pr.yml` workflow locally to ensure the workflow logic is sound.

## 8. Security Considerations
*   Consolidating dependencies into `pyproject.toml` is a standard practice and introduces no new inherent security risks.
*   It is recommended to use version specifiers for all dependencies (e.g., `requests>=2.28`) in the templates to mitigate the risk of installing a compromised or broken package. For applications, pinning dependencies via a lock file is best practice, though this specification does not mandate a specific locking tool.

## 9. Performance Considerations
*   This change has no impact on the runtime performance of the generated application.
*   CI/CD build times may be marginally affected by the change in dependency installation commands, but the difference is expected to be negligible. Caching mechanisms for `pip` should continue to function as before.

## 10. Dependencies
*   No new dependencies are required for the `hitoshura25-mcp-server-generator` project itself.