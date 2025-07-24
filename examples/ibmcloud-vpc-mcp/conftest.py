"""
Pytest configuration and shared fixtures
"""

import pytest
import os
import logging

# Configure logging for tests
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Disable verbose logging from IBM SDK during tests
logging.getLogger('ibm_cloud_sdk_core').setLevel(logging.WARNING)
logging.getLogger('urllib3').setLevel(logging.WARNING)


def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line(
        "markers", "integration: mark test as integration test requiring real API access"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers automatically"""
    for item in items:
        # Mark integration tests
        if "integration" in item.nodeid:
            item.add_marker(pytest.mark.integration)
        
        # Mark slow tests
        if any(keyword in item.name.lower() for keyword in ['performance', 'large', 'concurrent']):
            item.add_marker(pytest.mark.slow)


@pytest.fixture(scope="session")
def api_key():
    """Get IBM Cloud API key from environment"""
    return os.getenv('IBM_CLOUD_API_KEY')


@pytest.fixture(scope="session") 
def test_region():
    """Get test region from environment or use default"""
    return os.getenv('IBM_CLOUD_TEST_REGION', 'us-south')


@pytest.fixture(scope="session")
def test_resource_group():
    """Get test resource group from environment"""
    return os.getenv('IBM_CLOUD_TEST_RESOURCE_GROUP')


@pytest.fixture
def mock_datetime():
    """Mock datetime for consistent testing"""
    from unittest.mock import patch
    from datetime import datetime
    
    fixed_time = datetime(2023, 12, 1, 12, 0, 0)
    
    with patch('utils.datetime') as mock_dt:
        mock_dt.now.return_value = fixed_time
        mock_dt.side_effect = lambda *args, **kw: datetime(*args, **kw)
        yield mock_dt
