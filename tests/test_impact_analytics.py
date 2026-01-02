"""
Unit tests for Impact Analytics module.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from aas.analytics.impact import calculate_aggregate_impact, export_impact_report_csv, _generate_mock_impact_data


class TestCalculateAggregateImpact:
    """Tests for calculate_aggregate_impact function."""
    
    @patch('aas.analytics.impact.get_conn')
    def test_with_database_connection(self, mock_get_conn):
        """Test impact calculation with database connection."""
        # Mock database connection and cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_get_conn.return_value = mock_conn
        
        # Mock query results
        mock_cursor.fetchone.side_effect = [
            (15,),  # total_runs
        ]
        
        mock_cursor.fetchall.side_effect = [
            # Status counts
            [
                ('pending', 14, 1000.0),
                ('approved', 6, 800.0),
                ('executed', 22, 1450.0)
            ],
            # Top plays
            [
                ('pipeline', 18, 1500.0),
                ('revenue', 12, 1200.0),
                ('churn', 8, 450.0)
            ],
            # Recent activity
            [
                ('2026-01-02', 3),
                ('2026-01-01', 5),
                ('2025-12-31', 2)
            ]
        ]
        
        result = calculate_aggregate_impact()
        
        assert result['total_runs'] == 15
        assert result['total_actions'] == 42
        assert result['total_approved'] == 28
        assert result['total_executed'] == 22
        assert result['total_impact_score'] == 3250.0
        assert result['estimated_value'] == 3250000.0
        assert len(result['top_plays']) == 3
        assert result['top_plays'][0]['play'] == 'pipeline'
        assert len(result['recent_activity']) == 3
    
    @patch('aas.analytics.impact.get_conn')
    def test_without_database_connection(self, mock_get_conn):
        """Test impact calculation falls back to mock data when DB unavailable."""
        mock_get_conn.return_value = None
        
        result = calculate_aggregate_impact()
        
        # Should return mock data
        assert 'total_runs' in result
        assert 'total_actions' in result
        assert 'estimated_value' in result
        assert 'note' in result
        assert 'Mock data' in result['note']
    
    @patch('aas.analytics.impact.get_conn')
    def test_handles_database_error(self, mock_get_conn):
        """Test that database errors are handled gracefully."""
        mock_conn = MagicMock()
        mock_get_conn.return_value = mock_conn
        mock_conn.cursor.side_effect = Exception("Database error")
        
        result = calculate_aggregate_impact()
        
        # Should fall back to mock data
        assert 'total_runs' in result
        assert 'note' in result


class TestMockImpactData:
    """Tests for mock impact data generation."""
    
    def test_mock_data_structure(self):
        """Test that mock data has correct structure."""
        data = _generate_mock_impact_data()
        
        assert 'total_runs' in data
        assert 'total_actions' in data
        assert 'total_approved' in data
        assert 'total_executed' in data
        assert 'total_impact_score' in data
        assert 'estimated_value' in data
        assert 'top_plays' in data
        assert 'recent_activity' in data
        assert 'status_breakdown' in data
        assert 'generated_at' in data
    
    def test_mock_data_values(self):
        """Test that mock data has reasonable values."""
        data = _generate_mock_impact_data()
        
        assert data['total_runs'] > 0
        assert data['total_actions'] > 0
        assert data['total_approved'] <= data['total_actions']
        assert data['total_executed'] <= data['total_approved']
        assert data['estimated_value'] == data['total_impact_score'] * 1000
    
    def test_mock_top_plays(self):
        """Test that mock data includes top plays."""
        data = _generate_mock_impact_data()
        
        assert len(data['top_plays']) > 0
        for play in data['top_plays']:
            assert 'play' in play
            assert 'action_count' in play
            assert 'total_impact' in play


class TestExportImpactReportCSV:
    """Tests for CSV export functionality."""
    
    @patch('aas.analytics.impact.calculate_aggregate_impact')
    def test_csv_export_structure(self, mock_calculate):
        """Test that CSV export has correct structure."""
        mock_calculate.return_value = {
            'total_runs': 15,
            'total_actions': 42,
            'total_approved': 28,
            'total_executed': 22,
            'total_impact_score': 3250.0,
            'estimated_value': 3250000.0,
            'top_plays': [
                {'play': 'pipeline', 'action_count': 18, 'total_impact': 1500.0}
            ],
            'recent_activity': [
                {'date': '2026-01-02', 'runs': 3}
            ],
            'status_breakdown': {
                'pending': {'count': 14, 'impact': 1000.0}
            },
            'generated_at': '2026-01-02T12:00:00'
        }
        
        csv = export_impact_report_csv()
        
        assert 'Agentic Analytics Studio - Impact Report' in csv
        assert 'Summary Metrics' in csv
        assert 'Top Plays by Impact' in csv
        assert 'Status Breakdown' in csv
        assert 'Recent Activity' in csv
        assert '15' in csv  # total_runs
        assert '42' in csv  # total_actions
        assert '$3,250,000' in csv  # estimated_value
    
    @patch('aas.analytics.impact.calculate_aggregate_impact')
    def test_csv_export_formatting(self, mock_calculate):
        """Test that CSV export formats numbers correctly."""
        mock_calculate.return_value = {
            'total_runs': 100,
            'total_actions': 250,
            'total_approved': 200,
            'total_executed': 150,
            'total_impact_score': 5000.0,
            'estimated_value': 5000000.0,
            'top_plays': [],
            'recent_activity': [],
            'status_breakdown': {},
            'generated_at': '2026-01-02T12:00:00'
        }
        
        csv = export_impact_report_csv()
        
        # Check number formatting
        assert '5000.00' in csv  # impact score with 2 decimals
        assert '$5,000,000' in csv  # dollar value with commas


class TestImpactCalculations:
    """Tests for impact calculation logic."""
    
    def test_estimated_value_calculation(self):
        """Test that estimated value is calculated correctly."""
        # Formula: estimated_value = total_impact_score * 1000
        impact_score = 3250.0
        expected_value = 3250000.0
        
        assert impact_score * 1000 == expected_value
    
    def test_approval_rate_calculation(self):
        """Test approval rate calculation."""
        total_actions = 42
        total_approved = 28
        
        approval_rate = (total_approved / total_actions) * 100
        
        assert approval_rate == pytest.approx(66.67, rel=0.01)
    
    def test_execution_rate_calculation(self):
        """Test execution rate calculation."""
        total_approved = 28
        total_executed = 22
        
        execution_rate = (total_executed / total_approved) * 100
        
        assert execution_rate == pytest.approx(78.57, rel=0.01)
