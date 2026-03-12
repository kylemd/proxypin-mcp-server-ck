#!/usr/bin/env python3
"""
ProxyPin MCP Server - Enhanced Edition
=======================================

Original author: ProxyPin Team
Enhanced by: ChuanKangKK (GitHub: 1837620622)

Features:
- High-performance HTTP request capture and analysis
- Advanced request filtering and search
- Code generation and request replay
- HAR file import/export
- Request comparison and diff
- API endpoint extraction
- Enhanced error handling and logging
- Connection pooling
- Thread-safe operations

Version: 2.0.0-chuankangkk
"""

import os
import sys
import json
import logging
import time
import threading
from datetime import datetime
from typing import Dict, Any, Optional, List, Union
import ipaddress
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from fastmcp import FastMCP

# ========================================
# System Configuration
# ========================================

__version__ = "2.0.0-chuankangkk"
__author__ = "ChuanKangKK (GitHub: 1837620622)"
__contact__ = "Email: 2040168455@qq.com"

# Logging configuration - log file in same directory as script
_log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "proxypin_mcp.log")
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(_log_file, encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

# Reduce third-party library log noise
logging.getLogger('urllib3').setLevel(logging.WARNING)
logging.getLogger('requests').setLevel(logging.WARNING)

# ProxyPin HTTP API configuration
PROXYPIN_HOST = os.getenv("PROXYPIN_HOST", "127.0.0.1")
PROXYPIN_PORT = int(os.getenv("PROXYPIN_PORT", "17777"))
BASE_URL = f"http://{PROXYPIN_HOST}:{PROXYPIN_PORT}"
MESSAGES_URL = f"{BASE_URL}/messages"

# Connection pool configuration
MAX_RETRIES = 3
BACKOFF_FACTOR = 0.5
TIMEOUT = 30
POOL_CONNECTIONS = 20
POOL_MAXSIZE = 50
POOL_BLOCK = False
KEEP_ALIVE = True

# Create optimized HTTP session with connection pooling
def create_optimized_session() -> requests.Session:
    """Create an optimized HTTP session with retry logic and connection pooling."""
    session = requests.Session()
    session.trust_env = False

    # Retry strategy
    retry_strategy = Retry(
        total=MAX_RETRIES,
        backoff_factor=BACKOFF_FACTOR,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["HEAD", "GET", "PUT", "DELETE", "OPTIONS", "TRACE", "POST"]
    )

    # HTTP adapter with connection pooling
    adapter = HTTPAdapter(
        max_retries=retry_strategy,
        pool_connections=POOL_CONNECTIONS,
        pool_maxsize=POOL_MAXSIZE,
        pool_block=POOL_BLOCK
    )

    session.mount("http://", adapter)
    session.mount("https://", adapter)

    # Default request headers
    session.headers.update({
        'User-Agent': f'ProxyPin-MCP-Server/{__version__}',
        'Accept': 'application/json',
        'Connection': 'keep-alive' if KEEP_ALIVE else 'close'
    })

    logger.info("Created optimized HTTP session with connection pooling")
    return session

# Global session instance
session = create_optimized_session()
request_id_counter = 1
_counter_lock = threading.Lock()

def call_proxypin_tool(tool_name: str, arguments: Optional[Dict[str, Any]] = None) -> Any:
    """
    Call a ProxyPin MCP tool via JSON-RPC.

    Features:
    - Thread-safe request ID management
    - Performance monitoring and logging
    - Automatic retry on transient failures
    - Classified exception handling
    - Response data validation

    Args:
        tool_name: Name of the tool to call
        arguments: Tool arguments dict

    Returns:
        Tool call result

    Raises:
        Exception: When the tool call fails
    """
    global request_id_counter

    # Thread-safe counter increment
    with _counter_lock:
        current_id = request_id_counter
        request_id_counter += 1

    if arguments is None:
        arguments = {}

    # Record request start time for performance monitoring
    start_time = time.time()

    payload = {
        "jsonrpc": "2.0",
        "id": current_id,
        "method": "tools/call",
        "params": {
            "name": tool_name,
            "arguments": arguments
        }
    }

    logger.debug(f"Calling tool: {tool_name}, args: {arguments}, request_id: {current_id}")

    try:
        response = session.post(MESSAGES_URL, json=payload, timeout=TIMEOUT)
        response.raise_for_status()

        # Calculate response time in ms
        response_time = (time.time() - start_time) * 1000

        # Parse JSON response
        try:
            result = response.json()
        except json.JSONDecodeError as e:
            logger.error(f"JSON parse failed: {e}, response: {response.text[:500]}")
            raise Exception(f"ProxyPin returned invalid JSON: {e}")

        # Check for MCP errors
        if "error" in result:
            error_info = result["error"]
            logger.error(f"MCP tool call error: {error_info}")
            raise Exception(f"MCP Error: {error_info}")

        # Extract and validate result content
        result_data = result.get("result", {})
        content = result_data.get("content", [])

        if not content:
            logger.warning(f"Tool {tool_name} returned empty content")
            return {}

        # Parse response text
        response_text = content[0].get("text", "{}")
        try:
            parsed_result = json.loads(response_text)
            logger.info(f"Tool {tool_name} succeeded, response_time: {response_time:.2f}ms")
            return parsed_result
        except json.JSONDecodeError as e:
            logger.error(f"Tool response JSON parse failed: {e}, content: {response_text[:200]}")
            return {"raw_response": response_text, "parse_error": str(e)}

    except requests.exceptions.Timeout as e:
        logger.error(f"ProxyPin connection timeout: {e}")
        raise Exception(f"ProxyPin connection timeout: check service is running at {BASE_URL}")

    except requests.exceptions.ConnectionError as e:
        logger.error(f"ProxyPin connection error: {e}")
        raise Exception(f"Cannot connect to ProxyPin: ensure service is running at {BASE_URL}")

    except requests.exceptions.HTTPError as e:
        status_code = getattr(e.response, 'status_code', 'unknown') if hasattr(e, 'response') and e.response else 'unknown'
        logger.error(f"ProxyPin HTTP error: {e}, status: {status_code}")
        raise Exception(f"ProxyPin HTTP error: {e}")

    except requests.exceptions.RequestException as e:
        logger.error(f"ProxyPin request error: {e}")
        raise Exception(f"ProxyPin request failed: {e}")

    except Exception as e:
        logger.error(f"Tool call unknown error: {e}")
        raise Exception(f"Tool call failed: {e}")

# ========================================
# MCP Server Instance
# ========================================

mcp = FastMCP("ProxyPin-MCP-Server")

def log_tool_call(tool_name: str, **kwargs):
    """Log a tool call with its arguments."""
    logger.info(f"Executing tool: {tool_name}, args: {kwargs}")

# ========================================
# MCP Tool Functions
# ========================================

@mcp.tool()
def search_requests(
    query: str = None,
    method: str = None,
    status_code: str = None,
    domain: str = None,
    header_search: str = None,
    request_body_search: str = None,
    response_body_search: str = None,
    min_duration: int = None,
    max_duration: int = None,
    limit: int = 20
):
    """
    Search captured HTTP requests with advanced filtering.

    Supported filters:
    - query: URL keyword search
    - method: HTTP method (GET/POST/PUT/DELETE etc.)
    - status_code: Status code filter ("200" or "2xx" range)
    - domain: Exact domain match
    - header_search: Search in request/response headers
    - request_body_search: Search in request body (max 1MB)
    - response_body_search: Search in response body (max 1MB)
    - min_duration/max_duration: Response time range filter (ms)
    - limit: Max number of results to return

    Returns:
        List of matching HTTP requests with details
    """
    log_tool_call("search_requests",
                  query=query, method=method, status_code=status_code,
                  domain=domain, limit=limit)

    # Build search parameters
    args = {"limit": min(limit, 1000)}

    if query:
        args["query"] = str(query).strip()
    if method:
        args["method"] = str(method).upper()
    if status_code:
        args["status_code"] = str(status_code)
    if domain:
        args["domain"] = str(domain).lower()
    if header_search:
        args["header_search"] = str(header_search)
    if request_body_search:
        args["request_body_search"] = str(request_body_search)
    if response_body_search:
        args["response_body_search"] = str(response_body_search)
    if min_duration is not None:
        args["min_duration"] = max(0, int(min_duration))
    if max_duration is not None:
        args["max_duration"] = max(0, int(max_duration))

    return call_proxypin_tool("search_requests", args)

@mcp.tool()
def get_request_details(request_id: str):
    """Get full details of a captured request by ID."""
    log_tool_call("get_request_details", request_id=request_id)
    if not request_id or not request_id.strip():
        raise ValueError("Request ID must not be empty")
    return call_proxypin_tool("get_request_details", {"request_id": request_id.strip()})

@mcp.tool()
def replay_request(request_id: str):
    """Replay a captured request."""
    log_tool_call("replay_request", request_id=request_id)
    if not request_id or not request_id.strip():
        raise ValueError("Request ID must not be empty")
    return call_proxypin_tool("replay_request", {"request_id": request_id.strip()})

@mcp.tool()
def generate_code(request_id: str, language: str = "python"):
    """Generate code (Python/JS/cURL) to reproduce a captured request.

    Args:
        request_id: ID of the request to generate code for
        language: Target language (python, javascript, js, curl, php, java, go)
    """
    log_tool_call("generate_code", request_id=request_id, language=language)
    if not request_id or not request_id.strip():
        raise ValueError("Request ID must not be empty")

    supported_languages = ["python", "javascript", "js", "curl", "php", "java", "go"]
    language = language.lower().strip()

    if language not in supported_languages:
        raise ValueError(f"Unsupported language: {language}. Supported: {', '.join(supported_languages)}")

    return call_proxypin_tool("generate_code", {
        "request_id": request_id.strip(),
        "language": language
    })

@mcp.tool()
def get_curl(request_id: str):
    """Generate a cURL command from a captured request."""
    log_tool_call("get_curl", request_id=request_id)
    if not request_id or not request_id.strip():
        raise ValueError("Request ID must not be empty")
    return call_proxypin_tool("get_curl", {"request_id": request_id.strip()})

@mcp.tool()
def block_url(url_pattern: str, block_type: str = "blockRequest"):
    """Block a URL pattern.

    Args:
        url_pattern: URL pattern to block (supports wildcards)
        block_type: Block type - blockRequest or blockResponse
    """
    log_tool_call("block_url", url_pattern=url_pattern, block_type=block_type)

    if not url_pattern or not url_pattern.strip():
        raise ValueError("URL pattern must not be empty")

    if block_type not in ["blockRequest", "blockResponse"]:
        raise ValueError("block_type must be blockRequest or blockResponse")

    return call_proxypin_tool("block_url", {
        "url_pattern": url_pattern.strip(),
        "block_type": block_type
    })

@mcp.tool()
def add_response_rewrite(url_pattern: str, rewrite_type: str, value: str, key: str = None):
    """Add a response rewrite rule.

    Args:
        url_pattern: URL pattern to match
        rewrite_type: Type of rewrite
        value: Rewrite value
        key: Optional key name
    """
    log_tool_call("add_response_rewrite",
                  url_pattern=url_pattern,
                  rewrite_type=rewrite_type,
                  value=value,
                  key=key)

    if not url_pattern or not url_pattern.strip():
        raise ValueError("URL pattern must not be empty")
    if not rewrite_type or not rewrite_type.strip():
        raise ValueError("Rewrite type must not be empty")
    if not value or not value.strip():
        raise ValueError("Rewrite value must not be empty")

    args = {
        "url_pattern": url_pattern.strip(),
        "rewrite_type": rewrite_type.strip(),
        "value": value.strip()
    }
    if key:
        args["key"] = key.strip()

    return call_proxypin_tool("add_response_rewrite", args)

@mcp.tool()
def add_request_rewrite(url_pattern: str, rewrite_type: str, key: str, value: str):
    """Add a request rewrite rule.

    Args:
        url_pattern: URL pattern to match
        rewrite_type: Type of rewrite
        key: Key name
        value: Key value
    """
    log_tool_call("add_request_rewrite",
                  url_pattern=url_pattern,
                  rewrite_type=rewrite_type,
                  key=key,
                  value=value)

    if not url_pattern or not url_pattern.strip():
        raise ValueError("URL pattern must not be empty")
    if not rewrite_type or not rewrite_type.strip():
        raise ValueError("Rewrite type must not be empty")
    if not key or not key.strip():
        raise ValueError("Key must not be empty")
    if not value or not value.strip():
        raise ValueError("Value must not be empty")

    return call_proxypin_tool("add_request_rewrite", {
        "url_pattern": url_pattern.strip(),
        "rewrite_type": rewrite_type.strip(),
        "key": key.strip(),
        "value": value.strip()
    })

@mcp.tool()
def update_script(name: str, url_pattern: str, script_content: str):
    """Create or update a JavaScript script.

    Args:
        name: Script name
        url_pattern: URL pattern to match
        script_content: JavaScript code content
    """
    log_tool_call("update_script",
                  name=name,
                  url_pattern=url_pattern,
                  script_content_length=len(script_content) if script_content else 0)

    if not name or not name.strip():
        raise ValueError("Script name must not be empty")
    if not url_pattern or not url_pattern.strip():
        raise ValueError("URL pattern must not be empty")
    if not script_content or not script_content.strip():
        raise ValueError("Script content must not be empty")

    if len(script_content) > 100000:  # 100KB limit
        raise ValueError("Script content too large, max 100KB")

    return call_proxypin_tool("update_script", {
        "name": name.strip(),
        "url_pattern": url_pattern.strip(),
        "script_content": script_content
    })

@mcp.tool()
def get_scripts():
    """List all scripts."""
    return call_proxypin_tool("get_scripts")

@mcp.tool()
def set_config(system_proxy: bool = None, ssl_capture: bool = None):
    """Set ProxyPin configuration."""
    args = {}
    if system_proxy is not None:
        args["system_proxy"] = system_proxy
    if ssl_capture is not None:
        args["ssl_capture"] = ssl_capture
    return call_proxypin_tool("set_config", args)

@mcp.tool()
def add_host_mapping(domain: str, ip: str):
    """Add a host mapping (DNS override).

    Args:
        domain: Domain name
        ip: IP address to resolve to
    """
    log_tool_call("add_host_mapping", domain=domain, ip=ip)

    if not domain or not domain.strip():
        raise ValueError("Domain must not be empty")
    if not ip or not ip.strip():
        raise ValueError("IP address must not be empty")

    try:
        ipaddress.ip_address(ip.strip())
    except ValueError:
        raise ValueError("Invalid IP address format")

    return call_proxypin_tool("add_host_mapping", {
        "domain": domain.strip().lower(),
        "ip": ip.strip()
    })

@mcp.tool()
def get_proxy_status():
    """Get proxy server status."""
    return call_proxypin_tool("get_proxy_status")

@mcp.tool()
def export_har(limit: int = 100):
    """Export captured requests as HAR."""
    return call_proxypin_tool("export_har", {"limit": limit})

@mcp.tool()
def import_har(har_content: str):
    """Import a HAR file into ProxyPin.

    Args:
        har_content: HAR JSON string
    """
    log_tool_call("import_har", har_content_length=len(har_content) if har_content else 0)

    if not har_content or not har_content.strip():
        raise ValueError("HAR content must not be empty")

    # Validate HAR format
    try:
        har_data = json.loads(har_content)
        if not isinstance(har_data, dict) or 'log' not in har_data:
            raise ValueError("Invalid HAR format: missing 'log' field")
    except json.JSONDecodeError as e:
        raise ValueError(f"HAR content is not valid JSON: {e}")

    if len(har_content) > 10000000:  # 10MB limit
        raise ValueError("HAR file too large, max 10MB")

    return call_proxypin_tool("import_har", {"har_content": har_content})

@mcp.tool()
def start_proxy(port: int = 9099):
    """Start the proxy server.

    Args:
        port: Proxy port (default 9099)
    """
    log_tool_call("start_proxy", port=port)

    if not isinstance(port, int):
        raise TypeError("Port must be an integer")
    if port < 1024 or port > 65535:
        raise ValueError("Port must be between 1024 and 65535")

    return call_proxypin_tool("start_proxy", {"port": port})

@mcp.tool()
def stop_proxy():
    """Stop the proxy server."""
    return call_proxypin_tool("stop_proxy")

@mcp.tool()
def get_recent_requests(limit: int = 20, url_filter: str = None, method: str = None):
    """Get recent captured requests (legacy). Use search_requests instead."""
    args = {"limit": limit}
    if url_filter:
        args["url_filter"] = url_filter
    if method:
        args["method"] = method
    return call_proxypin_tool("get_recent_requests", args)

@mcp.tool()
def clear_requests():
    """Clear all captured requests."""
    return call_proxypin_tool("clear_requests")

@mcp.tool()
def get_statistics():
    """Get request statistics.

    Returns:
        Statistics including total count, method distribution, status code
        distribution (2xx/3xx/4xx/5xx), domain distribution, total size,
        average duration, and error count.
    """
    return call_proxypin_tool("get_statistics")

@mcp.tool()
def compare_requests(request_id_1: str, request_id_2: str):
    """Compare two captured requests and show differences.

    Returns detailed diff including request/response header diffs,
    request/response body diffs (supports JSON diff), and duration diff.
    """
    log_tool_call("compare_requests", request_id_1=request_id_1, request_id_2=request_id_2)

    if not request_id_1 or not request_id_1.strip():
        raise ValueError("First request ID must not be empty")
    if not request_id_2 or not request_id_2.strip():
        raise ValueError("Second request ID must not be empty")
    if request_id_1.strip() == request_id_2.strip():
        raise ValueError("Request IDs must be different")

    return call_proxypin_tool("compare_requests", {
        "request_id_1": request_id_1.strip(),
        "request_id_2": request_id_2.strip()
    })

@mcp.tool()
def find_similar_requests(request_id: str, limit: int = 10):
    """Find requests similar to a given request (same domain, path, method).

    Args:
        request_id: Reference request ID
        limit: Max results (1-100)
    """
    log_tool_call("find_similar_requests", request_id=request_id, limit=limit)

    if not request_id or not request_id.strip():
        raise ValueError("Request ID must not be empty")
    if not isinstance(limit, int):
        raise TypeError("limit must be an integer")
    if limit < 1 or limit > 100:
        raise ValueError("limit must be between 1 and 100")

    return call_proxypin_tool("find_similar_requests", {
        "request_id": request_id.strip(),
        "limit": limit
    })

@mcp.tool()
def extract_api_endpoints(domain_filter: str = None):
    """Extract and group all API endpoints.

    Returns endpoint list with method, domain, path, count, and status codes.
    Useful for auto-generating API documentation and understanding API structure.
    """
    args = {}
    if domain_filter:
        args["domain_filter"] = domain_filter
    return call_proxypin_tool("extract_api_endpoints", args)

# ========================================
# System Info
# ========================================

@mcp.tool()
def get_system_info():
    """Get MCP server version and capabilities."""
    return {
        "version": __version__,
        "author": __author__,
        "contact": __contact__,
        "features": [
            "High-performance HTTP request capture and analysis",
            "Advanced request filtering and search",
            "Code generation and request replay",
            "HAR file import/export",
            "Request comparison and diff",
            "API endpoint extraction",
            "Enhanced error handling and logging",
            "Connection pooling",
            "Thread-safe operations"
        ],
        "github": "https://github.com/1837620622"
    }

# ========================================
# Entry Point
# ========================================

def main():
    """Main entry point."""
    ver_line = f"  Version: {__version__:<20} Port: {PROXYPIN_PORT}"
    feat_line = "  Features: Connection pooling, retry logic, thread safety"
    print(f"""
╔{'═'*62}╗
║{'ProxyPin MCP Server (Enhanced)':^62}║
║{' '*62}║
║{ver_line:<62}║
║{feat_line:<62}║
║{' '*62}║
║{'Starting...':^62}║
╚{'═'*62}╝
    """)

    try:
        logger.info(f"Starting ProxyPin MCP Server {__version__}")
        logger.info(f"Target: {BASE_URL}")
        logger.info("Server started successfully!")
        mcp.run()
    except Exception as e:
        logger.error(f"Server startup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
