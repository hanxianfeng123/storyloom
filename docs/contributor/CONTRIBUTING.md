# Contributing to Storyloom

Thank you for your interest in contributing to Storyloom! We welcome contributions from everyone. This document outlines the process for contributing to the project.

## Code of Conduct

By participating in this project, you agree to abide by our [Code of Conduct](CODE_OF_CONDUCT.md). Please read it before making any contributions.

## Table of Contents

- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Coding Standards](#coding-standards)
- [Commit Conventions](#commit-conventions)
- [Pull Request Process](#pull-request-process)
- [Testing](#testing)
- [Documentation](#documentation)
- [Issue Reporting](#issue-reporting)
- [Feature Requests](#feature-requests)

## Getting Started

1. **Fork the repository** on GitHub.
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/your-username/storyloom.git
   cd storyloom
   ```
3. **Add the upstream repository** as a remote:
   ```bash
   git remote add upstream https://github.com/storyloom/storyloom.git
   ```
4. **Create a branch** for your work:
   ```bash
   git checkout -b feat/my-feature
   ```

## Development Setup

### Prerequisites

- Python 3.10 or higher
- pip (Python package manager)

### Install Dependencies

Install the project in editable mode with development dependencies:

```bash
make install
```

Or manually:

```bash
cd backend && pip install -e ".[dev]"
```

### Run Development Server

```bash
make dev
```

This starts the FastAPI development server with hot-reload on port 8000.

## Coding Standards

We use the following tools to maintain code quality:

- **Ruff**: For linting and formatting. Run with `make lint`.
- **MyPy**: For static type checking (where configured).

### Python Style Guidelines

- Follow [PEP 8](https://peps.python.org/pep-0008/) conventions.
- Use type hints for all function signatures.
- Write docstrings for public modules, classes, and functions (Google-style preferred).
- Keep functions focused and single-purpose.
- Maximum line length: 100 characters.

### Naming Conventions

- **Modules**: `snake_case`
- **Classes**: `PascalCase`
- **Functions/Methods**: `snake_case`
- **Constants**: `UPPER_SNAKE_CASE`
- **Private members**: Prefix with underscore (`_private_method`)

## Commit Conventions

We follow [Conventional Commits](https://www.conventionalcommits.org/) for commit messages. This allows for automatic changelog generation and semantic versioning.

### Format

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

### Types

- `feat`: A new feature
- `fix`: A bug fix
- `chore`: Routine tasks, maintenance, dependency updates
- `docs`: Documentation changes
- `style`: Code style changes (formatting, semicolons, etc.)
- `refactor`: Code changes that neither fix bugs nor add features
- `test`: Adding or modifying tests
- `perf`: Performance improvements
- `ci`: CI/CD configuration changes

### Scope

The scope should be the area of the codebase affected (e.g., `cli`, `api`, `pipeline`, `memory`).

### Examples

```
feat(cli): add `storyloom status` command for pipeline monitoring
fix(api): handle timeout when LLM provider is unresponsive
docs(readme): update quick-start guide with Windows instructions
chore(deps): bump fastapi from 0.104.0 to 0.105.0
```

## Pull Request Process

1. **Ensure your branch is up to date** with the upstream main branch:
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. **Run tests and linting** to verify nothing is broken:
   ```bash
   make test
   make lint
   ```

3. **Write or update tests** for your changes. Aim for adequate coverage of new functionality.

4. **Update documentation** if your changes affect the public API or user-facing behavior.

5. **Push your branch** to your fork:
   ```bash
   git push origin feat/my-feature
   ```

6. **Open a pull request** against the `main` branch of the upstream repository.
   - Use the pull request template (`.github/PULL_REQUEST_TEMPLATE.md`).
   - Link any related issues using GitHub keywords (e.g., "Closes #123").
   - Provide a clear description of the changes and their motivation.

7. **Respond to feedback** from reviewers. Make additional commits to your branch as needed.

8. **A maintainer will merge** your PR once it has been approved and all checks pass.

### PR Review Criteria

- Code follows project style guidelines
- Tests pass and new code has adequate test coverage
- Documentation is updated if needed
- No unnecessary dependencies are introduced
- Changes are focused on a single concern

## Testing

We use `pytest` for testing.

```bash
# Run all tests
make test

# Run specific test file
cd backend && pytest tests/test_pipeline.py -v

# Run tests with coverage
cd backend && pytest --cov=storyloom tests/
```

### Test Guidelines

- Unit tests should be fast and not require external services.
- Integration tests can use mock LLM providers.
- Keep test files organized to mirror the module structure.

## Documentation

Documentation is maintained in the `docs/` directory. When making changes:

- Update existing docs to reflect your changes.
- Add new docs for new features or modules.
- Use clear, concise language suitable for both technical and non-technical readers.
- Include code examples where helpful.

## Issue Reporting

### Bug Reports

When reporting a bug, please use the [bug report template](/.github/ISSUE_TEMPLATE/bug_report.md) and include:

- Your operating system and Python version
- Steps to reproduce the issue
- Expected behavior vs. actual behavior
- Relevant logs, error messages, or screenshots
- A minimal reproducible example if possible

### Feature Requests

For feature requests, please use the [feature request template](/.github/ISSUE_TEMPLATE/feature_request.md) and describe:

- The problem you're trying to solve
- The solution you'd like to see
- Any alternatives you've considered

## Questions?

If you have questions about contributing, feel free to open a [Discussion](https://github.com/storyloom/storyloom/discussions) on GitHub.
