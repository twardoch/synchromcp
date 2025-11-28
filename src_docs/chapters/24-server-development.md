# Chapter 24: MCP Server Development Guide

## Overview

This chapter provides comprehensive guidance for developing custom Model Context Protocol servers. Whether you're building a simple tool wrapper or a complex enterprise integration, understanding the MCP development patterns, best practices, and deployment strategies is essential. We'll cover the Python SDK patterns with FastMCP, Node.js/TypeScript server development, testing strategies, and community contribution guidelines.

---

## 1. Python SDK Patterns and FastMCP Framework

### 1.1 The FastMCP Framework Overview

FastMCP is the official Python framework for building MCP servers quickly and efficiently:

```python
from mcp.server.fastmcp import FastMCP

# Create an MCP server instance
mcp = FastMCP("My Custom Server")

# Define a tool
@mcp.tool()
def calculate_sum(a: int, b: int) -> int:
    """Add two numbers together."""
    return a + b

# Define a resource
@mcp.resource("config://weather")
def get_weather_config() -> str:
    """Get weather configuration."""
    return '{"api_key": "secret", "units": "metric"}'

# Define a prompt
@mcp.prompt()
def weather_report(location: str) -> str:
    """Generate a weather report prompt."""
    return f"Create a detailed weather report for {location}."

if __name__ == "__main__":
    mcp.run()
```

### 1.2 Core Server Structure

#### Basic Server Architecture
```python
# my_server.py
from mcp.server.fastmcp import FastMCP
from typing import Any, List, Optional
import asyncio
import json

class MyCustomMCPServer:
    def __init__(self, name: str, version: str = "1.0.0"):
        self.mcp = FastMCP(name)
        self.setup_tools()
        self.setup_resources()
        self.setup_prompts()
    
    def setup_tools(self):
        """Register all tool functions."""
        
        @self.mcp.tool()
        def list_files(directory: str, pattern: Optional[str] = None) -> List[str]:
            """
            List files in a directory with optional pattern matching.
            
            Args:
                directory: Path to the directory to list
                pattern: Optional glob pattern for filtering files
            """
            import glob
            import os
            
            if pattern:
                search_path = os.path.join(directory, pattern)
                return glob.glob(search_path)
            
            return os.listdir(directory)
        
        @self.mcp.tool()
        def get_file_info(file_path: str) -> dict:
            """
            Get detailed information about a file.
            
            Args:
                file_path: Path to the file to analyze
            """
            import os
            import hashlib
            
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")
            
            stat = os.stat(file_path)
            
            # Calculate file hash
            with open(file_path, 'rb') as f:
                file_hash = hashlib.md5(f.read()).hexdigest()
            
            return {
                "path": file_path,
                "size": stat.st_size,
                "modified": stat.st_mtime,
                "hash": file_hash,
                "readable": os.access(file_path, os.R_OK),
                "writable": os.access(file_path, os.W_OK)
            }
    
    def setup_resources(self):
        """Register all resource endpoints."""
        
        @self.mcp.resource("file://{path}")
        def get_file_content(path: str) -> str:
            """
            Get the content of a file as a resource.
            
            Args:
                path: Path to the file to read
            """
            with open(path, 'r') as f:
                return f.read()
    
    def setup_prompts(self):
        """Register all prompt templates."""
        
        @self.mcp.prompt()
        def analyze_code(file_path: str, focus_areas: Optional[List[str]] = None) -> str:
            """
            Generate a prompt for code analysis.
            
            Args:
                file_path: Path to the code file to analyze
                focus_areas: Optional list of specific areas to focus on
            """
            focus_text = ""
            if focus_areas:
                focus_text = f"Focus on: {', '.join(focus_areas)}"
            
            return f"""
            Analyze the code in {file_path}. {focus_text}
            
            Please provide:
            1. Code quality assessment
            2. Potential bugs or issues
            3. Performance suggestions
            4. Documentation recommendations
            """
    
    def run(self):
        """Start the MCP server."""
        self.mcp.run()

# Usage example
if __name__ == "__main__":
    server = MyCustomMCPServer("file-analyzer", "1.0.0")
    server.run()
```

### 1.3 Advanced FastMCP Features

#### Custom Error Handling
```python
from mcp.server.fastmcp import FastMCP
from mcp.server.models import ToolCallResult, ToolCallError
import logging

mcp = FastMCP("advanced-server")

@mcp.tool()
def risky_operation(param: str) -> str:
    """Tool with custom error handling."""
    try:
        # Potentially failing operation
        result = perform_operation(param)
        return result
    except ValueError as e:
        # Return structured error for better client handling
        raise ToolCallError(
            code=400,
            message=f"Invalid parameter: {e}",
            data={"parameter": param, "valid_values": ["opt1", "opt2"]}
        )
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        raise ToolCallError(
            code=500,
            message="Internal server error",
            data={"error_type": type(e).__name__}
        )

def perform_operation(param: str) -> str:
    """Simulated operation that might fail."""
    if param not in ["opt1", "opt2"]:
        raise ValueError(f"Invalid parameter: {param}")
    return f"Processed {param}"
```

#### Streaming Responses
```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("streaming-server")

@mcp.tool(streaming=True)
async def stream_large_file(file_path: str) -> str:
    """
    Stream file content in chunks for large files.
    
    Args:
        file_path: Path to the file to stream
    """
    chunk_size = 1024  # 1KB chunks
    
    try:
        with open(file_path, 'r') as f:
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                yield chunk  # Stream this chunk
                await asyncio.sleep(0.01)  # Prevent overwhelming the client
    except Exception as e:
        yield f"Error reading file: {e}"
```

#### Resource Subscriptions
```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("subscription-server")

@mcp.resource("log://application", subscribe=True)
async def get_application_logs() -> str:
    """Get application logs with subscription support."""
    return read_latest_logs()

@mcp.resource("config://settings")
def get_settings() -> str:
    """Get current configuration."""
    return json.dumps(load_current_settings())

# Notification system for subscription updates
@mcp.notification()
async def notify_config_changes():
    """Notify clients of configuration changes."""
    await mcp.send_notification(
        "notifications/resource/updated",
        {
            "uri": "config://settings",
            "change": "configuration_modified"
        }
    )
```

---

## 2. Node.js/TypeScript Server Development

### 2.1 TypeScript Server Setup

#### Project Structure
```
my-mcp-server/
├── src/
│   ├── index.ts          # Server entry point
│   ├── tools/            # Tool implementations
│   │   ├── fileManager.ts
│   │   └── dataProcessor.ts
│   └── resources/        # Resource handlers
│       └── config.ts
├── package.json
├── tsconfig.json
└── README.md
```

#### Basic TypeScript Server
```typescript
// src/index.ts
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";

// Create server instance
const server = new McpServer(
  {
    name: "my-typescript-server",
    version: "1.0.0",
  },
  {
    capabilities: {
      tools: {},
      resources: {},
      prompts: {},
    },
  }
);

// Register a tool with input validation
server.setRequestHandler("tools/call", async (request) => {
  const { name, arguments: args } = request.params;

  switch (name) {
    case "process_data":
      return await processData(args);
    default:
      throw new Error(`Unknown tool: ${name}`);
  }
});

// Data processing tool
const processDataSchema = z.object({
  data: z.string(),
  format: z.enum(["json", "csv", "xml"]),
  options: z.record(z.any()).optional(),
});

async function processData(args: unknown) {
  try {
    const validated = processDataSchema.parse(args);
    
    // Process data based on format
    switch (validated.format) {
      case "json":
        return {
          content: [{
            type: "text",
            text: JSON.parse(validated.data)
          }]
        };
      
      case "csv":
        const lines = validated.data.split('\n');
        const headers = lines[0].split(',');
        const rows = lines.slice(1).map(line => line.split(','));
        
        return {
          content: [{
            type: "text", 
            text: `Processed ${rows.length} rows with ${headers.length} columns`
          }]
        };
      
      default:
        throw new Error(`Unsupported format: ${validated.format}`);
    }
  } catch (error) {
    return {
      content: [{
        type: "text",
        text: `Error: ${error instanceof Error ? error.message : 'Unknown error'}`
      }],
      isError: true
    };
  }
}

// Register resources
server.setRequestHandler("resources/read", async (request) => {
  const { uri } = request.params;
  
  if (uri.startsWith("data://")) {
    const dataId = uri.replace("data://", "");
    const data = await fetchDataById(dataId);
    
    return {
      contents: [{
        uri,
        mimeType: "application/json",
        text: JSON.stringify(data)
      }]
    };
  }
  
  throw new Error(`Unknown resource: ${uri}`);
});

// Start the server
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("TypeScript MCP Server running on stdio");
}

main().catch(console.error);
```

#### Advanced TypeScript Patterns
```typescript
// src/tools/dataProcessor.ts
import { z } from "zod";

export interface DataProcessor {
  process(data: string, options?: ProcessOptions): Promise<ProcessResult>;
}

export const ProcessOptionsSchema = z.object({
  format: z.enum(["json", "csv", "xml"]),
  validate: z.boolean().default(false),
  outputFormat: z.enum(["compact", "pretty"]).default("pretty"),
});

export type ProcessOptions = z.infer<typeof ProcessOptionsSchema>;

export interface ProcessResult {
  success: boolean;
  data?: string;
  error?: string;
  metadata?: {
    rowsProcessed?: number;
    parseTime?: number;
    errors?: string[];
  };
}

export class JSONProcessor implements DataProcessor {
  async process(data: string, options?: ProcessOptions): Promise<ProcessResult> {
    const startTime = Date.now();
    
    try {
      if (options?.validate) {
        // Schema validation would go here
        JSON.parse(data);
      }
      
      const parsed = JSON.parse(data);
      const processTime = Date.now() - startTime;
      
      return {
        success: true,
        data: JSON.stringify(parsed, null, options?.outputFormat === "pretty" ? 2 : 0),
        metadata: {
          parseTime: processTime
        }
      };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : "Unknown error",
        metadata: {
          parseTime: Date.now() - startTime,
          errors: [error instanceof Error ? error.message : "Unknown error"]
        }
      };
    }
  }
}
```

---

## 3. Server Testing and Validation Strategies

### 3.1 Unit Testing Patterns

#### Python Server Testing
```python
# test_my_server.py
import pytest
import asyncio
from unittest.mock import patch, mock_open
from my_server import MyCustomMCPServer

class TestMyCustomMCPServer:
    @pytest.fixture
    def server(self):
        return MyCustomMCPServer("test-server")
    
    @pytest.mark.asyncio
    async def test_list_files_success(self, server):
        """Test successful file listing."""
        with patch('os.listdir', return_value=['file1.txt', 'file2.py']):
            result = await server.list_files("/test/directory")
            assert result == ['file1.txt', 'file2.py']
    
    @pytest.mark.asyncio
    async def test_list_files_with_pattern(self, server):
        """Test file listing with pattern matching."""
        with patch('glob.glob', return_value=['/test/file1.txt']):
            result = await server.list_files("/test", "*.txt")
            assert result == ['/test/file1.txt']
    
    @pytest.mark.asyncio
    async def test_get_file_info_success(self, server):
        """Test successful file info retrieval."""
        mock_stat = {
            'st_size': 1024,
            'st_mtime': 1234567890
        }
        
        with patch('os.path.exists', return_value=True), \
             patch('os.stat', return_value=type('MockStat', (), mock_stat)()), \
             patch('builtins.open', mock_open(read_data=b'test content')), \
             patch('os.access', return_value=True):
            
            result = await server.get_file_info("/test/file.txt")
            
            assert result['path'] == "/test/file.txt"
            assert result['size'] == 1024
            assert result['hash']  # MD5 hash should be calculated
    
    @pytest.mark.asyncio
    async def test_get_file_info_not_found(self, server):
        """Test file info with non-existent file."""
        with patch('os.path.exists', return_value=False):
            with pytest.raises(FileNotFoundError):
                await server.get_file_info("/nonexistent/file.txt")
```

#### Integration Testing with MCP Client
```python
# test_integration.py
import asyncio
import json
from mcp.client.session import ClientSession
from mcp.client.stdio import stdio_client

async def test_server_integration():
    """Test server with actual MCP client."""
    # Start server process
    server_process = await asyncio.create_subprocess_exec(
        'python', '-m', 'my_server',
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    
    try:
        # Create MCP client connection
        async with stdio_client(server_process.stdin, server_process.stdout) as (read, write):
            async with ClientSession(read, write) as session:
                # Initialize session
                await session.initialize()
                
                # Test tool availability
                tools = await session.list_tools()
                assert 'list_files' in [tool.name for tool in tools.tools]
                
                # Test tool execution
                result = await session.call_tool('list_files', {'directory': '/tmp'})
                assert not result.isError
                assert isinstance(result.content[0].text, str)
                
    finally:
        server_process.terminate()
        await server_process.wait()

if __name__ == "__main__":
    asyncio.run(test_server_integration())
```

### 3.2 TypeScript Server Testing

#### Unit Tests with Jest
```typescript
// tests/dataProcessor.test.ts
import { JSONProcessor } from '../src/tools/dataProcessor';
import { ProcessOptions } from '../src/tools/dataProcessor';

describe('JSONProcessor', () => {
  let processor: JSONProcessor;

  beforeEach(() => {
    processor = new JSONProcessor();
  });

  describe('process', () => {
    it('should process valid JSON data', async () => {
      const data = '{"name": "test", "value": 123}';
      const options: ProcessOptions = {
        format: 'json',
        validate: false,
        outputFormat: 'compact'
      };

      const result = await processor.process(data, options);

      expect(result.success).toBe(true);
      expect(result.data).toBe('{"name":"test","value":123}');
      expect(result.metadata?.parseTime).toBeGreaterThan(0);
    });

    it('should handle invalid JSON gracelly', async () => {
      const data = '{invalid json}';
      const options: ProcessOptions = {
        format: 'json',
        validate: false
      };

      const result = await processor.process(data, options);

      expect(result.success).toBe(false);
      expect(result.error).toContain('JSON');
    });

    it('should pretty-print when option is specified', async () => {
      const data = '{"name":"test"}';
      const options: ProcessOptions = {
        format: 'json',
        outputFormat: 'pretty'
      };

      const result = await processor.process(data, options);

      expect(result.success).toBe(true);
      expect(result.data).toEqual('{\n  "name": "test"\n}');
    });
  });
});
```

#### End-to-End Testing
```typescript
// tests/e2e/server.test.ts
import { spawn, ChildProcess } from 'child_process';
import { ClientSession } from '@modelcontextprotocol/sdk/client/session.js';
import { StdioClientTransport } from '@modelcontextprotocol/sdk/client/stdio.js';

describe('MCP Server E2E', () => {
  let serverProcess: ChildProcess;
  let session: ClientSession;

  beforeAll(async () => {
    // Start the server
    serverProcess = spawn('npm', ['run', 'dev'], {
      stdio: ['pipe', 'pipe', 'pipe']
    });

    // Wait for server to be ready
    await new Promise(resolve => setTimeout(resolve, 2000));

    // Create client session
    const transport = new StdioClientTransport({
      command: 'node',
      args: ['dist/index.js']
    });

    session = new ClientSession(transport);
    await session.initialize();
  });

  afterAll(async () => {
    if (session) {
      await session.close();
    }
    if (serverProcess) {
      serverProcess.kill();
    }
  });

  it('should register and execute tools', async () => {
    const tools = await session.listTools();
    expect(tools.tools).toHaveLength(1);
    expect(tools.tools[0].name).toBe('process_data');

    const result = await session.callTool('process_data', {
      data: '{"test": "value"}',
      format: 'json'
    });

    expect(result.isError).toBe(false);
    expect(result.content[0].text).toContain('{"test":"value"}');
  });
});
```

---

## 4. Publishing and Distribution Workflows

### 4.1 Python Package Publishing

#### pyproject.toml Configuration
```toml
[build-system]
requires = ["hatchling", "hatch-vcs"]
build-backend = "hatchling.build"

[project]
name = "my-mcp-server"
dynamic = ["version"]
description = "A custom MCP server for data processing"
readme = "README.md"
license = "MIT"
requires-python = ">=3.11"
authors = [{ name = "Your Name", email = "your.email@example.com" }]
keywords = ["mcp", "model-context-protocol", "data-processing"]
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
]
dependencies = [
    "mcp>=1.0.0",
    "fastmcp>=0.5.0",
    "pydantic>=2.0.0",
    "httpx>=0.25.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-cov>=4.0.0",
    "pytest-asyncio>=0.23.0",
    "mypy>=1.10.0",
    "black>=24.0.0",
    "ruff>=0.4.0",
]

[project.scripts]
my-mcp-server = "my_mcp_server.cli:main"

[project.urls]
Homepage = "https://github.com/username/my-mcp-server"
Repository = "https://github.com/username/my-mcp-server"
Issues = "https://github.com/username/my-mcp-server/issues"

[tool.hatch.version]
source = "vcs"

[tool.hatch.build.targets.wheel]
packages = ["src/my_mcp_server"]
```

#### CLI Script for Easy Installation
```python
# src/my_mcp_server/cli.py
import argparse
import asyncio
import sys
from .server import MyCustomMCPServer

async def main():
    parser = argparse.ArgumentParser(description="My Custom MCP Server")
    parser.add_argument("--host", default="localhost", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8080, help="Port to bind to")
    parser.add_argument("--config", help="Path to configuration file")
    
    args = parser.parse_args()
    
    server = MyCustomMCPServer("my-server")
    
    if args.host == "localhost" and args.port == 8080:
        # Default to stdio transport
        server.run()
    else:
        # Use HTTP transport for remote access
        await server.run_http(args.host, args.port)

if __name__ == "__main__":
    asyncio.run(main())
```

### 4.2 Node.js Package Publishing

#### package.json Configuration
```json
{
  "name": "@username/my-mcp-server",
  "version": "1.0.0",
  "description": "A custom MCP server for data processing",
  "main": "dist/index.js",
  "bin": {
    "my-mcp-server": "dist/cli.js"
  },
  "scripts": {
    "build": "tsc",
    "dev": "tsx src/index.ts",
    "start": "node dist/index.js",
    "test": "jest",
    "lint": "eslint src --ext .ts",
    "format": "prettier --write src/**/*.ts",
    "prepublishOnly": "npm run build && npm test"
  },
  "keywords": [
    "mcp",
    "model-context-protocol",
    "data-processing",
    "typescript"
  ],
  "author": "Your Name <your.email@example.com>",
  "license": "MIT",
  "dependencies": {
    "@modelcontextprotocol/sdk": "^1.0.0",
    "zod": "^3.22.0"
  },
  "devDependencies": {
    "@types/jest": "^29.5.0",
    "@types/node": "^20.0.0",
    "eslint": "^8.0.0",
    "jest": "^29.7.0",
    "prettier": "^3.0.0",
    "tsx": "^4.7.0",
    "typescript": "^5.0.0"
  },
  "files": [
    "dist",
    "README.md",
    "LICENSE"
  ],
  "repository": {
    "type": "git",
    "url": "https://github.com/username/my-mcp-server.git"
  },
  "bugs": {
    "url": "https://github.com/username/my-mcp-server/issues"
  },
  "homepage": "https://github.com/username/my-mcp-server#readme"
}
```

---

## 5. Community Contribution Guidelines

### 5.1 Open Source Best Practices

#### Repository Structure and Documentation
```
awesome-mcp-server/
├── .github/
│   ├── ISSUE_TEMPLATE/
│   ├── PULL_REQUEST_TEMPLATE.md
│   └── CONTRIBUTING.md
├── docs/
│   ├── installation.md
│   ├── configuration.md
│   ├── api-reference.md
│   └── examples/
├── examples/
│   ├── basic-usage.json
│   └── advanced-setup.json
├── src/
├── tests/
├── CHANGELOG.md
├── LICENSE
├── README.md
└── CONTRIBUTING.md
```

#### CONTRIBUTING.md Template
```markdown
# Contributing to My MCP Server

Thank you for your interest in contributing! This document provides guidelines for contributing to this project.

## Development Setup

1. **Fork and Clone**
   ```bash
   git clone https://github.com/username/my-mcp-server
   cd my-mcp-server
   ```

2. **Install Dependencies**
   ```bash
   # Python
   pip install -e ".[dev]"
   
   # Node.js
   npm install
   ```

3. **Run Tests**
   ```bash
   # Python
   pytest
   
   # Node.js
   npm test
   ```

## Contribution Types

### Bug Reports
- Use the provided bug report template
- Include reproduction steps
- Provide environment details

### Feature Requests
- Use the feature request template
- Describe the use case clearly
- Consider API compatibility

### Code Contributions
1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Update documentation
6. Submit a pull request

## Code Style

- Follow existing formatting (Black/Prettier)
- Include type hints where applicable
- Add docstrings for new functions
- Keep changes focused and atomic

## Testing Requirements

- Unit tests for all new functionality
- Integration tests for complex features
- Maintain test coverage above 80%
- Update fixtures as needed

Thank you for contributing!
```

### 5.2 Security Best Practices for Public Servers

#### Input Validation and Sanitization
```python
# Security-focused server implementation
from mcp.server.fastmcp import FastMCP
import os
import re
from pathlib import Path

mcp = FastMCP("secure-server")

# Define safe patterns
SAFE_PATH_PATTERN = re.compile(r'^[\w\-./]+$')
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

@mcp.tool()
def safe_read_file(file_path: str) -> str:
    """
    Safely read file contents with extensive validation.
    
    Args:
        file_path: Path to the file to read
    """
    # Validate input
    if not file_path:
        raise ValueError("File path cannot be empty")
    
    if not SAFE_PATH_PATTERN.match(file_path):
        raise ValueError("Invalid characters in file path")
    
    # Resolve path and prevent directory traversal
    resolved_path = Path(file_path).resolve()
    
    # Add your security logic here
    if not resolved_path.exists():
        raise FileNotFoundError("File not found")
    
    if resolved_path.stat().st_size > MAX_FILE_SIZE:
        raise ValueError("File too large")
    
    try:
        with open(resolved_path, 'r', encoding='utf-8') as f:
            return f.read()
    except UnicodeDecodeError:
        raise ValueError("File contains invalid characters")
```

#### Rate Limiting and Resource Control
```python
from mcp.server.fastmcp import FastMCP
import time
from collections import defaultdict
import threading

mcp = FastMCP("rate-limited-server")

# Simple in-memory rate limiter
class RateLimiter:
    def __init__(self, max_requests: int, time_window: int):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = defaultdict(list)
        self.lock = threading.Lock()
    
    def is_allowed(self, client_id: str) -> bool:
        with self.lock:
            now = time.time()
            client_requests = self.requests[client_id]
            
            # Remove old requests
            self.requests[client_id] = [
                req_time for req_time in client_requests
                if now - req_time < self.time_window
            ]
            
            if len(self.requests[client_id]) >= self.max_requests:
                return False
            
            self.requests[client_id].append(now)
            return True

rate_limiter = RateLimiter(max_requests=10, time_window=60)

@mcp.tool()
def expensive_operation(input_data: str, client_id: str = "default") -> str:
    """
    Expensive operation with rate limiting.
    
    Args:
        input_data: Data to process
        client_id: Client identifier for rate limiting
    """
    if not rate_limiter.is_allowed(client_id):
        raise Exception("Rate limit exceeded. Please try again later.")
    
    # Perform expensive operation
    time.sleep(1)  # Simulate work
    return f"Processed: {input_data}"
```

---

## 6. Performance Optimization Guidelines

### 6.1 Caching Strategies

#### Memory-Based Caching
```python
from functools import lru_cache
import time

class CacheManager:
    def __init__(self, max_size: int = 1000, ttl: int = 300):
        self.max_size = max_size
        self.ttl = ttl
        self.cache = {}
        self.timestamps = {}
    
    def get(self, key: str) -> Optional[Any]:
        if key not in self.cache:
            return None
        
        # Check TTL
        if time.time() - self.timestamps[key] > self.ttl:
            del self.cache[key]
            del self.timestamps[key]
            return None
        
        return self.cache[key]
    
    def set(self, key: str, value: Any) -> None:
        # Implement LRU eviction if needed
        if len(self.cache) >= self.max_size:
            oldest_key = min(self.timestamps.keys(), 
                           key=self.timestamps.get)
            del self.cache[oldest_key]
            del self.timestamps[oldest_key]
        
        self.cache[key] = value
        self.timestamps[key] = time.time()

# Usage in server
cache = CacheManager()

@mcp.tool()
def cached_operation(data: str) -> str:
    """Operation with caching to improve performance."""
    cache_key = hashlib.md5(data.encode()).hexdigest()
    
    # Try cache first
    cached_result = cache.get(cache_key)
    if cached_result:
        return cached_result
    
    # Perform expensive operation
    result = expensive_computation(data)
    
    # Cache the result
    cache.set(cache_key, result)
    return result
```

### 6.2 Async Optimization

#### Concurrent Operations
```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

@mcp.tool()
async def parallel_file_operations(file_paths: List[str]) -> List[dict]:
    """
    Process multiple files in parallel for better performance.
    
    Args:
        file_paths: List of files to process
    """
    
    # Create thread pool for I/O operations
    with ThreadPoolExecutor(max_workers=4) as executor:
        # Submit all tasks
        loop = asyncio.get_event_loop()
        tasks = [
            loop.run_in_executor(executor, process_single_file, path)
            for path in file_paths
        ]
        
        # Wait for all to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter exceptions and return successful results
        successful_results = [
            result for result in results 
            if not isinstance(result, Exception)
        ]
        
        return successful_results

def process_single_file(file_path: str) -> dict:
    """Process a single file (runs in thread pool)."""
    # Simulate file processing
    time.sleep(0.1)  # I/O bound operation
    return {"path": file_path, "size": os.path.getsize(file_path)}
```

---

## 7. Documentation and API Reference

### 7.1 Comprehensive API Documentation

#### Documenting MCP Servers
```markdown
# API Reference

## Tools

### process_data

Processes data in various formats and returns structured results.

**Parameters:**
- `data` (string): Raw data to process
- `format` (enum): Data format - "json", "csv", or "xml"
- `options` (object, optional): Processing options

**Returns:**
- Processed data with metadata including parse time and row count

**Example:**
```json
{
  "tool": "process_data",
  "arguments": {
    "data": "[{\"name\":\"test\"}]",
    "format": "json",
    "options": {
      "validate": true,
      "outputFormat": "pretty"
    }
  }
}
```

### list_files

Lists files in a directory with optional pattern filtering.

**Parameters:**
- `directory` (string): Directory path to list
- `pattern` (string, optional): Glob pattern for filtering

**Security Notes:**
- Only accessible within configured root directories
- Follows system permission model
- Prevents directory traversal attacks
```

### 7.2 Auto-Generated Examples

#### Configuration Examples
```json
{
  "title": "Basic Configuration",
  "description": "Minimal setup for development use",
  "config": {
    "mcpServers": {
      "my-server": {
        "command": "python",
        "args": ["-m", "my_mcp_server"],
        "env": {
          "LOG_LEVEL": "debug",
          "CACHE_ENABLED": "true"
        }
      }
    }
  }
}

{
  "title": "Production Configuration",
  "description": "Optimized setup for production deployment",
  "config": {
    "mcpServers": {
      "my-server-prod": {
        "command": "docker",
        "args": [
          "run", "--rm",
          "-e", "CACHE_SIZE=1000",
          "-e", "RATE_LIMIT=100",
          "my-mcp-server:latest"
        ]
      }
    }
  }
}
```

---

## 8. Debugging and Troubleshooting

### 8.1 Common Development Issues

| Problem | Common Cause | Solution |
|---------|--------------|----------|
| **Server fails to start** | Missing dependencies or import errors | Use virtual environments, check imports |
| **Tools not registered** | Decorator registration issues | Verify decorator syntax and registration order |
| **Memory leaks** | Unclosed resources or circular references | Use proper context managers and monitoring |
| **Performance degradation** | Inefficient algorithms or missing caching | Profile code and implement caching |
| **Authentication failures** | Missing or invalid credentials | Verify environment variables and tokens |

### 8.2 Debugging Tools and Techniques

#### Logging Configuration
```python
import logging
from mcp.server.fastmcp import FastMCP

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('mcp-server.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

mcp = FastMCP("debug-server")

@mcp.tool()
def debug_operation(param: str) -> str:
    """Operation with comprehensive debugging information."""
    logger.info(f"Starting debug_operation with param: {param}")
    
    try:
        result = perform_computation(param)
        logger.debug(f"Computation result: {result}")
        return result
    except Exception as e:
        logger.exception("Operation failed")
        raise

@mcp.tool()
async def debug_async_operation(data: dict) -> str:
    """Async operation with debug context tracking."""
    logger.info(f"Async operation started with data keys: {list(data.keys())}")
    
    # Add async context debugging
    current_task = asyncio.current_task()
    logger.debug(f"Running in task: {current_task.get_name() if current_task else 'unknown'}")
    
    # Process data
    result = await async_data_processing(data)
    logger.info("Async operation completed successfully")
    return result
```

---

## 9. Best Practices Summary

### Development Best Practices
1. **Start with FastMCP**: Use the high-level framework for rapid development
2. **Implement proper error handling**: Return structured errors for better client integration
3. **Add comprehensive tests**: Unit tests, integration tests, and end-to-end testing
4. **Use input validation**: Protect against malicious inputs and invalid data
5. **Follow security guidelines**: Implement proper sandboxing and permission controls

### Performance Best Practices
1. **Implement caching**: Cache expensive operations and frequently accessed data
2. **Use async operations**: Leverage asyncio for I/O-bound operations
3. **Monitor resource usage**: Track memory, CPU, and network usage
4. **Optimize data structures**: Use efficient algorithms and data structures
5. **Profile regularly**: Identify and address performance bottlenecks

### Community Best Practices
1. **Provide comprehensive documentation**: Include examples and troubleshooting guides
2. **Maintain semantic versioning**: Follow proper version bumping conventions
3. **Engage with users**: Respond to issues and feedback promptly
4. **Contribute back upstream**: Share improvements with the MCP community
5. **Security first**: Prioritize security in all development decisions

---

## 10. Conclusion

Developing custom MCP servers requires understanding the protocol specifications, using appropriate SDK patterns, implementing robust testing strategies, and following security and performance best practices. Whether you're building simple tool wrappers or complex enterprise integrations, the principles outlined in this chapter will help you create reliable, secure, and performant MCP servers.

The MCP ecosystem provides excellent tooling and frameworks that make server development accessible while maintaining the flexibility needed for sophisticated integrations. By following these guidelines and contributing back to the community, you can help build a robust ecosystem of MCP servers that extend AI capabilities across domains and use cases.

---

*Next: Chapter 25 provides comprehensive guidance for production deployment and operations.*
