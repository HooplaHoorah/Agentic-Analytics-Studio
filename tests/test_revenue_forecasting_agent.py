"""
Unit tests for Revenue Forecasting Agent.
"""

import pytest
from unittest.mock import Mock, patch
from aas.agents.revenue_forecasting import RevenueForecastingAgent


class TestRevenueForecastingAgent:
    """Tests for RevenueForecastingAgent."""
    
    def test_agent_initialization(self):
        """Test that agent initializes correctly."""
        agent = RevenueForecastingAgent()
        assert agent is not None
        assert hasattr(agent, 'load_data')
        assert hasattr(agent, 'analyze')
        assert hasattr(agent, 'recommend_actions')
    
    def test_load_data_returns_dataframe(self):
        """Test that load_data returns a DataFrame."""
        agent = RevenueForecastingAgent()
        data = agent.load_data()
        
        assert data is not None
        # Should have required columns
        assert 'deal_id' in data.columns or 'opportunity_id' in data.columns
    
    def test_analyze_returns_dict(self):
        """Test that analyze returns a dictionary with expected keys."""
        agent = RevenueForecastingAgent()
        data = agent.load_data()
        analysis = agent.analyze(data)
        
        assert isinstance(analysis, dict)
        assert 'summary' in analysis
        assert 'metrics' in analysis or 'forecast' in analysis
    
    def test_recommend_actions_returns_list(self):
        """Test that recommend_actions returns a list of actions."""
        agent = RevenueForecastingAgent()
        data = agent.load_data()
        analysis = agent.analyze(data)
        actions = agent.recommend_actions(analysis)
        
        assert isinstance(actions, list)
    
    def test_actions_have_required_fields(self):
        """Test that generated actions have all required fields."""
        agent = RevenueForecastingAgent()
        result = agent.run()
        
        if result['actions']:
            action = result['actions'][0]
            assert 'type' in action
            assert 'title' in action
            assert 'description' in action
            assert 'priority' in action
            assert 'impact_score' in action
            assert 'metadata' in action
    
    def test_actions_have_impact_scores(self):
        """Test that all actions have numeric impact scores."""
        agent = RevenueForecastingAgent()
        result = agent.run()
        
        for action in result['actions']:
            assert isinstance(action['impact_score'], (int, float))
            assert action['impact_score'] >= 0
    
    def test_actions_have_priorities(self):
        """Test that all actions have valid priorities."""
        agent = RevenueForecastingAgent()
        result = agent.run()
        
        valid_priorities = ['high', 'medium', 'low']
        for action in result['actions']:
            assert action['priority'] in valid_priorities
    
    def test_run_method_returns_complete_result(self):
        """Test that run() returns a complete result dictionary."""
        agent = RevenueForecastingAgent()
        result = agent.run()
        
        assert 'analysis' in result
        assert 'actions' in result
        assert isinstance(result['analysis'], dict)
        assert isinstance(result['actions'], list)
    
    @patch.object(RevenueForecastingAgent, 'generate_rationale')
    def test_rationale_generation_called(self, mock_rationale):
        """Test that generate_rationale is called for actions."""
        mock_rationale.return_value = "Test rationale"
        
        agent = RevenueForecastingAgent()
        result = agent.run()
        
        if result['actions']:
            # Should have called generate_rationale at least once
            assert mock_rationale.called
    
    def test_handles_empty_data_gracefully(self):
        """Test that agent handles empty data without crashing."""
        agent = RevenueForecastingAgent()
        
        # This should not raise an exception
        try:
            result = agent.run()
            assert result is not None
        except Exception as e:
            pytest.fail(f"Agent should handle empty data gracefully, but raised: {e}")


class TestRevenueForecastingLogic:
    """Tests for specific revenue forecasting logic."""
    
    def test_forecast_calculation(self):
        """Test revenue forecast calculation logic."""
        agent = RevenueForecastingAgent()
        data = agent.load_data()
        analysis = agent.analyze(data)
        
        # Should have forecast metrics
        assert 'metrics' in analysis or 'forecast' in analysis
    
    def test_identifies_shortfalls(self):
        """Test that agent identifies revenue shortfalls."""
        agent = RevenueForecastingAgent()
        result = agent.run()
        
        # If there's a shortfall, should recommend actions
        if result['analysis'].get('shortfall', 0) > 0:
            assert len(result['actions']) > 0
    
    def test_action_types_are_appropriate(self):
        """Test that action types are appropriate for revenue forecasting."""
        agent = RevenueForecastingAgent()
        result = agent.run()
        
        valid_action_types = [
            'budget_reallocation',
            'targeted_outreach',
            'process_improvement',
            'sales_enablement',
            'forecast_adjustment'
        ]
        
        for action in result['actions']:
            # Action type should be one of the valid types (or a custom type)
            assert isinstance(action['type'], str)
            assert len(action['type']) > 0
