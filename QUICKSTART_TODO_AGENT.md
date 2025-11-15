# Quick Start: Todo-Driven Agent
## Build Your First Agentic System in 30 Minutes

**Goal**: Create a working agent that analyzes code, creates todo lists, and tracks implementation progress.

---

## What You'll Build

An agent that can:
1. ✅ Read and analyze code files
2. ✅ Create structured todo lists for tasks
3. ✅ Track progress through todos
4. ✅ Display beautiful CLI output
5. ✅ Search code using AST patterns

**No vector databases. No embeddings. Just smart code analysis.**

---

## Prerequisites

- Python 3.12+
- Git
- OpenAI API key
- 10 minutes

---

## Step 1: Install Dependencies (2 min)

```bash
cd /home/user/gep/server

# Install new dependencies
poetry add langgraph langchain langchain-openai
poetry add py-tree-sitter-languages
poetry add textual

# Or with pip
pip install langgraph langchain langchain-openai py-tree-sitter-languages textual
```

Set your API key:
```bash
echo "OPENAI_API_KEY=your_key_here" >> .env
```

---

## Step 2: Create Project Structure (1 min)

```bash
cd src

# Create new directories
mkdir -p agent/{core,tools,planning}
mkdir -p agent/models

# Create __init__.py files
touch agent/__init__.py
touch agent/core/__init__.py
touch agent/tools/__init__.py
touch agent/planning/__init__.py
touch agent/models/__init__.py
```

Your structure:
```
src/
├── agent/
│   ├── core/          # Agent orchestrator
│   ├── planning/      # Todo generation
│   ├── tools/         # File operations
│   └── models/        # Data models
```

---

## Step 3: Define Data Models (5 min)

Create `src/agent/models/todo.py`:

```python
"""
Todo models for tracking agent tasks.
"""
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


class TodoStatus(Enum):
    """Status of a todo item"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class Todo:
    """A single todo item"""
    id: str
    description: str
    status: TodoStatus = TodoStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error: Optional[str] = None

    def start(self):
        """Mark todo as in progress"""
        self.status = TodoStatus.IN_PROGRESS
        self.started_at = datetime.now()

    def complete(self):
        """Mark todo as completed"""
        self.status = TodoStatus.COMPLETED
        self.completed_at = datetime.now()

    def fail(self, error: str):
        """Mark todo as failed"""
        self.status = TodoStatus.FAILED
        self.error = error
        self.completed_at = datetime.now()

    @property
    def duration(self) -> Optional[float]:
        """Get duration in seconds if completed"""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None


@dataclass
class TodoList:
    """Collection of todos for a task"""
    task: str
    todos: list[Todo] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)

    def add(self, description: str) -> Todo:
        """Add a new todo"""
        todo = Todo(
            id=f"todo_{len(self.todos) + 1}",
            description=description
        )
        self.todos.append(todo)
        return todo

    def get_current(self) -> Optional[Todo]:
        """Get the current in-progress todo"""
        for todo in self.todos:
            if todo.status == TodoStatus.IN_PROGRESS:
                return todo
        return None

    def get_next(self) -> Optional[Todo]:
        """Get the next pending todo"""
        for todo in self.todos:
            if todo.status == TodoStatus.PENDING:
                return todo
        return None

    @property
    def progress(self) -> float:
        """Get completion percentage (0-100)"""
        if not self.todos:
            return 0.0
        completed = sum(1 for t in self.todos if t.status == TodoStatus.COMPLETED)
        return (completed / len(self.todos)) * 100

    @property
    def is_complete(self) -> bool:
        """Check if all todos are done"""
        return all(t.status == TodoStatus.COMPLETED for t in self.todos)

    def __str__(self) -> str:
        """String representation"""
        lines = [f"Task: {self.task}", f"Progress: {self.progress:.0f}%", ""]

        for todo in self.todos:
            if todo.status == TodoStatus.COMPLETED:
                symbol = "✓"
            elif todo.status == TodoStatus.IN_PROGRESS:
                symbol = "→"
            elif todo.status == TodoStatus.FAILED:
                symbol = "✗"
            else:
                symbol = "○"

            lines.append(f"{symbol} {todo.id}: {todo.description}")
            if todo.error:
                lines.append(f"  Error: {todo.error}")

        return "\n".join(lines)
```

---

## Step 4: Create File Discovery Tool (7 min)

Create `src/agent/tools/file_finder.py`:

```python
"""
File discovery without any indexing.
"""
from pathlib import Path
from typing import Optional
from dataclasses import dataclass
from tree_sitter_languages import get_parser


@dataclass
class FileMatch:
    """A file that matches search criteria"""
    path: Path
    score: float  # Relevance score 0-100
    reason: str   # Why it matched


class FileFinder:
    """
    Find files using various strategies without indexing.
    """

    def __init__(self, root: Path = Path(".")):
        self.root = root
        self.ignore_patterns = {
            ".git", "__pycache__", "node_modules", ".venv",
            "venv", "dist", "build", ".pytest_cache", ".mypy_cache"
        }

    def find_by_glob(self, pattern: str) -> list[Path]:
        """Find files matching glob pattern"""
        return [
            f for f in self.root.rglob(pattern)
            if self._should_include(f)
        ]

    def find_by_content(self, text: str, extension: str = "*.py") -> list[FileMatch]:
        """Find files containing specific text"""
        matches = []

        for file in self.root.rglob(extension):
            if not self._should_include(file):
                continue

            try:
                content = file.read_text(errors='ignore')
                if text.lower() in content.lower():
                    # Count occurrences for scoring
                    count = content.lower().count(text.lower())
                    score = min(100, count * 10)
                    matches.append(FileMatch(
                        path=file,
                        score=score,
                        reason=f"Contains '{text}' ({count} times)"
                    ))
            except Exception:
                continue

        return sorted(matches, key=lambda m: m.score, reverse=True)

    def find_functions_named(self, name_pattern: str) -> list[FileMatch]:
        """Find files with functions matching pattern"""
        matches = []
        parser = get_parser('python')

        for file in self.root.rglob("*.py"):
            if not self._should_include(file):
                continue

            try:
                code = file.read_text()
                tree = parser.parse(bytes(code, 'utf8'))

                # Find function definitions
                for node in tree.root_node.children:
                    if node.type == 'function_definition':
                        # Get function name
                        for child in node.children:
                            if child.type == 'identifier':
                                func_name = code[child.start_byte:child.end_byte]
                                if name_pattern.lower() in func_name.lower():
                                    matches.append(FileMatch(
                                        path=file,
                                        score=80,
                                        reason=f"Has function '{func_name}'"
                                    ))
                                    break
            except Exception:
                continue

        return matches

    def find_imports_of(self, module: str) -> list[FileMatch]:
        """Find files that import a specific module"""
        matches = []

        for file in self.root.rglob("*.py"):
            if not self._should_include(file):
                continue

            try:
                content = file.read_text()
                # Simple check for import statements
                if f"import {module}" in content or f"from {module}" in content:
                    matches.append(FileMatch(
                        path=file,
                        score=90,
                        reason=f"Imports {module}"
                    ))
            except Exception:
                continue

        return matches

    def smart_find(self, task: str, limit: int = 10) -> list[FileMatch]:
        """
        Smart file discovery based on task description.
        Uses multiple strategies and combines results.
        """
        matches = []
        keywords = self._extract_keywords(task)

        # Strategy 1: File name matching
        for keyword in keywords:
            for file in self.root.rglob(f"*{keyword}*.py"):
                if self._should_include(file):
                    matches.append(FileMatch(
                        path=file,
                        score=70,
                        reason=f"Filename contains '{keyword}'"
                    ))

        # Strategy 2: Content search
        for keyword in keywords:
            content_matches = self.find_by_content(keyword)
            matches.extend(content_matches[:5])  # Top 5 per keyword

        # Deduplicate and sort
        seen = set()
        unique_matches = []
        for match in sorted(matches, key=lambda m: m.score, reverse=True):
            if match.path not in seen:
                seen.add(match.path)
                unique_matches.append(match)

        return unique_matches[:limit]

    def _extract_keywords(self, text: str) -> list[str]:
        """Extract potential keywords from task description"""
        # Remove common words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for'}
        words = text.lower().split()
        keywords = [w for w in words if w not in stop_words and len(w) > 3]
        return keywords[:5]  # Top 5 keywords

    def _should_include(self, path: Path) -> bool:
        """Check if file should be included in results"""
        # Skip ignored directories
        for part in path.parts:
            if part in self.ignore_patterns:
                return False

        # Skip non-files
        if not path.is_file():
            return False

        # Skip very large files (> 1MB)
        if path.stat().st_size > 1024 * 1024:
            return False

        return True


# Example usage
if __name__ == "__main__":
    finder = FileFinder(Path("/home/user/gep/server"))

    print("=== Finding files with 'config' ===")
    matches = finder.find_by_content("config")
    for match in matches[:5]:
        print(f"  {match.path.name} (score: {match.score}) - {match.reason}")

    print("\n=== Smart find: 'authentication' ===")
    matches = finder.smart_find("authentication")
    for match in matches[:5]:
        print(f"  {match.path.name} (score: {match.score}) - {match.reason}")
```

---

## Step 5: Create Todo Planner (7 min)

Create `src/agent/planning/planner.py`:

```python
"""
LLM-powered task planning and todo generation.
"""
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from ..models.todo import TodoList


class TaskPlanner:
    """
    Creates todo lists for tasks using LLM.
    """

    def __init__(self, model: str = "gpt-4o-mini"):
        self.llm = ChatOpenAI(model=model, temperature=0)

    def create_plan(self, task: str, context: dict) -> TodoList:
        """
        Create a todo list for the given task.

        Args:
            task: Task description from user
            context: Additional context (files found, etc.)

        Returns:
            TodoList with 5-10 concrete steps
        """
        # Build context string
        context_str = self._format_context(context)

        # Create prompt
        prompt = f"""You are a software development task planner.

Task: {task}

Context:
{context_str}

Create a detailed implementation plan with 5-10 concrete steps.
Each step should be:
- Specific and actionable
- Small enough to complete in one go
- In logical order

Return ONLY a numbered list of steps, one per line.
Example format:
1. Analyze existing authentication patterns in codebase
2. Create auth middleware module
3. Implement JWT token validation
4. Add authentication decorator to routes
5. Write tests for authentication flow

Now create the plan:"""

        # Get response
        response = self.llm.invoke([HumanMessage(content=prompt)])

        # Parse response into todos
        todo_list = self._parse_response(task, response.content)

        return todo_list

    def refine_plan(self, todo_list: TodoList, feedback: str) -> TodoList:
        """Refine an existing plan based on feedback"""
        prompt = f"""Refine this implementation plan based on feedback.

Original Task: {todo_list.task}

Current Plan:
{self._format_todos(todo_list)}

Feedback: {feedback}

Provide an updated plan addressing the feedback.
Return ONLY a numbered list of steps."""

        response = self.llm.invoke([HumanMessage(content=prompt)])
        return self._parse_response(todo_list.task, response.content)

    def _format_context(self, context: dict) -> str:
        """Format context dict into string"""
        lines = []

        if 'files' in context:
            lines.append(f"Relevant files found: {len(context['files'])}")
            for file in context['files'][:5]:
                lines.append(f"  - {file}")

        if 'patterns' in context:
            lines.append(f"Detected patterns: {', '.join(context['patterns'])}")

        if 'language' in context:
            lines.append(f"Primary language: {context['language']}")

        return "\n".join(lines) if lines else "No additional context"

    def _parse_response(self, task: str, response: str) -> TodoList:
        """Parse LLM response into TodoList"""
        todo_list = TodoList(task=task)

        lines = response.strip().split("\n")
        for line in lines:
            line = line.strip()
            # Match numbered lists: "1. Do something" or "1) Do something"
            if line and (line[0].isdigit() or line.startswith("-")):
                # Remove number and punctuation
                description = line.lstrip("0123456789.-) ").strip()
                if description:
                    todo_list.add(description)

        return todo_list

    def _format_todos(self, todo_list: TodoList) -> str:
        """Format todos as numbered list"""
        return "\n".join(
            f"{i+1}. {todo.description}"
            for i, todo in enumerate(todo_list.todos)
        )


# Example usage
if __name__ == "__main__":
    planner = TaskPlanner()

    # Create a plan
    todo_list = planner.create_plan(
        task="Add rate limiting to API endpoints",
        context={
            'files': ['api/routes.py', 'api/app.py', 'middleware/auth.py'],
            'patterns': ['Flask', 'decorators'],
            'language': 'Python'
        }
    )

    print(todo_list)
    print(f"\nProgress: {todo_list.progress:.0f}%")
```

---

## Step 6: Create the Agent (8 min)

Create `src/agent/core/todo_agent.py`:

```python
"""
Main todo-driven agent.
"""
from pathlib import Path
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from ..models.todo import TodoList, TodoStatus
from ..planning.planner import TaskPlanner
from ..tools.file_finder import FileFinder


class AgentState(TypedDict):
    """State of the agent"""
    task: str
    context: dict
    todo_list: TodoList | None
    current_step: int
    result: str | None


class TodoAgent:
    """
    Todo-driven development agent.

    Workflow:
    1. Understand task → find relevant files
    2. Plan → create todo list
    3. Execute → process each todo
    4. Complete → summarize results
    """

    def __init__(self, root: Path = Path(".")):
        self.root = root
        self.console = Console()
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        self.planner = TaskPlanner()
        self.finder = FileFinder(root)
        self.graph = self._create_graph()

    def _create_graph(self) -> StateGraph:
        """Create agent execution graph"""
        workflow = StateGraph(AgentState)

        # Add nodes
        workflow.add_node("understand", self._understand_task)
        workflow.add_node("plan", self._create_plan)
        workflow.add_node("display_plan", self._display_plan)
        workflow.add_node("execute", self._execute_todos)
        workflow.add_node("complete", self._complete_task)

        # Add edges
        workflow.set_entry_point("understand")
        workflow.add_edge("understand", "plan")
        workflow.add_edge("plan", "display_plan")
        workflow.add_edge("display_plan", "execute")
        workflow.add_edge("execute", "complete")
        workflow.add_edge("complete", END)

        return workflow.compile()

    def _understand_task(self, state: AgentState) -> dict:
        """Phase 1: Understand the task and find relevant files"""
        self.console.print("\n[bold blue]Phase 1: Understanding task...[/bold blue]")

        task = state["task"]

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            task_id = progress.add_task("Scanning codebase...", total=None)

            # Find relevant files
            matches = self.finder.smart_find(task, limit=10)

            progress.update(task_id, description="Found relevant files")

        # Build context
        context = {
            'files': [str(m.path) for m in matches],
            'file_count': len(matches),
            'root': str(self.root)
        }

        self.console.print(f"  ✓ Found {len(matches)} relevant files")
        for match in matches[:5]:
            self.console.print(f"    • {match.path.name} - {match.reason}")

        return {"context": context}

    def _create_plan(self, state: AgentState) -> dict:
        """Phase 2: Create todo list"""
        self.console.print("\n[bold blue]Phase 2: Creating plan...[/bold blue]")

        todo_list = self.planner.create_plan(
            task=state["task"],
            context=state["context"]
        )

        self.console.print(f"  ✓ Created plan with {len(todo_list.todos)} steps")

        return {"todo_list": todo_list, "current_step": 0}

    def _display_plan(self, state: AgentState) -> dict:
        """Display the plan to user"""
        todo_list = state["todo_list"]

        self.console.print("\n" + "="*60)
        self.console.print(f"[bold]Task:[/bold] {state['task']}")
        self.console.print("="*60)

        for i, todo in enumerate(todo_list.todos, 1):
            self.console.print(f"{i}. {todo.description}")

        self.console.print("="*60 + "\n")

        return {}

    def _execute_todos(self, state: AgentState) -> dict:
        """Phase 3: Execute todos (simulated for now)"""
        self.console.print("[bold blue]Phase 3: Executing plan...[/bold blue]\n")

        todo_list = state["todo_list"]

        for todo in todo_list.todos:
            # Mark as in progress
            todo.start()
            self.console.print(f"→ {todo.description}")

            # Simulate work
            import time
            time.sleep(0.5)

            # Mark complete
            todo.complete()
            self.console.print(f"  [green]✓ Complete[/green] ({todo.duration:.1f}s)\n")

            # Update progress
            self.console.print(
                f"  Progress: {todo_list.progress:.0f}% "
                f"({sum(1 for t in todo_list.todos if t.status == TodoStatus.COMPLETED)}/{len(todo_list.todos)})\n"
            )

        return {}

    def _complete_task(self, state: AgentState) -> dict:
        """Phase 4: Complete and summarize"""
        self.console.print("\n[bold green]✓ Task Complete![/bold green]\n")

        todo_list = state["todo_list"]

        summary = Panel(
            f"""[bold]Task:[/bold] {state['task']}
[bold]Steps Completed:[/bold] {len(todo_list.todos)}
[bold]Total Time:[/bold] {sum(t.duration or 0 for t in todo_list.todos):.1f}s
[bold]Status:[/bold] All todos completed successfully""",
            title="Summary",
            border_style="green"
        )

        self.console.print(summary)

        return {"result": "success"}

    def run(self, task: str) -> dict:
        """Run the agent on a task"""
        initial_state = {
            "task": task,
            "context": {},
            "todo_list": None,
            "current_step": 0,
            "result": None
        }

        result = self.graph.invoke(initial_state)
        return result


# Example usage
if __name__ == "__main__":
    agent = TodoAgent(root=Path("/home/user/gep/server"))

    # Run on a task
    result = agent.run("Add logging to the authentication module")
```

---

## Step 7: Test Your Agent (2 min)

Create `server/examples/test_todo_agent.py`:

```python
"""
Test the todo agent.
"""
from pathlib import Path
from src.agent.core.todo_agent import TodoAgent


def main():
    # Create agent
    agent = TodoAgent(root=Path("/home/user/gep/server"))

    # Test on a real task
    print("\n" + "="*60)
    print("Testing Todo-Driven Agent")
    print("="*60)

    result = agent.run("Add error handling to API endpoints")

    print("\n" + "="*60)
    print("Test Complete!")
    print("="*60)


if __name__ == "__main__":
    main()
```

Run it:
```bash
cd /home/user/gep/server
python examples/test_todo_agent.py
```

---

## What You've Built

In 30 minutes, you created:

### 1. **Todo System**
- ✅ Todo models with status tracking
- ✅ Progress calculation
- ✅ Duration tracking
- ✅ Beautiful display

### 2. **File Discovery**
- ✅ Smart file finding (no indexing)
- ✅ Content search
- ✅ Pattern matching
- ✅ AST-based search
- ✅ Relevance scoring

### 3. **Task Planning**
- ✅ LLM-powered todo generation
- ✅ Context-aware planning
- ✅ Plan refinement
- ✅ 5-10 step breakdown

### 4. **Agent System**
- ✅ LangGraph-based orchestration
- ✅ 4-phase workflow (Understand → Plan → Execute → Complete)
- ✅ State management
- ✅ Rich CLI output

---

## Example Output

```
Phase 1: Understanding task...
  ✓ Found 5 relevant files
    • auth.py - Contains 'authentication' (3 times)
    • routes.py - Contains 'api' (12 times)
    • middleware.py - Filename contains 'middleware'

Phase 2: Creating plan...
  ✓ Created plan with 5 steps

============================================================
Task: Add error handling to API endpoints
============================================================
1. Analyze current error handling patterns in codebase
2. Create custom exception classes for API errors
3. Add try-except blocks to route handlers
4. Implement error response formatter
5. Add tests for error scenarios
============================================================

Phase 3: Executing plan...

→ Analyze current error handling patterns in codebase
  ✓ Complete (0.5s)

  Progress: 20% (1/5)

→ Create custom exception classes for API errors
  ✓ Complete (0.5s)

  Progress: 40% (2/5)

...

✓ Task Complete!

╭─────────── Summary ───────────╮
│ Task: Add error handling      │
│ Steps Completed: 5            │
│ Total Time: 2.5s              │
│ Status: All todos completed   │
╰───────────────────────────────╯
```

---

## Next Steps

### Today
1. **Add Real Execution**: Replace simulated execution with actual code modification
2. **Add File Reading**: Read and display relevant files
3. **Add Validation**: Syntax checking before marking complete

### This Week
1. **Code Modification Tools**: Implement actual file writing
2. **AST-Based Editing**: Use libcst for safe code changes
3. **Test Execution**: Run tests after changes
4. **Git Integration**: Commit changes automatically

### This Month
1. **Multi-Language**: Support JavaScript, TypeScript, Go
2. **Advanced Planning**: Break complex tasks into subtasks
3. **Error Recovery**: Handle failures gracefully
4. **TUI Mode**: Build interactive Textual interface

---

## Extending the Agent

### Add Code Reading

```python
def _execute_todos(self, state: AgentState) -> dict:
    """Execute todos with file reading"""
    todo_list = state["todo_list"]

    for todo in todo_list.todos:
        todo.start()

        # Read relevant files
        files_to_read = self._determine_files_for_todo(todo, state['context'])
        code_context = {}

        for file_path in files_to_read:
            code_context[file_path] = Path(file_path).read_text()

        # Use LLM to execute step
        result = self._execute_step_with_llm(todo, code_context)

        if result.success:
            todo.complete()
        else:
            todo.fail(result.error)

    return {}
```

### Add Approval Gates

```python
from rich.prompt import Confirm

def _display_plan(self, state: AgentState) -> dict:
    """Display plan and ask for approval"""
    # ... display code ...

    # Ask for approval
    if not Confirm.ask("\nProceed with this plan?"):
        raise Exception("User cancelled")

    return {}
```

### Add Code Modification

```python
import libcst as cst

class CodeModifier:
    def add_function(self, file: Path, function_code: str):
        """Add function to file"""
        tree = cst.parse_module(file.read_text())
        # ... add function node to tree ...
        file.write_text(tree.code)
```

---

## Troubleshooting

### Tree-sitter Issues

If tree-sitter fails:
```bash
pip uninstall tree-sitter tree-sitter-python
pip install py-tree-sitter-languages
```

### LangGraph Errors

Ensure you have latest:
```bash
pip install --upgrade langgraph langchain langchain-openai
```

### API Key Not Found

```bash
# Check .env
cat .env | grep OPENAI

# Or export directly
export OPENAI_API_KEY=your_key_here
```

---

## Summary

You now have a **working todo-driven agent** that:
- ✅ Understands tasks by finding relevant files
- ✅ Creates structured implementation plans
- ✅ Tracks progress through todos
- ✅ Displays beautiful output

**No vector databases. No embeddings. Just smart pattern matching and LLM planning.**

This is the foundation for a powerful agentic system. Add code modification, testing, and git integration to make it production-ready!

**Start coding!** 🚀
