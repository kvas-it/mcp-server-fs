import os
import ast
import re
import json
import shutil
from typing import List, Tuple, Dict
from pathlib import Path

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("FileSystem")


@mcp.tool()
def ls(path: str) -> list[str]:
    """List files in a directory.

    :param path: Path to the directory. Can be relative to current working
                 directory (see cd tool).
    """
    return os.listdir(path)


@mcp.tool()
def cd(path: str) -> None:
    """Change the current working directory.

    :param path: New working directory. Can be relative to current working
                 directory.
    """
    os.chdir(path)


@mcp.tool()
def read_file(path: str) -> str:
    """Read a file from the filesystem.

    :param path: Path to the file. Can be relative (see cd tool).
    """
    with open(path, "rt", encoding="utf-8") as f:
        return f.read()


@mcp.tool()
def write_file(path: str, content: str) -> None:
    """Write content to a file.

    :param path: Path to the file. Can be relative (see cd tool).
    :param content: Content to write to the file.
    """
    with open(path, "wt", encoding="utf-8") as f:
        f.write(content)


@mcp.tool()
def patch_file(path: str, patches: List[Tuple[str, str]]) -> None:
    """Apply sequence of search/replace operations to a file.

    :param path: Path to the file to patch. Can be relative (see cd tool).
    :param patches: List of (search_text, replace_text) tuples.
    """
    with open(path, "rt", encoding="utf-8") as f:
        content = f.read()

    for search, replace in patches:
        content = content.replace(search, replace)

    with open(path, "wt", encoding="utf-8") as f:
        f.write(content)


@mcp.tool()
def summary(path: str) -> List[str]:
    """Generate a summary of a Python or Markdown file.

    :param path: Path to file to summarize. Supports .py and .md files.
    :returns: List of important lines (headers for md, functions/classes for py)
    """
    with open(path, "rt", encoding="utf-8") as f:
        content = f.read()

    if path.endswith(".md"):
        return [
            line.strip() for line in content.split("\n") if line.strip().startswith("#")
        ]

    elif path.endswith(".py"):
        tree = ast.parse(content)
        return [
            f"{type(node).__name__}: {node.name}"
            for node in ast.walk(tree)
            if isinstance(node, (ast.FunctionDef, ast.ClassDef))
        ]

    raise ValueError(f"Unsupported file type: {path}")


@mcp.tool()
def mkdir(path: str) -> None:
    """Create a directory.

    :param path: Directory path to create. Can be relative.
    """
    os.makedirs(path, exist_ok=True)


@mcp.tool()
def rm(path: str) -> None:
    """Remove a file or empty directory.

    :param path: Path to remove. Can be relative.
    """
    if os.path.isdir(path):
        os.rmdir(path)  # Will fail if not empty
    else:
        os.unlink(path)


@mcp.tool()
def rmdir(path: str) -> None:
    """Remove directory and all its contents.

    :param path: Directory to remove. Can be relative.
    """
    shutil.rmtree(path)


@mcp.tool()
def cp(src: str, dst: str) -> None:
    """Copy file or directory.

    :param src: Source path. Can be relative.
    :param dst: Destination path. Can be relative.
    """
    if os.path.isdir(src):
        shutil.copytree(src, dst)
    else:
        shutil.copy2(src, dst)


@mcp.tool()
def mv(src: str, dst: str) -> None:
    """Move file or directory.

    :param src: Source path. Can be relative.
    :param dst: Destination path. Can be relative.
    """
    shutil.move(src, dst)


def _get_notes_file() -> Path:
    """Find the root directory with .mcp-notes.json"""
    current = Path.cwd()
    while current != current.parent:
        if (current / ".mcp-notes.json").exists():
            return current / ".mcp-notes.json"
        current = current.parent
    return Path.cwd() / ".mcp-notes.json"


def _load_notes() -> Dict[str, Dict[str, str]]:
    """Load notes from file, creating if doesn't exist"""
    notes_file = _get_notes_file()
    if notes_file.exists():
        with open(notes_file, "r") as f:
            return json.load(f)
    return {}


def _save_notes(notes: Dict[str, Dict[str, str]]) -> None:
    """Save notes to file"""
    notes_file = _get_notes_file()
    with open(notes_file, "w") as f:
        json.dump(notes, f, indent=2)


def _get_relative_path(path: str) -> str:
    """Convert path to be relative to notes file location"""
    abs_path = Path(path).absolute()
    notes_root = _get_notes_file().parent.absolute()
    try:
        return str(abs_path.relative_to(notes_root))
    except ValueError:
        raise ValueError(f"Path {path} is not under notes root {notes_root}")


@mcp.tool()
def add_note(path: str, key: str, note: str) -> None:
    """Add or update a note about a file/directory.

    :param path: Path to file/directory to annotate
    :param key: Note key/category
    :param note: Note content
    """
    rel_path = _get_relative_path(path)
    notes = _load_notes()

    if rel_path not in notes:
        notes[rel_path] = {}
    notes[rel_path][key] = note

    _save_notes(notes)


@mcp.tool()
def get_all_notes() -> Dict[str, Dict[str, str]]:
    """Get all notes for all paths.

    :returns: Dict mapping paths to their notes (which are key-value dicts)
    """
    return _load_notes()


@mcp.tool()
def remove_note(path: str, key: str) -> None:
    """Remove a note about a file/directory.

    :param path: Path to file/directory
    :param key: Note key to remove
    """
    rel_path = _get_relative_path(path)
    notes = _load_notes()

    if rel_path in notes and key in notes[rel_path]:
        del notes[rel_path][key]
        if not notes[rel_path]:  # Remove empty entries
            del notes[rel_path]
        _save_notes(notes)


@mcp.tool()
def grep(pattern: str, path: str) -> List[str]:
    """Search for pattern in file(s).

    :param pattern: Regular expression to search for
    :param path: Path to file or directory. If directory, searches recursively.
    :returns: List of matches in format "filename:line_number:matched_line"
    """
    results = []
    pattern = re.compile(pattern)

    def search_file(filepath):
        try:
            with open(filepath, "rt", encoding="utf-8") as f:
                for i, line in enumerate(f, 1):
                    if pattern.search(line):
                        results.append(f"{filepath}:{i}:{line.rstrip()}")
        except UnicodeDecodeError:
            pass  # Skip binary files

    if os.path.isfile(path):
        search_file(path)
    else:
        for root, _, files in os.walk(path):
            for file in files:
                search_file(os.path.join(root, file))

    return results


@mcp.tool()
def ls_many(paths: list[str]) -> Dict[str, list[str]]:
    """List files in multiple directories.

    :param paths: List of directory paths
    :returns: Combined list of files from all directories
    """
    results = {}
    for path in paths:
        results[path] = ls(path)
    return results


@mcp.tool()
def read_files(paths: list[str]) -> Dict[str, str]:
    """Read multiple files.

    :param paths: List of file paths
    :returns: List of file contents in same order
    """
    return {path: read_file(path) for path in paths}


@mcp.tool()
def summarize(paths: list[str]) -> Dict[str, list[str]]:
    """Generate summaries for multiple files.

    :param paths: List of file paths
    :returns: List of summaries in same order as input paths
    """
    return {path: summary(path) for path in paths}
