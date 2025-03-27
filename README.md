# CML Auto-Complete Tool

A command-line tool that converts natural language descriptions into terminal commands using AI assistance.

## Features

- Natural language to terminal command conversion
- Interactive command confirmation
- Working directory management
- Safe command execution
- Beautiful terminal interface

## Installation

```bash
# Coming soon: Install via Homebrew
brew install cml-auto-complete-tool
```

## Development Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/cml-auto-complete-tool.git
cd cml-auto-complete-tool
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On macOS/Linux
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your OpenAI API key
```

## Usage

```bash
# Start the interactive shell
cml-auto-complete-tool

# Specify a working directory
cml-auto-complete-tool --dir /path/to/directory
```

## Development

- Run tests: `pytest`
- Format code: `black .`
- Sort imports: `isort .`
- Lint code: `flake8`

## License

MIT License 