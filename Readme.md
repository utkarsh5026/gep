# 🔍 GEP: Git-Enhanced Productivity

A semantic code search and analysis tool that makes your codebase feel like an open book.

## 🚀 What's this all about?

Hey there! I built GEP (Git-Enhanced Productivity) to solve that frustrating feeling of getting lost in large codebases. Ever spent hours trying to figure out "where's that function that does X?" or "how does this system actually work?" - I sure have, and that's why I created this tool.

GEP combines the power of vector embeddings and large language models to let you search and understand your code using natural language. Instead of grepping for exact text matches, you can ask questions like "how is authentication implemented?" or "where is the database connection handled?" and get meaningful results.

## ✨ Features

- 🔎 **Semantic Code Search**: Find code based on concepts and functionality, not just text patterns
- 🧠 **AI-Powered Analysis**: Get insights about code structure, patterns, and workflows
- 📊 **Project Visualization**: Understand your project structure at a glance
- 🔄 **Git Integration**: Track changes, analyze commit history, and generate meaningful commit messages
- 📄 **Documentation Generation**: Create documentation from your codebase with a single command
- 🔧 **Customizable Vector Stores**: Choose from FAISS, Chroma, and more for your embedding database
- 🔒 **Local-First**: All processing happens on your machine, keeping your code private

## 🛠️ Installation

```bash
# Using pip
pip install gep

# Or if you prefer to build from source
git clone https://github.com/yourusername/gep.git
cd gep
pip install -e .
```

## 🧩 Quick Start

### Initialize your project

First, navigate to your project directory and initialize GEP:

```bash
cd your-project
gep project init
```

This will create a `.gep` directory that stores your vector database and configuration.

### Vectorize your codebase

Next, let's create embeddings for your code:

```bash
gep project vectorize
```

This reads your files (respecting .gitignore patterns), splits them into chunks, and creates vector embeddings for semantic search.

### Search your code

Now the fun part! Ask questions about your codebase:

```bash
gep project files --query "How is authentication implemented?"
```

### Analyze commit history

Want to understand how your project has evolved?

```bash
gep repo history
```

This uses an LLM to analyze your commit history and provide insights about development patterns.

## 🔧 Configuration

GEP is highly configurable. When you initialize a project, it creates a `.gep/config.yaml` file with sensible defaults. You can edit this file to:

- Change embedding models
- Select different vector stores
- Customize LLM settings
- Specify custom file patterns to include/exclude

Here's a sample configuration:

```yaml
# Root directory of your project
root_dir: "./project"

# Embedding Configuration
embedding_config:
  embedding_type: "openai"
  model_name: "text-embedding-3-small"
  batch_size: 100
  dimension: 1536

# LLM Configuration
llm_config:
  llm_type: "openai"
  model_name: "gpt-4o-mini"
  temperature: 0.7

# Vector Store Configuration
vector_config:
  store_type: "faiss"
  persist_dir: "./vector_store"
  dimension: 1536
```

## 🧠 How It Works

I've designed GEP with a modular architecture:

1. **File Processing**: Files are read, filtered based on ignore patterns, and split into chunks
2. **Embedding Generation**: These chunks are converted to vector embeddings using models like OpenAI's text-embedding-3-small
3. **Vector Storage**: Embeddings are stored in a vector database (FAISS by default)
4. **Query Processing**: Your natural language queries are converted to embeddings and matched against the stored vectors
5. **Result Analysis**: Matching code chunks are ranked by relevance and formatted for display

The system has three main components:
- Core vector embedding and search functionality
- Git integration for repository analysis
- LLM integration for code explanation and insight generation

## 📝 Command Reference

### Project Commands

- `gep project vectorize`: Create vector embeddings for your code
- `gep project files`: Search your codebase with natural language
- `gep project docs`: Generate documentation for your code

### Repository Commands

- `gep repo history`: Analyze commit history
- `gep repo compare`: Compare changes between commits
- `gep repo commit-msg`: Generate a commit message from staged changes

### API Key Management

- `gep api-key add`: Add API keys for LLM providers
- `gep api-key get`: Retrieve stored API keys
- `gep api-key delete`: Remove API keys

## 🤝 Contributing

I'd love your help making GEP better! Here's how you can contribute:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Commit your changes (`git commit -m 'Add some amazing feature'`)
5. Push to the branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

## 🪲 Troubleshooting

### Common Issues

#### API Key Problems
If you're seeing authentication errors, ensure you've added your API keys:

```bash
gep api-key add --provider openai --key your-api-key
```

#### Vector Store Issues
If search isn't working well, try rebuilding your vector store:

```bash
gep project vectorize --from-scratch
```

## 🌱 Future Plans

I'm actively working on making GEP even better. Here's what's coming:

- Support for more embedding models including local options
- Enhanced visualization of code relationships
- Collaborative features for team environments
- IDE integrations
- Semantic search across multiple repositories

## 📜 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgements

Big thanks to:
- The LangChain team for their amazing tools
- OpenAI for their embedding and language models
- FAISS for efficient vector search
- And all the early users who provided valuable feedback!

---

Built with ❤️ to make codebases more accessible. If you have any questions or suggestions, please don't hesitate to reach out or open an issue.