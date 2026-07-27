# Contributing Guide

Thank you for your interest in contributing to the Cloud Infrastructure Hardening & Compliance Pipeline project.

## Code of Conduct

This project adheres to a code of conduct. By participating, you are expected to uphold this code.

## How to Contribute

### Reporting Bugs

Before creating bug reports, please check the existing issues as you might find that the problem is already known.

When creating a bug report, please include:
- Description of the problem
- Steps to reproduce
- Expected behavior
- Actual behavior
- Environment details (OS, versions, etc.)
- Relevant logs or screenshots

### Suggesting Enhancements

Enhancement suggestions are welcome. Please:
- Use a clear and descriptive title
- Provide a detailed description of the proposed enhancement
- Explain why this enhancement would be useful
- Provide examples of how the enhancement would be used

### Pull Requests

1. Fork the repository
2. Create a branch for your feature or fix
3. Make your changes
4. Follow the coding standards
5. Add tests if applicable
6. Update documentation
7. Submit a pull request

## Development Workflow

### Branching Strategy

- `main` - Production-ready code
- `develop` - Integration branch for features
- `feature/*` - Feature branches
- `bugfix/*` - Bug fix branches
- `hotfix/*` - Emergency fixes for production

### Commit Messages

Follow the conventional commits format:
```
<type>(<scope>): <subject>

<body>

<footer>
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

Example:
```
feat(terraform): add support for Azure Bastion

Add Azure Bastion resource to improve SSH access security.
This replaces the previous jump box approach with a managed service.

Closes #123
```

### Code Style

#### Terraform
- Use `terraform fmt` before committing
- Follow Terraform best practices
- Add comments for complex logic
- Use descriptive variable names

#### Ansible
- Use `ansible-lint` before committing
- Follow Ansible best practices
- Use descriptive task names
- Document role requirements

#### Go
- Use `gofmt` before committing
- Follow Go conventions
- Add godoc comments for exported functions
- Handle errors properly

#### Python
- Follow PEP 8 style guide
- Use `pylint` and `bandit` for linting
- Add docstrings to functions
- Type hints where appropriate

#### Bash
- Use ShellCheck for linting
- Follow Google Shell Style Guide
- Add comments for complex logic
- Use `set -e` for error handling

## Testing

### Terraform Testing
```bash
terraform fmt -check
terraform validate
terraform plan
```

### Ansible Testing
```bash
ansible-lint site.yml
ansible-playbook site.yml --syntax-check
ansible-playbook site.yml --check
```

### Go Testing
```bash
go test ./...
go vet ./...
gosec ./...
```

### Python Testing
```bash
pylint azure_orchestrator.py
bandit -r .
pytest
```

## Documentation

### Updating Documentation
- Keep documentation in sync with code changes
- Update README.md for user-facing changes
- Update ARCHITECTURE.md for structural changes
- Update DEPLOYMENT.md for deployment changes
- Add inline code comments for complex logic

### Adding New Features
1. Update relevant documentation
2. Add examples if applicable
3. Update the technology table in README.md if new tools are added

## Review Process

1. Automated checks must pass (CI/CD)
2. At least one approval from maintainers
3. All discussions must be resolved
4. No merge conflicts with target branch

## Release Process

1. Update version in relevant files
2. Update CHANGELOG.md
3. Create release tag
4. Generate release notes
5. Announce release

## Getting Help

- Open an issue for questions
- Check existing documentation
- Join community discussions (if available)

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
