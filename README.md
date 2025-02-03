# MCP File System Server

MCP server providing basic file system operations. Supports navigation,
reading, writing, and analyzing files.

## Tools

* `ls(path)` - List directory contents
* `cd(path)` - Change working directory  
* `read_file(path)` - Read file contents
* `write_file(path, content)` - Write content to a file
* `patch_file(path, patches)` - Apply multiple search/replace operations to a
  file
* `summary(path)` - Generate summary of Python (.py) and Markdown (.md) files:
  - Python: Lists functions and classes
  - Markdown: Lists headers (lines starting with #)
* `mkdir(path)` - Create directory
* `rm(path)` - Remove file or empty directory
* `rmdir(path)` - Remove directory and contents recursively  
* `cp(src, dst)` - Copy file or directory
* `mv(src, dst)` - Move file or directory
* `grep(pattern, path)` - Search for regex pattern in file(s)
* `add_note(path, key, note)` - Add/update a note about a file/directory
* `remove_note(path, key)` - Remove a note
* `get_all_notes()` - Get all notes for all paths
* `ls_many(paths)` - List contents of multiple directories, returns dict
  mapping paths to file lists
* `read_files(paths)` - Read multiple files, returns dict mapping paths to
  contents
* `summarize(paths)` - Generate summaries for multiple files, returns dict
  mapping paths to summaries
* `work_on(path)` - Change to directory, list its contents, and get all notes.
  Useful for getting familiar with a project at the start of a chat

## Roadmap

- [x] Add linting and formatting via `ruff` (via subprocess).
- [x] Add `work_on` tool for faster init.
- [ ] Add `find_files` function to search for files by name.
- [ ] Add support for git operations (via subprocess).
- [ ] Add support for running tests (via pytest).
- [ ] Rename to `mcp-server-pydev` becuase it's a better fit.
- [ ] Add `patch_files` function to apply multiple patches to multiple files.

## Ideas

- [ ] Modular command loading (with reload) via `importlib`. We'd separate more
  opinionated commands (like `summary`, `git`, `ruff`, `pytest`) from more
  generic ones (like `ls`). It would also become easier to add new commands
  without restarting the server.
- [ ] Add recursive `ls`?
