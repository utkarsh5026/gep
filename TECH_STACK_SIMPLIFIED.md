# Simplified Technology Stack
## Todo-Driven Agentic System (No Storage Required)

**Version:** 2.0 - Minimal
**Philosophy**: Use only what's needed. No databases, no embeddings, no persistence.

---

## Core Dependencies

### Agent & LLM (Required)

```toml
langgraph = "^0.0.20"        # Agent state management
langchain = "^0.3.11"         # Tool framework
langchain-openai = "^0.0.5"   # OpenAI GPT models
```

**Why?**
- **LangGraph**: Perfect for todo-based workflows with state tracking
- **LangChain**: Standard tool interface, well-documented
- **OpenAI**: Most reliable LLM, best function calling

**Usage**:
```python
from langgraph.graph import StateGraph
from langchain_openai import ChatOpenAI

# Simple, effective agent
llm = ChatOpenAI(model="gpt-4o", temperature=0)
workflow = StateGraph(AgentState)
```

---

### Code Analysis (Required)

```toml
tree-sitter = "^0.21.0"                # Universal AST parser
py-tree-sitter-languages = "*"         # Pre-built parsers
```

**Why?**
- Supports 50+ languages with one API
- Fast incremental parsing
- No need for language-specific parsers

**Usage**:
```python
from tree_sitter_languages import get_parser, get_language

# Parse any supported language
parser = get_parser('python')
tree = parser.parse(bytes(code, 'utf8'))

# Query AST
query = get_language('python').query("""
    (function_definition name: (identifier) @name)
""")
functions = query.captures(tree.root_node)
```

---

### Python Code Tools (Python-specific)

```toml
jedi = "^0.19.0"      # Auto-completion, go-to-definition
rope = "^1.11.0"      # Refactoring operations
libcst = "^1.1.0"     # Safe code transformation
radon = "^6.0.1"      # Code complexity metrics
```

**Why?**
- **jedi**: Understands Python semantics (imports, types)
- **rope**: Battle-tested refactoring (rename, extract, etc.)
- **libcst**: Preserves formatting during modifications
- **radon**: Quick complexity analysis

**Usage**:
```python
import jedi
import libcst as cst
from rope.base.project import Project
from radon.complexity import cc_visit

# Smart Python analysis
script = jedi.Script(code, path="file.py")
completions = script.complete(line, column)
definitions = script.goto(line, column)

# Safe refactoring
project = Project(".")
rope_file = project.get_file("module.py")
# ... refactoring operations

# Code transformation
tree = cst.parse_module(code)
modified = tree.visit(MyTransformer())

# Complexity analysis
complexity = cc_visit(code)
```

---

### CLI/TUI (User Interface)

```toml
rich = "^13.7.0"              # ✓ Already have
textual = "^0.47.0"           # TUI framework
prompt-toolkit = "^3.0.43"    # Interactive input
```

**Why?**
- **Rich**: Beautiful output you already use
- **Textual**: Modern TUI with CSS-like styling
- **prompt_toolkit**: Advanced CLI interactions

**Usage**:
```python
from rich.progress import track
from rich.syntax import Syntax
from rich.console import Console
from textual.app import App

console = Console()

# Beautiful code display
code_syntax = Syntax(code, "python", theme="monokai")
console.print(code_syntax)

# Progress tracking
for file in track(files, description="Analyzing..."):
    process(file)
```

---

### Git Integration (Required)

```toml
GitPython = "^3.1.44"  # ✓ Already have
```

**Why?**
- Already integrated in your codebase
- Comprehensive git operations
- Well-maintained

**Usage**:
```python
from git import Repo

repo = Repo(".")
repo.create_head("feature/new-feature")
repo.index.add(["file.py"])
repo.index.commit("Add feature")
```

---

### Testing & Validation (Required)

```toml
pytest = "^7.4.0"            # ✓ Already have
pytest-asyncio = "^0.21.0"   # ✓ Already have
pytest-cov = "*"             # Coverage reporting
```

**Why?**
- Standard Python testing
- Already in your stack
- Good enough for all needs

---

### Utilities (Already Have)

```toml
pydantic = "^2.10.0"      # ✓ Data validation
aiofiles = "^23.2.0"      # ✓ Async file I/O
loguru = "^0.7.2"         # ✓ Logging
tenacity = "^8.2.0"       # ✓ Retry logic
```

---

## Complete Minimal Stack

```toml
[tool.poetry.dependencies]
python = "^3.12"

# Agent & LLM
langgraph = "^0.0.20"
langchain = "^0.3.11"
langchain-openai = "^0.0.5"

# Code Analysis
tree-sitter = "^0.21.0"
py-tree-sitter-languages = "*"
jedi = "^0.19.0"
rope = "^1.11.0"
libcst = "^1.1.0"
radon = "^6.0.1"

# UI
rich = "^13.7.0"
textual = "^0.47.0"
prompt-toolkit = "^3.0.43"

# Git
GitPython = "^3.1.44"

# Utilities
pydantic = "^2.10.0"
aiofiles = "^23.2.0"
loguru = "^0.7.2"
tenacity = "^8.2.0"

# Testing
pytest = "^7.4.0"
pytest-asyncio = "^0.21.0"
pytest-cov = "*"

[tool.poetry.dev-dependencies]
black = "^24.0.0"
isort = "^5.13.0"
mypy = "^1.8.0"
ruff = "^0.1.0"
```

**Total new dependencies: ~8 packages**

---

## What We're NOT Using

### ❌ Vector Databases
- No FAISS
- No Qdrant
- No Chroma
- No Pinecone

**Why not?**
- Don't need semantic search
- AST + pattern matching is faster
- No indexing overhead
- Simpler architecture

### ❌ Embedding Providers
- No OpenAI embeddings
- No Cohere
- No local embedding models

**Why not?**
- Not needed for pattern-based search
- Saves API costs
- Faster results

### ❌ Graph Databases
- No Neo4j
- No NetworkX (maybe later for visualization)

**Why not?**
- Can build call graphs on-demand
- Don't need persistent graph storage

### ❌ Additional LLM Providers (Initially)
- No Claude (maybe later)
- No Gemini (maybe later)
- No local models (maybe later)

**Why not?**
- Start simple with OpenAI
- Add later if needed
- One provider = less complexity

### ❌ Heavy Infrastructure
- No Docker (unless user wants)
- No Redis
- No databases
- No caching layers

**Why not?**
- Session-based = no persistence needed
- Keep it lightweight
- Easier to install and run

---

## Installation

### Quick Install

```bash
cd server
poetry add langgraph langchain langchain-openai
poetry add tree-sitter py-tree-sitter-languages
poetry add jedi rope libcst radon
poetry add textual prompt-toolkit
poetry add pytest-cov
```

Or with pip:

```bash
pip install langgraph langchain langchain-openai
pip install tree-sitter py-tree-sitter-languages
pip install jedi rope libcst radon
pip install textual prompt-toolkit
pip install pytest-cov
```

### Verify Installation

```python
# test_install.py
import langgraph
import tree_sitter
import jedi
import textual
print("✓ All dependencies installed!")
```

---

## Architecture Patterns

### 1. File Discovery (No Indexing)

```python
from pathlib import Path
from tree_sitter_languages import get_parser

class FileFinder:
    """Find files without any indexing"""

    def find_by_name(self, pattern: str) -> list[Path]:
        """Find files by glob pattern"""
        return list(Path(".").rglob(pattern))

    def find_with_content(self, text: str) -> list[Path]:
        """Find files containing text (grep-like)"""
        matches = []
        for f in Path(".").rglob("*.py"):
            if text in f.read_text(errors='ignore'):
                matches.append(f)
        return matches

    def find_with_ast_pattern(self, pattern: str) -> list[Path]:
        """Find files with specific AST patterns"""
        parser = get_parser('python')
        matches = []

        for f in Path(".").rglob("*.py"):
            tree = parser.parse(bytes(f.read_text(), 'utf8'))
            # ... query AST for pattern
            if has_pattern(tree):
                matches.append(f)

        return matches
```

### 2. Session Context (In-Memory)

```python
from dataclasses import dataclass, field
from typing import Dict, List

@dataclass
class SessionContext:
    """All session state - cleared on exit"""

    task: str
    todos: List[Todo] = field(default_factory=list)
    files_read: Dict[Path, str] = field(default_factory=dict)
    changes_made: List[Change] = field(default_factory=list)
    test_results: Dict[str, bool] = field(default_factory=dict)

    def read_file(self, path: Path) -> str:
        """Read and cache file for session"""
        if path not in self.files_read:
            self.files_read[path] = path.read_text()
        return self.files_read[path]

    def clear(self):
        """Clear all session data"""
        self.todos.clear()
        self.files_read.clear()
        self.changes_made.clear()
        self.test_results.clear()
```

### 3. Smart File Prioritization

```python
class FilePrioritizer:
    """Determine which files to read first"""

    def prioritize(self, files: list[Path], task: str) -> list[Path]:
        """Order files by relevance to task"""
        scored = []

        for file in files:
            score = 0

            # Score by name match
            if any(word in file.name for word in task.lower().split()):
                score += 10

            # Score by recency (git)
            days_old = self.get_file_age(file)
            score += max(0, 10 - days_old)

            # Score by size (prefer smaller)
            size_kb = file.stat().st_size / 1024
            if size_kb < 100:
                score += 5

            scored.append((score, file))

        return [f for _, f in sorted(scored, reverse=True)]
```

### 4. AST-Based Code Search

```python
from tree_sitter_languages import get_language, get_parser

class CodeSearch:
    """Search code using AST patterns"""

    def find_functions(self, file: Path, name_pattern: str) -> list:
        """Find functions matching pattern"""
        parser = get_parser('python')
        tree = parser.parse(bytes(file.read_text(), 'utf8'))

        query = get_language('python').query(f"""
            (function_definition
                name: (identifier) @name
            ) @function
        """)

        functions = []
        for node, _ in query.captures(tree.root_node):
            func_name = node.text.decode('utf8')
            if name_pattern.lower() in func_name.lower():
                functions.append({
                    'name': func_name,
                    'line': node.start_point[0],
                    'code': self.get_node_text(node)
                })

        return functions

    def find_decorators(self, file: Path, decorator: str) -> list:
        """Find functions with specific decorator"""
        # Similar AST query for decorators
        pass

    def find_imports(self, file: Path, module: str) -> list:
        """Find import statements"""
        # AST query for imports
        pass
```

---

## Performance Considerations

### 1. Lazy File Reading
```python
# Don't read all files upfront
# Read only when needed

class LazyFileReader:
    def __init__(self):
        self._cache = {}

    def read(self, path: Path) -> str:
        if path not in self._cache:
            self._cache[path] = path.read_text()
        return self._cache[path]

    def clear_cache(self):
        """Clear at end of session"""
        self._cache.clear()
```

### 2. Parallel Analysis
```python
import asyncio

async def analyze_files(files: list[Path]) -> list[Analysis]:
    """Analyze multiple files in parallel"""
    tasks = [analyze_file(f) for f in files]
    return await asyncio.gather(*tasks)
```

### 3. Early Termination
```python
def find_first_match(files: list[Path], pattern: str) -> Path | None:
    """Stop searching once found"""
    for file in files:
        if pattern in file.read_text(errors='ignore'):
            return file
    return None
```

### 4. Smart Limits
```python
MAX_FILES_TO_READ = 50       # Don't read entire codebase
MAX_FILE_SIZE = 1024 * 100   # Skip files > 100KB
MAX_SEARCH_DEPTH = 10        # Limit directory depth
```

---

## Code Quality Tools

### Linting & Formatting

```toml
[tool.poetry.dev-dependencies]
black = "^24.0.0"      # Code formatting
isort = "^5.13.0"      # Import sorting
ruff = "^0.1.0"        # Fast linter
mypy = "^1.8.0"        # Type checking
```

### Usage in Agent

```python
class CodeQualityChecker:
    def format_code(self, file: Path):
        """Auto-format with black"""
        subprocess.run(["black", str(file)])

    def check_types(self, file: Path) -> list[Issue]:
        """Run mypy"""
        result = subprocess.run(
            ["mypy", str(file)],
            capture_output=True,
            text=True
        )
        return parse_mypy_output(result.stdout)

    def lint(self, file: Path) -> list[Issue]:
        """Run ruff"""
        result = subprocess.run(
            ["ruff", "check", str(file)],
            capture_output=True,
            text=True
        )
        return parse_ruff_output(result.stdout)
```

---

## Testing Strategy

### Unit Tests
```python
# Test individual components
def test_file_finder():
    finder = FileFinder()
    files = finder.find_by_name("*test*.py")
    assert len(files) > 0

def test_code_parser():
    parser = CodeParser()
    tree = parser.parse("def foo(): pass", "python")
    assert tree is not None
```

### Integration Tests
```python
# Test agent workflow
async def test_agent_workflow():
    agent = Agent()
    result = await agent.run("Add logging to auth.py")

    assert result.success
    assert len(result.todos) > 0
    assert all(t.status == "complete" for t in result.todos)
```

### Test Coverage
```bash
pytest --cov=src --cov-report=html
# Aim for 80%+ coverage
```

---

## Comparison: This Stack vs Vector-Based

| Feature | This Stack | Vector-Based |
|---------|-----------|--------------|
| **Setup Time** | 5 min | 30+ min |
| **Dependencies** | ~15 packages | 30+ packages |
| **Disk Usage** | <100 MB | >1 GB (with embeddings) |
| **Startup Time** | Instant | Need to index first |
| **Search Speed** | Fast (AST) | Fast (once indexed) |
| **Accuracy** | High (structural) | High (semantic) |
| **Maintenance** | Low | Medium (re-indexing) |
| **Cost** | LLM only | LLM + embeddings |

**Our approach wins on**:
- ✅ Simplicity
- ✅ Setup speed
- ✅ Maintenance
- ✅ Cost
- ✅ No pre-processing

**Vector approach wins on**:
- ✅ Semantic understanding
- ✅ Very large codebases (100k+ files)
- ✅ Natural language queries

**Our bet**: For most codebases (< 10k files), AST + patterns is better.

---

## Summary

### Total Stack Size
- **New dependencies**: ~8 packages
- **Disk space**: ~50 MB
- **Memory usage**: ~200 MB
- **Setup time**: 5 minutes

### What You Get
- ✅ Universal code parsing (50+ languages)
- ✅ Smart file discovery
- ✅ Safe code modification
- ✅ Beautiful CLI/TUI
- ✅ Agent orchestration
- ✅ Git integration
- ✅ Testing framework

### What You Don't Need
- ❌ Vector databases
- ❌ Embedding APIs
- ❌ Indexing step
- ❌ Persistent storage
- ❌ Complex infrastructure

**Simple, fast, effective.** 🚀
