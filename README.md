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
* `get_note(path, key)` - Get a specific note about a file/directory
* `list_notes(path)` - List all note keys for a file/directory
* `remove_note(path, key)` - Remove a note
* `ls_many(paths)` - List contents of multiple directories, returns dict
  mapping paths to file lists
* `read_files(paths)` - Read multiple files, returns dict mapping paths to
  contents
* `summarize(paths)` - Generate summaries for multiple files, returns dict
  mapping paths to summaries
