"""
Unit tests for Play Registry system.
"""

import pytest
from aas.plays.registry import PlayRegistry, PlaySpec, register_play, get_play, list_plays, get_agent
from aas.agents.base import AgentPlay


class MockAgent(AgentPlay):
    """Mock agent for testing."""
    
    def load_data(self):
        return {"test": "data"}
    
    def analyze(self, data):
        return {"metric": 100}
    
    def recommend_actions(self, analysis):
        return []


class TestPlayRegistry:
    """Tests for PlayRegistry class."""
    
    def setup_method(self):
        """Reset registry before each test."""
        PlayRegistry._instance = None
        PlayRegistry._plays = {}
    
    def test_singleton_pattern(self):
        """Test that PlayRegistry is a singleton."""
        registry1 = PlayRegistry()
        registry2 = PlayRegistry()
        assert registry1 is registry2
    
    def test_register_play(self):
        """Test registering a new play."""
        registry = PlayRegistry()
        
        spec = PlaySpec(
            id="test_play",
            label="Test Play",
            description="A test play",
            agent_class=MockAgent,
            tags=["test"],
            inputs_schema={},
            demo_seed=None,
            icon="🧪"
        )
        
        registry.register(spec)
        
        assert "test_play" in registry._plays
        assert registry._plays["test_play"].label == "Test Play"
    
    def test_register_duplicate_raises_error(self):
        """Test that registering duplicate play ID raises error."""
        registry = PlayRegistry()
        
        spec1 = PlaySpec(
            id="duplicate",
            label="First",
            description="First play",
            agent_class=MockAgent,
            tags=[],
            inputs_schema={},
            demo_seed=None,
            icon="🔴"
        )
        
        spec2 = PlaySpec(
            id="duplicate",
            label="Second",
            description="Second play",
            agent_class=MockAgent,
            tags=[],
            inputs_schema={},
            demo_seed=None,
            icon="🔵"
        )
        
        registry.register(spec1)
        
        with pytest.raises(ValueError, match="already registered"):
            registry.register(spec2)
    
    def test_get_play(self):
        """Test retrieving a play by ID."""
        registry = PlayRegistry()
        
        spec = PlaySpec(
            id="get_test",
            label="Get Test",
            description="Test retrieval",
            agent_class=MockAgent,
            tags=["retrieval"],
            inputs_schema={},
            demo_seed=None,
            icon="📥"
        )
        
        registry.register(spec)
        retrieved = registry.get("get_test")
        
        assert retrieved is not None
        assert retrieved.id == "get_test"
        assert retrieved.label == "Get Test"
    
    def test_get_nonexistent_play_returns_none(self):
        """Test that getting nonexistent play returns None."""
        registry = PlayRegistry()
        result = registry.get("nonexistent")
        assert result is None
    
    def test_list_plays(self):
        """Test listing all registered plays."""
        registry = PlayRegistry()
        
        spec1 = PlaySpec(
            id="play1",
            label="Play 1",
            description="First play",
            agent_class=MockAgent,
            tags=["tag1"],
            inputs_schema={},
            demo_seed=None,
            icon="1️⃣"
        )
        
        spec2 = PlaySpec(
            id="play2",
            label="Play 2",
            description="Second play",
            agent_class=MockAgent,
            tags=["tag2"],
            inputs_schema={},
            demo_seed=None,
            icon="2️⃣"
        )
        
        registry.register(spec1)
        registry.register(spec2)
        
        plays = registry.list()
        
        assert len(plays) == 2
        assert any(p["id"] == "play1" for p in plays)
        assert any(p["id"] == "play2" for p in plays)
    
    def test_get_agent_instantiates_correctly(self):
        """Test that get_agent returns an instance of the agent class."""
        registry = PlayRegistry()
        
        spec = PlaySpec(
            id="agent_test",
            label="Agent Test",
            description="Test agent instantiation",
            agent_class=MockAgent,
            tags=[],
            inputs_schema={},
            demo_seed=None,
            icon="🤖"
        )
        
        registry.register(spec)
        agent = registry.get_agent("agent_test")
        
        assert agent is not None
        assert isinstance(agent, MockAgent)
        assert isinstance(agent, AgentPlay)
    
    def test_get_agent_nonexistent_returns_none(self):
        """Test that get_agent returns None for nonexistent play."""
        registry = PlayRegistry()
        agent = registry.get_agent("nonexistent")
        assert agent is None


class TestGlobalFunctions:
    """Tests for global registry functions."""
    
    def setup_method(self):
        """Reset registry before each test."""
        PlayRegistry._instance = None
        PlayRegistry._plays = {}
    
    def test_register_play_function(self):
        """Test global register_play function."""
        register_play(
            id="global_test",
            label="Global Test",
            description="Test global function",
            agent_class=MockAgent,
            tags=["global"],
            inputs_schema={},
            demo_seed=None,
            icon="🌍"
        )
        
        play = get_play("global_test")
        assert play is not None
        assert play["id"] == "global_test"
    
    def test_list_plays_function(self):
        """Test global list_plays function."""
        register_play(
            id="list_test_1",
            label="List Test 1",
            description="First test",
            agent_class=MockAgent,
            tags=[],
            inputs_schema={},
            demo_seed=None,
            icon="📋"
        )
        
        register_play(
            id="list_test_2",
            label="List Test 2",
            description="Second test",
            agent_class=MockAgent,
            tags=[],
            inputs_schema={},
            demo_seed=None,
            icon="📝"
        )
        
        plays = list_plays()
        assert len(plays) >= 2
        assert any(p["id"] == "list_test_1" for p in plays)
        assert any(p["id"] == "list_test_2" for p in plays)
    
    def test_get_agent_function(self):
        """Test global get_agent function."""
        register_play(
            id="agent_func_test",
            label="Agent Function Test",
            description="Test get_agent function",
            agent_class=MockAgent,
            tags=[],
            inputs_schema={},
            demo_seed=None,
            icon="⚙️"
        )
        
        agent = get_agent("agent_func_test")
        assert agent is not None
        assert isinstance(agent, MockAgent)


class TestPlaySpecSerialization:
    """Tests for PlaySpec serialization."""
    
    def test_to_dict(self):
        """Test PlaySpec to_dict method."""
        spec = PlaySpec(
            id="serialize_test",
            label="Serialize Test",
            description="Test serialization",
            agent_class=MockAgent,
            tags=["serialize", "test"],
            inputs_schema={"param1": {"type": "string"}},
            demo_seed="test_seed",
            icon="💾"
        )
        
        result = spec.to_dict()
        
        assert result["id"] == "serialize_test"
        assert result["label"] == "Serialize Test"
        assert result["description"] == "Test serialization"
        assert result["tags"] == ["serialize", "test"]
        assert result["inputs_schema"] == {"param1": {"type": "string"}}
        assert result["demo_seed"] == "test_seed"
        assert result["icon"] == "💾"
        assert "agent_class" not in result  # Should not include class
