# GEP Agentic System - Simplified Roadmap
## Session-Based, Todo-Driven Development Assistant

**Version:** 2.0 - Simplified
**Date:** 2025-11-15
**Philosophy**: No storage, no embeddings. Read, analyze, plan, execute.

---

## Table of Contents
1. [Vision](#vision)
2. [Core Principles](#core-principles)
3. [Architecture](#architecture)
4. [Implementation Phases](#implementation-phases)
5. [Technology Stack](#technology-stack)
6. [Example Workflow](#example-workflow)

---

## Vision

Build an **autonomous coding agent** that:
- **Understands** codebases through direct file analysis (AST + pattern matching)
- **Plans** tasks as structured todo lists
- **Implements** changes autonomously with validation
- **Works** entirely in-session (no persistent storage)
- **Learns** patterns within each session
- **Provides** exceptional UX through clear progress tracking

### What Makes This Different

Unlike semantic search tools, this agent:
- ✅ Reads files on-demand (no pre-indexing)
- ✅ Uses AST and structural search (no embeddings)
- ✅ Creates explicit todo lists (clear progress)
- ✅ Validates each step (safe modifications)
- ✅ Works from scratch each session (no state to maintain)

---

## Core Principles

### 1. **Session-Based Analysis**
Every session starts fresh:
```
User: "Add authentication to the API"

Agent:
1. Scans project structure (find relevant files)
2. Reads API files (parse AST, understand structure)
3. Creates todo list (5-10 concrete steps)
4. Executes each todo item
5. Validates and commits
```

### 2. **Pattern-Based Search**
No embeddings needed:
```python
# Find functions by pattern
find_functions_matching("auth*")  # AST query
find_imports("flask")              # Structural search
find_similar_patterns(code_sample) # AST similarity
grep_codebase("@app.route")       # Text search
```

### 3. **Todo-Driven Execution**
Every task becomes a todo list:
```
Task: Add authentication

Todos:
☐ 1. Scan codebase for existing auth patterns
☐ 2. Find API route definitions
☐ 3. Create auth middleware module
☐ 4. Add JWT token handling
☐ 5. Update API routes with auth decorator
☐ 6. Write tests for auth flow
☐ 7. Update documentation
☐ 8. Run tests and validate
```

### 4. **Smart File Discovery**
Find relevant files without indexing:
```python
# Strategy 1: File name patterns
find_files("*auth*", "*api*", "*middleware*")

# Strategy 2: Import analysis
find_files_importing("flask")

# Strategy 3: AST analysis
find_files_with_decorators("@app.route")

# Strategy 4: Git history
find_recently_modified_files()
```

### 5. **No Persistent Storage**
- No vector databases
- No embedding caches
- No session history storage
- Everything computed on-demand
- Stateless agent design

---

## Architecture

### High-Level System

```
┌─────────────────────────────────────────────────────────────┐
│                      CLI Interface                           │
│             (Rich output + Textual TUI)                      │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│                   Agent Controller                           │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  Input: User task                                      │ │
│  │  Output: Completed implementation                      │ │
│  │                                                         │ │
│  │  1. Understand → 2. Plan → 3. Execute → 4. Validate   │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│                    Tool Layer                                │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ Code Search  │  │ Code Modify  │  │   Git Ops    │     │
│  ├──────────────┤  ├──────────────┤  ├──────────────┤     │
│  │ • AST parse  │  │ • Read file  │  │ • Create br. │     │
│  │ • Pattern    │  │ • Write file │  │ • Commit     │     │
│  │ • Grep       │  │ • Edit       │  │ • Diff       │     │
│  │ • File find  │  │ • Refactor   │  │ • Push       │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  Test/Build  │  │  Todo Mgmt   │  │   Analysis   │     │
│  ├──────────────┤  ├──────────────┤  ├──────────────┤     │
│  │ • Run tests  │  │ • Create     │  │ • Complexity │     │
│  │ • Lint       │  │ • Update     │  │ • Deps       │     │
│  │ • Type check │  │ • Track      │  │ • Structure  │     │
│  │ • Build      │  │ • Display    │  │ • Patterns   │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│                  Session Context                             │
│  (In-Memory Only - Resets Each Session)                      │
│                                                              │
│  • Current task                                              │
│  • Todo list (with status)                                   │
│  • Files read (cache for session)                            │
│  • Code changes made                                         │
│  • Test results                                              │
│  • Conversation history                                      │
└──────────────────────────────────────────────────────────────┘
```

### Agent Flow

```
┌──────────────┐
│  User Task   │
└──────┬───────┘
       │
       ▼
┌──────────────────────────────────────┐
│  PHASE 1: Understand                 │
│  • Scan project structure            │
│  • Find relevant files               │
│  • Read and parse key files          │
│  • Identify patterns and conventions │
└──────┬───────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────┐
│  PHASE 2: Plan (Create Todos)        │
│  • Break task into steps             │
│  • Create todo list (5-10 items)     │
│  • Estimate complexity               │
│  • Identify dependencies             │
└──────┬───────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────┐
│  PHASE 3: Execute (Process Todos)    │
│  FOR EACH TODO:                      │
│    • Read required files             │
│    • Make changes                    │
│    • Validate syntax                 │
│    • Run relevant tests              │
│    • Mark todo complete              │
└──────┬───────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────┐
│  PHASE 4: Validate & Commit          │
│  • Run full test suite               │
│  • Check linting/types               │
│  • Review all changes                │
│  • Create git commit                 │
│  • Push to branch                    │
└──────┬───────────────────────────────┘
       │
       ▼
┌──────────────┐
│   Complete   │
└──────────────┘
```

---

## Implementation Phases

### Phase 1: Core Agent & File Analysis (Week 1-2)

**Goal**: Agent that can read, understand, and analyze code

**Tasks**:

1. **LangGraph Agent Setup**
   - Agent state machine (understand → plan → execute → validate)
   - LLM integration (OpenAI GPT-4o primary)
   - Streaming responses
   - Error handling and recovery

2. **File Discovery System**
   ```python
   class FileDiscovery:
       def find_by_pattern(self, patterns: list[str]) -> list[Path]
       def find_by_content(self, search: str) -> list[Path]
       def find_by_imports(self, module: str) -> list[Path]
       def find_by_git_history(self, days: int) -> list[Path]
       def smart_discover(self, context: str) -> list[Path]
   ```

3. **AST-Based Code Analysis**
   ```python
   class CodeAnalyzer:
       def parse(self, file: Path) -> AST
       def extract_functions(self, file: Path) -> list[Function]
       def extract_classes(self, file: Path) -> list[Class]
       def find_patterns(self, pattern: str) -> list[Match]
       def get_imports(self, file: Path) -> list[Import]
       def find_references(self, symbol: str) -> list[Reference]
   ```

4. **Structural Search**
   ```python
   class StructuralSearch:
       def find_function_calls(self, func_name: str) -> list[Location]
       def find_decorators(self, decorator: str) -> list[Location]
       def find_similar_code(self, sample: str) -> list[Match]
       def find_patterns_like(self, template: AST) -> list[Match]
   ```

**Deliverables**:
- Agent can read and analyze any Python file
- AST parsing for Python, JavaScript, TypeScript
- Pattern-based code search
- File discovery system

---

### Phase 2: Todo System & Planning (Week 3)

**Goal**: Agent creates and manages todo lists

**Tasks**:

1. **Todo List Generator**
   ```python
   class TodoGenerator:
       def create_plan(self, task: str, context: dict) -> TodoList
       def break_down_task(self, task: str) -> list[SubTask]
       def estimate_complexity(self, todo: Todo) -> Complexity
       def order_by_dependencies(self, todos: list[Todo]) -> list[Todo]
   ```

2. **Todo Tracker**
   ```python
   class TodoTracker:
       def create_todo(self, description: str) -> Todo
       def mark_in_progress(self, todo_id: str)
       def mark_complete(self, todo_id: str)
       def mark_failed(self, todo_id: str, reason: str)
       def get_progress(self) -> dict  # % complete, time estimate
   ```

3. **CLI Todo Display**
   ```
   Task: Add authentication to API

   Progress: ████████░░░░░░░░░░░░ 40% (2/5 complete)

   ✓ 1. Scan codebase for auth patterns
   ✓ 2. Create auth middleware module
   → 3. Add JWT token handling         [IN PROGRESS]
   ○ 4. Update API routes with auth
   ○ 5. Write and run tests
   ```

**Deliverables**:
- LLM-powered task decomposition
- Todo list management
- Progress tracking
- Beautiful CLI display

---

### Phase 3: Code Modification Tools (Week 4-5)

**Goal**: Agent can modify code safely

**Tasks**:

1. **File Operations**
   ```python
   class FileOperations:
       def read_file(self, path: Path) -> str
       def write_file(self, path: Path, content: str)
       def edit_file(self, path: Path, changes: list[Edit])
       def create_file(self, path: Path, content: str)
       def delete_file(self, path: Path)
   ```

2. **Code Editing**
   ```python
   class CodeEditor:
       def insert_function(self, file: Path, function: str, after: str)
       def modify_function(self, file: Path, func_name: str, new_code: str)
       def add_import(self, file: Path, import_stmt: str)
       def rename_symbol(self, file: Path, old: str, new: str)
       def extract_function(self, file: Path, lines: range, name: str)
   ```

3. **Refactoring Operations**
   ```python
   class Refactoring:
       def rename_variable(self, file: Path, old: str, new: str)
       def extract_method(self, file: Path, start: int, end: int)
       def inline_function(self, file: Path, func_name: str)
       def move_function(self, from_file: Path, to_file: Path, func: str)
   ```

4. **Validation**
   ```python
   class CodeValidator:
       def validate_syntax(self, code: str, language: str) -> bool
       def check_imports(self, file: Path) -> list[Issue]
       def check_types(self, file: Path) -> list[Issue]
       def check_style(self, file: Path) -> list[Issue]
   ```

**Deliverables**:
- Safe file modification
- AST-based code editing
- Syntax validation
- Pre-commit validation

---

### Phase 4: Testing & Validation (Week 6)

**Goal**: Agent validates changes before committing

**Tasks**:

1. **Test Execution**
   ```python
   class TestRunner:
       def discover_tests(self) -> list[Test]
       def run_tests(self, test_filter: str = None) -> TestResults
       def run_affected_tests(self, files: list[Path]) -> TestResults
       def get_coverage(self) -> CoverageReport
   ```

2. **Build & Lint**
   ```python
   class BuildValidator:
       def run_linter(self) -> list[Issue]
       def run_type_checker(self) -> list[Issue]
       def run_formatter(self, fix: bool = False)
       def run_build(self) -> BuildResult
   ```

3. **Change Validation**
   ```python
   class ChangeValidator:
       def validate_change(self, file: Path, new_content: str) -> Validation
       def check_breaking_changes(self, changes: list[Change]) -> list[Issue]
       def suggest_tests(self, changes: list[Change]) -> list[TestSuggestion]
   ```

**Deliverables**:
- Automated test execution
- Lint and type checking
- Change validation pipeline
- Test coverage tracking

---

### Phase 5: Git Integration (Week 7)

**Goal**: Agent manages git operations

**Tasks**:

1. **Git Operations**
   ```python
   class GitOperations:
       def create_branch(self, name: str)
       def commit_changes(self, message: str)
       def push_branch(self)
       def show_diff(self) -> str
       def show_status(self) -> GitStatus
   ```

2. **Smart Commits**
   ```python
   class SmartCommit:
       def generate_commit_message(self, changes: list[Change]) -> str
       def split_into_commits(self, changes: list[Change]) -> list[Commit]
       def create_conventional_commit(self, changes: list[Change]) -> str
   ```

**Deliverables**:
- Git branch management
- Automated commits
- Smart commit messages
- Diff analysis

---

### Phase 6: Interactive UX (Week 8-9)

**Goal**: Beautiful, intuitive user experience

**Tasks**:

1. **CLI Enhancements**
   - Streaming LLM output
   - Real-time progress bars
   - Syntax-highlighted code diffs
   - Interactive confirmations

2. **TUI Mode (Textual)**
   ```
   ┌─────────────────────────────────────────────────────────┐
   │ GEP Agent                                    [Session 1] │
   ├─────────────────────────────────────────────────────────┤
   │ Task: Add user authentication                           │
   │                                                         │
   │ Progress: ████████████░░░░░░░░ 60%                     │
   │                                                         │
   │ ✓ Analyzed codebase (found 3 API files)                │
   │ ✓ Created auth middleware                              │
   │ ✓ Added JWT handling                                   │
   │ → Running tests...                                     │
   │   • test_auth_required ... ✓                           │
   │   • test_jwt_validation ... ✓                          │
   │   • test_unauthorized ... running...                   │
   │                                                         │
   │ [View Code] [View Diff] [Approve] [Rollback]           │
   └─────────────────────────────────────────────────────────┘
   ```

3. **Error Recovery**
   - Clear error messages
   - Suggested fixes
   - Rollback options
   - Retry logic

**Deliverables**:
- Rich CLI output
- Textual TUI
- Interactive approvals
- Error recovery

---

### Phase 7: Advanced Features (Week 10-12)

**Goal**: Polish and advanced capabilities

**Tasks**:

1. **Multi-Language Support**
   - Python ✓
   - JavaScript/TypeScript
   - Go
   - Rust
   - Java

2. **Smart Context Management**
   ```python
   class ContextManager:
       def get_relevant_files(self, task: str, limit: int = 10) -> list[Path]
       def prioritize_files(self, files: list[Path]) -> list[Path]
       def estimate_relevance(self, file: Path, task: str) -> float
   ```

3. **Learning & Patterns**
   ```python
   class PatternLearner:
       def detect_code_patterns(self) -> list[Pattern]
       def detect_naming_conventions(self) -> dict
       def detect_architecture_style(self) -> str
       def suggest_similar_implementations(self, task: str) -> list[Example]
   ```

4. **Performance Optimization**
   - Parallel file reading
   - AST caching (session only)
   - Smart file filtering
   - Incremental parsing

**Deliverables**:
- Multi-language support
- Pattern detection
- Performance optimizations
- Production-ready release

---

## Technology Stack

### Core Stack (Minimal)

```toml
[dependencies]
# Agent Framework
langgraph = "^0.0.20"           # Agent orchestration
langchain = "^0.3.11"            # Tools and LLM abstractions
langchain-openai = "^0.0.5"      # OpenAI integration

# Code Analysis
tree-sitter = "^0.21.0"          # Universal AST parsing
py-tree-sitter-languages = "*"   # Pre-built language bindings
jedi = "^0.19.0"                 # Python analysis
radon = "^6.0.1"                 # Complexity metrics

# Code Modification
libcst = "^1.1.0"                # Python code transformation
rope = "^1.11.0"                 # Python refactoring

# Git Integration
GitPython = "^3.1.44"            # Already have this

# CLI/TUI
rich = "^13.7.0"                 # Already have this
textual = "^0.47.0"              # TUI framework
prompt-toolkit = "^3.0.43"       # Advanced input

# Testing
pytest = "^7.4.0"                # Already have this
pytest-asyncio = "^0.21.0"       # Already have this

# Utilities
pydantic = "^2.10.0"             # Already have this
aiofiles = "^23.2.0"             # Already have this
loguru = "^0.7.2"                # Already have this
```

### What We're NOT Using

- ❌ Vector databases (FAISS, Qdrant, Chroma)
- ❌ Embedding providers (OpenAI embeddings, etc.)
- ❌ Persistent storage
- ❌ Neo4j or graph databases
- ❌ Redis or caching layers
- ❌ Docker (unless user wants sandboxing)

### Why This Stack Works

1. **LangGraph**: Perfect for stateful agent workflows
2. **tree-sitter**: Fast, universal AST parsing
3. **libcst/rope**: Safe Python code transformation
4. **Rich/Textual**: Beautiful terminal UX
5. **GitPython**: Already integrated

---

## Example Workflow

### User Request
```bash
gep task "Add rate limiting to the API endpoints"
```

### Agent Execution

**Phase 1: Understand** (5-10s)
```
[Agent] Analyzing codebase...
        • Scanning for API files... found 3 files
        • Reading server/api/routes.py
        • Reading server/api/app.py
        • Checking for existing middleware... none found
        • Analyzing rate limiting libraries... redis suggested
```

**Phase 2: Plan** (5s)
```
[Agent] Created implementation plan:

Todo List (5 items):
1. ☐ Install rate limiting library (flask-limiter)
2. ☐ Create rate limiter configuration
3. ☐ Add rate limiter middleware to app
4. ☐ Apply rate limits to API endpoints
5. ☐ Add tests for rate limiting
```

**Phase 3: Execute** (30-60s)
```
[Agent] Executing plan...

✓ 1. Install rate limiting library
     • Added flask-limiter to requirements.txt
     • Updated pyproject.toml

→ 2. Create rate limiter configuration
     • Creating server/config/rate_limit.py
     • Added default limits: 100/hour, 10/minute

[Show code diff? y/n]
```

**User approves, agent continues...**

```
✓ 2. Create rate limiter configuration
✓ 3. Add rate limiter middleware to app
     • Modified server/api/app.py
     • Initialized Limiter with Redis backend

→ 4. Apply rate limits to API endpoints
     • Adding @limiter.limit() decorators
     • Updated 5 endpoints in routes.py

     Modified functions:
     - get_users() -> 100/hour
     - create_user() -> 10/minute
     - update_user() -> 20/minute
     - delete_user() -> 10/minute
     - get_user_by_id() -> 100/hour
```

**Phase 4: Validate** (10-20s)
```
✓ 4. Apply rate limits to API endpoints
✓ 5. Add tests for rate limiting
     • Created tests/test_rate_limit.py
     • Added 3 test cases

[Agent] Running validation...
        • Syntax check... ✓
        • Import check... ✓
        • Type check... ✓
        • Running tests...
          - test_rate_limit_applied ... ✓
          - test_rate_limit_exceeded ... ✓
          - test_rate_limit_reset ... ✓
        • All tests passed (24/24) ✓

[Agent] Ready to commit. Review changes? [y/n]
```

**User reviews and approves**

```
[Agent] Creating commit...
        • Generated commit message:
          "feat: Add rate limiting to API endpoints

          - Install flask-limiter dependency
          - Configure rate limiter with Redis backend
          - Apply rate limits to user endpoints
          - Add comprehensive rate limit tests"

        • Committed to branch: feature/rate-limiting
        • Pushing to origin...

✓ Task complete!

Summary:
- Files changed: 5
- Lines added: 87
- Lines removed: 2
- Tests added: 3
- All tests passing ✓
```

---

## Success Metrics

### Task Success
- **Completion Rate**: >70% of tasks completed without intervention
- **Correctness**: >90% of changes pass tests
- **Speed**: <2 min for simple tasks, <10 min for complex

### Code Quality
- **Tests**: All changes tested
- **Style**: Follows project conventions
- **Type Safety**: No type errors introduced

### User Experience
- **Clarity**: Users understand what agent is doing
- **Control**: Users can approve/reject at any step
- **Recovery**: Clear error messages and rollback

### Research Value
- Novel todo-driven approach
- Session-based analysis effectiveness
- Pattern-based vs semantic search comparison
- Agent architecture learnings

---

## Research Questions

1. **How effective is pattern-based search vs embeddings?**
   - Measure: Search accuracy, speed, relevance
   - Hypothesis: For well-structured code, AST search is sufficient

2. **What's the optimal todo granularity?**
   - Measure: User satisfaction, task success rate
   - Hypothesis: 5-7 todos per task is ideal

3. **How much context is needed?**
   - Measure: Files read vs task success
   - Hypothesis: 10-20 files sufficient for most tasks

4. **Session-based vs persistent: trade-offs?**
   - Measure: Speed, accuracy, resource usage
   - Hypothesis: Session-based is simpler and fast enough

---

## Next Steps

### This Week
1. ✅ Read this roadmap
2. ⬜ Set up development environment
3. ⬜ Build Phase 1 (Core Agent)
4. ⬜ Build Phase 2 (Todo System)
5. ⬜ Test on real codebase

### This Month
- Complete Phases 1-4
- Working prototype that can:
  - Analyze code
  - Create todos
  - Modify code
  - Run tests

### This Quarter
- Complete all phases
- Production release
- Research paper on approach
- Open source release

---

## Conclusion

This simplified approach focuses on **what matters**:
- ✅ Understanding code (AST + patterns)
- ✅ Clear planning (todo lists)
- ✅ Safe execution (validation)
- ✅ Great UX (streaming, progress)

By eliminating unnecessary complexity (no vector DBs, no embeddings), we can:
- Build faster
- Maintain easier
- Research effectively
- Ship sooner

**Let's build it!** 🚀
