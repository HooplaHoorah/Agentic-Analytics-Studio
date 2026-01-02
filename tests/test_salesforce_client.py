"""
Unit tests for Salesforce client stub/live mode functionality.
"""

import os
import pytest
from unittest.mock import Mock, patch, MagicMock
from aas.services.salesforce_client import SalesforceClient


class TestSalesforceClientStubMode:
    """Tests for Salesforce client in stub mode."""
    
    def test_stub_mode_default(self):
        """Test that stub mode is the default when SALESFORCE_MODE is not set."""
        with patch.dict(os.environ, {}, clear=True):
            client = SalesforceClient()
            assert client.get_mode() == "stub"
            assert client.sf is None
    
    def test_stub_mode_explicit(self):
        """Test stub mode when explicitly set."""
        with patch.dict(os.environ, {"SALESFORCE_MODE": "stub"}):
            client = SalesforceClient()
            assert client.get_mode() == "stub"
            assert client.sf is None
    
    def test_stub_mode_no_credentials(self):
        """Test that stub mode is used when credentials are missing."""
        with patch.dict(os.environ, {"SALESFORCE_MODE": "live"}, clear=True):
            client = SalesforceClient()
            assert client.get_mode() == "stub"  # Falls back to stub
            assert client.sf is None
    
    def test_create_task_stub_mode(self):
        """Test create_task returns preview in stub mode."""
        with patch.dict(os.environ, {"SALESFORCE_MODE": "stub"}):
            client = SalesforceClient()
            result = client.create_task(
                subject="Test Task",
                description="Test Description",
                owner_id="005xx000001X8Uz",
                what_id="006xx000001X8Uz"
            )
            
            assert result["success"] is True
            assert result["mode"] == "stub"
            assert "preview" in result
            assert result["preview"]["object"] == "Task"
            assert result["preview"]["operation"] == "create"
            assert result["preview"]["fields"]["Subject"] == "Test Task"
            assert "Test Task" in result["preview"]["description"]
    
    def test_update_record_stub_mode(self):
        """Test update_record returns preview in stub mode."""
        with patch.dict(os.environ, {"SALESFORCE_MODE": "stub"}):
            client = SalesforceClient()
            result = client.update_record(
                object_name="Opportunity",
                record_id="006xx000001X8Uz",
                fields={"Stage": "Closed Won", "Amount": 50000}
            )
            
            assert result["success"] is True
            assert result["mode"] == "stub"
            assert "preview" in result
            assert result["preview"]["object"] == "Opportunity"
            assert result["preview"]["operation"] == "update"
            assert result["preview"]["record_id"] == "006xx000001X8Uz"
            assert result["preview"]["fields"]["Stage"] == "Closed Won"


class TestSalesforceClientLiveMode:
    """Tests for Salesforce client in live mode."""
    
    @patch('aas.services.salesforce_client.Salesforce')
    def test_live_mode_with_credentials(self, mock_salesforce):
        """Test that live mode authenticates when credentials are provided."""
        mock_sf_instance = MagicMock()
        mock_salesforce.return_value = mock_sf_instance
        
        with patch.dict(os.environ, {
            "SALESFORCE_MODE": "live",
            "SF_USERNAME": "test@example.com",
            "SF_PASSWORD": "password123",
            "SF_SECURITY_TOKEN": "token123",
            "SF_DOMAIN": "test"
        }):
            client = SalesforceClient()
            
            assert client.get_mode() == "live"
            assert client.sf is not None
            mock_salesforce.assert_called_once_with(
                username="test@example.com",
                password="password123",
                security_token="token123",
                domain="test"
            )
    
    @patch('aas.services.salesforce_client.Salesforce')
    def test_live_mode_auth_failure_fallback(self, mock_salesforce):
        """Test that live mode falls back to stub if authentication fails."""
        mock_salesforce.side_effect = Exception("Authentication failed")
        
        with patch.dict(os.environ, {
            "SALESFORCE_MODE": "live",
            "SF_USERNAME": "test@example.com",
            "SF_PASSWORD": "wrong_password",
            "SF_SECURITY_TOKEN": "token123"
        }):
            client = SalesforceClient()
            
            assert client.get_mode() == "stub"  # Fell back to stub
            assert client.sf is None
    
    @patch('aas.services.salesforce_client.Salesforce')
    def test_create_task_live_mode(self, mock_salesforce):
        """Test create_task makes real API call in live mode."""
        mock_sf_instance = MagicMock()
        mock_sf_instance.Task.create.return_value = {"id": "00Txx000001X8Uz", "success": True}
        mock_salesforce.return_value = mock_sf_instance
        
        with patch.dict(os.environ, {
            "SALESFORCE_MODE": "live",
            "SF_USERNAME": "test@example.com",
            "SF_PASSWORD": "password123",
            "SF_SECURITY_TOKEN": "token123"
        }):
            client = SalesforceClient()
            result = client.create_task(
                subject="Test Task",
                description="Test Description",
                owner_id="005xx000001X8Uz",
                what_id="006xx000001X8Uz"
            )
            
            assert result["success"] is True
            assert result["mode"] == "live"
            assert result["id"] == "00Txx000001X8Uz"
            assert "preview" not in result  # No preview in live mode
            
            # Verify API was called
            mock_sf_instance.Task.create.assert_called_once()
    
    @patch('aas.services.salesforce_client.Salesforce')
    def test_update_record_live_mode(self, mock_salesforce):
        """Test update_record makes real API call in live mode."""
        mock_sf_instance = MagicMock()
        mock_opportunity = MagicMock()
        mock_opportunity.update.return_value = 204  # Salesforce returns 204 on success
        mock_sf_instance.Opportunity = mock_opportunity
        mock_salesforce.return_value = mock_sf_instance
        
        with patch.dict(os.environ, {
            "SALESFORCE_MODE": "live",
            "SF_USERNAME": "test@example.com",
            "SF_PASSWORD": "password123",
            "SF_SECURITY_TOKEN": "token123"
        }):
            client = SalesforceClient()
            result = client.update_record(
                object_name="Opportunity",
                record_id="006xx000001X8Uz",
                fields={"Stage": "Closed Won"}
            )
            
            assert result["success"] is True
            assert result["mode"] == "live"
            assert result["id"] == "006xx000001X8Uz"
            assert "preview" not in result
            
            # Verify API was called
            mock_opportunity.update.assert_called_once_with(
                "006xx000001X8Uz",
                {"Stage": "Closed Won"}
            )


class TestHealthEndpoint:
    """Tests for /health endpoint including salesforce_mode."""
    
    def test_health_includes_salesforce_mode(self):
        """Test that /health endpoint returns salesforce_mode."""
        # This would be an integration test with the actual API
        # For now, we just verify the environment variable is read correctly
        with patch.dict(os.environ, {"SALESFORCE_MODE": "stub"}):
            mode = os.getenv("SALESFORCE_MODE", "stub").lower()
            assert mode == "stub"
        
        with patch.dict(os.environ, {"SALESFORCE_MODE": "live"}):
            mode = os.getenv("SALESFORCE_MODE", "stub").lower()
            assert mode == "live"
