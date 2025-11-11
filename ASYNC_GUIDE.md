# Async/Await Guide for MCP Servers

This guide explains how to use async operations in your generated MCP servers and how to avoid common pitfalls.

## Table of Contents

- [Overview](#overview)
- [The Problem](#the-problem)
- [The Solution](#the-solution)
- [Usage Examples](#usage-examples)
- [Best Practices](#best-practices)
- [Migration Guide](#migration-guide)

## Overview

As of version 0.1.0, mcp-server-generator creates async-compatible MCP servers by default. This means you can easily add asynchronous operations like:

- API calls (using `httpx`, `aiohttp`, etc.)
- Database queries (using `asyncpg`, `motor`, etc.)
- File I/O (using `aiofiles`)
- Subprocess execution (using `asyncio.create_subprocess_exec`)

## The Problem

### Before: RuntimeError with asyncio.run()

Previously, when developers tried to add async operations to their MCP servers, they would encounter this error:

```python
# ❌ PROBLEMATIC CODE (causes RuntimeError)
def my_tool(url: str) -> Dict[str, Any]:
    async def fetch():
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            return response.json()

    # This fails! RuntimeError: asyncio.run() cannot be called from a running event loop
    data = asyncio.run(fetch())
    return {'data': data}
```

**Why this fails:**
- FastMCP runs an event loop to handle MCP protocol messages
- Tool handlers execute within that event loop
- `asyncio.run()` tries to create a new event loop
- Python doesn't allow nested event loops

## The Solution

### Generated Code Structure

The generator now creates async-compatible handlers automatically:

**Generated server.py:**
```python
import inspect
from mcp.server.fastmcp import FastMCP

@mcp.tool()
async def my_tool(url: str) -> str:
    result = generator.my_tool(url)

    # Handle both sync and async business logic
    if inspect.iscoroutine(result):
        result = await result

    return str(result)
```

This means:
1. ✅ Handlers are async by default
2. ✅ They automatically detect and await async business logic
3. ✅ Backward compatible with existing sync code

## Usage Examples

### Example 1: Synchronous Code (Still Works)

Your existing synchronous code continues to work without changes:

```python
# generator.py
def fetch_data(url: str) -> Dict[str, Any]:
    """Simple synchronous implementation."""
    return {
        'success': True,
        'message': 'Data fetched',
        'url': url
    }
```

### Example 2: Asynchronous API Calls

To add async operations, simply make your function async:

```python
# generator.py
async def fetch_data(url: str) -> Dict[str, Any]:
    """Async implementation with HTTP client."""
    import httpx

    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        data = response.json()

    return {
        'success': True,
        'data': data,
        'status_code': response.status_code
    }
```

### Example 3: Database Queries

```python
# generator.py
async def query_database(query: str) -> Dict[str, Any]:
    """Async database query example."""
    import asyncpg

    conn = await asyncpg.connect(user='user', database='mydb')
    try:
        result = await conn.fetch(query)
        return {
            'success': True,
            'rows': [dict(row) for row in result]
        }
    finally:
        await conn.close()
```

### Example 4: Multiple Concurrent Operations

```python
# generator.py
async def fetch_multiple_sources(urls: list) -> Dict[str, Any]:
    """Fetch from multiple URLs concurrently."""
    import httpx
    import asyncio

    async def fetch_one(client, url):
        response = await client.get(url)
        return response.json()

    async with httpx.AsyncClient() as client:
        tasks = [fetch_one(client, url) for url in urls]
        results = await asyncio.gather(*tasks)

    return {
        'success': True,
        'results': results,
        'count': len(results)
    }
```

### Example 5: File Operations

```python
# generator.py
async def read_large_file(filepath: str) -> Dict[str, Any]:
    """Async file reading example."""
    import aiofiles

    async with aiofiles.open(filepath, 'r') as f:
        content = await f.read()

    return {
        'success': True,
        'length': len(content),
        'preview': content[:100]
    }
```

## Best Practices

### 1. Use Async for I/O Operations

Make your functions async when they perform I/O operations:

```python
# ✅ Good: Async for I/O
async def fetch_api(url: str) -> Dict[str, Any]:
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        return response.json()

# ✅ Also Good: Sync for CPU-bound or simple operations
def calculate(x: int, y: int) -> Dict[str, Any]:
    return {'result': x + y}
```

### 2. Never Use asyncio.run() in Your Tools

```python
# ❌ Bad: Don't use asyncio.run()
def my_tool(url: str) -> Dict[str, Any]:
    result = asyncio.run(some_async_function())
    return result

# ✅ Good: Make the function async instead
async def my_tool(url: str) -> Dict[str, Any]:
    result = await some_async_function()
    return result
```

### 3. Use Proper Error Handling

```python
async def fetch_with_retry(url: str, retries: int = 3) -> Dict[str, Any]:
    """Async function with error handling and retries."""
    import httpx
    import asyncio

    for attempt in range(retries):
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=10.0)
                response.raise_for_status()
                return {
                    'success': True,
                    'data': response.json()
                }
        except httpx.HTTPError as e:
            if attempt == retries - 1:
                return {
                    'success': False,
                    'error': str(e)
                }
            await asyncio.sleep(2 ** attempt)  # Exponential backoff
```

### 4. Use Context Managers for Resource Management

```python
async def query_with_connection(query: str) -> Dict[str, Any]:
    """Use context managers to ensure cleanup."""
    import asyncpg

    # Context manager ensures connection is closed
    async with asyncpg.create_pool(database='mydb') as pool:
        async with pool.acquire() as conn:
            result = await conn.fetch(query)
            return {'rows': [dict(r) for r in result]}
```

### 5. Avoid Blocking Operations in Async Functions

```python
# ❌ Bad: Blocking operations in async function
async def bad_example():
    time.sleep(5)  # Blocks the entire event loop!
    return "done"

# ✅ Good: Use async sleep
async def good_example():
    await asyncio.sleep(5)  # Non-blocking
    return "done"

# ✅ Also Good: Run blocking code in executor
async def better_example():
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, blocking_function)
    return result
```

## Migration Guide

### Converting Existing Sync Code to Async

If you have existing synchronous code that you want to make async:

**Before:**
```python
def fetch_data(url: str) -> Dict[str, Any]:
    import requests
    response = requests.get(url)
    return {'data': response.json()}
```

**After:**
```python
async def fetch_data(url: str) -> Dict[str, Any]:
    import httpx
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        return {'data': response.json()}
```

### Common Library Replacements

When converting to async, replace these common libraries:

| Sync Library | Async Alternative |
|--------------|------------------|
| `requests` | `httpx`, `aiohttp` |
| `psycopg2` (PostgreSQL) | `asyncpg` |
| `pymongo` (MongoDB) | `motor` |
| `open()` | `aiofiles.open()` |
| `time.sleep()` | `asyncio.sleep()` |
| `subprocess.run()` | `asyncio.create_subprocess_exec()` |

### Testing Async Code

Use `pytest-asyncio` for testing:

```python
import pytest

@pytest.mark.asyncio
async def test_fetch_data():
    result = await fetch_data("https://api.example.com")
    assert result['success'] is True
```

## Troubleshooting

### Error: "RuntimeError: asyncio.run() cannot be called from a running event loop"

**Cause:** You're using `asyncio.run()` inside a function that's already running in an event loop.

**Solution:** Remove `asyncio.run()` and make your function async instead:

```python
# ❌ Wrong
def my_function():
    result = asyncio.run(async_operation())
    return result

# ✅ Correct
async def my_function():
    result = await async_operation()
    return result
```

### Error: "coroutine was never awaited"

**Cause:** You called an async function without using `await`.

**Solution:** Make sure you're using `await` when calling async functions:

```python
# ❌ Wrong
async def my_function():
    result = some_async_function()  # Missing await!
    return result

# ✅ Correct
async def my_function():
    result = await some_async_function()
    return result
```

### Debugging Tip: Check if Function is Async

```python
import inspect

# Check if your function is async
if inspect.iscoroutinefunction(my_function):
    print("This is an async function")
else:
    print("This is a sync function")
```

## Performance Benefits

Using async operations properly can significantly improve performance:

```python
# Sync: Takes 3 seconds (sequential)
def fetch_three_apis():
    data1 = requests.get(url1).json()  # 1 second
    data2 = requests.get(url2).json()  # 1 second
    data3 = requests.get(url3).json()  # 1 second
    return [data1, data2, data3]

# Async: Takes ~1 second (concurrent)
async def fetch_three_apis():
    async with httpx.AsyncClient() as client:
        results = await asyncio.gather(
            client.get(url1),
            client.get(url2),
            client.get(url3)
        )
    return [r.json() for r in results]
```

## Further Reading

- [Python asyncio documentation](https://docs.python.org/3/library/asyncio.html)
- [Real Python: Async IO in Python](https://realpython.com/async-io-python/)
- [FastMCP Documentation](https://github.com/jlowin/fastmcp)
- [HTTPX Async Client](https://www.python-httpx.org/async/)

## Questions?

If you encounter issues with async operations in your MCP server:

1. Check this guide for common patterns
2. Verify you're not using `asyncio.run()` in your tools
3. Make sure async functions are properly awaited
4. Review the generated code in `server.py` to understand the handler pattern

For bugs or feature requests, please file an issue on GitHub.
