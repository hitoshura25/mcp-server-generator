# MCP SDK Migration Plan

## Overview
Migrate from manual JSON-RPC implementation to official MCP SDK (FastMCP) for both this generator AND the generated projects it creates.

## Problem Summary
- **Current Issue**: Server missing `initialize` method (MCP protocol requirement)
  - Test result: `{"error": {"code": -32601, "message": "Method not found: initialize"}}`
  - Root cause: Manual JSON-RPC implementation incomplete
- **Impact**:
  - This generator can't connect to Claude Desktop
  - ALL generated projects have the same issue
  - Manual protocol handling is error-prone and incomplete
- **Solution**: Official MCP SDK (FastMCP) handles all protocol details automatically

## Current Architecture Analysis

### What Works
- Core generator logic (`generator.py`) - solid templating system
- CLI interface (`cli.py`) - good dual-mode architecture
- Tool schema generation - correct JSON Schema output
- Project scaffolding - comprehensive file generation

### What's Broken
- `server.py` (both in templates and this project):
  - Missing `initialize` method handler
  - Missing `initialized` notification handler
  - No capabilities negotiation
  - Manual JSON-RPC message handling
  - No proper protocol version checking

### Dependencies Gap
- **Current**: Jinja2, pytest, pytest-asyncio
- **Needed**: `mcp>=1.0.0` (official SDK)
- **Templates**: No MCP SDK dependency specified

## Two-Track Implementation Strategy

### Track 1: Update Templates (Priority 1)
**Goal**: Ensure all NEW generated projects work correctly

**Files to modify:**
1. **`templates/python/server.py.j2`**
   - Replace manual `MCPServer` class with FastMCP
   - Use `@mcp.tool()` decorators instead of manual tool registration
   - Remove manual JSON-RPC handling
   - Simplify to ~30 lines vs current ~112 lines

2. **`templates/python/pyproject.toml.j2`**
   - Add `mcp>=1.0.0` to dependencies array (line 28-30)
   - Update `requires-python` to `>=3.10` (MCP SDK requirement)

3. **`templates/python/requirements.txt.j2`**
   - Add `mcp>=1.0.0` for development/testing

4. **`templates/python/tests/test_server.py.j2`**
   - Update tests to work with FastMCP API
   - Remove manual protocol tests (SDK handles this)
   - Focus on tool functionality testing

5. **`templates/python/README.md.j2`**
   - Update installation instructions
   - Show FastMCP-based examples
   - Update minimum Python version to 3.10

6. **`templates/python/MCP-USAGE.md.j2`**
   - Update protocol details section
   - Mention FastMCP handles initialization
   - Update troubleshooting section

**Key Template Changes:**

```python
# OLD (current template):
class MCPServer:
    def __init__(self):
        self.name = "{{ package_name }}"

    async def handle_list_tools(self):
        return {"tools": ...}

    async def handle_call_tool(self, tool_name, arguments):
        if tool_name == "foo":
            result = foo(**arguments)
            return {"content": [...], "isError": False}

    async def run(self):
        while True:
            line = sys.stdin.readline()
            # Manual JSON-RPC parsing...

# NEW (FastMCP):
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("{{ package_name }}")

{% for tool in tools %}
@mcp.tool()
def {{ tool.name }}(
    {% for param in tool.parameters %}
    {{ param.name }}: {% if param.type in ['string', 'str'] %}str{% elif ... %}
) -> str:
    """{{ tool.description }}"""
    from .generator import {{ tool.name }} as impl_{{ tool.name }}
    result = impl_{{ tool.name }}({{ params }})
    return str(result)
{% endfor %}
```

### Track 2: Dogfood on This Project (Priority 2)
**Goal**: Fix immediate connection issue + validate templates work

**Files to modify:**
1. **`hitoshura25_mcp_server_generator/server.py`**
   - Apply same FastMCP migration as template
   - Wrap generator.generate_mcp_server and generator.validate_project_name
   - Keep current tool interface (no changes to generator.py needed)

2. **`pyproject.toml`**
   - Add `"mcp>=1.0.0"` to dependencies (line 28-31)
   - Update `requires-python` to `">=3.10"`
   - Update Python version classifiers

3. **`requirements.txt`**
   - Add `mcp>=1.0.0`

4. **`hitoshura25_mcp_server_generator/tests/test_server.py`**
   - Update to test FastMCP implementation
   - Keep existing test coverage

**Validation Steps:**
```bash
# 1. Install updated dependencies
pip install mcp>=1.0.0

# 2. Test initialization locally
echo '{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "test", "version": "1.0"}}}' | python -m hitoshura25_mcp_server_generator.server

# 3. Test with MCP Inspector
uvx mcp dev hitoshura25_mcp_server_generator/server.py

# 4. Test with Claude Desktop
claude mcp add mcp-server-generator uvx hitoshura25-mcp-server-generator

# 5. Generate a test project with updated templates
python -m hitoshura25_mcp_server_generator.cli --interactive

# 6. Test the generated project
cd test-project && uvx mcp dev test_project/server.py
```

### Track 3: Testing & Validation (Priority 3)
**Goal**: Comprehensive validation of both tracks

**Test Scenarios:**
1. **Generator Tests** (this project)
   - ✅ Server initializes properly
   - ✅ Server responds to initialize request
   - ✅ Tools list correctly
   - ✅ Tools execute and return results
   - ✅ Connects to Claude Desktop

2. **Generated Project Tests** (using updated templates)
   - ✅ Generate project with single tool
   - ✅ Generate project with multiple tools
   - ✅ Generated server initializes
   - ✅ Generated server connects to Claude Desktop
   - ✅ Generated tests pass
   - ✅ CLI mode still works

3. **Regression Tests**
   - ✅ Existing generator.py functions unchanged
   - ✅ CLI interface unchanged
   - ✅ Tool schema generation unchanged
   - ✅ File generation still works
   - ✅ Prefix logic still works

## Implementation Phases

### Phase 1: Update Templates (Days 1-2)
1. Modify `templates/python/server.py.j2` → FastMCP version
2. Update `templates/python/pyproject.toml.j2` → add mcp dependency
3. Update `templates/python/requirements.txt.j2` → add mcp
4. Update `templates/python/tests/test_server.py.j2` → new test approach
5. Update documentation templates (README, MCP-USAGE)
6. Test template rendering (ensure no Jinja2 errors)

### Phase 2: Fix This Project (Days 2-3)
1. Add `mcp>=1.0.0` to this project's dependencies
2. Rewrite `hitoshura25_mcp_server_generator/server.py` using FastMCP
3. Update `hitoshura25_mcp_server_generator/tests/test_server.py`
4. Test locally with manual JSON-RPC
5. Test with MCP Inspector
6. Test with Claude Desktop connection

### Phase 3: Dogfooding Validation (Day 3)
1. Generate a test project using updated templates
2. Verify generated project structure
3. Run generated project's tests
4. Test generated project with MCP Inspector
5. Test generated project with Claude Desktop
6. Compare with manually-working MCP servers

### Phase 4: Documentation & Release (Day 4)
1. Update main README.md with migration notes
2. Add CHANGELOG entry
3. Version bump (0.x.x → 0.y.0, minor bump for feature)
4. Create migration guide for existing users
5. Test PyPI package build
6. Release new version

## Breaking Changes & Migration

### For This Project Users
**Breaking Changes:**
- Minimum Python version: 3.8 → 3.10 (MCP SDK requirement)
- New dependency: `mcp>=1.0.0`

**Migration Path:**
- Update Python to 3.10+
- Re-install: `pip install --upgrade hitoshura25-mcp-server-generator`
- No config changes needed (transparent)

### For Generated Project Users
**Breaking Changes:**
- Projects generated with new version require Python 3.10+
- New runtime dependency: `mcp>=1.0.0`

**Migration Path for Existing Generated Projects:**
1. Update `pyproject.toml`: requires-python = ">=3.10"
2. Add to dependencies: `"mcp>=1.0.0"`
3. Replace `server.py` with FastMCP implementation
4. Update tests to match new API
5. Test thoroughly before deploying

**Recommendation**:
- Mark this as a **minor version bump** (0.x → 0.y)
- Clearly document in release notes
- Consider keeping old template version available for Python 3.8-3.9 users

## Benefits of Migration

### Immediate Benefits
✅ **Works with Claude Desktop** - proper protocol implementation
✅ **Less code** - ~112 lines → ~30 lines in server.py
✅ **Better error handling** - SDK handles edge cases
✅ **Proper initialization** - initialize/initialized handshake
✅ **Capabilities negotiation** - automatic protocol version handling

### Long-term Benefits
✅ **Future-proof** - SDK evolves with MCP spec
✅ **Better testing** - official test utilities
✅ **Community alignment** - uses official tooling
✅ **Reduced maintenance** - less protocol code to maintain
✅ **Better debugging** - MCP Inspector integration

### Developer Experience
✅ **Simpler template** - decorators vs manual routing
✅ **Type safety** - proper type hints in decorators
✅ **Documentation** - official SDK docs available
✅ **Examples** - many reference implementations

## Risks & Mitigation

### Risk 1: Python 3.10+ Requirement
**Impact**: Users on 3.8/3.9 can't use new version
**Mitigation**:
- Document clearly in README
- Consider maintaining 3.8-compatible branch
- Most modern systems have 3.10+ available

### Risk 2: Breaking Change for Existing Generated Projects
**Impact**: Existing projects need manual migration
**Mitigation**:
- Provide detailed migration guide
- Version bump clearly indicates breaking change
- Old version remains on PyPI for legacy use

### Risk 3: FastMCP API Changes
**Impact**: Future SDK updates might break our implementation
**Mitigation**:
- Pin to `mcp>=1.0.0,<2.0.0` for stability
- Monitor MCP SDK releases
- Keep tests comprehensive

### Risk 4: Template Complexity
**Impact**: FastMCP decorators harder to template
**Mitigation**:
- Already analyzed - Jinja2 can handle it
- Decorators actually simpler than manual routing
- Test thoroughly during Phase 1

## Success Criteria

### Must Have (Phase 1-2)
- [ ] Templates generate FastMCP-based servers
- [ ] This project uses FastMCP
- [ ] `initialize` method works correctly
- [ ] Server connects to Claude Desktop
- [ ] All existing tests pass (updated)
- [ ] CLI mode still works

### Should Have (Phase 3)
- [ ] Generated project passes all tests
- [ ] Generated project connects to Claude Desktop
- [ ] MCP Inspector shows tools correctly
- [ ] Documentation updated

### Nice to Have (Phase 4)
- [ ] Migration guide for existing users
- [ ] Example projects updated
- [ ] Performance benchmarks (SDK vs manual)

## Timeline Estimate

- **Phase 1** (Templates): 8-12 hours
- **Phase 2** (This Project): 4-6 hours
- **Phase 3** (Validation): 4-6 hours
- **Phase 4** (Documentation): 2-4 hours

**Total**: 18-28 hours (2-4 days of focused work)

## Next Steps

1. **Immediate**: Update templates/python/server.py.j2 with FastMCP
2. **Next**: Add mcp dependency to template pyproject.toml.j2
3. **Then**: Update this project's server.py
4. **Finally**: Comprehensive testing and validation

## Notes

- Keep `generator.py` unchanged - core logic is solid
- Keep `cli.py` unchanged - CLI interface is separate
- Focus changes on MCP server protocol implementation only
- Maintain dual-mode architecture (MCP + CLI)
- Preserve all existing features (prefix, tool schemas, etc.)
