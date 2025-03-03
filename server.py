import os
import ast
import re
import shutil
import subprocess

from typing import List, Tuple, Dict, Union
from pathlib import Path

from mcp.server.fastmcp import FastMCP

RUFF_PATH = Path(__file__).parent / ".venv" / "bin" / "ruff"

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
                 directory. Supports home directory expansion (~/path).
    """
    expanded_path = os.path.expanduser(path)
    os.chdir(expanded_path)


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
def edit_file(path: str, patches: List[Tuple[str, str]]) -> None:
    """Apply sequence of search/replace operations to a file.

    :param path: Path to the file to edit. Can be relative (see cd tool).
    :param patches: List of (search_text, replace_text) tuples.

    Ideally, try to replace entire lines to avoid partial matches. Including
    a few lines of context in the search text helps to ensure the right match.
    """
    with open(path, "rt", encoding="utf-8") as f:
        content = f.read()

    for search, replace in patches:
        old_content = content
        content = content.replace(search, replace)
        if old_content == content:
            raise ValueError(f"Search text not found in file:\n\n{search}")

    with open(path, "wt", encoding="utf-8") as f:
        f.write(content)


@mcp.tool()
def apply_diff(diff: str) -> Dict[str, str]:
    """Apply a unified diff to files in the working directory.

    :param diff: A unified diff string (output of diff -u or git diff)
    :returns: Dictionary mapping filenames to operation results

    The unified diff should include file paths and can contain multiple file changes.
    Each change is applied to the corresponding file in the working directory.

    Supports git-style diffs with 'a/' and 'b/' prefixes.
    For best results:
    - Ensure each file section is properly formatted with file paths, hunk
      headers, and context lines
    - When patching multiple files, consider applying them separately for
      better error handling
    - Make sure the files being patched exist in the working directory

    Example diff format:
    ```
    --- a/path/to/file.py
    +++ b/path/to/file.py
    @@ -10,7 +10,7 @@
     unchanged line
     unchanged line
    -line to remove
    +line to add instead
     unchanged line
    ```
    """
    import tempfile
    import os

    # Write the diff to a temporary file
    with tempfile.NamedTemporaryFile(
        mode="w", delete=False, suffix=".patch"
    ) as temp_file:
        temp_file.write(diff)
        patch_file = temp_file.name

    results = {}

    try:
        # Apply the patch with -p0 (no path stripping)
        result = subprocess.run(
            ["patch", "-p1", "-i", patch_file, "--forward"],
            capture_output=True,
            text=True,
            check=False,
        )

        # Extract files being patched using regex
        file_pattern = re.compile(r"^\+\+\+ (.+)$", re.MULTILINE)
        modified_files = [m.group(1) for m in file_pattern.finditer(diff)]

        # Remove 'b/' prefix if it exists
        modified_files = [f[2:] if f.startswith("b/") else f for f in modified_files]

        # Process results
        if result.returncode == 0:
            # Success
            for file in modified_files:
                results[file] = "Successfully applied changes"
        else:
            # Error
            error_msg = result.stderr.strip() or result.stdout.strip()
            for file in modified_files:
                results[file] = f"Error applying changes: {error_msg}"
            results["error"] = error_msg

    except Exception as e:
        results["error"] = f"Error: {str(e)}"

    finally:
        # Clean up temporary file
        try:
            os.unlink(patch_file)
        except Exception:
            pass

    return results


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


def _read_claude_md() -> str:
    """Read the CLAUDE.md file, or return empty string if not found"""
    claude_md = Path.cwd() / "CLAUDE.md"
    if claude_md.exists():
        with open(claude_md, "r", encoding="utf-8") as f:
            return f.read()
    return ""


@mcp.tool()
def work_on(path: str) -> Dict[str, Union[List[str], str]]:
    """Change to directory, list its contents, and get all notes.
    Useful for getting familiar with a project at the start of a chat.

    :param path: Directory to work on. Supports home expansion (~/path).
    :returns: Dict with 'files' and 'notes' keys
    """
    cd(path)
    return {"files": ls("."), "notes": _read_claude_md()}


@mcp.tool()
def ruff_check(paths: list[str]) -> Dict[str, Union[str, int]]:
    """Run ruff linter on specified files. Useful to check that nothing was broken.

    :param paths: List of file paths to check
    :returns: Dict with 'output' and 'exit_code' keys
    """
    try:
        result = subprocess.run(
            [str(RUFF_PATH), "check"] + paths,
            capture_output=True,
            text=True,
            check=False,
        )
        return {"output": result.stdout + result.stderr, "exit_code": result.returncode}
    except FileNotFoundError:
        return {
            "output": "Error: ruff not found. Please install ruff package.",
            "exit_code": -1,
        }


@mcp.tool()
def ruff_format(paths: list[str]) -> Dict[str, Union[str, int]]:
    """Format files using ruff. Useful for fixing formatting issues after edits.

    :param paths: List of file paths to format
    :returns: Dict with 'output' and 'exit_code' keys
    """
    try:
        result = subprocess.run(
            [str(RUFF_PATH), "format"] + paths,
            capture_output=True,
            text=True,
            check=False,
        )
        return {"output": result.stdout + result.stderr, "exit_code": result.returncode}
    except FileNotFoundError:
        return {
            "output": "Error: ruff not found. Please install ruff package.",
            "exit_code": -1,
        }


@mcp.tool()
def shell_command(
    command: str, args: list[str] = None, cmdline: str = None, timeout: int = 30
) -> Dict[str, Union[str, int]]:
    """Run a shell command and return its output.

    :param command: The command to run (ignored if cmdline is provided)
    :param args: List of arguments for the command (ignored if cmdline is provided)
    :param cmdline: Full command line string including all arguments (alternative to command+args)
    :param timeout: Maximum execution time in seconds (default: 30)
    :returns: Dict with 'stdout', 'stderr', and 'exit_code' keys
    """
    try:
        if cmdline is not None:
            # Use shell=True for convenience with complex commands
            result = subprocess.run(
                cmdline,
                shell=True,
                capture_output=True,
                text=True,
                check=False,
                timeout=timeout,
            )
        else:
            # Use args list for safer command execution
            if args is None:
                args = []
            result = subprocess.run(
                [command] + args,
                capture_output=True,
                text=True,
                check=False,
                timeout=timeout,
            )

        return {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "exit_code": result.returncode,
        }
    except FileNotFoundError:
        return {"stdout": "", "stderr": "Error: Command not found.", "exit_code": 127}
    except subprocess.TimeoutExpired:
        return {
            "stdout": "",
            "stderr": f"Error: Command timed out after {timeout} seconds.",
            "exit_code": 124,
        }
    except Exception as e:
        return {
            "stdout": "",
            "stderr": f"Error executing command: {str(e)}",
            "exit_code": 1,
        }
