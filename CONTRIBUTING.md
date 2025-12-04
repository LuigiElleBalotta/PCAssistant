# Contributing to PC Assistant

First off, thank you for considering contributing to PC Assistant! It's people like you that make PC Assistant such a great tool.

## Code of Conduct

This project and everyone participating in it is governed by our Code of Conduct. By participating, you are expected to uphold this code.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the existing issues to avoid duplicates. When you create a bug report, include as many details as possible:

- **Use a clear and descriptive title**
- **Describe the exact steps to reproduce the problem**
- **Provide specific examples**
- **Describe the behavior you observed and what you expected**
- **Include screenshots if possible**
- **Include your environment details** (Windows version, Python version if running from source)

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, include:

- **Use a clear and descriptive title**
- **Provide a detailed description of the suggested enhancement**
- **Explain why this enhancement would be useful**
- **List any similar features in other applications**

### Pull Requests

1. Fork the repository
2. Create a new branch from `develop`:
   ```bash
   git checkout -b feature/your-feature-name develop
   ```
3. Make your changes
4. Test your changes thoroughly
5. Commit your changes with clear commit messages:
   ```bash
   git commit -m "Add feature: description of feature"
   ```
6. Push to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```
7. Open a Pull Request against the `develop` branch

## Development Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/luigiellebalotta/PCAssistant.git
   cd pc_assistant
   ```

2. **Create virtual environment:**
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

3. **Install dependencies:**
   ```powershell
   pip install -r requirements.txt
   ```

4. **Run the application:**
   ```powershell
   python src/main.py
   ```

## Coding Standards

- Follow PEP 8 style guide for Python code
- Use meaningful variable and function names
- Add docstrings to all functions and classes
- Keep functions focused and concise
- Add comments for complex logic
- Use type hints where appropriate

## Project Structure

```
src/
├── core/       # Core functionality (cleaning, scanning, etc.)
├── gui/        # PyQt5 user interface components
├── utils/      # Utility functions (logging, config, etc.)
└── resources/  # Stylesheets and resources
```

## Testing

Before submitting a pull request:

1. Test your changes manually
2. Ensure the application runs without errors
3. Test on Windows 10 and/or Windows 11 if possible
4. Verify that existing features still work

## Commit Message Guidelines

- Use the present tense ("Add feature" not "Added feature")
- Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
- Limit the first line to 72 characters or less
- Reference issues and pull requests after the first line

Examples:
```
Add duplicate file deletion feature

- Implement file deletion with confirmation dialog
- Add progress tracking for batch deletions
- Update UI to reflect deleted files

Fixes #123
```

## Branch Naming

- `feature/feature-name` - New features
- `bugfix/bug-description` - Bug fixes
- `hotfix/critical-fix` - Critical fixes for production
- `docs/documentation-update` - Documentation updates

## Release Process

Releases are automated through GitHub Actions:

1. Update `CHANGELOG.md` with new version
2. Create and push a version tag:
   ```bash
   git tag -a v1.1.0 -m "Release version 1.1.0"
   git push origin v1.1.0
   ```
3. GitHub Actions will automatically build and create the release

## Questions?

Feel free to open an issue with the `question` label if you have any questions about contributing.

## License

By contributing to PC Assistant, you agree that your contributions will be licensed under the MIT License.
