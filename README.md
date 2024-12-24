
# GEP

A powerful CLI tool for processing queries and managing embeddings with support for multiple API providers and vector stores.

## 🚀 Features

- Query processing with customizable prompts
- Project initialization and configuration
- Embedding management
- API key management
- Multiple API provider support (including OpenAI)
- Gitignore integration
- Vector store management

## 📋 Installation

[Add installation instructions here]

## 🛠️ Commands

### Initialize Project
```bash
project init [OPTIONS]

Options:
  -r, --root-path PATH      The root path to watch [default: .]
  -o, --overwrite          Overwrite existing project
  -a, --api-provider       API provider to use [default: openai]
  -k, --api-key TEXT      The API key to use
```

### Process Query

```bash
project process-query QUERY [RELEVANCE_SCORE] [MAX_RESULTS] [OPTIONS]

Options:
  -t, --prompt-type       Type of prompt to use [default: file_wise]
  -p, --prompt-provider   Prompt provider to use [default: semantic]
```

### Load Project

```bash
project load [OPTIONS]

Options:
  -r, --root-path PATH     The root path to watch [default: .]
  -c, --config-path PATH   Path to configuration file [default: config.yaml]
  -a, --api-provider      API provider to use [default: openai]
  -g, --use-gitignore     Use gitignore to ignore files
```

### Create Sample Config

```bash
project csc [OPTIONS]

Options:
  -c, --config-path PATH   Path to configuration file [default: config.yaml]
  -o, --on-screen         Display configuration on screen
```

### Update Ignore Rules

```bash
project upnore [OPTIONS]

Options:
  -v, --update-vector-store   Update vector store (remove ignored files)
```

### Embed Project

```bash
project embed
```

### Manage API Keys

```bash
project api-key [OPTIONS]

Options:
  -o, --op-type TEXT        Operation type (add/delete/get)
  -a, --api-provider TEXT   API provider to use
  -k, --api-key TEXT       API key to use
```

## ⚙️ Configuration

The project uses a YAML configuration file (default: `config.yaml`) to manage settings. You can create a sample configuration using the `csc` command.

## 🔑 API Providers

Supported API providers:

- OpenAI
- [List other providers based on LLMType enum]

## 🗄️ Vector Stores

[Add information about supported vector stores based on VectorStoreType enum]

## 📝 Prompt Types

Available prompt types:

- File-wise (default)
- [List other prompt types based on PromptType enum]

## 🤝 Contributing

[Add contributing guidelines]

## 📄 License

[Add license information]

```

This README provides a comprehensive overview of your CLI tool's capabilities and usage. You may want to:

1. Add specific installation instructions
2. List all supported API providers from your `LLMType` enum
3. Add details about supported vector stores
4. Include all available prompt types
5. Add contributing guidelines
6. Specify the license
7. Add any additional configuration details or examples
8. Include prerequisites or dependencies

Would you like me to expand on any of these sections?
```
