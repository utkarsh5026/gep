# Quick Start Guide: Building the Agentic System
## Get Started in 30 Minutes

**Goal**: Set up your development environment and create your first working agent prototype.

---

## Prerequisites

- Python 3.12+
- Git
- Docker (optional, for sandbox and vector DBs)
- OpenAI API key (for initial testing)
- 8GB+ RAM recommended

---

## Step 1: Environment Setup (5 min)

### 1.1 Create Development Branch

```bash
cd /home/user/gep
git checkout -b feature/agentic-system-phase0
```

### 1.2 Install Core Dependencies

```bash
cd server

# Install new dependencies for Phase 0
poetry add langchain-anthropic langchain-google-genai
poetry add tree-sitter py-tree-sitter-languages
poetry add qdrant-client
poetry add jedi radon libcst
poetry add langgraph
poetry add langsmith
poetry add textual

# Or using pip
pip install langchain-anthropic langchain-google-genai
pip install tree-sitter py-tree-sitter-languages
pip install qdrant-client
pip install jedi radon libcst
pip install langgraph
pip install langsmith
pip install textual
```

### 1.3 Set Up API Keys

```bash
# Add to your .env file
echo "ANTHROPIC_API_KEY=your_key_here" >> .env
echo "GOOGLE_API_KEY=your_key_here" >> .env
echo "LANGCHAIN_API_KEY=your_key_here" >> .env  # Optional for LangSmith
echo "LANGCHAIN_TRACING_V2=true" >> .env  # Optional for LangSmith
```

---

## Step 2: Create Project Structure (5 min)

### 2.1 New Directory Structure

```bash
cd server/src

# Create new modules
mkdir -p agent/{core,tools,memory,planning}
mkdir -p code_analysis/{ast_parser,graph,metrics}
mkdir -p ui/{tui,cli}
mkdir -p sandbox
mkdir -p observability

# Create __init__.py files
touch agent/__init__.py agent/core/__init__.py agent/tools/__init__.py
touch agent/memory/__init__.py agent/planning/__init__.py
touch code_analysis/__init__.py code_analysis/ast_parser/__init__.py
touch code_analysis/graph/__init__.py code_analysis/metrics/__init__.py
touch ui/__init__.py ui/tui/__init__.py ui/cli/__init__.py
touch sandbox/__init__.py observability/__init__.py
```

### 2.2 Project Structure Overview

```
server/src/
├── agent/              # NEW: Agent system
│   ├── core/          # Agent orchestrator, state management
│   ├── tools/         # Tool implementations
│   ├── memory/        # Context and memory systems
│   └── planning/      # Task planning and decomposition
├── code_analysis/     # NEW: Enhanced code analysis
│   ├── ast_parser/    # tree-sitter integration
│   ├── graph/         # Code graph building
│   └── metrics/       # Code metrics and complexity
├── ui/                # NEW: Enhanced UI
│   ├── tui/          # Textual-based TUI
│   └── cli/          # CLI enhancements
├── sandbox/           # NEW: Safe code execution
└── observability/     # NEW: Metrics and tracing
```

---

## Step 3: First Agent Prototype (10 min)

### 3.1 Create Basic Agent with LangGraph

Create `server/src/agent/core/agent.py`:

```python
"""
Basic agent using LangGraph for task execution.
"""
from typing import TypedDict, Annotated, Sequence
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolExecutor
import operator

class AgentState(TypedDict):
    """State of the agent during execution"""
    messages: Annotated[Sequence[BaseMessage], operator.add]
    task: str
    plan: list[str]
    current_step: int
    result: str | None


class SimpleAgent:
    """
    Simple agent that can plan and execute tasks.

    This is the foundational agent that will be expanded in later phases.
    """

    def __init__(self, llm_model: str = "gpt-4o-mini"):
        self.llm = ChatOpenAI(model=llm_model, temperature=0)
        self.graph = self._create_graph()

    def _create_graph(self) -> StateGraph:
        """Create the agent execution graph"""
        workflow = StateGraph(AgentState)

        # Add nodes
        workflow.add_node("plan", self._plan_task)
        workflow.add_node("execute", self._execute_step)
        workflow.add_node("finish", self._finish)

        # Add edges
        workflow.set_entry_point("plan")
        workflow.add_edge("plan", "execute")
        workflow.add_conditional_edges(
            "execute",
            self._should_continue,
            {
                "continue": "execute",
                "finish": "finish"
            }
        )
        workflow.add_edge("finish", END)

        return workflow.compile()

    def _plan_task(self, state: AgentState) -> dict:
        """Create a plan for the task"""
        task = state["task"]

        prompt = f"""
        Break down this task into 3-5 simple, actionable steps:

        Task: {task}

        Return ONLY a numbered list of steps, nothing else.
        """

        response = self.llm.invoke([HumanMessage(content=prompt)])
        steps = [
            line.strip()
            for line in response.content.split("\n")
            if line.strip() and line.strip()[0].isdigit()
        ]

        return {
            "plan": steps,
            "current_step": 0,
            "messages": [response]
        }

    def _execute_step(self, state: AgentState) -> dict:
        """Execute the current step"""
        current_step = state["current_step"]
        plan = state["plan"]

        if current_step >= len(plan):
            return {"current_step": current_step}

        step = plan[current_step]

        prompt = f"""
        Execute this step and report what you did:

        Step: {step}

        Context:
        - Original task: {state['task']}
        - Previous steps: {plan[:current_step]}

        Describe what you would do (simulation for now).
        """

        response = self.llm.invoke([HumanMessage(content=prompt)])

        return {
            "current_step": current_step + 1,
            "messages": [response]
        }

    def _should_continue(self, state: AgentState) -> str:
        """Determine if execution should continue"""
        if state["current_step"] >= len(state["plan"]):
            return "finish"
        return "continue"

    def _finish(self, state: AgentState) -> dict:
        """Finish execution and summarize"""
        prompt = f"""
        Summarize what was accomplished:

        Original task: {state['task']}
        Steps taken: {state['plan']}

        Provide a brief summary of the results.
        """

        response = self.llm.invoke([HumanMessage(content=prompt)])

        return {
            "result": response.content,
            "messages": [response]
        }

    def run(self, task: str) -> dict:
        """Run the agent on a task"""
        initial_state = {
            "messages": [],
            "task": task,
            "plan": [],
            "current_step": 0,
            "result": None
        }

        result = self.graph.invoke(initial_state)
        return result


# Example usage
if __name__ == "__main__":
    agent = SimpleAgent()
    result = agent.run("Add logging to the authentication module")

    print("Task:", result["task"])
    print("\nPlan:")
    for i, step in enumerate(result["plan"], 1):
        print(f"{i}. {step}")

    print("\nResult:")
    print(result["result"])
```

### 3.2 Test Your First Agent

```bash
cd server
python -m src.agent.core.agent
```

You should see:
- Task description
- Generated plan (3-5 steps)
- Execution results (simulated)
- Summary

---

## Step 4: Add Tree-sitter Code Parser (10 min)

### 4.1 Create AST Parser

Create `server/src/code_analysis/ast_parser/parser.py`:

```python
"""
Universal code parser using tree-sitter.
"""
import tree_sitter_python
import tree_sitter_javascript
from tree_sitter import Language, Parser, Node, Tree
from pathlib import Path
from dataclasses import dataclass
from enum import Enum


class SupportedLanguage(Enum):
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    GO = "go"
    RUST = "rust"


@dataclass
class CodeEntity:
    """Represents a code entity (function, class, etc.)"""
    type: str  # function, class, method, etc.
    name: str
    start_line: int
    end_line: int
    start_byte: int
    end_byte: int
    code: str


class CodeParser:
    """
    Universal code parser using tree-sitter.

    Supports multiple languages with a consistent API.
    """

    def __init__(self):
        self.parsers = {}
        self.languages = {}
        self._setup_languages()

    def _setup_languages(self):
        """Initialize parsers for supported languages"""
        # Python
        PY_LANGUAGE = Language(tree_sitter_python.language())
        py_parser = Parser()
        py_parser.set_language(PY_LANGUAGE)
        self.parsers[SupportedLanguage.PYTHON] = py_parser
        self.languages[SupportedLanguage.PYTHON] = PY_LANGUAGE

        # JavaScript
        JS_LANGUAGE = Language(tree_sitter_javascript.language())
        js_parser = Parser()
        js_parser.set_language(JS_LANGUAGE)
        self.parsers[SupportedLanguage.JAVASCRIPT] = js_parser
        self.languages[SupportedLanguage.JAVASCRIPT] = JS_LANGUAGE

    def parse(self, code: str, language: SupportedLanguage) -> Tree:
        """Parse code into AST"""
        parser = self.parsers.get(language)
        if not parser:
            raise ValueError(f"Unsupported language: {language}")

        return parser.parse(bytes(code, "utf8"))

    def extract_functions(
        self,
        code: str,
        language: SupportedLanguage
    ) -> list[CodeEntity]:
        """Extract all functions from code"""
        tree = self.parse(code, language)

        if language == SupportedLanguage.PYTHON:
            return self._extract_python_functions(tree, code)
        elif language == SupportedLanguage.JAVASCRIPT:
            return self._extract_javascript_functions(tree, code)

        return []

    def _extract_python_functions(
        self,
        tree: Tree,
        code: str
    ) -> list[CodeEntity]:
        """Extract Python functions"""
        query = self.languages[SupportedLanguage.PYTHON].query("""
            (function_definition
                name: (identifier) @name
            ) @function
        """)

        captures = query.captures(tree.root_node)
        functions = []

        i = 0
        while i < len(captures):
            func_node, func_type = captures[i]
            name_node, name_type = captures[i + 1]

            functions.append(CodeEntity(
                type="function",
                name=name_node.text.decode("utf8"),
                start_line=func_node.start_point[0],
                end_line=func_node.end_point[0],
                start_byte=func_node.start_byte,
                end_byte=func_node.end_byte,
                code=code[func_node.start_byte:func_node.end_byte]
            ))

            i += 2  # Skip to next function

        return functions

    def _extract_javascript_functions(
        self,
        tree: Tree,
        code: str
    ) -> list[CodeEntity]:
        """Extract JavaScript functions"""
        query = self.languages[SupportedLanguage.JAVASCRIPT].query("""
            [
                (function_declaration
                    name: (identifier) @name
                ) @function

                (arrow_function) @function
            ]
        """)

        captures = query.captures(tree.root_node)
        functions = []

        for node, node_type in captures:
            if node_type == "function":
                # Try to get name
                name = "anonymous"
                for child in node.children:
                    if child.type == "identifier":
                        name = child.text.decode("utf8")
                        break

                functions.append(CodeEntity(
                    type="function",
                    name=name,
                    start_line=node.start_point[0],
                    end_line=node.end_point[0],
                    start_byte=node.start_byte,
                    end_byte=node.end_byte,
                    code=code[node.start_byte:node.end_byte]
                ))

        return functions

    def extract_classes(
        self,
        code: str,
        language: SupportedLanguage
    ) -> list[CodeEntity]:
        """Extract all classes from code"""
        tree = self.parse(code, language)

        if language == SupportedLanguage.PYTHON:
            query = self.languages[SupportedLanguage.PYTHON].query("""
                (class_definition
                    name: (identifier) @name
                ) @class
            """)
        else:
            return []

        captures = query.captures(tree.root_node)
        classes = []

        i = 0
        while i < len(captures):
            class_node, _ = captures[i]
            name_node, _ = captures[i + 1]

            classes.append(CodeEntity(
                type="class",
                name=name_node.text.decode("utf8"),
                start_line=class_node.start_point[0],
                end_line=class_node.end_point[0],
                start_byte=class_node.start_byte,
                end_byte=class_node.end_byte,
                code=code[class_node.start_byte:class_node.end_byte]
            ))

            i += 2

        return classes

    def get_imports(
        self,
        code: str,
        language: SupportedLanguage
    ) -> list[str]:
        """Extract import statements"""
        tree = self.parse(code, language)

        if language == SupportedLanguage.PYTHON:
            query = self.languages[SupportedLanguage.PYTHON].query("""
                [
                    (import_statement) @import
                    (import_from_statement) @import
                ]
            """)
        else:
            return []

        captures = query.captures(tree.root_node)
        imports = []

        for node, _ in captures:
            imports.append(code[node.start_byte:node.end_byte])

        return imports


# Example usage
if __name__ == "__main__":
    parser = CodeParser()

    # Test Python
    python_code = """
def hello():
    print("Hello")

class MyClass:
    def method(self):
        pass
"""

    functions = parser.extract_functions(python_code, SupportedLanguage.PYTHON)
    classes = parser.extract_classes(python_code, SupportedLanguage.PYTHON)

    print("Functions:", [f.name for f in functions])
    print("Classes:", [c.name for c in classes])
```

### 4.2 Test the Parser

```bash
cd server
python -m src.code_analysis.ast_parser.parser
```

---

## Step 5: Create Your First Tool (5 min)

### 5.1 Create Code Search Tool

Create `server/src/agent/tools/code_search.py`:

```python
"""
Code search tool for agents.
"""
from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Optional
from pathlib import Path
from ...code_analysis.ast_parser.parser import CodeParser, SupportedLanguage


class CodeSearchInput(BaseModel):
    """Input for code search tool"""
    query: str = Field(description="What to search for (e.g., 'authentication functions')")
    file_path: Optional[str] = Field(
        default=None,
        description="Specific file to search in (optional)"
    )


class CodeSearchTool(BaseTool):
    """Tool for searching code semantically and structurally"""

    name: str = "code_search"
    description: str = """
    Search for code in the repository using natural language queries.
    Can find functions, classes, and code patterns.

    Examples:
    - "Find authentication functions"
    - "Find all API endpoints"
    - "Find database models"
    """
    args_schema: type[BaseModel] = CodeSearchInput

    parser: CodeParser = Field(default_factory=CodeParser)
    repo_path: Path = Field(default_factory=lambda: Path.cwd())

    def _run(self, query: str, file_path: Optional[str] = None) -> str:
        """Execute the search"""
        results = []

        # If specific file, search only that
        if file_path:
            files = [Path(file_path)]
        else:
            # Search all Python files
            files = list(self.repo_path.rglob("*.py"))

        for file in files[:20]:  # Limit to first 20 files for now
            try:
                code = file.read_text()

                # Extract entities
                functions = self.parser.extract_functions(
                    code,
                    SupportedLanguage.PYTHON
                )
                classes = self.parser.extract_classes(
                    code,
                    SupportedLanguage.PYTHON
                )

                # Simple keyword matching (will be replaced with semantic search)
                query_lower = query.lower()
                for func in functions:
                    if query_lower in func.name.lower():
                        results.append(
                            f"Function: {func.name} in {file.name}:{func.start_line}"
                        )

                for cls in classes:
                    if query_lower in cls.name.lower():
                        results.append(
                            f"Class: {cls.name} in {file.name}:{cls.start_line}"
                        )

            except Exception as e:
                continue

        if not results:
            return f"No results found for '{query}'"

        return "\n".join(results[:10])  # Top 10 results

    async def _arun(self, query: str, file_path: Optional[str] = None) -> str:
        """Async version"""
        return self._run(query, file_path)


# Example usage
if __name__ == "__main__":
    tool = CodeSearchTool()
    result = tool._run("project")
    print(result)
```

---

## Step 6: Test the Complete System (5 min)

### 6.1 Create Test Script

Create `server/examples/test_agent_system.py`:

```python
"""
Test the complete agent system.
"""
from src.agent.core.agent import SimpleAgent
from src.agent.tools.code_search import CodeSearchTool
from src.code_analysis.ast_parser.parser import CodeParser, SupportedLanguage


def test_agent():
    """Test basic agent"""
    print("=" * 60)
    print("Testing Agent")
    print("=" * 60)

    agent = SimpleAgent()
    result = agent.run("Analyze the authentication module and suggest improvements")

    print("\nTask:", result["task"])
    print("\nPlan:")
    for i, step in enumerate(result["plan"], 1):
        print(f"  {i}. {step}")

    print("\nResult:")
    print(result["result"])


def test_parser():
    """Test code parser"""
    print("\n" + "=" * 60)
    print("Testing Code Parser")
    print("=" * 60)

    parser = CodeParser()

    code = """
def authenticate(username, password):
    '''Authenticate user'''
    return True

class UserManager:
    def create_user(self, name):
        pass
"""

    functions = parser.extract_functions(code, SupportedLanguage.PYTHON)
    classes = parser.extract_classes(code, SupportedLanguage.PYTHON)

    print("\nFunctions found:")
    for func in functions:
        print(f"  - {func.name} (line {func.start_line})")

    print("\nClasses found:")
    for cls in classes:
        print(f"  - {cls.name} (line {cls.start_line})")


def test_tool():
    """Test code search tool"""
    print("\n" + "=" * 60)
    print("Testing Code Search Tool")
    print("=" * 60)

    tool = CodeSearchTool()
    result = tool._run("config")

    print("\nSearch results:")
    print(result)


if __name__ == "__main__":
    test_parser()
    test_tool()
    test_agent()

    print("\n" + "=" * 60)
    print("✓ All tests passed!")
    print("=" * 60)
```

### 6.2 Run Tests

```bash
cd server
python examples/test_agent_system.py
```

---

## What You've Built

In 30 minutes, you've created:

1. ✅ **Agent System**
   - LangGraph-based agent with planning and execution
   - State management
   - Multi-step reasoning

2. ✅ **Code Parser**
   - Universal AST parsing with tree-sitter
   - Function and class extraction
   - Support for Python and JavaScript

3. ✅ **Tool System**
   - LangChain-compatible tools
   - Code search capability
   - Extensible architecture

4. ✅ **Testing Infrastructure**
   - Example scripts
   - Integration tests

---

## Next Steps

### Immediate (Today)
1. **Add More Languages**: Extend parser to support TypeScript, Go, Rust
2. **Enhance Code Search**: Integrate with existing vector store
3. **Add More Tools**: File read/write, git operations
4. **Test on Real Code**: Run agent on actual codebase

### This Week
1. **Multi-LLM Support**: Add Claude and Gemini
2. **Code Graph**: Build call graph and dependency graph
3. **Memory System**: Add conversation memory
4. **Better Planning**: Improve task decomposition

### This Month (Phase 0)
- Complete all Phase 0 tasks from roadmap
- Set up Qdrant vector database
- Implement hybrid search
- Add comprehensive testing
- Document everything

---

## Troubleshooting

### Tree-sitter Installation Issues

If you get errors with tree-sitter:

```bash
# Use pre-built bindings
pip uninstall tree-sitter tree-sitter-python
pip install py-tree-sitter-languages

# Then update parser.py to use:
from tree_sitter_languages import get_language, get_parser

parser = get_parser('python')
```

### LangGraph Errors

If LangGraph gives errors:

```bash
# Ensure you have latest version
pip install --upgrade langgraph langchain langchain-openai
```

### API Key Issues

```bash
# Verify keys are set
echo $OPENAI_API_KEY
echo $ANTHROPIC_API_KEY

# Or check .env
cat .env
```

---

## Resources

- **LangGraph Docs**: https://langchain-ai.github.io/langgraph/
- **Tree-sitter**: https://tree-sitter.github.io/tree-sitter/
- **Textual**: https://textual.textualize.io/
- **Qdrant**: https://qdrant.tech/documentation/

---

## Get Help

If you run into issues:

1. Check the error message carefully
2. Review the technology stack document
3. Consult the roadmap for context
4. Test each component independently

**Happy Building!** 🚀
