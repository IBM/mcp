"""
IBM Cloud VPC Utilities
Provides VPC resource management functionality for IBM Cloud
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

import ibm_vpc
from ibm_cloud_sdk_core import ApiException
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator

logger = logging.getLogger(__name__)


class VPCManager:
    """Manages IBM Cloud VPC operations"""
    
    def __init__(self, authenticator: IAMAuthenticator):
        self.authenticator = authenticator
        self.vpc_clients = {}  # Cache VPC clients by region
        self.regions = []


    def _get_vpc_client(self, region: str) -> ibm_vpc.VpcV1:
        """Get or create VPC client for a specific region"""
        if region not in self.vpc_clients:
            service = ibm_vpc.VpcV1(
                version='2025-04-08',
                authenticator=self.authenticator
            )
            service.set_service_url(f'https://{region}.iaas.cloud.ibm.com/v1')
            self.vpc_clients[region] = service
        return self.vpc_clients[region]

    async def list_regions(self) -> Dict[str, Any]:
        """List all available regions"""
        # Use us-south to get region list
        service = self._get_vpc_client('us-south')
        response = service.list_regions().get_result()
        
        self.regions = [region['name'] for region in response['regions']]
        
        return {
            'regions': response['regions'],
            'count': len(response['regions'])
        }
    
    async def list_vpcs(self, region: Optional[str] = None) -> Dict[str, Any]:
        """List VPCs in specified region or all regions"""
        all_vpcs = []
        
        if region:
            regions_to_check = [region]
        else:
            # Get all regions if not cached
            if not self.regions:
                await self.list_regions()
            regions_to_check = self.regions
        
        for region_name in regions_to_check:
            try:
                service = self._get_vpc_client(region_name)
                response = service.list_vpcs().get_result()
                
                for vpc in response['vpcs']:
                    vpc['region'] = region_name
                    all_vpcs.append(vpc)
                    
            except ApiException as e:
                logger.warning(f"Error listing VPCs in region {region_name}: {e}")
        
        return {
            'vpcs': all_vpcs,
            'count': len(all_vpcs),
            'regions_checked': regions_to_check
        }
    
    async def get_vpc(self, vpc_id: str, region: str) -> Dict[str, Any]:
        """Get details of a specific VPC"""
        service = self._get_vpc_client(region)
        vpc = service.get_vpc(id=vpc_id).get_result()
        vpc['region'] = region
        return vpc
    
    async def list_subnets(self, region: str, vpc_id: Optional[str] = None) -> Dict[str, Any]:
        """List subnets in a region, optionally filtered by VPC"""
        service = self._get_vpc_client(region)
        response = service.list_subnets().get_result()
        
        subnets = response['subnets']
        
        # Filter by VPC if specified
        if vpc_id:
            subnets = [s for s in subnets if s['vpc']['id'] == vpc_id]
        
        # Add additional subnet details
        for subnet in subnets:
            subnet['region'] = region
            subnet['available_ipv4_address_count'] = subnet.get('available_ipv4_address_count', 0)
            subnet['total_ipv4_address_count'] = subnet.get('total_ipv4_address_count', 0)
            
        return {
            'subnets': subnets,
            'count': len(subnets),
            'region': region,
            'vpc_filter': vpc_id
        }
    
    async def list_instances(self, region: str, vpc_id: Optional[str] = None) -> Dict[str, Any]:
        """List compute instances"""
        service = self._get_vpc_client(region)
        response = service.list_instances().get_result()
        
        instances = response['instances']
        
        # Filter by VPC if specified
        if vpc_id:
            instances = [i for i in instances if i['vpc']['id'] == vpc_id]
        
        # Summarize instance data
        instance_summary = []
        for instance in instances:
            instance_summary.append({
                'id': instance['id'],
                'name': instance['name'],
                'status': instance['status'],
                'profile': instance['profile']['name'],
                'vpc': instance['vpc'],
                'zone': instance['zone']['name'],
                'primary_network_interface': {
                    'id': instance['primary_network_interface']['id'],
                    'primary_ipv4_address': instance['primary_network_interface'].get('primary_ipv4_address')
                },
                'created_at': instance['created_at']
            })
        
        return {
            'instances': instance_summary,
            'count': len(instance_summary),
            'region': region,
            'vpc_filter': vpc_id
        }
    
    async def list_instance_profiles(self, region: str) -> Dict[str, Any]:
        """List available instance profiles"""
        service = self._get_vpc_client(region)
        response = service.list_instance_profiles().get_result()
        
        profiles = []
        for profile in response['profiles']:
            profiles.append({
                'name': profile['name'],
                'family': profile.get('family'),
                'vcpu_count': profile.get('vcpu_count'),
                'memory': profile.get('memory'),
                'network_interface_count': profile.get('network_interface_count'),
                'bandwidth': profile.get('bandwidth')
            })
        
        return {
            'profiles': profiles,
            'count': len(profiles),
            'region': region
        }
    
    async def list_public_gateways(self, region: str, vpc_id: Optional[str] = None) -> Dict[str, Any]:
        """List public gateways"""
        service = self._get_vpc_client(region)
        response = service.list_public_gateways().get_result()
        
        gateways = response['public_gateways']
        
        # Filter by VPC if specified
        if vpc_id:
            gateways = [g for g in gateways if g['vpc']['id'] == vpc_id]
        
        return {
            'public_gateways': gateways,
            'count': len(gateways),
            'region': region,
            'vpc_filter': vpc_id
        }
    
    async def list_security_groups(self, region: str, vpc_id: Optional[str] = None) -> Dict[str, Any]:
        """List security groups"""
        service = self._get_vpc_client(region)
        response = service.list_security_groups().get_result()
        
        security_groups = response['security_groups']
        
        # Filter by VPC if specified
        if vpc_id:
            security_groups = [sg for sg in security_groups if sg['vpc']['id'] == vpc_id]
        
        # Summarize security groups
        sg_summary = []
        for sg in security_groups:
            sg_summary.append({
                'id': sg['id'],
                'name': sg['name'],
                'vpc': sg['vpc'],
                'rules_count': len(sg.get('rules', [])),
                'created_at': sg['created_at']
            })
        
        return {
            'security_groups': sg_summary,
            'count': len(sg_summary),
            'region': region,
            'vpc_filter': vpc_id
        }
    
    async def get_security_group(self, security_group_id: str, region: str) -> Dict[str, Any]:
        """Get detailed information about a specific security group including rules"""
        service = self._get_vpc_client(region)
        response = service.get_security_group(id=security_group_id).get_result()
        response['region'] = region
        return response
    
    async def list_security_group_rules(self, security_group_id: str, region: str) -> Dict[str, Any]:
        """List all rules for a specific security group"""
        service = self._get_vpc_client(region)
        response = service.list_security_group_rules(security_group_id=security_group_id).get_result()
        
        return {
            'security_group_id': security_group_id,
            'rules': response['rules'],
            'count': len(response['rules']),
            'region': region
        }
    
    async def analyze_ssh_security_groups(self, region: str, vpc_id: Optional[str] = None) -> Dict[str, Any]:
        """Find security groups with SSH access open to 0.0.0.0/0"""
        service = self._get_vpc_client(region)
        
        # Get all security groups
        sg_response = service.list_security_groups().get_result()
        security_groups = sg_response['security_groups']
        
        # Filter by VPC if specified
        if vpc_id:
            security_groups = [sg for sg in security_groups if sg['vpc']['id'] == vpc_id]
        
        risky_groups = []
        
        for sg in security_groups:
            try:
                # Get rules for this security group
                rules_response = service.list_security_group_rules(security_group_id=sg['id']).get_result()
                rules = rules_response['rules']
                
                risky_rules = []
                for rule in rules:
                    # Check for SSH access from anywhere
                    if (rule.get('protocol') == 'tcp' and 
                        rule.get('direction') == 'inbound'):
                        
                        # Check if port 22 is included in the rule
                        port_min = rule.get('port_min', 0)
                        port_max = rule.get('port_max', 65535)
                        
                        if port_min <= 22 <= port_max:
                            # Check if source is 0.0.0.0/0
                            remote = rule.get('remote', {})
                            if (isinstance(remote, dict) and 
                                remote.get('cidr_block') == '0.0.0.0/0'):
                                risky_rules.append(rule)
                
                if risky_rules:
                    risky_groups.append({
                        'security_group_id': sg['id'],
                        'security_group_name': sg['name'],
                        'vpc': sg['vpc'],
                        'risky_rules': risky_rules,
                        'rule_count': len(risky_rules)
                    })
                    
            except ApiException as e:
                logger.warning(f"Error analyzing security group {sg['id']}: {e}")
        
        return {
            'risky_security_groups': risky_groups,
            'count': len(risky_groups),
            'region': region,
            'vpc_filter': vpc_id,
            'analysis_type': 'SSH access from 0.0.0.0/0'
        }
    
    async def analyze_security_groups_by_protocol(self, region: str, protocol: str, 
                                                 port: Optional[int] = None, 
                                                 source_cidr: str = '0.0.0.0/0',
                                                 vpc_id: Optional[str] = None) -> Dict[str, Any]:
        """Analyze security groups for specific protocol/port combinations from a source CIDR"""
        service = self._get_vpc_client(region)
        
        # Get all security groups
        sg_response = service.list_security_groups().get_result()
        security_groups = sg_response['security_groups']
        
        # Filter by VPC if specified
        if vpc_id:
            security_groups = [sg for sg in security_groups if sg['vpc']['id'] == vpc_id]
        
        matching_groups = []
        
        for sg in security_groups:
            try:
                # Get rules for this security group
                rules_response = service.list_security_group_rules(security_group_id=sg['id']).get_result()
                rules = rules_response['rules']
                
                matching_rules = []
                for rule in rules:
                    # Check protocol and direction
                    if (rule.get('protocol') == protocol and 
                        rule.get('direction') == 'inbound'):
                        
                        # Check port if specified
                        if port is not None:
                            port_min = rule.get('port_min', 0)
                            port_max = rule.get('port_max', 65535)
                            
                            if not (port_min <= port <= port_max):
                                continue
                        
                        # Check source CIDR
                        remote = rule.get('remote', {})
                        if (isinstance(remote, dict) and 
                            remote.get('cidr_block') == source_cidr):
                            matching_rules.append(rule)
                
                if matching_rules:
                    matching_groups.append({
                        'security_group_id': sg['id'],
                        'security_group_name': sg['name'],
                        'vpc': sg['vpc'],
                        'matching_rules': matching_rules,
                        'rule_count': len(matching_rules)
                    })
                    
            except ApiException as e:
                logger.warning(f"Error analyzing security group {sg['id']}: {e}")
        
        analysis_desc = f"{protocol.upper()}"
        if port:
            analysis_desc += f" port {port}"
        analysis_desc += f" from {source_cidr}"
        
        return {
            'matching_security_groups': matching_groups,
            'count': len(matching_groups),
            'region': region,
            'vpc_filter': vpc_id,
            'analysis_type': analysis_desc,
            'criteria': {
                'protocol': protocol,
                'port': port,
                'source_cidr': source_cidr
            }
        }
    
    async def list_floating_ips(self, region: str) -> Dict[str, Any]:
        """List all floating IPs in a region"""
        service = self._get_vpc_client(region)
        response = service.list_floating_ips().get_result()
        
        return {
            'floating_ips': response['floating_ips'],
            'count': len(response['floating_ips']),
            'region': region
        }
    
    async def list_routing_tables(self, region: str, vpc_id: str,
                                 start: Optional[str] = None,
                                 limit: Optional[int] = None,
                                 is_default: Optional[bool] = None,
                                 name: Optional[str] = None) -> Dict[str, Any]:
        """List routing tables in a VPC (vpc_id is required)"""
        service = self._get_vpc_client(region)
        
        try:
            # Build parameters dict, excluding None values
            params = {
                'vpc_id': vpc_id,
                'start': start,
                'limit': limit,
                'is_default': is_default
            }
            
            # Remove None values
            params = {k: v for k, v in params.items() if v is not None}
            
            logger.debug(f"Calling list_vpc_routing_tables with params: {params}")
            response = service.list_vpc_routing_tables(**params).get_result()
            logger.debug(f"Got response keys: {list(response.keys())}")
            
            # Extract and enhance routing table information
            routing_tables = []
            response_tables = response.get('routing_tables', [])
            logger.debug(f"Found {len(response_tables)} routing tables")
            
            for table in response_tables:
                table_info = {
                    'id': table.get('id', 'unknown'),
                    'name': table.get('name', 'unknown'),
                    'vpc': table.get('vpc', {}),
                    'is_default': table.get('is_default', False),
                    'lifecycle_state': table.get('lifecycle_state', 'unknown'),
                    'resource_group': table.get('resource_group', {}),
                    'created_at': table.get('created_at', 'unknown'),
                    'href': table.get('href', 'unknown'),
                    'route_direct_link_ingress': table.get('route_direct_link_ingress', False),
                    'route_transit_gateway_ingress': table.get('route_transit_gateway_ingress', False),
                    'route_vpc_zone_ingress': table.get('route_vpc_zone_ingress', False)
                }
                
                # Add subnets if present
                if 'subnets' in table and table['subnets']:
                    subnets = []
                    for subnet in table['subnets']:
                        subnets.append({
                            'id': subnet.get('id', 'unknown'),
                            'name': subnet.get('name', 'unknown'),
                            'href': subnet.get('href', 'unknown')
                        })
                    table_info['subnets'] = subnets
                
                # Add routes count if present
                if 'routes' in table:
                    table_info['routes_count'] = len(table['routes'])
                
                routing_tables.append(table_info)
            
            # Apply name filter if specified (since API doesn't support it)
            if name:
                routing_tables = [rt for rt in routing_tables if name.lower() in rt['name'].lower()]
            
            return {
                'routing_tables': routing_tables,
                'count': len(routing_tables),
                'region': region,
                'filters': {
                    'vpc_id': vpc_id,
                    'is_default': is_default,
                    'name': name
                }
            }
            
        except Exception as e:
            logger.error(f"Error listing routing tables in region {region}: {str(e)}")
            logger.debug(f"Exception details: {type(e).__name__}: {e}")
            return {
                'error': str(e),
                'region': region,
                'routing_tables': [],
                'count': 0
            }
    
    async def get_routing_table(self, vpc_id: str, routing_table_id: str, region: str) -> Dict[str, Any]:
        """Get detailed information about a specific routing table"""
        service = self._get_vpc_client(region)
        
        try:
            logger.debug(f"Getting VPC routing table {routing_table_id} in VPC {vpc_id} in region {region}")
            response = service.get_vpc_routing_table(vpc_id=vpc_id, id=routing_table_id).get_result()
            
            # Extract and enhance routing table information
            table_info = {
                'id': response.get('id', 'unknown'),
                'name': response.get('name', 'unknown'),
                'vpc': response.get('vpc', {}),
                'is_default': response.get('is_default', False),
                'lifecycle_state': response.get('lifecycle_state', 'unknown'),
                'resource_group': response.get('resource_group', {}),
                'created_at': response.get('created_at', 'unknown'),
                'href': response.get('href', 'unknown'),
                'route_direct_link_ingress': response.get('route_direct_link_ingress', False),
                'route_transit_gateway_ingress': response.get('route_transit_gateway_ingress', False),
                'route_vpc_zone_ingress': response.get('route_vpc_zone_ingress', False)
            }
            
            # Add subnets if present
            if 'subnets' in response and response['subnets']:
                subnets = []
                for subnet in response['subnets']:
                    subnets.append({
                        'id': subnet.get('id', 'unknown'),
                        'name': subnet.get('name', 'unknown'),
                        'href': subnet.get('href', 'unknown')
                    })
                table_info['subnets'] = subnets
            
            # Add routes if present
            if 'routes' in response and response['routes']:
                routes = []
                for route in response['routes']:
                    route_info = {
                        'id': route.get('id', 'unknown'),
                        'name': route.get('name', 'unknown'),
                        'destination': route.get('destination', 'unknown'),
                        'action': route.get('action', 'unknown'),
                        'zone': route.get('zone', {}),
                        'created_at': route.get('created_at', 'unknown'),
                        'href': route.get('href', 'unknown'),
                        'lifecycle_state': route.get('lifecycle_state', 'unknown')
                    }
                    
                    # Add next hop information
                    if 'next_hop' in route:
                        route_info['next_hop'] = route['next_hop']
                    
                    routes.append(route_info)
                
                table_info['routes'] = routes
                table_info['routes_count'] = len(routes)
            
            return table_info
            
        except Exception as e:
            logger.error(f"Error getting routing table {routing_table_id} in region {region}: {str(e)}")
            logger.debug(f"Exception details: {type(e).__name__}: {e}")
            return {
                'error': str(e),
                'vpc_id': vpc_id,
                'routing_table_id': routing_table_id,
                'region': region
            }
    
    async def find_routing_table_by_name(self, region: str, vpc_id: str, name: str) -> Dict[str, Any]:
        """Find a routing table by name and return its UUID and details"""
        try:
            # Use the existing list_routing_tables method to search by name
            tables_result = await self.list_routing_tables(region, vpc_id, name=name)
            
            if 'error' in tables_result:
                return {
                    'error': tables_result['error'],
                    'region': region,
                    'vpc_id': vpc_id,
                    'name': name
                }
            
            matching_tables = tables_result.get('routing_tables', [])
            
            if not matching_tables:
                return {
                    'error': f"No routing table found with name '{name}' in VPC {vpc_id}",
                    'region': region,
                    'vpc_id': vpc_id,
                    'name': name,
                    'found_count': 0
                }
            
            # Check for exact match first
            exact_matches = [table for table in matching_tables if table['name'] == name]
            
            if exact_matches:
                if len(exact_matches) > 1:
                    # Multiple exact matches - return all with warning
                    return {
                        'warning': f"Multiple routing tables found with exact name '{name}'",
                        'region': region,
                        'vpc_id': vpc_id,
                        'name': name,
                        'found_count': len(exact_matches),
                        'matches': exact_matches,
                        'primary_match': exact_matches[0]  # Return first as primary
                    }
                else:
                    # Single exact match - ideal case
                    return {
                        'region': region,
                        'vpc_id': vpc_id,
                        'name': name,
                        'found_count': 1,
                        'match': exact_matches[0],
                        'id': exact_matches[0]['id']  # Convenience field for easy access
                    }
            else:
                # No exact matches, return partial matches with warning
                return {
                    'warning': f"No exact match found for '{name}', returning partial matches",
                    'region': region,
                    'vpc_id': vpc_id,
                    'name': name,
                    'found_count': len(matching_tables),
                    'matches': matching_tables
                }
                
        except Exception as e:
            logger.error(f"Error finding routing table by name '{name}' in region {region}: {str(e)}")
            return {
                'error': str(e),
                'region': region,
                'vpc_id': vpc_id,
                'name': name
            }
    
    # Backup Policy Methods
    async def list_backup_policies(self, region: str, 
                                 resource_group_id: Optional[str] = None,
                                 name: Optional[str] = None,
                                 tag: Optional[str] = None,
                                 start: Optional[str] = None,
                                 limit: Optional[int] = None) -> Dict[str, Any]:
        """List backup policies in a region"""
        service = self._get_vpc_client(region)
        
        try:
            response = service.list_backup_policies(
                start=start,
                limit=limit,
                resource_group_id=resource_group_id,
                name=name,
                tag=tag
            ).get_result()
            
            policies = response.get('backup_policies', [])
            
            # Add region info to each policy
            for policy in policies:
                policy['region'] = region
            
            return {
                'backup_policies': policies,
                'count': len(policies),
                'region': region,
                'filters': {
                    'resource_group_id': resource_group_id,
                    'name': name,
                    'tag': tag
                }
            }
        except ApiException as e:
            logger.error(f"Error listing backup policies in region {region}: {e}")
            raise
    
    async def list_backup_policy_jobs(self, backup_policy_id: str, region: str,
                                    status: Optional[str] = None,
                                    backup_policy_plan_id: Optional[str] = None,
                                    start: Optional[str] = None,
                                    limit: Optional[int] = None,
                                    sort: Optional[str] = None,
                                    source_id: Optional[str] = None,
                                    target_snapshots_id: Optional[str] = None,
                                    target_snapshots_crn: Optional[str] = None) -> Dict[str, Any]:
        """List jobs for a specific backup policy"""
        service = self._get_vpc_client(region)
        
        try:
            response = service.list_backup_policy_jobs(
                backup_policy_id=backup_policy_id,
                status=status,
                backup_policy_plan_id=backup_policy_plan_id,
                start=start,
                limit=limit,
                sort=sort,
                source_id=source_id,
                target_snapshots_id=target_snapshots_id,
                target_snapshots_crn=target_snapshots_crn
            ).get_result()
            
            jobs = response.get('jobs', [])
            
            # Add metadata to each job
            for job in jobs:
                job['region'] = region
                job['backup_policy_id'] = backup_policy_id
            
            # Summarize job statuses
            status_summary = {}
            for job in jobs:
                job_status = job.get('status', 'unknown')
                status_summary[job_status] = status_summary.get(job_status, 0) + 1
            
            return {
                'jobs': jobs,
                'count': len(jobs),
                'backup_policy_id': backup_policy_id,
                'region': region,
                'status_summary': status_summary,
                'filters': {
                    'status': status,
                    'backup_policy_plan_id': backup_policy_plan_id,
                    'source_id': source_id
                }
            }
        except ApiException as e:
            logger.error(f"Error listing backup policy jobs for policy {backup_policy_id}: {e}")
            raise
    
    async def list_backup_policy_plans(self, backup_policy_id: str, region: str,
                                     name: Optional[str] = None) -> Dict[str, Any]:
        """List plans for a specific backup policy"""
        service = self._get_vpc_client(region)
        
        try:
            response = service.list_backup_policy_plans(
                backup_policy_id=backup_policy_id,
                name=name
            ).get_result()
            
            plans = response.get('plans', [])
            
            # Add metadata to each plan
            for plan in plans:
                plan['region'] = region
                plan['backup_policy_id'] = backup_policy_id
            
            return {
                'plans': plans,
                'count': len(plans),
                'backup_policy_id': backup_policy_id,
                'region': region,
                'filters': {
                    'name': name
                }
            }
        except ApiException as e:
            logger.error(f"Error listing backup policy plans for policy {backup_policy_id}: {e}")
            raise
    
    async def get_backup_policy_summary(self, backup_policy_id: str, region: str) -> Dict[str, Any]:
        """Get comprehensive information about a backup policy including plans and recent jobs"""
        summary = {
            'backup_policy_id': backup_policy_id,
            'region': region,
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            # Get policy details (this would require get_backup_policy method)
            service = self._get_vpc_client(region)
            policy_response = service.get_backup_policy(id=backup_policy_id).get_result()
            summary['policy_details'] = policy_response
            summary['policy_details']['region'] = region
        except Exception as e:
            summary['policy_details'] = {'error': str(e)}
        
        try:
            # Get plans
            plans_data = await self.list_backup_policy_plans(backup_policy_id, region)
            summary['plans'] = {
                'count': plans_data['count'],
                'plans': plans_data['plans']
            }
        except Exception as e:
            summary['plans'] = {'error': str(e)}
        
        try:
            # Get recent jobs (last 50)
            jobs_data = await self.list_backup_policy_jobs(
                backup_policy_id, region, limit=50, sort='-created_at'
            )
            summary['recent_jobs'] = {
                'count': jobs_data['count'],
                'status_summary': jobs_data['status_summary'],
                'jobs': jobs_data['jobs'][:10]  # Only include last 10 jobs in summary
            }
        except Exception as e:
            summary['recent_jobs'] = {'error': str(e)}
        
        return summary
    
    async def analyze_backup_policies(self, region: str, 
                                    resource_group_id: Optional[str] = None) -> Dict[str, Any]:
        """Analyze backup policies in a region for health and compliance"""
        try:
            # Get all backup policies
            policies_data = await self.list_backup_policies(
                region, resource_group_id=resource_group_id
            )
            policies = policies_data['backup_policies']
            
            analysis = {
                'region': region,
                'timestamp': datetime.now().isoformat(),
                'total_policies': len(policies),
                'policy_health': [],
                'summary': {
                    'active_policies': 0,
                    'inactive_policies': 0,
                    'policies_with_failed_jobs': 0,
                    'policies_without_recent_jobs': 0
                }
            }
            
            for policy in policies:
                policy_id = policy['id']
                policy_name = policy.get('name', 'Unnamed')
                
                policy_health = {
                    'policy_id': policy_id,
                    'policy_name': policy_name,
                    'status': policy.get('lifecycle_state', 'unknown'),
                    'issues': []
                }
                
                # Check if policy is active
                if policy.get('lifecycle_state') == 'stable':
                    analysis['summary']['active_policies'] += 1
                else:
                    analysis['summary']['inactive_policies'] += 1
                    policy_health['issues'].append('Policy is not in stable state')
                
                try:
                    # Check recent jobs
                    jobs_data = await self.list_backup_policy_jobs(
                        policy_id, region, limit=10, sort='-created_at'
                    )
                    
                    recent_jobs = jobs_data['jobs']
                    if not recent_jobs:
                        analysis['summary']['policies_without_recent_jobs'] += 1
                        policy_health['issues'].append('No recent backup jobs found')
                    else:
                        # Check for failed jobs
                        failed_jobs = [j for j in recent_jobs if j.get('status') == 'failed']
                        if failed_jobs:
                            analysis['summary']['policies_with_failed_jobs'] += 1
                            policy_health['issues'].append(f'{len(failed_jobs)} recent failed jobs')
                        
                        policy_health['last_job_status'] = recent_jobs[0].get('status')
                        policy_health['last_job_date'] = recent_jobs[0].get('created_at')
                
                except Exception as e:
                    policy_health['issues'].append(f'Error retrieving jobs: {str(e)}')
                
                analysis['policy_health'].append(policy_health)
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing backup policies in region {region}: {e}")
            raise
    
    async def get_vpc_resources_summary(self, vpc_id: str, region: str) -> Dict[str, Any]:
        """Get a comprehensive summary of all resources in a VPC"""
        summary = {
            'vpc_id': vpc_id,
            'region': region,
            'timestamp': datetime.now().isoformat(),
            'resources': {}
        }
        
        # Get VPC details
        try:
            vpc = await self.get_vpc(vpc_id, region)
            summary['vpc_details'] = {
                'name': vpc['name'],
                'status': vpc['status'],
                'created_at': vpc['created_at']
            }
        except Exception as e:
            summary['vpc_details'] = {'error': str(e)}
        
        # Count subnets
        try:
            subnets_data = await self.list_subnets(region, vpc_id)
            summary['resources']['subnets'] = {
                'count': subnets_data['count'],
                'zones': list(set(s['zone']['name'] for s in subnets_data['subnets']))
            }
        except Exception as e:
            summary['resources']['subnets'] = {'error': str(e)}
        
        # Count instances
        try:
            instances_data = await self.list_instances(region, vpc_id)
            summary['resources']['instances'] = {
                'count': instances_data['count'],
                'by_status': {}
            }
            for instance in instances_data['instances']:
                status = instance['status']
                summary['resources']['instances']['by_status'][status] = \
                    summary['resources']['instances']['by_status'].get(status, 0) + 1
        except Exception as e:
            summary['resources']['instances'] = {'error': str(e)}
        
        # Count security groups
        try:
            sg_data = await self.list_security_groups(region, vpc_id)
            summary['resources']['security_groups'] = {
                'count': sg_data['count']
            }
        except Exception as e:
            summary['resources']['security_groups'] = {'error': str(e)}
        
        # Count public gateways
        try:
            pg_data = await self.list_public_gateways(region, vpc_id)
            summary['resources']['public_gateways'] = {
                'count': pg_data['count']
            }
        except Exception as e:
            summary['resources']['public_gateways'] = {'error': str(e)}
        
        # Analyze SSH security
        try:
            ssh_analysis = await self.analyze_ssh_security_groups(region, vpc_id)
            summary['security_analysis'] = {
                'ssh_open_to_internet': {
                    'risky_groups_count': ssh_analysis['count'],
                    'risky_groups': [
                        {
                            'name': group['security_group_name'],
                            'id': group['security_group_id']
                        } for group in ssh_analysis['risky_security_groups']
                    ]
                }
            }
        except Exception as e:
            summary['security_analysis'] = {'error': str(e)}
        
        return summary

    async def list_vpn_gateways(self, region: str, vpc_id: Optional[str] = None, limit: int = 50, start: Optional[str] = None) -> Dict[str, Any]:
        """List VPN gateways in a region with optional VPC filtering"""
        try:
            service = self._get_vpc_client(region)
            
            kwargs = {"limit": limit}
            if start:
                kwargs["start"] = start
            
            response = service.list_vpn_gateways(**kwargs).get_result()
            gateways = response.get('vpn_gateways', [])
            
            # Filter by VPC if specified
            if vpc_id:
                gateways = [gw for gw in gateways if gw.get('vpc', {}).get('id') == vpc_id]
            
            # Add region context
            for gateway in gateways:
                gateway['region'] = region
            
            return {
                'vpn_gateways': gateways,
                'count': len(gateways),
                'region': region,
                'vpc_id': vpc_id
            }
            
        except ApiException as e:
            logger.error(f"Error listing VPN gateways in region {region}: {e}")
            raise

    async def get_vpn_gateway(self, vpn_gateway_id: str, region: str) -> Dict[str, Any]:
        """Get detailed information about a specific VPN gateway"""
        try:
            service = self._get_vpc_client(region)
            response = service.get_vpn_gateway(vpn_gateway_id).get_result()
            
            # Add region context
            response['region'] = region
            
            return response
            
        except ApiException as e:
            logger.error(f"Error getting VPN gateway {vpn_gateway_id} in region {region}: {e}")
            raise

    async def list_vpn_servers(self, region: str, limit: int = 50, start: Optional[str] = None, name: Optional[str] = None) -> Dict[str, Any]:
        """List VPN servers in a region with optional name filtering"""
        try:
            service = self._get_vpc_client(region)
            
            kwargs = {"limit": limit}
            if start:
                kwargs["start"] = start
            if name:
                kwargs["name"] = name
            
            response = service.list_vpn_servers(**kwargs).get_result()
            servers = response.get('vpn_servers', [])
            
            # Add region context
            for server in servers:
                server['region'] = region
            
            return {
                'vpn_servers': servers,
                'count': len(servers),
                'region': region
            }
            
        except ApiException as e:
            logger.error(f"Error listing VPN servers in region {region}: {e}")
            raise

    async def get_vpn_server(self, vpn_server_id: str, region: str) -> Dict[str, Any]:
        """Get detailed information about a specific VPN server including authentication methods"""
        try:
            service = self._get_vpc_client(region)
            response = service.get_vpn_server(vpn_server_id).get_result()
            
            # Add region context
            response['region'] = region
            
            # Extract and highlight authentication information if available
            auth_info = {}
            
            # Check for certificate-based authentication
            if 'certificate_instance' in response:
                auth_info['certificate_based'] = {
                    'enabled': True,
                    'certificate_instance': response.get('certificate_instance')
                }
            
            # Check for client authentication methods
            if 'client_authentication' in response:
                auth_info['client_authentication'] = response['client_authentication']
            
            # Check for authentication method in the response
            if 'authentication' in response:
                auth_info['authentication_method'] = response['authentication']
            
            # Add authentication summary if we found any auth info
            if auth_info:
                response['authentication_summary'] = auth_info
            
            return response
            
        except ApiException as e:
            logger.error(f"Error getting VPN server {vpn_server_id} in region {region}: {e}")
            raise

    async def get_ike_policy(self, ike_policy_id: str, region: str) -> Dict[str, Any]:
        """Get detailed information about a specific IKE policy"""
        try:
            service = self._get_vpc_client(region)
            response = service.get_ike_policy(ike_policy_id).get_result()
            
            # Add region context
            response['region'] = region
            
            return response
            
        except ApiException as e:
            logger.error(f"Error getting IKE policy {ike_policy_id} in region {region}: {e}")
            raise

    async def get_ipsec_policy(self, ipsec_policy_id: str, region: str) -> Dict[str, Any]:
        """Get detailed information about a specific IPsec policy"""
        try:
            service = self._get_vpc_client(region)
            response = service.get_ipsec_policy(ipsec_policy_id).get_result()
            
            # Add region context
            response['region'] = region
            
            return response
            
        except ApiException as e:
            logger.error(f"Error getting IPsec policy {ipsec_policy_id} in region {region}: {e}")
            raise

    async def get_vpn_server_client_configuration(self, vpn_server_id: str, region: str) -> Dict[str, Any]:
        """Get client configuration for a VPN server"""
        try:
            service = self._get_vpc_client(region)
            response = service.get_vpn_server_client_configuration(vpn_server_id).get_result()
            
            # The API returns a string containing the client configuration file content
            # Handle potential encoding issues with the configuration string
            if isinstance(response, bytes):
                try:
                    config_content = response.decode('utf-8')
                except UnicodeDecodeError:
                    # If it's binary data that can't be decoded, base64 encode it
                    import base64
                    config_content = base64.b64encode(response).decode('ascii')
                    encoding_used = "base64"
                else:
                    encoding_used = "utf-8"
            else:
                # Already a string - ensure it's properly encoded
                try:
                    config_content = str(response).encode('utf-8').decode('utf-8')
                    encoding_used = "utf-8"
                except UnicodeDecodeError:
                    # If there are encoding issues, replace problematic characters
                    config_content = str(response).encode('utf-8', errors='replace').decode('utf-8')
                    encoding_used = "utf-8-replaced"
            
            # Return structured response with metadata
            result = {
                'vpn_server_id': vpn_server_id,
                'region': region,
                'client_configuration_content': config_content,
                'metadata': {
                    'content_type': 'openvpn_configuration',
                    'encoding': encoding_used,
                    'description': 'OpenVPN client configuration file content'
                }
            }
            
            return result
            
        except ApiException as e:
            logger.error(f"Error getting VPN server client configuration for {vpn_server_id} in region {region}: {e}")
            raise

    async def list_vpn_server_clients(self, vpn_server_id: str, region: str, limit: int = 50, start: Optional[str] = None, sort: Optional[str] = None) -> Dict[str, Any]:
        """List clients for a VPN server"""
        try:
            service = self._get_vpc_client(region)
            
            kwargs = {"limit": limit}
            if start:
                kwargs["start"] = start
            if sort:
                kwargs["sort"] = sort
            
            response = service.list_vpn_server_clients(vpn_server_id, **kwargs).get_result()
            clients = response.get('clients', [])
            
            # Add region context and additional metadata
            for client in clients:
                client['region'] = region
                client['vpn_server_id'] = vpn_server_id
            
            return {
                'vpn_server_id': vpn_server_id,
                'clients': clients,
                'count': len(clients),
                'region': region,
                'total_count': response.get('total_count', len(clients)),
                'limit': response.get('limit', limit)
            }
            
        except ApiException as e:
            logger.error(f"Error listing VPN server clients for {vpn_server_id} in region {region}: {e}")
            raise

    async def list_vpn_server_routes(self, vpn_server_id: str, region: str, limit: int = 50, start: Optional[str] = None) -> Dict[str, Any]:
        """List routes for a VPN server"""
        try:
            service = self._get_vpc_client(region)
            
            kwargs = {"limit": limit}
            if start:
                kwargs["start"] = start
            
            response = service.list_vpn_server_routes(vpn_server_id, **kwargs).get_result()
            routes = response.get('routes', [])
            
            # Add region context
            for route in routes:
                route['region'] = region
            
            return {
                'vpn_server_id': vpn_server_id,
                'routes': routes,
                'count': len(routes),
                'region': region
            }
            
        except ApiException as e:
            logger.error(f"Error listing VPN server routes for {vpn_server_id} in region {region}: {e}")
            raise


# Convenience functions for backward compatibility and ease of use
async def create_vpc_manager(api_key: str) -> VPCManager:
    """Create a VPC manager instance with API key authentication"""
    authenticator = IAMAuthenticator(apikey=api_key)
    return VPCManager(authenticator)


def analyze_security_rule_risk(rule: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze a single security group rule for potential risks"""
    risk_factors = []
    risk_level = "low"
    
    if rule.get('direction') == 'inbound':
        # Check for overly permissive source
        remote = rule.get('remote', {})
        if isinstance(remote, dict) and remote.get('cidr_block') == '0.0.0.0/0':
            risk_factors.append("Source allows traffic from anywhere (0.0.0.0/0)")
            risk_level = "high"
        
        # Check for commonly attacked ports
        protocol = rule.get('protocol')
        port_min = rule.get('port_min', 0)
        port_max = rule.get('port_max', 65535)
        
        risky_ports = {
            22: "SSH",
            23: "Telnet",
            3389: "RDP",
            1433: "SQL Server",
            3306: "MySQL",
            5432: "PostgreSQL",
            21: "FTP",
            25: "SMTP"
        }
        
        for port, service in risky_ports.items():
            if port_min <= port <= port_max and protocol == 'tcp':
                risk_factors.append(f"Exposes {service} (port {port})")
                if port in [22, 23, 3389] and risk_level != "high":
                    risk_level = "medium"
        
        # Check for wide port ranges
        if port_max - port_min > 1000:
            risk_factors.append(f"Very wide port range ({port_min}-{port_max})")
            if risk_level == "low":
                risk_level = "medium"
    
    return {
        'rule_id': rule.get('id'),
        'risk_level': risk_level,
        'risk_factors': risk_factors,
        'protocol': rule.get('protocol'),
        'direction': rule.get('direction'),
        'port_range': f"{rule.get('port_min', 'any')}-{rule.get('port_max', 'any')}" if rule.get('port_min') else "all"
    }


def analyze_backup_policy_health(policy: Dict[str, Any], jobs: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze the health of a backup policy based on its configuration and recent jobs"""
    health_score = 100
    issues = []
    recommendations = []
    
    # Check policy state
    if policy.get('lifecycle_state') != 'stable':
        health_score -= 30
        issues.append(f"Policy is in {policy.get('lifecycle_state', 'unknown')} state")
        recommendations.append("Ensure policy is in stable state")
    
    # Check if there are any jobs
    if not jobs:
        health_score -= 40
        issues.append("No backup jobs found")
        recommendations.append("Verify that backup schedules are active and resources are attached")
    else:
        # Check recent job failures
        recent_jobs = jobs[:10]  # Last 10 jobs
        failed_jobs = [j for j in recent_jobs if j.get('status') == 'failed']
        
        if failed_jobs:
            failure_rate = len(failed_jobs) / len(recent_jobs)
            if failure_rate > 0.5:
                health_score -= 30
                issues.append(f"High failure rate: {len(failed_jobs)}/{len(recent_jobs)} recent jobs failed")
                recommendations.append("Investigate job failures and fix underlying issues")
            elif failure_rate > 0.2:
                health_score -= 15
                issues.append(f"Some recent failures: {len(failed_jobs)}/{len(recent_jobs)} recent jobs failed")
                recommendations.append("Monitor job failures and address any issues")
        
        # Check job frequency
        if len(recent_jobs) < 5:
            health_score -= 10
            issues.append("Few recent backup jobs")
            recommendations.append("Consider increasing backup frequency if appropriate")
        
        # Check for very old last job
        if recent_jobs:
            try:
                from datetime import datetime, timedelta
                last_job_date = datetime.fromisoformat(recent_jobs[0]['created_at'].replace('Z', '+00:00'))
                days_ago = (datetime.now().astimezone() - last_job_date).days
                
                if days_ago > 7:
                    health_score -= 20
                    issues.append(f"Last backup job was {days_ago} days ago")
                    recommendations.append("Check if backup schedule is still active")
                elif days_ago > 3:
                    health_score -= 10
                    issues.append(f"Last backup job was {days_ago} days ago")
            except Exception:
                pass  # Skip date analysis if parsing fails
    
    # Determine overall health status
    if health_score >= 80:
        status = "healthy"
    elif health_score >= 60:
        status = "warning"
    else:
        status = "critical"
    
    return {
        'health_score': max(0, health_score),
        'status': status,
        'issues': issues,
        'recommendations': recommendations,
        'analysis_timestamp': datetime.now().isoformat()
    }