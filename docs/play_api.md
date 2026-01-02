# Play API Documentation

## Overview

The Agentic Analytics Studio (AAS) Play API provides a modular, extensible framework for creating and registering "hero plays" - intelligent agents that analyze data and recommend actions.

This document explains how to:
1. Understand the play architecture
2. Create a new play
3. Register your play
4. Test and deploy your play

---

## Architecture

### Core Components

1. **AgentPlay** (`aas/agents/base.py`): Abstract base class for all plays
2. **PlayRegistry** (`aas/plays/registry.py`): Central registry for play discovery
3. **PlaySpec** (`aas/plays/registry.py`): Metadata specification for each play
4. **API Integration** (`aas/api.py`): REST endpoints that use the registry

### Play Lifecycle

```
1. Define Play Class (inherit from AgentPlay)
   ↓
2. Register Play (via register_play())
   ↓
3. API Discovery (GET /plays)
   ↓
4. Execution (POST /run/{play_id})
   ↓
5. Action Generation & Approval
```

---

## Creating a New Play

### Step 1: Create Your Agent Class

Create a new file in `aas/agents/` (e.g., `my_play.py`):

```python
"""My Custom Play - Brief description."""

from typing import Any, Dict, List
from .base import AgentPlay
from ..models.action import Action

class MyCustomAgent(AgentPlay):
    """
    Detailed description of what this play does.
    
    This agent:
    1. Loads data from X
    2. Analyzes Y
    3. Recommends Z
    """
    
    def __init__(self):
        self.params = {}
    
    def load_data(self) -> Any:
        """
        Load or fetch the data needed for this play.
        
        Returns:
            Data structure (DataFrame, dict, list, etc.)
        """
        # Your data loading logic here
        # Can load from CSV, database, API, etc.
        pass
    
    def analyze(self, data: Any) -> Dict[str, Any]:
        """
        Perform analysis on the loaded data.
        
        Args:
            data: The data returned from load_data()
        
        Returns:
            Dictionary of analysis results/findings
        """
        # Your analysis logic here
        return {
            "metric_1": 123,
            "metric_2": 456,
            "findings": ["finding 1", "finding 2"]
        }
    
    def recommend_actions(self, analysis: Dict[str, Any]) -> List[Action]:
        """
        Generate recommended actions based on analysis.
        
        Args:
            analysis: The analysis results from analyze()
        
        Returns:
            List of Action objects
        """
        actions = []
        
        # Example action
        actions.append(Action(
            type="my_action_type",
            title="Do Something Important",
            description="Detailed description of the action",
            priority="high",  # "high", "medium", or "low"
            impact_score=100,  # Numeric impact score
            metadata={
                "key1": "value1",
                "key2": "value2"
            },
            reasoning=self.generate_rationale("Context for AI rationale")
        ))
        
        return actions
```

### Step 2: Register Your Play

Add registration in `aas/plays/plays.py`:

```python
from ..agents.my_play import MyCustomAgent

def register_all_plays():
    # ... existing registrations ...
    
    # Your new play
    register_play(
        id="my_play",
        label="My Custom Play",
        description="Brief description for the UI dropdown",
        agent_class=MyCustomAgent,
        tags=["category1", "category2"],
        inputs_schema={
            "param1": {
                "type": "string",
                "description": "Description of param1",
                "optional": True
            },
            "param2": {
                "type": "integer",
                "description": "Description of param2",
                "default": 10
            }
        },
        demo_seed="my_play_demo_1",
        icon="🎯"  # Optional emoji icon
    )
```

### Step 3: Test Your Play

Create a test script:

```python
"""Test script for My Custom Play."""

from aas.plays import get_agent

def test_my_play():
    agent = get_agent("my_play")
    result = agent.run()
    
    print(f"Analysis: {result['analysis']}")
    print(f"Actions: {len(result['actions'])} generated")
    
    for action in result['actions']:
        print(f"  - [{action['priority']}] {action['title']}")

if __name__ == "__main__":
    test_my_play()
```

---

## Play Interface Reference

### Required Methods

All plays must implement these methods from `AgentPlay`:

#### `load_data() -> Any`
- **Purpose**: Load or fetch data for analysis
- **Returns**: Any data structure (DataFrame, dict, list, etc.)
- **Can return**: `None` if no data is needed

#### `analyze(data: Any) -> Dict[str, Any]`
- **Purpose**: Perform analysis on the data
- **Args**: `data` - The data from `load_data()`
- **Returns**: Dictionary of analysis results
- **Must return**: A dictionary (can be empty)

#### `recommend_actions(analysis: Dict[str, Any]) -> List[Action]`
- **Purpose**: Generate recommended actions
- **Args**: `analysis` - The results from `analyze()`
- **Returns**: List of `Action` objects
- **Can return**: Empty list if no actions

### Optional Methods

#### `generate_rationale(context: str) -> str`
- **Purpose**: Generate AI-powered rationale for actions
- **Inherited from**: `AgentPlay` base class
- **Supports**: OpenAI, Ollama, or rule-based fallback
- **Usage**: `reasoning=self.generate_rationale("context string")`

---

## Action Model

Actions must be instances of `aas.models.action.Action`:

```python
Action(
    type="action_type",           # Required: string identifier
    title="Action Title",          # Required: short title
    description="Full description", # Required: detailed description
    priority="high",               # Optional: "high", "medium", "low"
    impact_score=100.0,            # Optional: numeric impact score
    metadata={},                   # Optional: additional data
    reasoning=""                   # Optional: AI-generated rationale
)
```

---

## Registry API

### Programmatic Access

```python
from aas.plays import list_plays, get_play, get_agent

# List all registered plays
plays = list_plays()
# Returns: [{"id": "pipeline", "label": "Pipeline Leakage", ...}, ...]

# Get play specification
spec = get_play("pipeline")
# Returns: PlaySpec object

# Get agent instance
agent = get_agent("pipeline")
# Returns: PipelineLeakageAgent instance

# Run the agent
result = agent.run()
# Returns: {"analysis": {...}, "actions": [...]}
```

### REST API

```bash
# List all plays
GET /plays
Response: {"plays": ["pipeline", "churn", "spend", "revenue"]}

# Run a specific play
POST /run/{play_id}
Body: {"params": {"param1": "value1"}}
Response: {
  "run_id": "uuid",
  "play": "pipeline",
  "analysis": {...},
  "actions": [...]
}
```

---

## Best Practices

### 1. Data Loading
- **Use sample data**: Include a fallback dataset for demo purposes
- **Handle errors**: Gracefully handle missing data sources
- **Document sources**: Clearly document where data comes from

### 2. Analysis
- **Be deterministic**: Same input should produce same output
- **Return structured data**: Use consistent dictionary keys
- **Include metrics**: Quantify findings with numbers

### 3. Actions
- **Prioritize correctly**: Use "high" for urgent, "low" for nice-to-have
- **Calculate impact**: Provide meaningful impact scores
- **Add context**: Use metadata for additional details
- **Generate rationales**: Use `generate_rationale()` for transparency

### 4. Testing
- **Unit test each method**: Test `load_data()`, `analyze()`, `recommend_actions()` separately
- **Integration test**: Test full `run()` workflow
- **Mock external deps**: Use mocks for APIs, databases, etc.

---

## Example: Complete Minimal Play

```python
"""Minimal Example Play."""

from typing import Any, Dict, List
from .base import AgentPlay
from ..models.action import Action

class MinimalAgent(AgentPlay):
    """Minimal example play for demonstration."""
    
    def load_data(self) -> Dict[str, Any]:
        return {"value": 42}
    
    def analyze(self, data: Any) -> Dict[str, Any]:
        return {"result": data["value"] * 2}
    
    def recommend_actions(self, analysis: Dict[str, Any]) -> List[Action]:
        return [
            Action(
                type="example",
                title="Example Action",
                description=f"Result was {analysis['result']}",
                priority="medium",
                impact_score=analysis['result']
            )
        ]
```

Register it:

```python
register_play(
    id="minimal",
    label="Minimal Example",
    description="A minimal example play",
    agent_class=MinimalAgent,
    icon="✨"
)
```

---

## Adding to UI

Once registered, your play automatically appears in:
1. **API**: `GET /plays` endpoint
2. **Dropdown**: Frontend play selector (if using dynamic loading)
3. **Execution**: `POST /run/{your_play_id}`

For static frontends, add to `web/index.html`:

```html
<select id="play-select">
  <!-- existing options -->
  <option value="my_play">My Custom Play</option>
</select>
```

---

## FAQ

**Q: Can I use external APIs in my play?**  
A: Yes! Use `load_data()` to fetch from APIs, just handle errors gracefully.

**Q: How do I add parameters to my play?**  
A: Use `self.params` dict. The API passes `params` from the request body.

**Q: Can I use pandas/numpy/other libraries?**  
A: Yes! Add them to `requirements.txt` and import in your agent file.

**Q: How do I test with real data?**  
A: Create a test script that instantiates your agent and calls `run()`.

**Q: Can I create plays outside the `aas/agents/` directory?**  
A: Yes! As long as you can import the class and register it, it works.

---

## Support

For questions or issues:
1. Check existing plays in `aas/agents/` for examples
2. Review the base class in `aas/agents/base.py`
3. See the registry implementation in `aas/plays/registry.py`

---

**Last Updated**: 2026-01-02  
**Version**: 1.0
