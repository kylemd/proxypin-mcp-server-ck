# Developer Documentation

## ProxyPin MCP Server ChuanKangKK Enhanced Edition - Developer Guide

### Project Overview

This project is a deeply optimized and feature-enhanced version of the original ProxyPin MCP Server, developed as a secondary release by ChuanKangKK. The main improvements are in system performance, stability, and usability.

### Developer Information

- **Developer**: ChuanKangKK
- **GitHub**: [1837620622](https://github.com/1837620622)
- **WeChat**: 1837620622
- **Email**: 2040168455@qq.com
- **Platforms**: Xianyu / Bilibili - Universal Programmer

### Core Optimization Features

#### 1. Connection Pooling
- HTTP connection reuse via `requests.Session`
- Configurable retry strategy and timeout mechanism
- Concurrent request handling support

#### 2. Thread Safety
- Shared resource protection using `threading.Lock`
- Atomic operations ensure counter safety
- Stable operation in multi-threaded environments

#### 3. Enhanced Exception Handling
- Classified exception handling mechanism
- Detailed error message output
- Automatic retry for network requests

#### 4. Performance Monitoring
- Real-time response time statistics
- Detailed call logging
- System resource usage monitoring

#### 5. Parameter Validation
- Strict input parameter checking
- Data type conversion and sanitization
- Boundary condition handling

### Technical Architecture

#### Dependencies
```python
fastmcp>=1.0.0      # MCP framework
requests>=2.31.0    # HTTP request library
urllib3>=1.26.0     # HTTP client
```

#### Core Modules

1. **Connection Management Module**
   ```python
   def create_optimized_session() -> requests.Session
   ```
   - Creates an optimized HTTP session
   - Configures retry strategy
   - Sets connection pool parameters

2. **Tool Invocation Module**
   ```python
   def call_proxypin_tool(tool_name: str, arguments: dict) -> Any
   ```
   - Thread-safe tool invocation
   - Performance monitoring and logging
   - Classified exception handling

3. **MCP Tool Functions**
   - 30+ optimized tool functions
   - Parameter validation and error handling
   - Detailed docstrings

### Project Structure

```
proxypin-mcp-server-1.0.0/
├── proxypin_mcp_server.py    # Main program file
├── requirements.txt          # Dependency configuration
├── setup.py                 # Installation configuration
├── README.md               # User documentation
├── DEVELOPER.md            # Developer documentation
├── LICENSE                 # Open source license
├── .gitignore             # Git ignore file
├── proxypin_mcp_server.spec # PyInstaller configuration
└── .github/workflows/
    └── release.yml         # CI/CD configuration
```

### Development Environment Setup

#### 1. Requirements
- Python 3.8+
- Git
- ProxyPin application

#### 2. Local Development
```bash
# Clone the repository
git clone https://github.com/1837620622/proxypin-mcp-server.git
cd proxypin-mcp-server

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Run the server
python proxypin_mcp_server.py
```

#### 3. Development & Debugging
```bash
# Set debug environment variables
export PROXYPIN_HOST=127.0.0.1
export PROXYPIN_PORT=17777

# Enable debug logging
export PYTHONPATH=.
python -c "import logging; logging.getLogger().setLevel(logging.DEBUG)"
```

### Release Process

#### 1. Version Management
```bash
# Update version number
# Edit the __version__ variable in proxypin_mcp_server.py
# Edit the version parameter in setup.py
```

#### 2. Automated Builds
This project uses GitHub Actions for automated building and publishing:

- **Windows builds**: x64 and x86 architectures
- **macOS builds**: Intel (x64) and Apple Silicon (arm64) architectures
- **Python packages**: Source and wheel formats

#### 3. Release Commands
```bash
# Create a release tag
git tag -a v2.0.0-chuankangkk -m "ChuanKangKK Enhanced Edition v2.0.0"
git push origin v2.0.0-chuankangkk

# GitHub Actions will automatically build and publish
```

### Testing Guide

#### 1. Unit Tests
```bash
# Install test dependencies
pip install pytest pytest-cov

# Run tests
pytest tests/ -v

# Test coverage
pytest --cov=proxypin_mcp_server tests/
```

#### 2. Integration Tests
```bash
# Ensure ProxyPin service is running
# Start the test server
python proxypin_mcp_server.py &

# Run integration tests
python -m pytest tests/integration/ -v
```

#### 3. Performance Tests
```bash
# Stress test
python tests/performance_test.py

# Memory leak detection
python -m memory_profiler proxypin_mcp_server.py
```

### Code Quality

#### 1. Code Standards
- **PEP 8**: Python code style guide
- **Type hints**: Using the typing module
- **Docstrings**: Detailed function descriptions

#### 2. Quality Checks
```bash
# Code formatting
black proxypin_mcp_server.py

# Code linting
flake8 proxypin_mcp_server.py

# Type checking
mypy proxypin_mcp_server.py
```

#### 3. Performance Optimization
- Connection pool reuse reduces TCP handshakes
- Asynchronous operations improve response speed
- Memory management prevents leaks
- Dynamic log level adjustment

### Security Considerations

#### 1. Input Validation
- Strict parameter type checking
- SQL injection protection
- XSS attack prevention

#### 2. Network Security
- HTTPS support
- Certificate verification
- Timeout configuration

#### 3. Log Security
- Sensitive information redaction
- Log file permission control
- Audit logging

### Debugging Guide

#### 1. Common Issues
- **Connection failure**: Check ProxyPin service status
- **Permission error**: Verify file access permissions
- **Performance issues**: Review performance monitoring logs

#### 2. Log Analysis
```bash
# View detailed logs
tail -f proxypin_mcp.log

# Filter by level
grep "ERROR" proxypin_mcp.log
grep "INFO" proxypin_mcp.log
```

#### 3. Debugging Tools
```python
# Enable debug mode
import logging
logging.getLogger().setLevel(logging.DEBUG)

# Performance profiling
import cProfile
cProfile.run('main()')
```

### Performance Optimization Tips

#### 1. Connection Optimization
- Set appropriate connection pool sizes
- Enable HTTP keep-alive
- Use HTTP/2 protocol

#### 2. Memory Optimization
- Release large objects promptly
- Use generators to reduce memory footprint
- Periodic garbage collection

#### 3. CPU Optimization
- Avoid unnecessary serialization
- Use caching to reduce redundant computation
- Asynchronous I/O processing

### Contribution Guidelines

#### 1. Commit Convention
```bash
# Commit format
git commit -m "feat: add new feature description"
git commit -m "fix: fix bug description"
git commit -m "docs: update documentation"
git commit -m "style: code formatting"
git commit -m "refactor: code refactoring"
git commit -m "test: add tests"
```

#### 2. Branch Strategy
- `main`: Main branch, stable releases
- `develop`: Development branch
- `feature/*`: Feature branches
- `hotfix/*`: Hotfix branches

#### 3. Pull Requests
- Provide a detailed description of changes
- Include test cases
- Update related documentation
- Pass code review

### Technical Support

For technical questions, please contact the developer:

- **GitHub Issues**: [Submit an issue](https://github.com/1837620622/proxypin-mcp-server/issues)
- **WeChat**: 1837620622
- **Email**: 2040168455@qq.com
- **Platforms**: Xianyu / Bilibili - Universal Programmer

### License

This project is open-sourced under the MIT License. Contributions are welcome.

---

**ProxyPin MCP Server ChuanKangKK Enhanced Edition**
*Making HTTP request analysis simpler and more efficient*

Author: ChuanKangKK
Version: 2.0.0-chuankangkk
Last updated: 2025-12-19
