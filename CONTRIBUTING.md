# Contributing to Agentic Analytics Studio

Thank you for your interest in contributing to AAS! This document provides guidelines and instructions for contributing to the project.

---

## 🎯 Ways to Contribute

- **🐛 Report Bugs**: Open an issue with reproduction steps
- **💡 Suggest Features**: Propose new plays, integrations, or enhancements
- **📝 Improve Documentation**: Fix typos, add examples, clarify instructions
- **🧪 Add Tests**: Increase coverage for existing features
- **🎨 Enhance UI/UX**: Improve design, accessibility, or user experience
- **🎯 Create New Plays**: Add hero plays using the modular registry

---

## 🚀 Getting Started

### 1. Fork and Clone
```bash
# Fork the repository on GitHub, then:
git clone https://github.com/YOUR_USERNAME/Agentic-Analytics-Studio.git
cd Agentic-Analytics-Studio
```

### 2. Set Up Development Environment
```bash
# Backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Development dependencies

# Frontend
cd web
npm install
cd ..

# Configure environment
cp .env.example .env
```

### 3. Create a Feature Branch
```bash
git checkout -b feat/my-feature
# or
git checkout -b fix/bug-description
```

---

## 📋 Development Guidelines

### Code Style

#### Python
- Follow **PEP 8** style guide
- Use **type hints** for function signatures
- Maximum line length: **100 characters**
- Use **docstrings** for all public functions/classes
- Format code with **black**: `black aas/`
- Lint with **flake8**: `flake8 aas/`

Example:
```python
def calculate_impact(deal_value: float, probability: float) -> float:
    """
    Calculate impact score for a deal.
    
    Args:
        deal_value: Total value of the deal in dollars
        probability: Probability of closing (0.0 to 1.0)
    
    Returns:
        Impact score in thousands of dollars
    """
    return (deal_value * probability) / 1000
```

#### JavaScript
- Use **ES6+** syntax
- Use **const/let** (no var)
- Use **arrow functions** for callbacks
- Use **template literals** for strings
- Follow existing code style
- Run linter: `npm run lint`

Example:
```javascript
const calculateImpact = (dealValue, probability) => {
    return (dealValue * probability) / 1000;
};
```

### Commit Messages

Use **Conventional Commits** format:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, no logic change)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples:**
```bash
feat(agents): add customer segmentation play

Implements K-Means clustering to segment customers by value and risk.
Generates targeted recommendations for each segment.

Closes #123
```

```bash
fix(salesforce): handle auth failure gracefully

Adds try/catch around Salesforce authentication to prevent crashes.
Falls back to stub mode if credentials are invalid.
```

---

## 🎯 Adding a New Hero Play

The modular play registry makes it easy to add new plays. Follow these steps:

### 1. Create Agent File
Create `aas/agents/my_play.py`:

```python
"""My Play - Brief description."""

from typing import Any, Dict, List
from .base import AgentPlay
from ..models.action import Action

class MyPlayAgent(AgentPlay):
    """Detailed description of what this play does."""
    
    def load_data(self) -> Any:
        """Load data for analysis."""
        # Your data loading logic
        return data
    
    def analyze(self, data: Any) -> Dict[str, Any]:
        """Analyze data and return findings."""
        # Your analysis logic
        return {
            "metric_1": value1,
            "metric_2": value2,
            "findings": [...]
        }
    
    def recommend_actions(self, analysis: Dict[str, Any]) -> List[Action]:
        """Generate recommended actions."""
        actions = []
        
        # Create actions based on analysis
        actions.append(Action(
            type="my_action_type",
            title="Action Title",
            description="Detailed description",
            priority="high",
            impact_score=100,
            metadata={...},
            reasoning=self.generate_rationale("context")
        ))
        
        return actions
```

### 2. Register the Play
Add to `aas/plays/plays.py`:

```python
from ..agents.my_play import MyPlayAgent

register_play(
    id="my_play",
    label="My Play",
    description="Brief description for UI dropdown",
    agent_class=MyPlayAgent,
    tags=["category1", "category2"],
    inputs_schema={
        "param1": {
            "type": "string",
            "description": "Description of param1",
            "optional": True
        }
    },
    demo_seed="my_play_demo_1",
    icon="🎯"
)
```

### 3. Add Sample Data (Optional)
Create `aas/sample_data/my_play_data.csv` with representative records.

### 4. Add Tests
Create `tests/test_my_play.py`:

```python
def test_my_play_agent():
    agent = MyPlayAgent()
    result = agent.run()
    
    assert "analysis" in result
    assert "actions" in result
    assert len(result["actions"]) > 0
```

### 5. Update Documentation
- Add play to README.md hero plays table
- Document in `docs/play_api.md` if needed

See [docs/play_api.md](docs/play_api.md) for complete guide.

---

## 🧪 Testing

### Running Tests
```bash
# All tests
pytest

# Specific file
pytest tests/test_salesforce_client.py

# With coverage
pytest --cov=aas --cov-report=html

# Verbose
pytest -v
```

### Writing Tests
- Place tests in `tests/` directory
- Mirror the source structure (e.g., `tests/agents/test_pipeline_leakage.py`)
- Use descriptive test names: `test_<function>_<scenario>_<expected_result>`
- Use fixtures for common setup
- Mock external dependencies (Salesforce, LLMs, etc.)

Example:
```python
import pytest
from unittest.mock import Mock, patch
from aas.agents.pipeline_leakage import PipelineLeakageAgent

def test_pipeline_agent_generates_actions():
    """Test that pipeline agent generates at least one action."""
    agent = PipelineLeakageAgent()
    result = agent.run()
    
    assert len(result["actions"]) > 0
    assert all("impact_score" in action for action in result["actions"])
```

### Test Coverage Goals
- **Minimum**: 60% overall coverage
- **Target**: 80% for core modules (agents, services, api)
- **Critical**: 100% for security-sensitive code (auth, credentials)

---

## 📝 Documentation

### Updating Documentation
- **README.md**: High-level overview, quick start, configuration
- **docs/play_api.md**: Play development guide
- **docs/architecture.md**: System architecture and data flow
- **Docstrings**: All public functions and classes
- **Comments**: Complex logic or non-obvious decisions

### Documentation Style
- Use **Markdown** for all docs
- Include **code examples** where applicable
- Add **diagrams** for complex concepts (Mermaid preferred)
- Keep **language clear and concise**
- Assume reader is familiar with Python/JavaScript but not AAS internals

---

## 🔄 Pull Request Process

### Before Submitting
1. ✅ Run tests: `pytest`
2. ✅ Run linter: `flake8 aas/` or `black aas/`
3. ✅ Update documentation if needed
4. ✅ Add tests for new features
5. ✅ Ensure all tests pass
6. ✅ Rebase on latest `main`

### PR Template
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Changes Made
- Change 1
- Change 2

## Testing
- [ ] Unit tests added/updated
- [ ] Manual testing completed
- [ ] All tests pass

## Screenshots (if applicable)
[Add screenshots for UI changes]

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No new warnings
```

### Review Process
1. **Automated checks** run (tests, linting)
2. **Maintainer review** (1-2 business days)
3. **Address feedback** if requested
4. **Approval** and merge

---

## 🐛 Reporting Bugs

### Before Reporting
- Search existing issues to avoid duplicates
- Try to reproduce on latest `main` branch
- Gather relevant information (logs, environment, steps)

### Bug Report Template
```markdown
## Bug Description
Clear description of the bug

## Steps to Reproduce
1. Step 1
2. Step 2
3. ...

## Expected Behavior
What should happen

## Actual Behavior
What actually happens

## Environment
- OS: [e.g., Windows 11, macOS 13, Ubuntu 22.04]
- Python version: [e.g., 3.10.5]
- Node version: [e.g., 18.16.0]
- Browser: [e.g., Chrome 120]

## Logs
```
Paste relevant logs here
```

## Screenshots
[If applicable]
```

---

## 💡 Feature Requests

### Suggesting Features
- Open an issue with `[Feature Request]` prefix
- Describe the problem it solves
- Provide use cases
- Suggest implementation approach (optional)

### Feature Request Template
```markdown
## Feature Description
What feature would you like to see?

## Problem It Solves
What problem does this address?

## Proposed Solution
How might this be implemented?

## Alternatives Considered
What other solutions did you consider?

## Additional Context
Any other relevant information
```

---

## 📜 Code of Conduct

### Our Pledge
We are committed to providing a welcoming and inclusive environment for all contributors.

### Our Standards
- **Be respectful** of differing viewpoints
- **Be constructive** in feedback
- **Be collaborative** in problem-solving
- **Be patient** with newcomers

### Unacceptable Behavior
- Harassment or discrimination
- Trolling or insulting comments
- Personal attacks
- Publishing private information

### Enforcement
Violations may result in temporary or permanent ban from the project.

---

## 🙏 Recognition

Contributors will be recognized in:
- GitHub contributors page
- Release notes for significant contributions
- README acknowledgments section

---

## 📞 Questions?

- **General questions**: Open a [Discussion](https://github.com/HooplaHoorah/Agentic-Analytics-Studio/discussions)
- **Bug reports**: Open an [Issue](https://github.com/HooplaHoorah/Agentic-Analytics-Studio/issues)
- **Security issues**: Email security@example.com (do not open public issue)

---

**Thank you for contributing to Agentic Analytics Studio!** 🎉
