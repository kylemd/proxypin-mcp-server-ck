# ProxyPin MCP Server (Enhanced)

![Version](https://img.shields.io/badge/version-2.0.0-blue)
![Python](https://img.shields.io/badge/python-3.10+-green)
![License](https://img.shields.io/badge/license-MIT-yellow)

High-performance HTTP request capture and analysis tool via MCP (Model Context Protocol). Connects to ProxyPin desktop and exposes 24 tools for LLM-driven traffic analysis.

## Features

- **Connection pooling** with automatic retry on transient failures
- **Thread-safe operations** for concurrent request handling
- **24 MCP tools** for searching, replaying, comparing, and rewriting HTTP traffic
- **Code generation** in Python, JavaScript, cURL, PHP, Java, Go
- **HAR import/export** for interoperability
- **API endpoint extraction** for auto-generating API documentation
- **Request comparison** with JSON diff support

## Quick Start

### Requirements
- Python 3.10+
- ProxyPin desktop running on port 17777

### Install with uv (recommended)

```bash
git clone https://github.com/1837620622/proxypin-mcp-server-ck.git
cd proxypin-mcp-server-ck
uv venv .venv --python 3.11
uv pip install -e . --python .venv/Scripts/python.exe  # Windows
# or: uv pip install -e . --python .venv/bin/python     # macOS/Linux
```

### Install with pip

```bash
git clone https://github.com/1837620622/proxypin-mcp-server-ck.git
cd proxypin-mcp-server-ck
pip install -e .
```

### Run directly

```bash
python proxypin_mcp_server.py
```

## Configuration

### Environment Variables

```bash
export PROXYPIN_HOST=127.0.0.1   # Default: localhost
export PROXYPIN_PORT=17777        # Default: 17777
```

### Claude Code MCP Config

Add to `~/.claude.json` under `"mcpServers"`:

```json
{
  "proxypin": {
    "type": "stdio",
    "command": "/path/to/.venv/Scripts/python.exe",
    "args": ["/path/to/proxypin_mcp_server.py"],
    "env": {
      "PROXYPIN_HOST": "127.0.0.1",
      "PROXYPIN_PORT": "17777"
    }
  }
}
```

### Codex CLI Config

Add to `~/.codex/config.toml`:

```toml
[mcp_servers.proxypin]
command = '/path/to/.venv/Scripts/python.exe'
args = ['/path/to/proxypin_mcp_server.py']

[mcp_servers.proxypin.env]
PROXYPIN_HOST = "127.0.0.1"
PROXYPIN_PORT = "17777"
```

## Tools Reference

### Search & Inspect
| Tool | Description |
|------|-------------|
| `search_requests` | Search captured HTTP requests with advanced filtering |
| `get_request_details` | Get full details of a captured request |
| `find_similar_requests` | Find requests with same domain, path, method |
| `get_recent_requests` | Get recent requests (legacy, use search_requests) |

### Actions
| Tool | Description |
|------|-------------|
| `replay_request` | Replay a captured request |
| `generate_code` | Generate code (Python/JS/cURL/PHP/Java/Go) |
| `get_curl` | Generate cURL command |
| `clear_requests` | Clear all captured requests |

### Analysis
| Tool | Description |
|------|-------------|
| `get_statistics` | Get request statistics |
| `compare_requests` | Compare two requests (diff) |
| `extract_api_endpoints` | Extract and group API endpoints |

### Rewriting
| Tool | Description |
|------|-------------|
| `add_response_rewrite` | Add response rewrite rule |
| `add_request_rewrite` | Add request rewrite rule |
| `block_url` | Block a URL pattern |
| `update_script` | Create/update a JavaScript script |
| `get_scripts` | List all scripts |

### Configuration
| Tool | Description |
|------|-------------|
| `start_proxy` | Start proxy server |
| `stop_proxy` | Stop proxy server |
| `set_config` | Set ProxyPin configuration |
| `add_host_mapping` | Add DNS host mapping |
| `get_proxy_status` | Get proxy status |
| `export_har` | Export requests as HAR |
| `import_har` | Import HAR file |
| `get_system_info` | Get server version and capabilities |

## Usage Examples

```python
# Search by domain
search_requests(domain="example.com", limit=10)

# Search by method and status
search_requests(method="POST", status_code="200")

# Generate Python code from a request
generate_code(request_id="12345", language="python")

# Compare two requests
compare_requests(request_id_1="123", request_id_2="456")

# Extract all API endpoints for a domain
extract_api_endpoints(domain_filter="api.example.com")
```

## Troubleshooting

**Cannot connect to ProxyPin:**
1. Ensure ProxyPin desktop is running
2. Check port 17777 is listening: `curl http://127.0.0.1:17777/sse`
3. Check firewall rules

**Import errors:**
```bash
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

## License

MIT - see [LICENSE](LICENSE)

## Credits

Original: ProxyPin Team | Enhanced by: [ChuanKangKK](https://github.com/1837620622)
