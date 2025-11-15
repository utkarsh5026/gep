# Technology Stack Deep Dive
## Detailed Analysis and Recommendations for GEP Agentic System

**Version:** 1.0
**Date:** 2025-11-15

---

## Table of Contents
1. [Agent Frameworks](#agent-frameworks)
2. [LLM Providers](#llm-providers)
3. [Code Analysis Tools](#code-analysis-tools)
4. [Vector Databases](#vector-databases)
5. [Graph Databases](#graph-databases)
6. [UI Frameworks](#ui-frameworks)
7. [Testing & Sandbox](#testing--sandbox)
8. [Observability](#observability)

---

## Agent Frameworks

### Options Comparison

| Framework | Pros | Cons | Best For | Recommendation |
|-----------|------|------|----------|----------------|
| **LangGraph** | State-based, flexible, visualization, human-in-loop | Learning curve, newer | Complex multi-step workflows | ⭐ **PRIMARY** |
| **LangChain Agents** | Mature, many integrations, good docs | Can be opinionated, complex | Quick prototypes | **SECONDARY** |
| **AutoGPT** | Full autonomy, good examples | Less control, resource-intensive | Inspiration only | Research only |
| **CrewAI** | Multi-agent, role-based | Heavy abstraction, less flexible | Multi-agent scenarios | **CONSIDER** |
| **Custom** | Full control, lightweight | Build everything, more time | Specific use cases | **FALLBACK** |

### Recommendation: **LangGraph + LangChain**

**Why LangGraph?**
```python
# LangGraph allows explicit state management
from langgraph.graph import StateGraph, END

class AgentState(TypedDict):
    task: str
    plan: list[str]
    current_step: int
    code_changes: dict
    test_results: dict
    human_feedback: str | None

workflow = StateGraph(AgentState)

# Define nodes (actions)
workflow.add_node("analyze", analyze_task)
workflow.add_node("plan", create_plan)
workflow.add_node("execute", execute_step)
workflow.add_node("validate", validate_changes)
workflow.add_node("human_review", get_human_approval)

# Define edges (flow)
workflow.add_edge("analyze", "plan")
workflow.add_edge("plan", "execute")
workflow.add_conditional_edges(
    "execute",
    should_validate,
    {
        "validate": "validate",
        "continue": "execute",
        "done": END
    }
)
workflow.add_conditional_edges(
    "validate",
    needs_human_review,
    {
        "approve": "execute",
        "review": "human_review",
        "retry": "execute"
    }
)

# Compile and run
app = workflow.compile()
result = app.invoke({"task": "Add authentication"})
```

**Benefits**:
- **Explicit State**: Every step's state is tracked
- **Visualization**: Auto-generate flowcharts
- **Checkpoints**: Save/restore at any step
- **Human-in-Loop**: Built-in approval gates
- **Debugging**: Inspect state at each node

**Use LangChain For**:
- Tool definitions and management
- Memory systems
- LLM wrappers and callbacks
- Retrieval-augmented generation
- Prompt templates

---

## LLM Providers

### Provider Comparison

| Provider | Models | Strengths | Cost (1M tokens) | Function Calling | Context Window |
|----------|--------|-----------|------------------|------------------|----------------|
| **OpenAI** | GPT-4o, GPT-4o-mini | Best all-around, reliable | $2.50/$10 | ⭐ Excellent | 128k |
| **Anthropic** | Claude 3.5 Sonnet/Opus | Long context, reasoning | $3/$15 | ⭐ Excellent | 200k |
| **Google** | Gemini 1.5 Pro/Flash | Fast, multimodal | $1.25/$3.50 | ✓ Good | 2M |
| **Cohere** | Command R+ | Multilingual, RAG | $3/$15 | ✓ Good | 128k |
| **Local (Ollama)** | Llama 3, CodeLlama | Free, private | $0 | ⚠️ Limited | 8-32k |

### Recommendation: **Multi-Provider Strategy**

```python
class LLMRouter:
    """Route tasks to optimal LLM based on requirements"""

    def select_provider(
        self,
        task_type: TaskType,
        context_size: int,
        budget: Budget,
        privacy: Privacy
    ) -> LLMProvider:
        # Privacy-sensitive: Use local
        if privacy == Privacy.HIGH:
            return OllamaProvider("codellama")

        # Large context: Use Gemini or Claude
        if context_size > 100_000:
            if budget == Budget.LOW:
                return GeminiProvider("gemini-1.5-flash")
            return ClaudeProvider("claude-3.5-sonnet")

        # Code generation: Use GPT-4o or Claude
        if task_type == TaskType.CODE_GENERATION:
            if budget == Budget.HIGH:
                return ClaudeProvider("claude-3-opus")
            return OpenAIProvider("gpt-4o")

        # Planning/reasoning: Use Claude or GPT-4o
        if task_type == TaskType.PLANNING:
            return ClaudeProvider("claude-3.5-sonnet")

        # Quick queries: Use fast models
        if task_type == TaskType.SIMPLE_QUERY:
            return OpenAIProvider("gpt-4o-mini")

        # Default: GPT-4o (best balance)
        return OpenAIProvider("gpt-4o")
```

**Strategy**:
1. **Primary**: OpenAI GPT-4o (best all-around performance)
2. **Complex Reasoning**: Claude 3.5 Sonnet (superior reasoning)
3. **Large Context**: Gemini 1.5 Pro (2M context window)
4. **Cost-Sensitive**: GPT-4o-mini or Gemini Flash
5. **Privacy-Sensitive**: Ollama with Llama 3 or CodeLlama
6. **Specialized Code**: CodeLlama or StarCoder

**Implementation**:
```toml
# config.toml
[llm]
primary = "openai:gpt-4o"
fallback = ["anthropic:claude-3.5-sonnet", "google:gemini-1.5-pro"]

[llm.routing]
planning = "anthropic:claude-3.5-sonnet"
code_generation = "openai:gpt-4o"
code_review = "anthropic:claude-3.5-sonnet"
quick_query = "openai:gpt-4o-mini"
documentation = "google:gemini-1.5-flash"
refactoring = "openai:gpt-4o"

[llm.local]
enabled = true
models = ["codellama:13b", "llama3:8b"]
use_for = ["privacy_mode", "offline_mode"]
```

---

## Code Analysis Tools

### AST Parsing

| Tool | Languages | Performance | Ease of Use | Recommendation |
|------|-----------|-------------|-------------|----------------|
| **tree-sitter** | 50+ | ⭐⭐⭐ Very Fast | ⭐⭐ Moderate | ⭐ **PRIMARY** |
| **srcML** | C/C++/Java/C# | ⭐⭐ Fast | ⭐ Complex | Specific langs |
| **Language-specific** | 1 each | ⭐⭐⭐ Fast | ⭐⭐⭐ Easy | Python only |

### Recommendation: **tree-sitter**

**Why tree-sitter?**
- **Universal**: 50+ languages with consistent API
- **Incremental**: Fast re-parsing on edits
- **Error Recovery**: Parses incomplete code
- **Queries**: Powerful pattern matching

**Example Usage**:
```python
from tree_sitter import Language, Parser
import tree_sitter_python
import tree_sitter_javascript

class UniversalCodeParser:
    def __init__(self):
        self.parsers = {
            'python': self._create_parser(tree_sitter_python.language()),
            'javascript': self._create_parser(tree_sitter_javascript.language()),
            # Add more languages...
        }

    def _create_parser(self, language):
        parser = Parser()
        parser.set_language(language)
        return parser

    def parse(self, code: str, language: str) -> Tree:
        """Parse code into AST"""
        return self.parsers[language].parse(bytes(code, 'utf8'))

    def query(self, tree: Tree, pattern: str, language: str) -> list:
        """Query AST with S-expression pattern"""
        query = Language.query(self.parsers[language].language, pattern)
        return query.captures(tree.root_node)

# Example: Find all function definitions
parser = UniversalCodeParser()
tree = parser.parse(python_code, 'python')
functions = parser.query(tree, """
    (function_definition
        name: (identifier) @func_name
        parameters: (parameters) @params
        body: (block) @body)
""", 'python')
```

**Additional Tools**:

1. **Python-Specific**: `jedi` for completions and analysis
```python
import jedi

# Get completions
script = jedi.Script("import os\nos.", path="example.py")
completions = script.complete(1, 10)

# Get definitions
script = jedi.Script("from flask import Flask\nFlask", path="app.py")
definitions = script.goto(2, 0)
```

2. **Code Complexity**: `radon`
```python
from radon.complexity import cc_visit
from radon.metrics import mi_visit

complexity = cc_visit(code)  # Cyclomatic complexity
maintainability = mi_visit(code, multi=True)  # Maintainability index
```

3. **Python Refactoring**: `rope` or `libcst`
```python
import libcst as cst

# Transform code
class AddLoggingTransformer(cst.CSTTransformer):
    def leave_FunctionDef(self, original_node, updated_node):
        # Add logging to every function
        logging_stmt = cst.parse_statement('logger.info(f"Calling {__name__}")')
        new_body = [logging_stmt] + list(updated_node.body.body)
        return updated_node.with_changes(
            body=updated_node.body.with_changes(body=new_body)
        )

tree = cst.parse_module(code)
transformed = tree.visit(AddLoggingTransformer())
```

---

## Vector Databases

### Comparison

| Database | Type | Performance | Features | Cost | Recommendation |
|----------|------|-------------|----------|------|----------------|
| **FAISS** | Local | ⭐⭐⭐ | Basic, fast | Free | ⭐ Small projects |
| **Qdrant** | Server/Local | ⭐⭐⭐ | Rich filtering, hybrid | Free/Paid | ⭐ **PRIMARY** |
| **Chroma** | Local/Server | ⭐⭐ | Simple API, metadata | Free | **SECONDARY** |
| **Weaviate** | Server | ⭐⭐ | GraphQL, multimodal | Free/Paid | Enterprise |
| **Pinecone** | Cloud | ⭐⭐⭐ | Managed, scalable | Paid | Production |

### Recommendation: **Qdrant + FAISS**

**Use Qdrant for**:
- Projects with >10k files
- Complex metadata filtering
- Hybrid search (semantic + keyword)
- Multi-tenant scenarios

**Use FAISS for**:
- Small projects (<10k files)
- Offline/embedded use
- Maximum speed
- Simple use cases

**Qdrant Example**:
```python
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
)

class QdrantCodeStore:
    def __init__(self, path: str = "./qdrant_db"):
        self.client = QdrantClient(path=path)  # Local mode
        self._initialize_collections()

    def _initialize_collections(self):
        # Create collection for code chunks
        self.client.create_collection(
            collection_name="code_chunks",
            vectors_config=VectorParams(
                size=1536,  # OpenAI embedding size
                distance=Distance.COSINE
            )
        )

    def add_code(
        self,
        chunk_id: str,
        embedding: list[float],
        code: str,
        file_path: str,
        language: str,
        function_name: str | None = None,
        class_name: str | None = None,
        complexity: int | None = None
    ):
        """Add code chunk with rich metadata"""
        self.client.upsert(
            collection_name="code_chunks",
            points=[
                PointStruct(
                    id=chunk_id,
                    vector=embedding,
                    payload={
                        "code": code,
                        "file_path": file_path,
                        "language": language,
                        "function_name": function_name,
                        "class_name": class_name,
                        "complexity": complexity,
                        "lines": len(code.split('\n')),
                        "indexed_at": datetime.now().isoformat()
                    }
                )
            ]
        )

    def search(
        self,
        query_vector: list[float],
        language: str | None = None,
        max_complexity: int | None = None,
        limit: int = 10
    ) -> list:
        """Search with filters"""
        # Build filter
        filter_conditions = []
        if language:
            filter_conditions.append(
                FieldCondition(key="language", match=MatchValue(value=language))
            )
        if max_complexity:
            filter_conditions.append(
                FieldCondition(
                    key="complexity",
                    range={"lte": max_complexity}
                )
            )

        # Search
        results = self.client.search(
            collection_name="code_chunks",
            query_vector=query_vector,
            query_filter=Filter(must=filter_conditions) if filter_conditions else None,
            limit=limit
        )

        return results

# Usage
store = QdrantCodeStore()

# Add code
embedding = embed_model.embed("def authenticate(user, password):")
store.add_code(
    chunk_id="auth_py_123",
    embedding=embedding,
    code=auth_function_code,
    file_path="src/auth.py",
    language="python",
    function_name="authenticate",
    complexity=5
)

# Search with filters
query_embedding = embed_model.embed("how to authenticate users")
results = store.search(
    query_vector=query_embedding,
    language="python",
    max_complexity=10,
    limit=5
)
```

**Hybrid Search (Semantic + Keyword)**:
```python
from qdrant_client.models import SearchRequest, Filter, FieldCondition

class HybridSearch:
    def __init__(self, qdrant_client, bm25_index):
        self.qdrant = qdrant_client
        self.bm25 = bm25_index

    def search(
        self,
        query: str,
        semantic_weight: float = 0.7,
        keyword_weight: float = 0.3,
        limit: int = 10
    ) -> list:
        """Combine semantic and keyword search"""
        # Semantic search
        semantic_results = self.qdrant.search(
            collection_name="code_chunks",
            query_vector=self.embed(query),
            limit=limit * 2
        )

        # Keyword search
        keyword_results = self.bm25.search(query, limit=limit * 2)

        # Combine and re-rank
        combined = self._reciprocal_rank_fusion(
            semantic_results,
            keyword_results,
            semantic_weight,
            keyword_weight
        )

        return combined[:limit]
```

---

## Graph Databases

### Comparison

| Database | Type | Performance | Query Language | Use Case |
|----------|------|-------------|----------------|----------|
| **NetworkX** | In-memory | ⭐⭐⭐ Fast | Python API | ⭐ **PRIMARY** |
| **Neo4j** | Server | ⭐⭐ Good | Cypher | Large codebases |
| **SQLite** | File | ⭐⭐⭐ Fast | SQL | Simple relations |
| **TinkerGraph** | In-memory | ⭐⭐ Good | Gremlin | Graph algorithms |

### Recommendation: **NetworkX + SQLite**

**Use NetworkX for**:
- In-memory graph operations
- Quick analysis (centrality, paths, etc.)
- Graph algorithms
- Visualization

**Use SQLite for**:
- Persistent metadata
- Fast lookups
- Relational data

**Code Graph Example**:
```python
import networkx as nx
from dataclasses import dataclass
from enum import Enum

class EdgeType(Enum):
    CALLS = "calls"
    IMPORTS = "imports"
    INHERITS = "inherits"
    CONTAINS = "contains"
    REFERENCES = "references"

@dataclass
class CodeNode:
    id: str
    type: str  # file, class, function, variable
    name: str
    file_path: str
    start_line: int
    end_line: int
    language: str
    metadata: dict

class CodeGraph:
    def __init__(self):
        self.graph = nx.MultiDiGraph()

    def add_node(self, node: CodeNode):
        """Add code entity"""
        self.graph.add_node(
            node.id,
            type=node.type,
            name=node.name,
            file_path=node.file_path,
            start_line=node.start_line,
            end_line=node.end_line,
            language=node.language,
            **node.metadata
        )

    def add_edge(self, from_id: str, to_id: str, edge_type: EdgeType, **kwargs):
        """Add relationship"""
        self.graph.add_edge(from_id, to_id, type=edge_type.value, **kwargs)

    def get_call_graph(self, function_id: str, max_depth: int = 3) -> nx.DiGraph:
        """Get function call graph"""
        subgraph = nx.DiGraph()

        def traverse(node_id, depth):
            if depth > max_depth:
                return

            # Add node
            subgraph.add_node(node_id, **self.graph.nodes[node_id])

            # Add outgoing calls
            for _, target, edge_data in self.graph.out_edges(node_id, data=True):
                if edge_data.get('type') == EdgeType.CALLS.value:
                    subgraph.add_edge(node_id, target, **edge_data)
                    traverse(target, depth + 1)

        traverse(function_id, 0)
        return subgraph

    def find_dependencies(self, file_path: str) -> set[str]:
        """Find all files this file depends on"""
        file_nodes = [
            n for n, d in self.graph.nodes(data=True)
            if d['file_path'] == file_path
        ]

        dependencies = set()
        for node in file_nodes:
            for _, target, edge_data in self.graph.out_edges(node, data=True):
                if edge_data.get('type') in [EdgeType.IMPORTS.value, EdgeType.CALLS.value]:
                    target_file = self.graph.nodes[target]['file_path']
                    if target_file != file_path:
                        dependencies.add(target_file)

        return dependencies

    def get_entry_points(self) -> list[str]:
        """Find functions not called by anything (entry points)"""
        all_functions = [
            n for n, d in self.graph.nodes(data=True)
            if d['type'] == 'function'
        ]

        called_functions = set()
        for _, target, edge_data in self.graph.edges(data=True):
            if edge_data.get('type') == EdgeType.CALLS.value:
                called_functions.add(target)

        return [f for f in all_functions if f not in called_functions]

    def complexity_hotspots(self, threshold: int = 10) -> list[tuple]:
        """Find complex, highly-connected functions"""
        hotspots = []
        for node, data in self.graph.nodes(data=True):
            if data['type'] != 'function':
                continue

            complexity = data.get('complexity', 0)
            in_degree = self.graph.in_degree(node)  # How many call it
            out_degree = self.graph.out_degree(node)  # How many it calls

            if complexity >= threshold or in_degree + out_degree >= threshold:
                hotspots.append((
                    node,
                    data['name'],
                    complexity,
                    in_degree,
                    out_degree
                ))

        return sorted(hotspots, key=lambda x: x[2] * (x[3] + x[4]), reverse=True)

# Usage
graph = CodeGraph()

# Build graph from codebase
for file in repo.files:
    tree = parser.parse(file.content, file.language)

    # Add file node
    file_node = CodeNode(
        id=f"file:{file.path}",
        type="file",
        name=file.name,
        file_path=file.path,
        start_line=0,
        end_line=len(file.content.split('\n')),
        language=file.language,
        metadata={"size": len(file.content)}
    )
    graph.add_node(file_node)

    # Add functions
    for func in extract_functions(tree):
        func_node = CodeNode(
            id=f"func:{file.path}:{func.name}",
            type="function",
            name=func.name,
            file_path=file.path,
            start_line=func.start_line,
            end_line=func.end_line,
            language=file.language,
            metadata={"complexity": calculate_complexity(func)}
        )
        graph.add_node(func_node)
        graph.add_edge(file_node.id, func_node.id, EdgeType.CONTAINS)

        # Add calls
        for call in extract_calls(func):
            graph.add_edge(
                func_node.id,
                f"func:{call.file}:{call.name}",
                EdgeType.CALLS,
                line=call.line
            )

# Analyze
hotspots = graph.complexity_hotspots()
entry_points = graph.get_entry_points()
deps = graph.find_dependencies("src/api/auth.py")
```

---

## UI Frameworks

### Comparison

| Framework | Type | Features | Learning Curve | Use Case |
|-----------|------|----------|----------------|----------|
| **Textual** | TUI | Modern, reactive, CSS | ⭐⭐ Moderate | ⭐ **PRIMARY** |
| **Rich** | CLI | Beautiful output | ⭐⭐⭐ Easy | ✓ Already using |
| **prompt_toolkit** | TUI | Advanced input | ⭐⭐ Moderate | Dialogs |
| **Typer** | CLI | Click alternative | ⭐⭐⭐ Easy | Commands |
| **urwid** | TUI | Mature, flexible | ⭐ Hard | Legacy |

### Recommendation: **Textual + Rich + prompt_toolkit**

**Textual for Interactive Mode**:
```python
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static, Input, RichLog
from textual.containers import Container, Horizontal, Vertical
from textual.reactive import reactive

class GEPAgentTUI(App):
    """GEP Agent Terminal UI"""

    CSS = """
    #chat {
        width: 1fr;
        height: 1fr;
        border: solid blue;
    }

    #code-preview {
        width: 1fr;
        height: 1fr;
        border: solid green;
    }

    #logs {
        height: 10;
        border: solid yellow;
    }
    """

    task_status = reactive("Idle")

    def compose(self) -> ComposeResult:
        yield Header()

        with Horizontal():
            with Vertical(id="left-pane"):
                yield Static("Chat", id="chat-header")
                yield RichLog(id="chat")
                yield Input(placeholder="Enter your task...", id="input")

            with Vertical(id="right-pane"):
                yield Static("Code Preview", id="preview-header")
                yield RichLog(id="code-preview")

        yield RichLog(id="logs")
        yield Footer()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle user input"""
        chat = self.query_one("#chat", RichLog)
        chat.write(f"[bold blue]You:[/] {event.value}")

        # Process with agent
        self.run_agent(event.value)

    async def run_agent(self, task: str):
        """Run agent on task"""
        chat = self.query_one("#chat", RichLog)
        logs = self.query_one("#logs", RichLog)
        preview = self.query_one("#code-preview", RichLog)

        # Show thinking
        chat.write("[bold green]Agent:[/] Let me analyze that...")

        # Run agent (async)
        async for update in agent.stream_task(task):
            if update.type == "plan":
                chat.write(f"[bold]Plan:[/]\n{update.content}")
            elif update.type == "code":
                preview.write(update.content)
            elif update.type == "log":
                logs.write(update.content)
            elif update.type == "complete":
                chat.write("[bold green]✓[/] Task complete!")

# Run
app = GEPAgentTUI()
app.run()
```

**prompt_toolkit for Dialogs**:
```python
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.validation import Validator

# Auto-completion
command_completer = WordCompleter([
    'analyze', 'refactor', 'test', 'document', 'search'
], ignore_case=True)

user_input = prompt(
    'GEP> ',
    completer=command_completer,
    complete_while_typing=True
)

# Validation
class TaskValidator(Validator):
    def validate(self, document):
        if len(document.text) < 3:
            raise ValidationError(
                message='Task too short',
                cursor_position=len(document.text)
            )

task = prompt('Task: ', validator=TaskValidator())
```

---

## Testing & Sandbox

### Sandbox Options

| Option | Isolation | Performance | Setup | Recommendation |
|--------|-----------|-------------|-------|----------------|
| **Docker** | ⭐⭐⭐ | ⭐⭐ | ⭐⭐ | ⭐ **PRIMARY** |
| **pytest** | ⭐ | ⭐⭐⭐ | ⭐⭐⭐ | Testing only |
| **subprocess** | ⭐ | ⭐⭐⭐ | ⭐⭐⭐ | Light isolation |
| **pyodide** | ⭐⭐ | ⭐ | ⭐⭐ | Browser only |
| **VM** | ⭐⭐⭐ | ⭐ | ⭐ | Heavy tasks |

### Recommendation: **Docker + pytest**

**Docker Sandbox**:
```python
import docker
from pathlib import Path

class CodeSandbox:
    def __init__(self):
        self.client = docker.from_env()

    def execute_code(
        self,
        code: str,
        language: str,
        timeout: int = 30,
        memory_limit: str = "512m"
    ) -> dict:
        """Execute code in isolated container"""

        # Select image
        images = {
            'python': 'python:3.12-slim',
            'javascript': 'node:20-slim',
            'go': 'golang:1.21',
        }

        # Create temp file
        with tempfile.TemporaryDirectory() as tmpdir:
            code_file = Path(tmpdir) / f"code.{self._ext(language)}"
            code_file.write_text(code)

            # Run container
            try:
                container = self.client.containers.run(
                    image=images[language],
                    command=self._command(language, "code"),
                    volumes={tmpdir: {'bind': '/code', 'mode': 'ro'}},
                    working_dir='/code',
                    mem_limit=memory_limit,
                    network_disabled=True,  # No network access
                    remove=True,
                    detach=True,
                    timeout=timeout
                )

                # Get output
                result = container.wait(timeout=timeout)
                output = container.logs().decode('utf-8')

                return {
                    'success': result['StatusCode'] == 0,
                    'output': output,
                    'exit_code': result['StatusCode']
                }

            except docker.errors.ContainerError as e:
                return {
                    'success': False,
                    'output': str(e),
                    'exit_code': e.exit_status
                }
            except Exception as e:
                return {
                    'success': False,
                    'output': f"Error: {e}",
                    'exit_code': -1
                }

    def run_tests(
        self,
        project_path: Path,
        test_command: str = "pytest",
        timeout: int = 300
    ) -> dict:
        """Run tests in sandbox"""
        try:
            container = self.client.containers.run(
                image='python:3.12-slim',
                command=f"sh -c 'pip install -r requirements.txt && {test_command}'",
                volumes={str(project_path): {'bind': '/app', 'mode': 'rw'}},
                working_dir='/app',
                remove=True,
                detach=True,
                timeout=timeout
            )

            result = container.wait(timeout=timeout)
            output = container.logs().decode('utf-8')

            # Parse output
            return {
                'success': result['StatusCode'] == 0,
                'output': output,
                'tests_run': self._parse_test_count(output),
                'tests_passed': self._parse_passed_count(output),
                'coverage': self._parse_coverage(output)
            }

        except Exception as e:
            return {
                'success': False,
                'output': str(e),
                'error': str(e)
            }
```

---

## Observability

### LLM Tracing: **LangSmith**

```python
from langsmith import Client
from langsmith.run_helpers import traceable

# Initialize
client = Client()

@traceable(run_type="llm")
def plan_task(task: str) -> dict:
    """Traceable LLM call"""
    response = llm.invoke(f"Create a plan for: {task}")
    return {"plan": response}

@traceable(run_type="chain")
def execute_task(task: str):
    """Traceable chain"""
    plan = plan_task(task)  # Nested trace

    for step in plan['steps']:
        execute_step(step)  # Each step traced

    return {"status": "complete"}

# All calls automatically logged to LangSmith dashboard
```

### Metrics: **Custom + Prometheus**

```python
from prometheus_client import Counter, Histogram, Gauge
import time

# Define metrics
task_counter = Counter('gep_tasks_total', 'Total tasks processed')
task_duration = Histogram('gep_task_duration_seconds', 'Task duration')
task_success = Counter('gep_task_success_total', 'Successful tasks')
task_failure = Counter('gep_task_failure_total', 'Failed tasks')
llm_calls = Counter('gep_llm_calls_total', 'LLM API calls', ['provider', 'model'])
llm_tokens = Counter('gep_llm_tokens_total', 'LLM tokens used', ['type'])  # input/output

class MetricsCollector:
    @contextmanager
    def track_task(self, task_type: str):
        """Track task execution"""
        task_counter.inc()
        start = time.time()

        try:
            yield
            task_success.inc()
        except Exception:
            task_failure.inc()
            raise
        finally:
            duration = time.time() - start
            task_duration.observe(duration)

    def track_llm_call(self, provider: str, model: str, input_tokens: int, output_tokens: int):
        """Track LLM usage"""
        llm_calls.labels(provider=provider, model=model).inc()
        llm_tokens.labels(type='input').inc(input_tokens)
        llm_tokens.labels(type='output').inc(output_tokens)

# Usage
metrics = MetricsCollector()

with metrics.track_task('code_generation'):
    result = agent.generate_code(spec)

metrics.track_llm_call('openai', 'gpt-4o', 1000, 500)
```

---

## Summary & Quick Start

### Recommended Stack

```toml
[dependencies]
# Agent Framework
langgraph = "^0.0.20"
langchain = "^0.3.11"
langchain-openai = "^0.0.5"
langchain-anthropic = "^0.1.0"
langchain-google-genai = "^0.0.6"

# Code Analysis
tree-sitter = "^0.21.0"
tree-sitter-python = "^0.21.0"
tree-sitter-javascript = "^0.21.0"
jedi = "^0.19.0"
rope = "^1.11.0"
libcst = "^1.1.0"
radon = "^6.0.1"

# Vector & Graph
qdrant-client = "^1.7.0"
faiss-cpu = "^1.7.4"  # or faiss-gpu
networkx = "^3.2"
rank-bm25 = "^0.2.2"

# UI
textual = "^0.47.0"
rich = "^13.7.0"  # Already included
prompt-toolkit = "^3.0.43"

# Testing & Sandbox
pytest = "^7.4.0"
pytest-asyncio = "^0.21.0"
pytest-xdist = "^3.5.0"
docker = "^7.0.0"

# Observability
langsmith = "^0.0.75"
loguru = "^0.7.2"  # Already included
prometheus-client = "^0.19.0"

# Utilities
tenacity = "^8.2.0"  # Already included
pydantic = "^2.10.0"  # Already included
aiofiles = "^23.2.0"  # Already included
```

### Installation Order

**Phase 0** (Weeks 1-2):
```bash
pip install langchain-anthropic langchain-google-genai
pip install tree-sitter tree-sitter-python tree-sitter-javascript
pip install qdrant-client
pip install jedi radon
```

**Phase 1** (Weeks 3-5):
```bash
pip install langgraph
pip install rope libcst ast-grep-py
pip install docker pytest-xdist
```

**Phase 2** (Weeks 6-8):
```bash
pip install networkx
pip install langsmith prometheus-client
```

**Phase 3+** (Weeks 9+):
```bash
pip install textual prompt-toolkit
pip install hypothesis pytest-timeout
```

---

## Next Steps

1. **Experiment with LangGraph**: Build simple agent
2. **Test tree-sitter**: Parse Python and JavaScript
3. **Set up Qdrant**: Local instance with Docker
4. **Try Textual**: Create basic TUI
5. **Integrate Claude**: Add Anthropic API key

**First Working Prototype** (2 weeks):
- LangGraph agent with 3 tools
- tree-sitter AST parsing
- Qdrant vector search
- Simple CLI interface
- Basic task execution

This will validate the stack and inform Phase 0 development.
