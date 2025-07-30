#!/usr/bin/env python3
# Author: Ryan Tiffany
# Copyright (c) 2023
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#     http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

"""
Storage module for IBM Cloud VPC MCP Server
Provides block storage and file storage management capabilities
"""

import logging
from typing import Dict, List, Any, Optional
import ibm_vpc
from ibm_cloud_sdk_core import ApiException
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator

logger = logging.getLogger(__name__)

class StorageManager:
    """
    Manages IBM Cloud VPC storage resources including block volumes and file shares
    """
    
    def __init__(self, vpc_service, authenticator):
        """Initialize with VPC service client and authenticator"""
        self.authenticator = authenticator
        self.vpc_clients = {}  # Cache VPC clients by region
    
    def _get_vpc_client(self, region: str):
        """Get or create VPC client for a specific region"""
        if region not in self.vpc_clients:
            import ibm_vpc
            service = ibm_vpc.VpcV1(version='2025-04-08',authenticator=self.authenticator)
            service.set_service_url(f'https://{region}.iaas.cloud.ibm.com/v1')
            self.vpc_clients[region] = service
        return self.vpc_clients[region]
    
    async def list_volumes(self, region: str, 
                          start: Optional[str] = None,
                          limit: Optional[int] = None,
                          attachment_state: Optional[str] = None,
                          encryption: Optional[str] = None,
                          name: Optional[str] = None,
                          operating_system_family: Optional[str] = None,
                          operating_system_architecture: Optional[str] = None,
                          tag: Optional[str] = None,
                          zone_name: Optional[str] = None) -> Dict[str, Any]:
        """
        List block storage volumes in a region with optional filtering
        
        Parameters:
            region (str): Region name
            start (str, optional): Pagination start token
            limit (int, optional): Maximum number of volumes to return
            attachment_state (str, optional): Filter by attachment state
            encryption (str, optional): Filter by encryption type
            name (str, optional): Filter by volume name
            operating_system_family (str, optional): Filter by OS family
            operating_system_architecture (str, optional): Filter by OS architecture
            tag (str, optional): Filter by tag
            zone_name (str, optional): Filter by zone name
            
        Returns:
            Dict with volumes list and metadata
        """
        try:
            service = self._get_vpc_client(region)
            
            # Build parameters dict, excluding None values
            params = {
                'start': start,
                'limit': limit,
                'attachment_state': attachment_state,
                'encryption': encryption,
                'name': name,
                'operating_system.family': operating_system_family,
                'operating_system.architecture': operating_system_architecture,
                'tag': tag,
                'zone.name': zone_name
            }
            
            # Remove None values
            params = {k: v for k, v in params.items() if v is not None}
            
            logger.debug(f"Calling list_volumes with params: {params}")
            response = service.list_volumes(**params).get_result()
            logger.debug(f"Got response keys: {list(response.keys())}")
            
            # Extract and enhance volume information
            volumes = []
            response_volumes = response.get('volumes', [])
            logger.debug(f"Found {len(response_volumes)} volumes")
            
            for volume in response_volumes:
                volume_info = {
                    'id': volume.get('id', 'unknown'),
                    'name': volume.get('name', 'unknown'),
                    'status': volume.get('status', 'unknown'),
                    'capacity': volume.get('capacity', 0),
                    'iops': volume.get('iops', 0),
                    'profile': {
                        'name': volume.get('profile', {}).get('name', 'unknown')
                    },
                    'encryption': volume.get('encryption'),
                    'zone': {
                        'name': volume.get('zone', {}).get('name', 'unknown')
                    },
                    'created_at': volume.get('created_at', 'unknown'),
                    'attachment_state': volume.get('attachment_state', 'unattached')
                }
                
                # Add attachment info if present
                if 'volume_attachments' in volume and volume['volume_attachments']:
                    attachments = []
                    for attachment in volume['volume_attachments']:
                        attachments.append({
                            'id': attachment.get('id', 'unknown'),
                            'instance': {
                                'id': attachment.get('instance', {}).get('id', 'unknown'),
                                'name': attachment.get('instance', {}).get('name', 'Unknown')
                            },
                            'type': attachment.get('type', 'unknown'),
                            'status': attachment.get('status', 'unknown')
                        })
                    volume_info['attachments'] = attachments
                
                volumes.append(volume_info)
            
            return {
                'volumes': volumes,
                'count': len(volumes),
                'region': region,
                'filters': {
                    'attachment_state': attachment_state,
                    'encryption': encryption,
                    'name': name,
                    'tag': tag,
                    'zone_name': zone_name
                }
            }
            
        except Exception as e:
            logger.error(f"Error listing volumes in region {region}: {str(e)}")
            logger.debug(f"Exception details: {type(e).__name__}: {e}")
            return {
                'error': str(e),
                'region': region,
                'volumes': [],
                'count': 0
            }
    
    async def list_volume_profiles(self, region: str, start: Optional[str] = None, limit: Optional[int] = None) -> Dict[str, Any]:
        """
        List available volume profiles in a region
        
        Parameters:
            region (str): Region name
            start (str, optional): Pagination start token
            limit (int, optional): Maximum number of profiles to return
            
        Returns:
            Dict with volume profiles and metadata
        """
        try:
            service = self._get_vpc_client(region)
            
            params = {}
            if start:
                params['start'] = start
            if limit:
                params['limit'] = limit
                
            response = service.list_volume_profiles(**params).get_result()
            
            profiles = []
            for profile in response['profiles']:
                profile_info = {
                    'name': profile['name'],
                    'family': profile.get('family'),
                    'href': profile['href']
                }
                
                # Add performance details if available
                if 'performance' in profile:
                    profile_info['performance'] = {
                        'max_iops': profile['performance'].get('max_iops'),
                        'max_throughput': profile['performance'].get('max_throughput'),
                        'max_volume_size': profile['performance'].get('max_volume_size')
                    }
                
                profiles.append(profile_info)
            
            return {
                'profiles': profiles,
                'count': len(profiles),
                'region': region
            }
            
        except Exception as e:
            logger.error(f"Error listing volume profiles in region {region}: {str(e)}")
            return {
                'error': str(e),
                'region': region,
                'profiles': [],
                'count': 0
            }
    
    async def get_volume(self, volume_id: str, region: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific volume
        
        Parameters:
            volume_id (str): Volume ID
            region (str): Region name
            
        Returns:
            Dict with volume details
        """
        try:
            service = self._get_vpc_client(region)
            response = service.get_volume(id=volume_id).get_result()
            
            # Extract and enhance volume information
            volume_info = {
                'id': response.get('id', 'unknown'),
                'name': response.get('name', 'unknown'),
                'status': response.get('status', 'unknown'),
                'capacity': response.get('capacity', 0),
                'iops': response.get('iops', 0),
                'profile': {
                    'name': response.get('profile', {}).get('name', 'unknown')
                },
                'encryption': response.get('encryption'),
                'zone': {
                    'name': response.get('zone', {}).get('name', 'unknown')
                },
                'created_at': response.get('created_at', 'unknown'),
                'attachment_state': response.get('attachment_state', 'unattached'),
                'crn': response.get('crn', 'unknown'),
                'resource_group': response.get('resource_group', {}),
                'bootable': response.get('bootable', False),
                'bandwidth': response.get('bandwidth')
            }
            
            # Add attachment info if present
            if 'volume_attachments' in response and response['volume_attachments']:
                attachments = []
                for attachment in response['volume_attachments']:
                    attachments.append({
                        'id': attachment.get('id', 'unknown'),
                        'instance': {
                            'id': attachment.get('instance', {}).get('id', 'unknown'),
                            'name': attachment.get('instance', {}).get('name', 'Unknown')
                        },
                        'type': attachment.get('type', 'unknown'),
                        'status': attachment.get('status', 'unknown'),
                        'device': attachment.get('device', {})
                    })
                volume_info['attachments'] = attachments
            
            # Add tags if present
            if 'user_tags' in response:
                volume_info['user_tags'] = response['user_tags']
            
            return volume_info
            
        except Exception as e:
            logger.error(f"Error getting volume {volume_id} in region {region}: {str(e)}")
            return {
                'error': str(e),
                'volume_id': volume_id,
                'region': region
            }
    
    async def analyze_storage_usage(self, region: str) -> Dict[str, Any]:
        """
        Analyze storage usage in a region
        
        Parameters:
            region (str): Region name
            
        Returns:
            Dict with storage usage analysis
        """
        try:
            # Get all volumes in the region
            volumes_data = await self.list_volumes(region)
            
            if 'error' in volumes_data:
                return {
                    'error': volumes_data['error'],
                    'region': region
                }
            
            volumes = volumes_data['volumes']
            
            # Calculate storage usage statistics
            total_volumes = len(volumes)
            total_capacity_gb = sum(v['capacity'] for v in volumes)
            attached_volumes = sum(1 for v in volumes if v.get('attachment_state') == 'attached')
            unattached_volumes = total_volumes - attached_volumes
            
            # Group by profile
            profiles = {}
            for volume in volumes:
                profile_name = volume['profile']['name']
                if profile_name not in profiles:
                    profiles[profile_name] = {
                        'count': 0,
                        'total_capacity_gb': 0,
                        'total_iops': 0
                    }
                
                profiles[profile_name]['count'] += 1
                profiles[profile_name]['total_capacity_gb'] += volume['capacity']
                profiles[profile_name]['total_iops'] += volume['iops']
            
            # Group by zone
            zones = {}
            for volume in volumes:
                zone_name = volume['zone']['name']
                if zone_name not in zones:
                    zones[zone_name] = {
                        'count': 0,
                        'total_capacity_gb': 0
                    }
                
                zones[zone_name]['count'] += 1
                zones[zone_name]['total_capacity_gb'] += volume['capacity']
            
            return {
                'region': region,
                'timestamp': import_datetime_and_return_now_iso(),
                'summary': {
                    'total_volumes': total_volumes,
                    'total_capacity_gb': total_capacity_gb,
                    'attached_volumes': attached_volumes,
                    'unattached_volumes': unattached_volumes,
                    'attachment_percentage': round((attached_volumes / total_volumes) * 100, 2) if total_volumes > 0 else 0
                },
                'by_profile': profiles,
                'by_zone': zones
            }
            
        except Exception as e:
            logger.error(f"Error analyzing storage usage in region {region}: {str(e)}")
            return {
                'error': str(e),
                'region': region
            }
    
    async def list_shares(self, region: str, 
                         start: Optional[str] = None,
                         limit: Optional[int] = None,
                         resource_group_id: Optional[str] = None,
                         name: Optional[str] = None,
                         sort: Optional[str] = None,
                         replication_role: Optional[str] = None) -> Dict[str, Any]:
        """
        List file shares in a region with optional filtering
        
        Parameters:
            region (str): Region name
            start (str, optional): Pagination start token
            limit (int, optional): Maximum number of shares to return
            resource_group_id (str, optional): Filter by resource group ID
            name (str, optional): Filter by share name
            sort (str, optional): Sort order
            replication_role (str, optional): Filter by replication role
            
        Returns:
            Dict with shares list and metadata
        """
        try:
            service = self._get_vpc_client(region)
            
            # Build parameters dict, excluding None values
            params = {
                'start': start,
                'limit': limit,
                'resource_group.id': resource_group_id,
                'name': name,
                'sort': sort,
                'replication_role': replication_role
            }
            
            # Remove None values
            params = {k: v for k, v in params.items() if v is not None}
            
            logger.debug(f"Calling list_shares with params: {params}")
            response = service.list_shares(**params).get_result()
            logger.debug(f"Got response keys: {list(response.keys())}")
            
            # Extract and enhance share information
            shares = []
            response_shares = response.get('shares', [])
            logger.debug(f"Found {len(response_shares)} shares")
            
            for share in response_shares:
                share_info = {
                    'id': share.get('id', 'unknown'),
                    'name': share.get('name', 'unknown'),
                    'status': share.get('status', 'unknown'),
                    'size': share.get('size', 0),
                    'iops': share.get('iops', 0),
                    'profile': {
                        'name': share.get('profile', {}).get('name', 'unknown')
                    },
                    'zone': {
                        'name': share.get('zone', {}).get('name', 'unknown')
                    },
                    'created_at': share.get('created_at', 'unknown'),
                    'crn': share.get('crn', 'unknown'),
                    'resource_group': share.get('resource_group', {}),
                    'replication_role': share.get('replication_role'),
                    'lifecycle_state': share.get('lifecycle_state')
                }
                
                # Add mount targets if present
                if 'mount_targets' in share and share['mount_targets']:
                    mount_targets = []
                    for target in share['mount_targets']:
                        mount_targets.append({
                            'id': target.get('id', 'unknown'),
                            'name': target.get('name'),
                            'vpc': target.get('vpc'),
                            'subnet': target.get('subnet')
                        })
                    share_info['mount_targets'] = mount_targets
                
                shares.append(share_info)
            
            return {
                'shares': shares,
                'count': len(shares),
                'region': region,
                'filters': {
                    'resource_group_id': resource_group_id,
                    'name': name,
                    'sort': sort,
                    'replication_role': replication_role
                }
            }
            
        except Exception as e:
            logger.error(f"Error listing shares in region {region}: {str(e)}")
            logger.debug(f"Exception details: {type(e).__name__}: {e}")
            return {
                'error': str(e),
                'region': region,
                'shares': [],
                'count': 0
            }
    
    async def get_share(self, share_id: str, region: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific file share
        
        Parameters:
            share_id (str): Share ID
            region (str): Region name
            
        Returns:
            Dict with share details
        """
        try:
            service = self._get_vpc_client(region)
            response = service.get_share(id=share_id).get_result()
            
            # Extract and enhance share information
            share_info = {
                'id': response.get('id', 'unknown'),
                'name': response.get('name', 'unknown'),
                'status': response.get('status', 'unknown'),
                'size': response.get('size', 0),
                'iops': response.get('iops', 0),
                'profile': {
                    'name': response.get('profile', {}).get('name', 'unknown')
                },
                'zone': {
                    'name': response.get('zone', {}).get('name', 'unknown')
                },
                'created_at': response.get('created_at', 'unknown'),
                'crn': response.get('crn', 'unknown'),
                'resource_group': response.get('resource_group', {}),
                'replication_role': response.get('replication_role'),
                'lifecycle_state': response.get('lifecycle_state'),
                'href': response.get('href', 'unknown')
            }
            
            # Add mount targets if present
            if 'mount_targets' in response and response['mount_targets']:
                mount_targets = []
                for target in response['mount_targets']:
                    mount_targets.append({
                        'id': target.get('id', 'unknown'),
                        'name': target.get('name'),
                        'vpc': target.get('vpc'),
                        'subnet': target.get('subnet'),
                        'href': target.get('href', 'unknown')
                    })
                share_info['mount_targets'] = mount_targets
            
            # Add user tags if present
            if 'user_tags' in response:
                share_info['user_tags'] = response['user_tags']
            
            return share_info
            
        except Exception as e:
            logger.error(f"Error getting share {share_id} in region {region}: {str(e)}")
            return {
                'error': str(e),
                'share_id': share_id,
                'region': region
            }
    
    async def list_share_profiles(self, region: str, 
                                 start: Optional[str] = None,
                                 limit: Optional[int] = None,
                                 sort: Optional[str] = None) -> Dict[str, Any]:
        """
        List available share profiles in a region
        
        Parameters:
            region (str): Region name
            start (str, optional): Pagination start token
            limit (int, optional): Maximum number of profiles to return
            sort (str, optional): Sort order
            
        Returns:
            Dict with share profiles and metadata
        """
        try:
            service = self._get_vpc_client(region)
            
            params = {}
            if start:
                params['start'] = start
            if limit:
                params['limit'] = limit
            if sort:
                params['sort'] = sort
                
            response = service.list_share_profiles(**params).get_result()
            
            profiles = []
            for profile in response['profiles']:
                profile_info = {
                    'name': profile['name'],
                    'family': profile.get('family'),
                    'href': profile['href']
                }
                
                # Add performance details if available
                if 'performance' in profile:
                    profile_info['performance'] = {
                        'max_iops': profile['performance'].get('max_iops'),
                        'max_throughput': profile['performance'].get('max_throughput'),
                        'max_share_size': profile['performance'].get('max_share_size')
                    }
                
                profiles.append(profile_info)
            
            return {
                'profiles': profiles,
                'count': len(profiles),
                'region': region
            }
            
        except Exception as e:
            logger.error(f"Error listing share profiles in region {region}: {str(e)}")
            return {
                'error': str(e),
                'region': region,
                'profiles': [],
                'count': 0
            }
    
    async def list_snapshots(self, region: str, 
                            start: Optional[str] = None,
                            limit: Optional[int] = None,
                            name: Optional[str] = None,
                            source_volume_id: Optional[str] = None,
                            resource_group_id: Optional[str] = None,
                            sort: Optional[str] = None) -> Dict[str, Any]:
        """
        List block storage snapshots in a region with optional filtering
        
        Parameters:
            region (str): Region name
            start (str, optional): Pagination start token
            limit (int, optional): Maximum number of snapshots to return
            name (str, optional): Filter by snapshot name
            source_volume_id (str, optional): Filter by source volume ID
            resource_group_id (str, optional): Filter by resource group ID
            sort (str, optional): Sort order
            
        Returns:
            Dict with snapshots list and metadata
        """
        try:
            service = self._get_vpc_client(region)
            
            # Build parameters dict, excluding None values
            params = {
                'start': start,
                'limit': limit,
                'name': name,
                'source_volume.id': source_volume_id,
                'resource_group.id': resource_group_id,
                'sort': sort
            }
            
            # Remove None values
            params = {k: v for k, v in params.items() if v is not None}
            
            logger.debug(f"Calling list_snapshots with params: {params}")
            response = service.list_snapshots(**params).get_result()
            logger.debug(f"Got response keys: {list(response.keys())}")
            
            # Extract and enhance snapshot information
            snapshots = []
            response_snapshots = response.get('snapshots', [])
            logger.debug(f"Found {len(response_snapshots)} snapshots")
            
            for snapshot in response_snapshots:
                snapshot_info = {
                    'id': snapshot.get('id', 'unknown'),
                    'name': snapshot.get('name', 'unknown'),
                    'status': snapshot.get('status', 'unknown'),
                    'size': snapshot.get('size', 0),
                    'minimum_capacity': snapshot.get('minimum_capacity', 0),
                    'resource_group': snapshot.get('resource_group', {}),
                    'created_at': snapshot.get('created_at', 'unknown'),
                    'crn': snapshot.get('crn', 'unknown'),
                    'encryption': snapshot.get('encryption', {}),
                    'lifecycle_state': snapshot.get('lifecycle_state', 'unknown'),
                    'href': snapshot.get('href', 'unknown'),
                    'bootable': snapshot.get('bootable', False)
                }
                
                # Add source volume information if present
                if 'source_volume' in snapshot:
                    snapshot_info['source_volume'] = {
                        'id': snapshot['source_volume'].get('id', 'unknown'),
                        'name': snapshot['source_volume'].get('name', 'unknown'),
                        'href': snapshot['source_volume'].get('href', 'unknown')
                    }
                
                # Add operating system information if present
                if 'operating_system' in snapshot:
                    snapshot_info['operating_system'] = {
                        'architecture': snapshot['operating_system'].get('architecture', 'unknown'),
                        'family': snapshot['operating_system'].get('family', 'unknown'),
                        'name': snapshot['operating_system'].get('name', 'unknown'),
                        'vendor': snapshot['operating_system'].get('vendor', 'unknown'),
                        'version': snapshot['operating_system'].get('version', 'unknown')
                    }
                
                # Add backup policy information if present
                if 'backup_policy_plan' in snapshot:
                    snapshot_info['backup_policy_plan'] = {
                        'id': snapshot['backup_policy_plan'].get('id', 'unknown'),
                        'name': snapshot['backup_policy_plan'].get('name', 'unknown'),
                        'href': snapshot['backup_policy_plan'].get('href', 'unknown')
                    }
                
                # Add user tags if present
                if 'user_tags' in snapshot:
                    snapshot_info['user_tags'] = snapshot['user_tags']
                
                snapshots.append(snapshot_info)
            
            return {
                'snapshots': snapshots,
                'count': len(snapshots),
                'region': region,
                'filters': {
                    'name': name,
                    'source_volume_id': source_volume_id,
                    'resource_group_id': resource_group_id,
                    'sort': sort
                }
            }
            
        except Exception as e:
            logger.error(f"Error listing snapshots in region {region}: {str(e)}")
            logger.debug(f"Exception details: {type(e).__name__}: {e}")
            return {
                'error': str(e),
                'region': region,
                'snapshots': [],
                'count': 0
            }
    
    async def get_snapshot(self, snapshot_id: str, region: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific snapshot
        
        Parameters:
            snapshot_id (str): Snapshot ID
            region (str): Region name
            
        Returns:
            Dict with snapshot details
        """
        try:
            service = self._get_vpc_client(region)
            logger.debug(f"Getting snapshot {snapshot_id} in region {region}")
            response = service.get_snapshot(id=snapshot_id).get_result()
            
            # Extract and enhance snapshot information
            snapshot_info = {
                'id': response.get('id', 'unknown'),
                'name': response.get('name', 'unknown'),
                'status': response.get('status', 'unknown'),
                'size': response.get('size', 0),
                'minimum_capacity': response.get('minimum_capacity', 0),
                'resource_group': response.get('resource_group', {}),
                'created_at': response.get('created_at', 'unknown'),
                'crn': response.get('crn', 'unknown'),
                'encryption': response.get('encryption', {}),
                'lifecycle_state': response.get('lifecycle_state', 'unknown'),
                'href': response.get('href', 'unknown'),
                'bootable': response.get('bootable', False)
            }
            
            # Add source volume information if present
            if 'source_volume' in response:
                snapshot_info['source_volume'] = {
                    'id': response['source_volume'].get('id', 'unknown'),
                    'name': response['source_volume'].get('name', 'unknown'),
                    'href': response['source_volume'].get('href', 'unknown')
                }
            
            # Add operating system information if present
            if 'operating_system' in response:
                snapshot_info['operating_system'] = {
                    'architecture': response['operating_system'].get('architecture', 'unknown'),
                    'family': response['operating_system'].get('family', 'unknown'),
                    'name': response['operating_system'].get('name', 'unknown'),
                    'vendor': response['operating_system'].get('vendor', 'unknown'),
                    'version': response['operating_system'].get('version', 'unknown')
                }
            
            # Add backup policy information if present
            if 'backup_policy_plan' in response:
                snapshot_info['backup_policy_plan'] = {
                    'id': response['backup_policy_plan'].get('id', 'unknown'),
                    'name': response['backup_policy_plan'].get('name', 'unknown'),
                    'href': response['backup_policy_plan'].get('href', 'unknown')
                }
            
            # Add clone information if present
            if 'clones' in response and response['clones']:
                clones = []
                for clone in response['clones']:
                    clones.append({
                        'available': clone.get('available', False),
                        'created_at': clone.get('created_at', 'unknown'),
                        'zone': clone.get('zone', {})
                    })
                snapshot_info['clones'] = clones
            
            # Add user tags if present
            if 'user_tags' in response:
                snapshot_info['user_tags'] = response['user_tags']
            
            return snapshot_info
            
        except Exception as e:
            logger.error(f"Error getting snapshot {snapshot_id} in region {region}: {str(e)}")
            logger.debug(f"Exception details: {type(e).__name__}: {e}")
            return {
                'error': str(e),
                'snapshot_id': snapshot_id,
                'region': region
            }
    
    async def analyze_snapshot_usage(self, region: str) -> Dict[str, Any]:
        """
        Analyze snapshot usage in a region
        
        Parameters:
            region (str): Region name
            
        Returns:
            Dict with snapshot usage analysis
        """
        try:
            # Get all snapshots in the region
            snapshots_data = await self.list_snapshots(region)
            
            if 'error' in snapshots_data:
                return {
                    'error': snapshots_data['error'],
                    'region': region
                }
            
            snapshots = snapshots_data['snapshots']
            
            # Calculate snapshot usage statistics
            total_snapshots = len(snapshots)
            total_size_gb = sum(s['size'] for s in snapshots)
            
            # Group by status
            by_status = {}
            for snapshot in snapshots:
                status = snapshot.get('status', 'unknown')
                if status not in by_status:
                    by_status[status] = {'count': 0, 'total_size_gb': 0}
                by_status[status]['count'] += 1
                by_status[status]['total_size_gb'] += snapshot['size']
            
            # Group by source volume
            by_source_volume = {}
            for snapshot in snapshots:
                source_volume = snapshot.get('source_volume', {})
                source_id = source_volume.get('id', 'unknown')
                source_name = source_volume.get('name', 'unknown')
                
                if source_id not in by_source_volume:
                    by_source_volume[source_id] = {
                        'source_name': source_name,
                        'count': 0,
                        'total_size_gb': 0
                    }
                by_source_volume[source_id]['count'] += 1
                by_source_volume[source_id]['total_size_gb'] += snapshot['size']
            
            # Group by resource group
            by_resource_group = {}
            for snapshot in snapshots:
                rg = snapshot.get('resource_group', {})
                rg_id = rg.get('id', 'unknown')
                rg_name = rg.get('name', 'unknown')
                
                if rg_id not in by_resource_group:
                    by_resource_group[rg_id] = {
                        'name': rg_name,
                        'count': 0,
                        'total_size_gb': 0
                    }
                by_resource_group[rg_id]['count'] += 1
                by_resource_group[rg_id]['total_size_gb'] += snapshot['size']
            
            # Count bootable snapshots
            bootable_count = sum(1 for s in snapshots if s.get('bootable', False))
            
            # Count snapshots with backup policy
            backup_policy_count = sum(1 for s in snapshots if 'backup_policy_plan' in s)
            
            return {
                'region': region,
                'timestamp': import_datetime_and_return_now_iso(),
                'summary': {
                    'total_snapshots': total_snapshots,
                    'total_size_gb': total_size_gb,
                    'bootable_snapshots': bootable_count,
                    'backup_policy_snapshots': backup_policy_count,
                    'average_size_gb': round(total_size_gb / total_snapshots, 2) if total_snapshots > 0 else 0
                },
                'by_status': by_status,
                'by_source_volume': by_source_volume,
                'by_resource_group': by_resource_group
            }
            
        except Exception as e:
            logger.error(f"Error analyzing snapshot usage in region {region}: {str(e)}")
            logger.debug(f"Exception details: {type(e).__name__}: {e}")
            return {
                'error': str(e),
                'region': region
            }

# Helper function to get current datetime in ISO format
def import_datetime_and_return_now_iso():
    from datetime import datetime
    return datetime.now().isoformat()
