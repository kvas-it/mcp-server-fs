# MCP Server for Filesystem Access

## Project Overview
- **Project Type**: MCP server implementing file system operations
- **Core Files**:
  - `server.py`: Main implementation
  - `pyproject.toml`: Dependencies
  - `README.md`: Documentation

## File Notes

### server.py
- **Purpose**: Main server file implementing all filesystem operations and tools
- **Tools**: 
  - Basic operations: ls, cd, read/write files
  - File editing: edit_file
  - Search: grep
  - File operations: mkdir, rm, rmdir, cp, mv
  - Shell command execution: shell_command
  - Notes system: Using CLAUDE.md file
  - Multi-file operations: read_files, summarize
  - Code quality tools: ruff_check, ruff_format
- **API Changes**:
  - 2025-03-03: Added 'shell_command' tool to execute shell commands with captured output
  - 2025-03-03: Replaced JSON-based notes system with markdown-based CLAUDE.md
  - 2024-01-31: Added batch operations (read_files, summarize) and simplified notes API
  - 2025-03-03: Renamed 'patch_file' to 'edit_file' for better clarity

- **Server Changes**: The server needs to be restarted after making changes to this file for them to take effect.

### pyproject.toml
- **Purpose**: Project configuration and dependencies
- **Dependencies**: 
  - mcp[cli]>=1.2.1
  - ruff>=0.9.4

### README.md
- **Purpose**: Documentation for the MCP file system server and its tools
