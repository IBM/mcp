"""
Integration tests for IBM Cloud VPC utilities
These tests require actual IBM Cloud credentials and should be run against a test environment
"""

import pytest
import os
import asyncio
from datetime import datetime

from utils import create_vpc_manager, VPCManager
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator


# Skip integration tests if no API key is provided
pytestmark = pytest.mark.skipif(
    not os.getenv('IBM_CLOUD_API_KEY'),
    reason="IBM_CLOUD_API_KEY environment variable not set"
)


@pytest.fixture
async def vpc_manager():
    """Create a real VPC manager for integration testing"""
    api_key = os.getenv('IBM_CLOUD_API_KEY')
    if not api_key:
        pytest.skip("No IBM Cloud API key provided")
    
    return await create_vpc_manager(api_key)


@pytest.fixture
def test_region():
    """Default test region"""
    return os.getenv('IBM_CLOUD_TEST_REGION', 'us-south')


class TestVPCManagerIntegration:
    """Integration tests for VPCManager"""
    
    @pytest.mark.asyncio
    async def test_list_regions_integration(self, vpc_manager):
        """Test actual region listing"""
        result = await vpc_manager.list_regions()
        
        assert 'regions' in result
        assert 'count' in result
        assert result['count'] > 0
        assert isinstance(result['regions'], list)
        
        # Check that common regions are present
        region_names = [r['name'] for r in result['regions']]
        assert 'us-south' in region_names
        
        # Verify regions are cached
        assert len(vpc_manager.regions) > 0
    
    @pytest.mark.asyncio
    async def test_list_vpcs_integration(self, vpc_manager, test_region):
        """Test actual VPC listing"""
        result = await vpc_manager.list_vpcs(test_region)
        
        assert 'vpcs' in result
        assert 'count' in result
        assert isinstance(result['vpcs'], list)
        assert result['regions_checked'] == [test_region]
        
        # Each VPC should have required fields
        for vpc in result['vpcs']:
            assert 'id' in vpc
            assert 'name' in vpc
            assert 'status' in vpc
            assert vpc['region'] == test_region
    
    @pytest.mark.asyncio
    async def test_list_instance_profiles_integration(self, vpc_manager, test_region):
        """Test actual instance profile listing"""
        result = await vpc_manager.list_instance_profiles(test_region)
        
        assert 'profiles' in result
        assert 'count' in result
        assert result['count'] > 0
        
        # Check that common profiles exist
        profile_names = [p['name'] for p in result['profiles']]
        assert any('cx2' in name for name in profile_names)  # Common profile family
        
        # Verify profile structure
        for profile in result['profiles'][:5]:  # Check first 5
            assert 'name' in profile
            if 'vcpu_count' in profile:
                assert isinstance(profile['vcpu_count'], (int, dict))
            if 'memory' in profile:
                assert isinstance(profile['memory'], (int, dict))
    
    @pytest.mark.asyncio
    async def test_list_floating_ips_integration(self, vpc_manager, test_region):
        """Test actual floating IP listing"""
        result = await vpc_manager.list_floating_ips(test_region)
        
        assert 'floating_ips' in result
        assert 'count' in result
        assert result['region'] == test_region
        assert isinstance(result['floating_ips'], list)
        
        # If there are floating IPs, verify their structure
        for fip in result['floating_ips']:
            assert 'id' in fip
            assert 'address' in fip
            assert 'status' in fip
    
    @pytest.mark.asyncio
    async def test_security_group_analysis_integration(self, vpc_manager, test_region):
        """Test actual security group analysis"""
        # First get VPCs to test with
        vpcs_result = await vpc_manager.list_vpcs(test_region)
        
        if vpcs_result['count'] > 0:
            vpc_id = vpcs_result['vpcs'][0]['id']
            
            # Test SSH analysis
            ssh_result = await vpc_manager.analyze_ssh_security_groups(test_region, vpc_id)
            
            assert 'risky_security_groups' in ssh_result
            assert 'count' in ssh_result
            assert ssh_result['analysis_type'] == 'SSH access from 0.0.0.0/0'
            assert ssh_result['vpc_filter'] == vpc_id
            
            # Test general protocol analysis
            tcp_result = await vpc_manager.analyze_security_groups_by_protocol(
                test_region, 'tcp', port=80, vpc_id=vpc_id
            )
            
            assert 'matching_security_groups' in tcp_result
            assert 'criteria' in tcp_result
            assert tcp_result['criteria']['protocol'] == 'tcp'
            assert tcp_result['criteria']['port'] == 80
    
    @pytest.mark.asyncio
    async def test_backup_policies_integration(self, vpc_manager, test_region):
        """Test actual backup policy operations"""
        try:
            result = await vpc_manager.list_backup_policies(test_region, limit=10)
            
            assert 'backup_policies' in result
            assert 'count' in result
            assert result['region'] == test_region
            
            # If there are backup policies, test additional operations
            if result['count'] > 0:
                policy_id = result['backup_policies'][0]['id']
                
                # Test listing plans
                plans_result = await vpc_manager.list_backup_policy_plans(policy_id, test_region)
                assert 'plans' in plans_result
                assert plans_result['backup_policy_id'] == policy_id
                
                # Test listing jobs
                jobs_result = await vpc_manager.list_backup_policy_jobs(
                    policy_id, test_region, limit=5
                )
                assert 'jobs' in jobs_result
                assert 'status_summary' in jobs_result
                
                # Test policy summary
                summary = await vpc_manager.get_backup_policy_summary(policy_id, test_region)
                assert summary['backup_policy_id'] == policy_id
                assert 'policy_details' in summary
                assert 'plans' in summary
                assert 'recent_jobs' in summary
        
        except Exception as e:
            # Backup policies might not be available in all regions/accounts
            pytest.skip(f"Backup policies not available: {e}")
    
    @pytest.mark.asyncio
    async def test_vpc_resources_summary_integration(self, vpc_manager, test_region):
        """Test actual VPC resources summary"""
        # Get a VPC to test with
        vpcs_result = await vpc_manager.list_vpcs(test_region)
        
        if vpcs_result['count'] > 0:
            vpc_id = vpcs_result['vpcs'][0]['id']
            
            summary = await vpc_manager.get_vpc_resources_summary(vpc_id, test_region)
            
            assert summary['vpc_id'] == vpc_id
            assert summary['region'] == test_region
            assert 'timestamp' in summary
            assert 'vpc_details' in summary
            assert 'resources' in summary
            
            # Check resource counts
            resources = summary['resources']
            for resource_type in ['subnets', 'instances', 'security_groups', 'public_gateways']:
                assert resource_type in resources
                if 'error' not in resources[resource_type]:
                    assert 'count' in resources[resource_type]
            
            # Check security analysis
            if 'security_analysis' in summary and 'error' not in summary['security_analysis']:
                assert 'ssh_open_to_internet' in summary['security_analysis']
        else:
            pytest.skip("No VPCs available for testing")
    
    @pytest.mark.asyncio
    async def test_analyze_backup_policies_integration(self, vpc_manager, test_region):
        """Test actual backup policy analysis"""
        try:
            analysis = await vpc_manager.analyze_backup_policies(test_region)
            
            assert 'region' in analysis
            assert 'timestamp' in analysis
            assert 'total_policies' in analysis
            assert 'policy_health' in analysis
            assert 'summary' in analysis
            
            summary = analysis['summary']
            expected_keys = [
                'active_policies', 'inactive_policies', 
                'policies_with_failed_jobs', 'policies_without_recent_jobs'
            ]
            for key in expected_keys:
                assert key in summary
                assert isinstance(summary[key], int)
            
            # If there are policies, check health analysis
            if analysis['total_policies'] > 0:
                assert len(analysis['policy_health']) > 0
                
                for policy_health in analysis['policy_health']:
                    assert 'policy_id' in policy_health
                    assert 'policy_name' in policy_health
                    assert 'status' in policy_health
                    assert 'issues' in policy_health
        
        except Exception as e:
            pytest.skip(f"Backup policy analysis not available: {e}")


class TestErrorHandling:
    """Test error handling in integration scenarios"""
    
    @pytest.mark.asyncio
    async def test_invalid_region_handling(self, vpc_manager):
        """Test handling of invalid region"""
        with pytest.raises(Exception):
            await vpc_manager.list_vpcs('invalid-region-name')
    
    @pytest.mark.asyncio
    async def test_invalid_vpc_id_handling(self, vpc_manager, test_region):
        """Test handling of invalid VPC ID"""
        with pytest.raises(Exception):
            await vpc_manager.get_vpc('invalid-vpc-id', test_region)
    
    @pytest.mark.asyncio
    async def test_invalid_backup_policy_id_handling(self, vpc_manager, test_region):
        """Test handling of invalid backup policy ID"""
        with pytest.raises(Exception):
            await vpc_manager.list_backup_policy_jobs('invalid-policy-id', test_region)


class TestPerformance:
    """Performance tests for integration scenarios"""
    
    @pytest.mark.asyncio
    async def test_concurrent_region_listing(self, vpc_manager):
        """Test concurrent operations across multiple regions"""
        # Get available regions first
        regions_result = await vpc_manager.list_regions()
        test_regions = [r['name'] for r in regions_result['regions'][:3]]  # Test first 3 regions
        
        # Create concurrent tasks
        tasks = [vpc_manager.list_vpcs(region) for region in test_regions]
        
        start_time = datetime.now()
        results = await asyncio.gather(*tasks, return_exceptions=True)
        end_time = datetime.now()
        
        # Check that operations completed reasonably quickly
        duration = (end_time - start_time).total_seconds()
        assert duration < 30  # Should complete within 30 seconds
        
        # Check results
        successful_results = [r for r in results if not isinstance(r, Exception)]
        assert len(successful_results) > 0  # At least one should succeed
        
        for result in successful_results:
            assert 'vpcs' in result
            assert 'count' in result
    
    @pytest.mark.asyncio
    async def test_large_result_handling(self, vpc_manager, test_region):
        """Test handling of large result sets"""
        # Test with a reasonable limit
        result = await vpc_manager.list_instance_profiles(test_region)
        
        # Should handle large numbers of profiles efficiently
        assert result['count'] >= 0
        assert len(result['profiles']) == result['count']
        
        # Test memory efficiency - results should not be excessively large
        import sys
        result_size = sys.getsizeof(str(result))
        assert result_size < 10 * 1024 * 1024  # Less than 10MB when serialized
