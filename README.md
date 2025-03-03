# MCP File System Server



MCP server providing basic file system operations. Supports navigation,
reading, writing, and analyzing files.

## Tools

* `ls(path)` - List directory contents
* `cd(path)` - Change working directory  
* `read_file(path)` - Read file contents
* `write_file(path, content)` - Write content to a file
* `edit_file(path, patches)` - Apply multiple search/replace operations to a
  file
* `apply_diff(diff)` - Apply a unified diff to files in the working directory.
  Supports both standard and git-style diffs with `a/` and `b/` prefixes
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
- [ ] Add `edit_files` function to apply multiple edits to multiple files.

## Ideas

- [ ] Modular command loading (with reload) via `importlib`. We'd separate more
  opinionated commands (like `summary`, `git`, `ruff`, `pytest`) from more
  generic ones (like `ls`). It would also become easier to add new commands
  without restarting the server.
- [ ] Add recursive `ls`?

## Using the Edit Tools

This server provides two complementary tools for modifying files:

### edit_file

The `edit_file` tool is useful for making targeted changes to specific parts of a file using search/replace operations.

```python
edit_file("file.py", [("old text", "new text"), ("another old part", "another new part")])
```

Best practices:
* Include several lines of context around the text you want to replace to ensure unique matches
* Replace entire lines rather than partial lines when possible
* Make changes one at a time for complex edits

### apply_diff

The `apply_diff` tool is ideal for more complex changes, especially when modifying multiple parts of a file or multiple files at once. It uses the system's `patch` command to apply unified diffs.

```python
apply_diff("""
--- a/file.py
+++ b/file.py
@@ -10,7 +10,7 @@
 unchanged line
 unchanged line
-line to remove
+line to add instead
 unchanged line
""")
```

Best practices:
* Ensure each diff is well-formed with proper context lines
* The tool supports both standard unified diffs and git-style diffs with `a/` and `b/` prefixes
* For complex multi-file patches, consider applying them one file at a time for better error handling
* Make sure target files exist in the working directory before applying patches
