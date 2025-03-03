# MCP File System Server

MCP server providing file system operations. Supports navigation, reading,
writing, analyzing files and command execution.

## Tools

### File and Directory Operations
* `ls(path)` - List directory contents
* `cd(path)` - Change working directory (supports home directory expansion with ~)
* `read_file(path)` - Read file contents
* `write_file(path, content)` - Write content to a file
* `mkdir(path)` - Create directory
* `rm(path)` - Remove file or empty directory
* `rmdir(path)` - Remove directory and contents recursively  
* `cp(src, dst)` - Copy file or directory
* `mv(src, dst)` - Move file or directory

### Editing and Searching
* `edit_file(path, changes)` - Apply multiple search/replace operations to a
  file, where changes is a list of (search_text, replace_text) tuples
* `grep(pattern, path)` - Search for regex pattern in file(s)

### Analysis
* `summary(path)` - Generate summary of Python (.py) and Markdown (.md) files:
  - Python: Lists functions and classes
  - Markdown: Lists headers (lines starting with #)

### Batch Operations
* `read_files(paths)` - Read multiple files, returns dict mapping paths to contents
* `summarize(paths)` - Generate summaries for multiple files, returns dict mapping paths to summaries

### Project Navigation
* `work_on(path)` - Change to directory, list its contents, and get the notes from CLAUDE.md.
  Useful for getting familiar with a project at the start of a chat

### Code Quality
* `ruff_check(paths)` - Run ruff linter on specified files
* `ruff_format(paths)` - Format files using ruff

### Command Execution
* `shell_command(command, args=None, cmdline=None, timeout=30)` - Run shell commands and capture their output
  > **⚠️ Security Warning**: This tool allows arbitrary command execution on the host system. Always inspect and validate commands before allowing them to run, especially if the input source is untrusted.
