# Contributing to Unified Memory System

Thank you for your interest in contributing to the Unified Memory System! This document provides guidelines and information about contributing to this project.

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- Docker and Docker Compose
- OpenAI API Key
- Git

### Development Setup

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/yourusername/unified-memory-system.git
   cd unified-memory-system
   ```

3. Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

5. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

6. Start the development environment:
   ```bash
   docker-compose -f docker-compose.unified.yml up -d
   python src/unified_memory_server.py
   ```

## 🛠️ Development Guidelines

### Code Style

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guidelines
- Use meaningful variable and function names
- Add docstrings to all functions and classes
- Keep functions focused and small

### Testing

- Write tests for new features
- Ensure all tests pass before submitting PR
- Run tests with: `python -m pytest tests/`
- Maintain test coverage above 80%

### Commit Messages

Use clear, descriptive commit messages:

```
feat: add graph memory search optimization
fix: resolve Neo4j connection timeout
docs: update API documentation
test: add integration tests for memory tools
```

### Branch Naming

- `feature/feature-name` for new features
- `fix/bug-description` for bug fixes
- `docs/documentation-update` for documentation
- `test/test-improvement` for testing

## 📝 Types of Contributions

### 🐛 Bug Reports

When filing a bug report, please include:

- Clear description of the issue
- Steps to reproduce
- Expected vs actual behavior
- Environment details (OS, Python version, etc.)
- Relevant logs or error messages

### ✨ Feature Requests

For feature requests, please provide:

- Clear description of the feature
- Use case and motivation
- Proposed implementation approach
- Any alternative solutions considered

### 🔧 Code Contributions

1. **Fork and Clone**: Fork the repo and clone your fork
2. **Create Branch**: Create a feature branch from `main`
3. **Develop**: Implement your changes with tests
4. **Test**: Ensure all tests pass
5. **Document**: Update documentation if needed
6. **Submit**: Create a pull request

### 📚 Documentation

- Fix typos and improve clarity
- Add examples and use cases
- Update API documentation
- Create tutorials and guides

## 🔍 Pull Request Process

1. **Pre-submission Checklist**:
   - [ ] Tests pass locally
   - [ ] Code follows style guidelines
   - [ ] Documentation updated
   - [ ] CHANGELOG.md updated
   - [ ] No merge conflicts

2. **PR Description**:
   - Clear title describing the change
   - Detailed description of what was changed
   - Link to related issues
   - Screenshots for UI changes

3. **Review Process**:
   - Maintainers will review within 2-3 days
   - Address feedback promptly
   - Keep PRs focused and small
   - Rebase if necessary

## 🧪 Testing Guidelines

### Unit Tests

- Test individual functions and methods
- Mock external dependencies
- Cover edge cases and error conditions

### Integration Tests

- Test component interactions
- Use real database connections
- Test end-to-end workflows

### Running Tests

```bash
# All tests
python -m pytest tests/

# With coverage
python -m pytest tests/ --cov=src

# Specific test file
python -m pytest tests/test_memory.py

# Integration tests
python -m pytest tests/integration/
```

## 📊 Performance Guidelines

- Profile code for performance bottlenecks
- Optimize database queries
- Use async/await for I/O operations
- Monitor memory usage

## 🔒 Security Guidelines

- Never commit secrets or API keys
- Validate all user inputs
- Use parameterized queries
- Follow secure coding practices

## 📋 Code Review Criteria

Reviewers will check for:

- **Functionality**: Does the code work as intended?
- **Tests**: Are there adequate tests?
- **Performance**: Are there any performance issues?
- **Security**: Are there security vulnerabilities?
- **Documentation**: Is the code well-documented?
- **Style**: Does it follow project conventions?

## 🤝 Community Guidelines

- Be respectful and inclusive
- Help newcomers get started
- Share knowledge and best practices
- Collaborate constructively

## 📞 Getting Help

- **Discord**: [Join our community](https://discord.gg/unified-memory)
- **Issues**: [GitHub Issues](https://github.com/yourusername/unified-memory-system/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/unified-memory-system/discussions)

## 🎉 Recognition

Contributors will be:

- Listed in the README acknowledgments
- Added to the CONTRIBUTORS.md file
- Mentioned in release notes
- Invited to the contributors' Discord channel

## 📄 License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to the Unified Memory System! 🚀 