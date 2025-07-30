"""
Unit tests for IBM Cloud VPC utilities
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
import json

from utils import (
    VPCManager, 
    create_vpc_manager, 
    analyze_security_rule_risk, 
    analyze_backup_policy_health
)
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_cloud_sdk_core import ApiException


class TestVPCManager:
    """Test cases for VPCManager class"""
    
    @pytest.fixture
    def mock_authenticator(self):
        """Create a mock IAM authenticator"""
        return Mock(spec=IAMAuthenticator)
    
    @pytest.fixture
    def vpc_manager(self, mock_authenticator):
        """Create a VPCManager instance with mocked authenticator"""
        return VPCManager(mock_authenticator)
    
    @pytest.fixture
    def mock_vpc_service(self):
        """Create a mock VPC service"""
        service = Mock()
        service.set_service_url = Mock()
        return service
    
    def test_init(self, mock_authenticator):
        """Test VPCManager initialization"""
        manager = VPCManager(mock_authenticator)
        assert manager.authenticator == mock_authenticator
        assert manager.vpc_clients == {}
        assert manager.regions == []
    
    @patch('utils.ibm_vpc.VpcV1')
    def test_get_vpc_client_new_region(self, mock_vpc_class, vpc_manager):
        """Test creating a new VPC client for a region"""
        mock_service = Mock()
        mock_vpc_class.return_value = mock_service
        
        client = vpc_manager._get_vpc_client('us-south')
        
        mock_vpc_class.assert_called_once_with(
            version='2025-04-08',
            authenticator=vpc_manager.authenticator
        )
        mock_service.set_service_url.assert_called_once_with(
            'https://us-south.iaas.cloud.ibm.com/v1'
        )
        assert vpc_manager.vpc_clients['us-south'] == mock_service
        assert client == mock_service
    
    @patch('utils.ibm_vpc.VpcV1')
    def test_get_vpc_client_cached_region(self, mock_vpc_class, vpc_manager):
        """Test retrieving cached VPC client"""
        mock_service = Mock()
        vpc_manager.vpc_clients['us-south'] = mock_service
        
        client = vpc_manager._get_vpc_client('us-south')
        
        mock_vpc_class.assert_not_called()
        assert client == mock_service
    
    @pytest.mark.asyncio
    async def test_list_regions_success(self, vpc_manager):
        """Test successful region listing"""
        mock_service = Mock()
        mock_response = {
            'regions': [
                {'name': 'us-south', 'status': 'available'},
                {'name': 'us-east', 'status': 'available'}
            ]
        }
        mock_service.list_regions.return_value.get_result.return_value = mock_response
        
        with patch.object(vpc_manager, '_get_vpc_client', return_value=mock_service):
            result = await vpc_manager.list_regions()
        
        assert result['count'] == 2
        assert len(result['regions']) == 2
        assert vpc_manager.regions == ['us-south', 'us-east']
    
    @pytest.mark.asyncio
    async def test_list_vpcs_single_region(self, vpc_manager):
        """Test listing VPCs in a single region"""
        mock_service = Mock()
        mock_response = {
            'vpcs': [
                {'id': 'vpc-1', 'name': 'test-vpc-1'},
                {'id': 'vpc-2', 'name': 'test-vpc-2'}
            ]
        }
        mock_service.list_vpcs.return_value.get_result.return_value = mock_response
        
        with patch.object(vpc_manager, '_get_vpc_client', return_value=mock_service):
            result = await vpc_manager.list_vpcs('us-south')
        
        assert result['count'] == 2
        assert len(result['vpcs']) == 2
        assert all(vpc['region'] == 'us-south' for vpc in result['vpcs'])
        assert result['regions_checked'] == ['us-south']
    
    @pytest.mark.asyncio
    async def test_list_vpcs_all_regions(self, vpc_manager):
        """Test listing VPCs across all regions"""
        vpc_manager.regions = ['us-south', 'us-east']
        
        mock_service = Mock()
        mock_response = {
            'vpcs': [{'id': 'vpc-1', 'name': 'test-vpc'}]
        }
        mock_service.list_vpcs.return_value.get_result.return_value = mock_response
        
        with patch.object(vpc_manager, '_get_vpc_client', return_value=mock_service):
            result = await vpc_manager.list_vpcs()
        
        assert result['count'] == 2  # One VPC per region
        assert result['regions_checked'] == ['us-south', 'us-east']
    
    @pytest.mark.asyncio
    async def test_list_vpcs_with_api_exception(self, vpc_manager):
        """Test handling API exceptions when listing VPCs"""
        vpc_manager.regions = ['us-south', 'us-east']
        
        def mock_get_client(region):
            service = Mock()
            if region == 'us-south':
                service.list_vpcs.return_value.get_result.return_value = {
                    'vpcs': [{'id': 'vpc-1', 'name': 'test-vpc'}]
                }
            else:
                service.list_vpcs.side_effect = ApiException(
                    message="Region not available", code=404
                )
            return service
        
        with patch.object(vpc_manager, '_get_vpc_client', side_effect=mock_get_client):
            result = await vpc_manager.list_vpcs()
        
        assert result['count'] == 1  # Only successful region
        assert result['vpcs'][0]['region'] == 'us-south'
    
    @pytest.mark.asyncio
    async def test_get_vpc_success(self, vpc_manager):
        """Test getting a specific VPC"""
        mock_service = Mock()
        mock_vpc = {'id': 'vpc-1', 'name': 'test-vpc', 'status': 'available'}
        mock_service.get_vpc.return_value.get_result.return_value = mock_vpc
        
        with patch.object(vpc_manager, '_get_vpc_client', return_value=mock_service):
            result = await vpc_manager.get_vpc('vpc-1', 'us-south')
        
        mock_service.get_vpc.assert_called_once_with(id='vpc-1')
        assert result['region'] == 'us-south'
        assert result['id'] == 'vpc-1'
    
    @pytest.mark.asyncio
    async def test_list_subnets_with_vpc_filter(self, vpc_manager):
        """Test listing subnets filtered by VPC"""
        mock_service = Mock()
        mock_response = {
            'subnets': [
                {'id': 'subnet-1', 'vpc': {'id': 'vpc-1'}, 'available_ipv4_address_count': 250},
                {'id': 'subnet-2', 'vpc': {'id': 'vpc-2'}, 'available_ipv4_address_count': 100},
                {'id': 'subnet-3', 'vpc': {'id': 'vpc-1'}, 'available_ipv4_address_count': 200}
            ]
        }
        mock_service.list_subnets.return_value.get_result.return_value = mock_response
        
        with patch.object(vpc_manager, '_get_vpc_client', return_value=mock_service):
            result = await vpc_manager.list_subnets('us-south', vpc_id='vpc-1')
        
        assert result['count'] == 2  # Only subnets in vpc-1
        assert all(subnet['vpc']['id'] == 'vpc-1' for subnet in result['subnets'])
        assert result['vpc_filter'] == 'vpc-1'
    
    @pytest.mark.asyncio
    async def test_analyze_ssh_security_groups(self, vpc_manager):
        """Test SSH security group analysis"""
        mock_service = Mock()
        
        # Mock security groups response
        sg_response = {
            'security_groups': [
                {'id': 'sg-1', 'name': 'risky-sg', 'vpc': {'id': 'vpc-1'}},
                {'id': 'sg-2', 'name': 'safe-sg', 'vpc': {'id': 'vpc-1'}}
            ]
        }
        mock_service.list_security_groups.return_value.get_result.return_value = sg_response
        
        # Mock rules responses
        def mock_list_rules(security_group_id):
            if security_group_id == 'sg-1':
                # Risky rule: SSH from anywhere
                return Mock(get_result=lambda: {
                    'rules': [{
                        'id': 'rule-1',
                        'protocol': 'tcp',
                        'direction': 'inbound',
                        'port_min': 22,
                        'port_max': 22,
                        'remote': {'cidr_block': '0.0.0.0/0'}
                    }]
                })
            else:
                # Safe rule: SSH from specific IP
                return Mock(get_result=lambda: {
                    'rules': [{
                        'id': 'rule-2',
                        'protocol': 'tcp',
                        'direction': 'inbound',
                        'port_min': 22,
                        'port_max': 22,
                        'remote': {'cidr_block': '10.0.0.0/8'}
                    }]
                })
        
        mock_service.list_security_group_rules = mock_list_rules
        
        with patch.object(vpc_manager, '_get_vpc_client', return_value=mock_service):
            result = await vpc_manager.analyze_ssh_security_groups('us-south', 'vpc-1')
        
        assert result['count'] == 1
        assert len(result['risky_security_groups']) == 1
        assert result['risky_security_groups'][0]['security_group_name'] == 'risky-sg'
        assert result['analysis_type'] == 'SSH access from 0.0.0.0/0'
    
    @pytest.mark.asyncio
    async def test_list_backup_policies_success(self, vpc_manager):
        """Test successful backup policy listing"""
        mock_service = Mock()
        mock_response = {
            'backup_policies': [
                {'id': 'policy-1', 'name': 'daily-backup'},
                {'id': 'policy-2', 'name': 'weekly-backup'}
            ]
        }
        mock_service.list_backup_policies.return_value.get_result.return_value = mock_response
        
        with patch.object(vpc_manager, '_get_vpc_client', return_value=mock_service):
            result = await vpc_manager.list_backup_policies('us-south', name='daily')
        
        mock_service.list_backup_policies.assert_called_once_with(
            start=None,
            limit=None,
            resource_group_id=None,
            name='daily',
            tag=None
        )
        assert result['count'] == 2
        assert all(policy['region'] == 'us-south' for policy in result['backup_policies'])
    
    @pytest.mark.asyncio
    async def test_get_vpc_resources_summary(self, vpc_manager):
        """Test VPC resources summary generation"""
        # Mock all the individual method calls
        with patch.object(vpc_manager, 'get_vpc') as mock_get_vpc, \
             patch.object(vpc_manager, 'list_subnets') as mock_list_subnets, \
             patch.object(vpc_manager, 'list_instances') as mock_list_instances, \
             patch.object(vpc_manager, 'list_security_groups') as mock_list_sg, \
             patch.object(vpc_manager, 'list_public_gateways') as mock_list_pg, \
             patch.object(vpc_manager, 'analyze_ssh_security_groups') as mock_analyze_ssh:
            
            # Setup mock returns
            mock_get_vpc.return_value = {
                'name': 'test-vpc', 'status': 'available', 'created_at': '2023-01-01T00:00:00Z'
            }
            mock_list_subnets.return_value = {
                'count': 2, 'subnets': [
                    {'zone': {'name': 'us-south-1'}},
                    {'zone': {'name': 'us-south-2'}}
                ]
            }
            mock_list_instances.return_value = {
                'count': 3, 'instances': [
                    {'status': 'running'},
                    {'status': 'running'},
                    {'status': 'stopped'}
                ]
            }
            mock_list_sg.return_value = {'count': 2}
            mock_list_pg.return_value = {'count': 1}
            mock_analyze_ssh.return_value = {
                'count': 1, 'risky_security_groups': [
                    {'security_group_name': 'risky-sg', 'security_group_id': 'sg-1'}
                ]
            }
            
            result = await vpc_manager.get_vpc_resources_summary('vpc-1', 'us-south')
        
        assert result['vpc_id'] == 'vpc-1'
        assert result['region'] == 'us-south'
        assert result['vpc_details']['name'] == 'test-vpc'
        assert result['resources']['subnets']['count'] == 2
        assert result['resources']['instances']['count'] == 3
        assert result['resources']['instances']['by_status']['running'] == 2
        assert result['resources']['instances']['by_status']['stopped'] == 1
        assert result['security_analysis']['ssh_open_to_internet']['risky_groups_count'] == 1


class TestUtilityFunctions:
    """Test cases for utility functions"""
    
    @pytest.mark.asyncio
    async def test_create_vpc_manager(self):
        """Test VPC manager creation with API key"""
        with patch('utils.IAMAuthenticator') as mock_auth_class:
            mock_authenticator = Mock()
            mock_auth_class.return_value = mock_authenticator
            
            manager = await create_vpc_manager('test-api-key')
            
            mock_auth_class.assert_called_once_with(apikey='test-api-key')
            assert isinstance(manager, VPCManager)
            assert manager.authenticator == mock_authenticator
    
    def test_analyze_security_rule_risk_high_risk(self):
        """Test security rule risk analysis for high-risk rule"""
        rule = {
            'id': 'rule-1',
            'protocol': 'tcp',
            'direction': 'inbound',
            'port_min': 22,
            'port_max': 22,
            'remote': {'cidr_block': '0.0.0.0/0'}
        }
        
        result = analyze_security_rule_risk(rule)
        
        assert result['risk_level'] == 'high'
        assert 'Source allows traffic from anywhere (0.0.0.0/0)' in result['risk_factors']
        assert 'Exposes SSH (port 22)' in result['risk_factors']
        assert result['protocol'] == 'tcp'
        assert result['port_range'] == '22-22'
    
    def test_analyze_security_rule_risk_medium_risk(self):
        """Test security rule risk analysis for medium-risk rule"""
        rule = {
            'id': 'rule-2',
            'protocol': 'tcp',
            'direction': 'inbound',
            'port_min': 3389,
            'port_max': 3389,
            'remote': {'cidr_block': '10.0.0.0/8'}
        }
        
        result = analyze_security_rule_risk(rule)
        
        assert result['risk_level'] == 'medium'
        assert 'Exposes RDP (port 3389)' in result['risk_factors']
        assert len(result['risk_factors']) == 1  # No 0.0.0.0/0 risk
    
    def test_analyze_security_rule_risk_low_risk(self):
        """Test security rule risk analysis for low-risk rule"""
        rule = {
            'id': 'rule-3',
            'protocol': 'tcp',
            'direction': 'inbound',
            'port_min': 80,
            'port_max': 80,
            'remote': {'cidr_block': '10.0.0.0/8'}
        }
        
        result = analyze_security_rule_risk(rule)
        
        assert result['risk_level'] == 'low'
        assert len(result['risk_factors']) == 0
    
    def test_analyze_security_rule_risk_wide_port_range(self):
        """Test security rule risk analysis for wide port range"""
        rule = {
            'id': 'rule-4',
            'protocol': 'tcp',
            'direction': 'inbound',
            'port_min': 1000,
            'port_max': 5000,
            'remote': {'cidr_block': '10.0.0.0/8'}
        }
        
        result = analyze_security_rule_risk(rule)
        
        assert result['risk_level'] == 'medium'
        assert 'Very wide port range (1000-5000)' in result['risk_factors']
    
    def test_analyze_backup_policy_health_healthy(self):
        """Test backup policy health analysis for healthy policy"""
        policy = {
            'id': 'policy-1',
            'lifecycle_state': 'stable'
        }
        
        jobs = [
            {'status': 'completed', 'created_at': '2023-12-01T00:00:00Z'},
            {'status': 'completed', 'created_at': '2023-11-30T00:00:00Z'},
            {'status': 'completed', 'created_at': '2023-11-29T00:00:00Z'}
        ]
        
        result = analyze_backup_policy_health(policy, jobs)
        
        assert result['status'] == 'healthy'
        assert result['health_score'] >= 80
        assert len(result['issues']) == 0
    
    def test_analyze_backup_policy_health_critical(self):
        """Test backup policy health analysis for critical policy"""
        policy = {
            'id': 'policy-2',
            'lifecycle_state': 'failed'
        }
        
        jobs = [
            {'status': 'failed', 'created_at': '2023-12-01T00:00:00Z'},
            {'status': 'failed', 'created_at': '2023-11-30T00:00:00Z'}
        ]
        
        result = analyze_backup_policy_health(policy, jobs)
        
        assert result['status'] == 'critical'
        assert result['health_score'] < 60
        assert any('failed state' in issue for issue in result['issues'])
        assert any('failure rate' in issue for issue in result['issues'])
    
    def test_analyze_backup_policy_health_no_jobs(self):
        """Test backup policy health analysis with no jobs"""
        policy = {
            'id': 'policy-3',
            'lifecycle_state': 'stable'
        }
        
        jobs = []
        
        result = analyze_backup_policy_health(policy, jobs)
        
        assert result['status'] == 'warning'
        assert 'No backup jobs found' in result['issues']
        assert 'Verify that backup schedules are active' in result['recommendations']


@pytest.fixture
def sample_vpc_data():
    """Sample VPC data for testing"""
    return {
        'vpcs': [
            {
                'id': 'vpc-1',
                'name': 'production-vpc',
                'status': 'available',
                'created_at': '2023-01-01T00:00:00Z'
            },
            {
                'id': 'vpc-2', 
                'name': 'development-vpc',
                'status': 'available',
                'created_at': '2023-01-02T00:00:00Z'
            }
        ]
    }


@pytest.fixture
def sample_security_group_data():
    """Sample security group data for testing"""
    return {
        'security_groups': [
            {
                'id': 'sg-1',
                'name': 'web-sg',
                'vpc': {'id': 'vpc-1'},
                'rules': [
                    {
                        'id': 'rule-1',
                        'protocol': 'tcp',
                        'direction': 'inbound',
                        'port_min': 80,
                        'port_max': 80,
                        'remote': {'cidr_block': '0.0.0.0/0'}
                    }
                ]
            }
        ]
    }


class TestIntegrationScenarios:
    """Integration test scenarios"""
    
    @pytest.mark.asyncio
    async def test_full_vpc_analysis_workflow(self, sample_vpc_data):
        """Test a complete VPC analysis workflow"""
        authenticator = Mock(spec=IAMAuthenticator)
        manager = VPCManager(authenticator)
        
        # Mock the service calls
        with patch.object(manager, '_get_vpc_client') as mock_get_client:
            mock_service = Mock()
            mock_get_client.return_value = mock_service
            
            # Setup mock responses
            mock_service.list_vpcs.return_value.get_result.return_value = sample_vpc_data
            mock_service.list_subnets.return_value.get_result.return_value = {'subnets': []}
            mock_service.list_instances.return_value.get_result.return_value = {'instances': []}
            
            # Test the workflow
            vpcs = await manager.list_vpcs('us-south')
            assert vpcs['count'] == 2
            
            for vpc in vpcs['vpcs']:
                subnets = await manager.list_subnets('us-south', vpc['id'])
                instances = await manager.list_instances('us-south', vpc['id'])
                
                assert 'subnets' in subnets
                assert 'instances' in instances


class TestVPNMethods:
    """Test cases for VPN-related methods"""
    
    @pytest.fixture
    def mock_authenticator(self):
        """Create a mock IAM authenticator"""
        return Mock(spec=IAMAuthenticator)
    
    @pytest.fixture
    def vpc_manager(self, mock_authenticator):
        """Create a VPCManager instance with mocked authenticator"""
        return VPCManager(mock_authenticator)
    
    @pytest.fixture
    def sample_vpn_gateway_data(self):
        """Sample VPN gateway data for testing"""
        return {
            'vpn_gateways': [
                {
                    'id': 'vpn-gateway-1',
                    'name': 'main-site-to-site',
                    'status': 'available',
                    'vpc': {'id': 'vpc-1', 'name': 'main-vpc'},
                    'created_at': '2023-01-01T00:00:00Z',
                    'connections': []
                },
                {
                    'id': 'vpn-gateway-2', 
                    'name': 'backup-gateway',
                    'status': 'available',
                    'vpc': {'id': 'vpc-2', 'name': 'backup-vpc'},
                    'created_at': '2023-01-02T00:00:00Z',
                    'connections': []
                }
            ]
        }
    
    @pytest.fixture
    def sample_vpn_server_data(self):
        """Sample VPN server data for testing"""
        return {
            'vpn_servers': [
                {
                    'id': 'vpn-server-1',
                    'name': 'client-access-server',
                    'status': 'available',
                    'created_at': '2023-01-01T00:00:00Z',
                    'client_ip_pool': '192.168.1.0/24',
                    'port': 443
                },
                {
                    'id': 'vpn-server-2',
                    'name': 'dev-access-server', 
                    'status': 'available',
                    'created_at': '2023-01-02T00:00:00Z',
                    'client_ip_pool': '192.168.2.0/24',
                    'port': 443
                }
            ]
        }
    
    @pytest.mark.asyncio
    async def test_list_vpn_gateways(self, vpc_manager, sample_vpn_gateway_data):
        """Test listing VPN gateways"""
        with patch.object(vpc_manager, '_get_vpc_client') as mock_get_client:
            mock_service = Mock()
            mock_get_client.return_value = mock_service
            mock_service.list_vpn_gateways.return_value.get_result.return_value = sample_vpn_gateway_data
            
            result = await vpc_manager.list_vpn_gateways('us-south')
            
            assert result['count'] == 2
            assert result['region'] == 'us-south'
            assert result['vpc_id'] is None
            assert len(result['vpn_gateways']) == 2
            assert result['vpn_gateways'][0]['id'] == 'vpn-gateway-1'
            assert result['vpn_gateways'][0]['region'] == 'us-south'
            
            mock_service.list_vpn_gateways.assert_called_once_with(limit=50)
    
    @pytest.mark.asyncio
    async def test_list_vpn_gateways_with_vpc_filter(self, vpc_manager, sample_vpn_gateway_data):
        """Test listing VPN gateways with VPC filtering"""
        with patch.object(vpc_manager, '_get_vpc_client') as mock_get_client:
            mock_service = Mock()
            mock_get_client.return_value = mock_service
            mock_service.list_vpn_gateways.return_value.get_result.return_value = sample_vpn_gateway_data
            
            result = await vpc_manager.list_vpn_gateways('us-south', vpc_id='vpc-1')
            
            assert result['count'] == 1
            assert result['region'] == 'us-south'
            assert result['vpc_id'] == 'vpc-1'
            assert len(result['vpn_gateways']) == 1
            assert result['vpn_gateways'][0]['vpc']['id'] == 'vpc-1'
    
    @pytest.mark.asyncio
    async def test_get_vpn_gateway(self, vpc_manager):
        """Test getting a specific VPN gateway"""
        gateway_data = {
            'id': 'vpn-gateway-1',
            'name': 'main-site-to-site',
            'status': 'available',
            'vpc': {'id': 'vpc-1', 'name': 'main-vpc'}
        }
        
        with patch.object(vpc_manager, '_get_vpc_client') as mock_get_client:
            mock_service = Mock()
            mock_get_client.return_value = mock_service
            mock_service.get_vpn_gateway.return_value.get_result.return_value = gateway_data
            
            result = await vpc_manager.get_vpn_gateway('vpn-gateway-1', 'us-south')
            
            assert result['id'] == 'vpn-gateway-1'
            assert result['region'] == 'us-south'
            
            mock_service.get_vpn_gateway.assert_called_once_with('vpn-gateway-1')
    
    @pytest.mark.asyncio
    async def test_list_vpn_servers(self, vpc_manager, sample_vpn_server_data):
        """Test listing VPN servers"""
        with patch.object(vpc_manager, '_get_vpc_client') as mock_get_client:
            mock_service = Mock()
            mock_get_client.return_value = mock_service
            mock_service.list_vpn_servers.return_value.get_result.return_value = sample_vpn_server_data
            
            result = await vpc_manager.list_vpn_servers('us-south')
            
            assert result['count'] == 2
            assert result['region'] == 'us-south'
            assert len(result['vpn_servers']) == 2
            assert result['vpn_servers'][0]['id'] == 'vpn-server-1'
            assert result['vpn_servers'][0]['region'] == 'us-south'
            
            mock_service.list_vpn_servers.assert_called_once_with(limit=50)
    
    @pytest.mark.asyncio
    async def test_list_vpn_servers_with_name_filter(self, vpc_manager, sample_vpn_server_data):
        """Test listing VPN servers with name filtering"""
        with patch.object(vpc_manager, '_get_vpc_client') as mock_get_client:
            mock_service = Mock()
            mock_get_client.return_value = mock_service
            mock_service.list_vpn_servers.return_value.get_result.return_value = sample_vpn_server_data
            
            result = await vpc_manager.list_vpn_servers('us-south', name='client-access-server')
            
            assert result['count'] == 2
            assert result['region'] == 'us-south'
            
            mock_service.list_vpn_servers.assert_called_once_with(limit=50, name='client-access-server')
    
    @pytest.mark.asyncio
    async def test_get_vpn_server(self, vpc_manager):
        """Test getting a specific VPN server"""
        server_data = {
            'id': 'vpn-server-1',
            'name': 'client-access-server',
            'status': 'available',
            'client_ip_pool': '192.168.1.0/24'
        }
        
        with patch.object(vpc_manager, '_get_vpc_client') as mock_get_client:
            mock_service = Mock()
            mock_get_client.return_value = mock_service
            mock_service.get_vpn_server.return_value.get_result.return_value = server_data
            
            result = await vpc_manager.get_vpn_server('vpn-server-1', 'us-south')
            
            assert result['id'] == 'vpn-server-1'
            assert result['region'] == 'us-south'
            
            mock_service.get_vpn_server.assert_called_once_with('vpn-server-1')

    @pytest.mark.asyncio
    async def test_get_vpn_server_with_authentication(self, vpc_manager):
        """Test getting a VPN server with authentication information"""
        server_data = {
            'id': 'vpn-server-1',
            'name': 'client-access-server',
            'status': 'available',
            'client_ip_pool': '192.168.1.0/24',
            'certificate_instance': {
                'id': 'cert-1',
                'name': 'server-cert'
            },
            'client_authentication': [
                {'method': 'certificate'},
                {'method': 'username'}
            ]
        }
        
        with patch.object(vpc_manager, '_get_vpc_client') as mock_get_client:
            mock_service = Mock()
            mock_get_client.return_value = mock_service
            mock_service.get_vpn_server.return_value.get_result.return_value = server_data
            
            result = await vpc_manager.get_vpn_server('vpn-server-1', 'us-south')
            
            assert result['id'] == 'vpn-server-1'
            assert result['region'] == 'us-south'
            assert 'authentication_summary' in result
            assert result['authentication_summary']['certificate_based']['enabled'] == True
            assert result['authentication_summary']['client_authentication'] == [
                {'method': 'certificate'},
                {'method': 'username'}
            ]
            
            mock_service.get_vpn_server.assert_called_once_with('vpn-server-1')
    
    @pytest.mark.asyncio
    async def test_vpn_gateway_api_exception(self, vpc_manager):
        """Test VPN gateway API exception handling"""
        with patch.object(vpc_manager, '_get_vpc_client') as mock_get_client:
            mock_service = Mock()
            mock_get_client.return_value = mock_service
            mock_service.list_vpn_gateways.side_effect = ApiException('Not Found')
            
            with pytest.raises(ApiException):
                await vpc_manager.list_vpn_gateways('us-south')
    
    @pytest.mark.asyncio 
    async def test_vpn_server_api_exception(self, vpc_manager):
        """Test VPN server API exception handling"""
        with patch.object(vpc_manager, '_get_vpc_client') as mock_get_client:
            mock_service = Mock()
            mock_get_client.return_value = mock_service
            mock_service.list_vpn_servers.side_effect = ApiException('Not Found')
            
            with pytest.raises(ApiException):
                await vpc_manager.list_vpn_servers('us-south')

    @pytest.mark.asyncio
    async def test_get_ike_policy(self, vpc_manager):
        """Test getting a specific IKE policy"""
        ike_policy_data = {
            'id': 'ike-policy-1',
            'name': 'main-ike-policy',
            'authentication_algorithm': 'sha1',
            'encryption_algorithm': 'aes128',
            'dh_group': 2,
            'ike_version': 1
        }
        
        with patch.object(vpc_manager, '_get_vpc_client') as mock_get_client:
            mock_service = Mock()
            mock_get_client.return_value = mock_service
            mock_service.get_ike_policy.return_value.get_result.return_value = ike_policy_data
            
            result = await vpc_manager.get_ike_policy('ike-policy-1', 'us-south')
            
            assert result['id'] == 'ike-policy-1'
            assert result['region'] == 'us-south'
            assert result['authentication_algorithm'] == 'sha1'
            
            mock_service.get_ike_policy.assert_called_once_with('ike-policy-1')

    @pytest.mark.asyncio
    async def test_get_ipsec_policy(self, vpc_manager):
        """Test getting a specific IPsec policy"""
        ipsec_policy_data = {
            'id': 'ipsec-policy-1',
            'name': 'main-ipsec-policy',
            'authentication_algorithm': 'sha1',
            'encryption_algorithm': 'aes128',
            'pfs': 'group_2',
            'protocol': 'esp'
        }
        
        with patch.object(vpc_manager, '_get_vpc_client') as mock_get_client:
            mock_service = Mock()
            mock_get_client.return_value = mock_service
            mock_service.get_ipsec_policy.return_value.get_result.return_value = ipsec_policy_data
            
            result = await vpc_manager.get_ipsec_policy('ipsec-policy-1', 'us-south')
            
            assert result['id'] == 'ipsec-policy-1'
            assert result['region'] == 'us-south'
            assert result['protocol'] == 'esp'
            
            mock_service.get_ipsec_policy.assert_called_once_with('ipsec-policy-1')

    @pytest.mark.asyncio
    async def test_get_vpn_server_client_configuration(self, vpc_manager):
        """Test getting VPN server client configuration"""
        # API returns a string containing the OpenVPN configuration file content
        config_content = """client
dev tun
proto udp
remote vpn-server.example.com 1194
cert client.crt
key client.key
ca ca.crt
"""
        
        with patch.object(vpc_manager, '_get_vpc_client') as mock_get_client:
            mock_service = Mock()
            mock_get_client.return_value = mock_service
            mock_service.get_vpn_server_client_configuration.return_value.get_result.return_value = config_content
            
            result = await vpc_manager.get_vpn_server_client_configuration('vpn-server-1', 'us-south')
            
            assert result['vpn_server_id'] == 'vpn-server-1'
            assert result['region'] == 'us-south'
            assert 'client_configuration_content' in result
            assert 'metadata' in result
            assert result['client_configuration_content'] == config_content
            assert result['metadata']['content_type'] == 'openvpn_configuration'
            assert result['metadata']['encoding'] == 'utf-8'
            
            mock_service.get_vpn_server_client_configuration.assert_called_once_with('vpn-server-1')

    @pytest.mark.asyncio
    async def test_get_vpn_server_client_configuration_with_binary_data(self, vpc_manager):
        """Test getting VPN server client configuration with binary data handling"""
        # Simulate binary response that needs base64 encoding
        config_binary = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR'  # Binary data that can't be decoded as UTF-8
        
        with patch.object(vpc_manager, '_get_vpc_client') as mock_get_client:
            mock_service = Mock()
            mock_get_client.return_value = mock_service
            mock_service.get_vpn_server_client_configuration.return_value.get_result.return_value = config_binary
            
            result = await vpc_manager.get_vpn_server_client_configuration('vpn-server-1', 'us-south')
            
            assert result['vpn_server_id'] == 'vpn-server-1'
            assert result['region'] == 'us-south'
            assert 'client_configuration_content' in result
            assert result['metadata']['encoding'] == 'base64'
            # Should be base64 encoded
            import base64
            expected_content = base64.b64encode(config_binary).decode('ascii')
            assert result['client_configuration_content'] == expected_content
            
            mock_service.get_vpn_server_client_configuration.assert_called_once_with('vpn-server-1')

    @pytest.mark.asyncio
    async def test_list_vpn_server_routes(self, vpc_manager):
        """Test listing VPN server routes"""
        routes_data = {
            'routes': [
                {
                    'id': 'route-1',
                    'name': 'main-route',
                    'destination': '10.0.0.0/24',
                    'action': 'translate'
                },
                {
                    'id': 'route-2',
                    'name': 'secondary-route', 
                    'destination': '192.168.0.0/16',
                    'action': 'translate'
                }
            ]
        }
        
        with patch.object(vpc_manager, '_get_vpc_client') as mock_get_client:
            mock_service = Mock()
            mock_get_client.return_value = mock_service
            mock_service.list_vpn_server_routes.return_value.get_result.return_value = routes_data
            
            result = await vpc_manager.list_vpn_server_routes('vpn-server-1', 'us-south')
            
            assert result['vpn_server_id'] == 'vpn-server-1'
            assert result['region'] == 'us-south'
            assert result['count'] == 2
            assert len(result['routes']) == 2
            assert result['routes'][0]['id'] == 'route-1'
            assert result['routes'][0]['region'] == 'us-south'
            
            mock_service.list_vpn_server_routes.assert_called_once_with('vpn-server-1', limit=50)

    @pytest.mark.asyncio
    async def test_list_vpn_server_routes_with_pagination(self, vpc_manager):
        """Test listing VPN server routes with pagination"""
        routes_data = {'routes': []}
        
        with patch.object(vpc_manager, '_get_vpc_client') as mock_get_client:
            mock_service = Mock()
            mock_get_client.return_value = mock_service
            mock_service.list_vpn_server_routes.return_value.get_result.return_value = routes_data
            
            result = await vpc_manager.list_vpn_server_routes('vpn-server-1', 'us-south', limit=25, start='next-token')
            
            assert result['count'] == 0
            mock_service.list_vpn_server_routes.assert_called_once_with('vpn-server-1', limit=25, start='next-token')

    @pytest.mark.asyncio
    async def test_ike_policy_api_exception(self, vpc_manager):
        """Test IKE policy API exception handling"""
        with patch.object(vpc_manager, '_get_vpc_client') as mock_get_client:
            mock_service = Mock()
            mock_get_client.return_value = mock_service
            mock_service.get_ike_policy.side_effect = ApiException('Not Found')
            
            with pytest.raises(ApiException):
                await vpc_manager.get_ike_policy('ike-policy-1', 'us-south')

    @pytest.mark.asyncio
    async def test_ipsec_policy_api_exception(self, vpc_manager):
        """Test IPsec policy API exception handling"""
        with patch.object(vpc_manager, '_get_vpc_client') as mock_get_client:
            mock_service = Mock()
            mock_get_client.return_value = mock_service
            mock_service.get_ipsec_policy.side_effect = ApiException('Not Found')
            
            with pytest.raises(ApiException):
                await vpc_manager.get_ipsec_policy('ipsec-policy-1', 'us-south')

    @pytest.mark.asyncio
    async def test_vpn_server_client_configuration_api_exception(self, vpc_manager):
        """Test VPN server client configuration API exception handling"""
        with patch.object(vpc_manager, '_get_vpc_client') as mock_get_client:
            mock_service = Mock()
            mock_get_client.return_value = mock_service
            mock_service.get_vpn_server_client_configuration.side_effect = ApiException('Not Found')
            
            with pytest.raises(ApiException):
                await vpc_manager.get_vpn_server_client_configuration('vpn-server-1', 'us-south')

    @pytest.mark.asyncio
    async def test_vpn_server_routes_api_exception(self, vpc_manager):
        """Test VPN server routes API exception handling"""
        with patch.object(vpc_manager, '_get_vpc_client') as mock_get_client:
            mock_service = Mock()
            mock_get_client.return_value = mock_service
            mock_service.list_vpn_server_routes.side_effect = ApiException('Not Found')
            
            with pytest.raises(ApiException):
                await vpc_manager.list_vpn_server_routes('vpn-server-1', 'us-south')

    @pytest.mark.asyncio
    async def test_list_vpn_server_clients(self, vpc_manager):
        """Test listing VPN server clients"""
        clients_data = {
            'clients': [
                {
                    'id': 'client-1',
                    'common_name': 'user1.example.com',
                    'username': 'user1',
                    'status': 'connected',
                    'client_ip': '10.240.0.4',
                    'created_at': '2023-01-01T00:00:00Z',
                    'connected_at': '2023-01-01T10:00:00Z'
                },
                {
                    'id': 'client-2',
                    'common_name': 'user2.example.com',
                    'username': 'user2',
                    'status': 'disconnected',
                    'client_ip': '10.240.0.5',
                    'created_at': '2023-01-02T00:00:00Z'
                }
            ],
            'total_count': 2,
            'limit': 50
        }
        
        with patch.object(vpc_manager, '_get_vpc_client') as mock_get_client:
            mock_service = Mock()
            mock_get_client.return_value = mock_service
            mock_service.list_vpn_server_clients.return_value.get_result.return_value = clients_data
            
            result = await vpc_manager.list_vpn_server_clients('vpn-server-1', 'us-south')
            
            assert result['vpn_server_id'] == 'vpn-server-1'
            assert result['region'] == 'us-south'
            assert result['count'] == 2
            assert result['total_count'] == 2
            assert len(result['clients']) == 2
            assert result['clients'][0]['id'] == 'client-1'
            assert result['clients'][0]['region'] == 'us-south'
            assert result['clients'][0]['vpn_server_id'] == 'vpn-server-1'
            assert result['clients'][0]['status'] == 'connected'
            
            mock_service.list_vpn_server_clients.assert_called_once_with('vpn-server-1', limit=50)

    @pytest.mark.asyncio
    async def test_list_vpn_server_clients_with_pagination_and_sort(self, vpc_manager):
        """Test listing VPN server clients with pagination and sort"""
        clients_data = {
            'clients': [
                {
                    'id': 'client-3',
                    'common_name': 'user3.example.com',
                    'username': 'user3',
                    'status': 'connected',
                    'created_at': '2023-01-03T00:00:00Z'
                }
            ],
            'total_count': 1,
            'limit': 25
        }
        
        with patch.object(vpc_manager, '_get_vpc_client') as mock_get_client:
            mock_service = Mock()
            mock_get_client.return_value = mock_service
            mock_service.list_vpn_server_clients.return_value.get_result.return_value = clients_data
            
            result = await vpc_manager.list_vpn_server_clients(
                'vpn-server-1', 'us-south', limit=25, start='next-token', sort='created_at'
            )
            
            assert result['count'] == 1
            assert result['total_count'] == 1
            assert result['limit'] == 25
            
            mock_service.list_vpn_server_clients.assert_called_once_with(
                'vpn-server-1', limit=25, start='next-token', sort='created_at'
            )

    @pytest.mark.asyncio
    async def test_list_vpn_server_clients_api_exception(self, vpc_manager):
        """Test VPN server clients API exception handling"""
        with patch.object(vpc_manager, '_get_vpc_client') as mock_get_client:
            mock_service = Mock()
            mock_get_client.return_value = mock_service
            mock_service.list_vpn_server_clients.side_effect = ApiException('Not Found')
            
            with pytest.raises(ApiException):
                await vpc_manager.list_vpn_server_clients('vpn-server-1', 'us-south')
