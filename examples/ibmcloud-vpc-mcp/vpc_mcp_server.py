"""
IBM Cloud VPC MCP Server
Provides VPC resource management capabilities through MCP protocol
"""

import os
import json
import logging
from typing import Dict, List, Any
import asyncio

from mcp.server import Server
from mcp.types import Tool, TextContent
import mcp.server.stdio

from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from utils import VPCManager
from storage import StorageManager


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VPCMCPServer:
    def __init__(self):
        self.server = Server("ibm-vpc-mcp")
        self.vpc_manager = None
        self._setup_handlers()
        # Add this line to initialize the StorageManager
        self.storage_manager = None
        self._setup_handlers()

    def _setup_handlers(self):
        """Set up MCP server handlers"""
        @self.server.list_tools()
        async def list_tools() -> List[Tool]:
            return [
                Tool(
                    name="list_regions",
                    description="List all available IBM Cloud VPC regions",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                ),
                Tool(
                    name="list_vpcs",
                    description="List VPCs in account or specific region",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "region": {
                                "type": "string",
                                "description": "Region name (optional, defaults to all regions)"
                            }
                        }
                    }
                ),
                Tool(
                    name="get_vpc",
                    description="Get details of a specific VPC",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "vpc_id": {
                                "type": "string",
                                "description": "VPC ID"
                            },
                            "region": {
                                "type": "string",
                                "description": "Region where VPC is located"
                            }
                        },
                        "required": ["vpc_id", "region"]
                    }
                ),
                Tool(
                    name="list_subnets",
                    description="List subnets in a VPC or region",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "region": {
                                "type": "string",
                                "description": "Region name"
                            },
                            "vpc_id": {
                                "type": "string",
                                "description": "Filter by VPC ID (optional)"
                            }
                        },
                        "required": ["region"]
                    }
                ),
                Tool(
                    name="list_instances",
                    description="List compute instances",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "region": {
                                "type": "string",
                                "description": "Region name"
                            },
                            "vpc_id": {
                                "type": "string",
                                "description": "Filter by VPC ID (optional)"
                            }
                        },
                        "required": ["region"]
                    }
                ),
                Tool(
                    name="list_instance_profiles",
                    description="List available instance profiles",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "region": {
                                "type": "string",
                                "description": "Region name"
                            }
                        },
                        "required": ["region"]
                    }
                ),
                Tool(
                    name="list_public_gateways",
                    description="List public gateways",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "region": {
                                "type": "string",
                                "description": "Region name"
                            },
                            "vpc_id": {
                                "type": "string",
                                "description": "Filter by VPC ID (optional)"
                            }
                        },
                        "required": ["region"]
                    }
                ),
                Tool(
                    name="list_security_groups",
                    description="List security groups",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "region": {
                                "type": "string",
                                "description": "Region name"
                            },
                            "vpc_id": {
                                "type": "string",
                                "description": "Filter by VPC ID (optional)"
                            }
                        },
                        "required": ["region"]
                    }
                ),
                Tool(
                    name="get_security_group",
                    description="Get detailed information about a specific security group including rules",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "security_group_id": {
                                "type": "string",
                                "description": "Security group ID"
                            },
                            "region": {
                                "type": "string",
                                "description": "Region name"
                            }
                        },
                        "required": ["security_group_id", "region"]
                    }
                ),
                Tool(
                    name="list_security_group_rules",
                    description="List all rules for a specific security group",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "security_group_id": {
                                "type": "string",
                                "description": "Security group ID"
                            },
                            "region": {
                                "type": "string",
                                "description": "Region name"
                            }
                        },
                        "required": ["security_group_id", "region"]
                    }
                ),
                Tool(
                    name="analyze_ssh_security_groups",
                    description="Find security groups with SSH access open to 0.0.0.0/0",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "region": {
                                "type": "string",
                                "description": "Region name"
                            },
                            "vpc_id": {
                                "type": "string",
                                "description": "Filter by VPC ID (optional)"
                            }
                        },
                        "required": ["region"]
                    }
                ),
                Tool(
                    name="analyze_security_groups_by_protocol",
                    description="Analyze security groups for specific protocol/port combinations from a source CIDR",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "region": {
                                "type": "string",
                                "description": "Region name"
                            },
                            "protocol": {
                                "type": "string",
                                "description": "Protocol (tcp, udp, icmp)"
                            },
                            "port": {
                                "type": "integer",
                                "description": "Port number (optional)"
                            },
                            "source_cidr": {
                                "type": "string",
                                "description": "Source CIDR block (default: 0.0.0.0/0)",
                                "default": "0.0.0.0/0"
                            },
                            "vpc_id": {
                                "type": "string",
                                "description": "Filter by VPC ID (optional)"
                            }
                        },
                        "required": ["region", "protocol"]
                    }
                ),
                Tool(
                    name="list_floating_ips",
                    description="List all floating IPs in a region",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "region": {
                                "type": "string",
                                "description": "Region name"
                            }
                        },
                        "required": ["region"]
                    }
                ),
                Tool(
                    name="get_vpc_resources_summary",
                    description="Get a summary of all resources in a VPC including security analysis",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "vpc_id": {
                                "type": "string",
                                "description": "VPC ID"
                            },
                            "region": {
                                "type": "string",
                                "description": "Region where VPC is located"
                            }
                        },
                        "required": ["vpc_id", "region"]
                    }
                ),
                # Backup Policy Tools
                Tool(
                    name="list_backup_policies",
                    description="List backup policies in a region with optional filtering",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "region": {
                                "type": "string",
                                "description": "Region name"
                            },
                            "resource_group_id": {
                                "type": "string",
                                "description": "Filter by resource group ID (optional)"
                            },
                            "name": {
                                "type": "string",
                                "description": "Filter by policy name (optional)"
                            },
                            "tag": {
                                "type": "string",
                                "description": "Filter by tag (optional)"
                            },
                            "start": {
                                "type": "string",
                                "description": "Pagination start token (optional)"
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Maximum number of results (optional)"
                            }
                        },
                        "required": ["region"]
                    }
                ),
                Tool(
                    name="list_backup_policy_jobs",
                    description="List jobs for a specific backup policy",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "backup_policy_id": {
                                "type": "string",
                                "description": "Backup policy ID"
                            },
                            "region": {
                                "type": "string",
                                "description": "Region name"
                            },
                            "status": {
                                "type": "string",
                                "description": "Filter by job status (optional)"
                            },
                            "backup_policy_plan_id": {
                                "type": "string",
                                "description": "Filter by plan ID (optional)"
                            },
                            "start": {
                                "type": "string",
                                "description": "Pagination start token (optional)"
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Maximum number of results (optional)"
                            },
                            "sort": {
                                "type": "string",
                                "description": "Sort order (optional, e.g., '-created_at')"
                            },
                            "source_id": {
                                "type": "string",
                                "description": "Filter by source ID (optional)"
                            },
                            "target_snapshots_id": {
                                "type": "string",
                                "description": "Filter by target snapshot ID (optional)"
                            },
                            "target_snapshots_crn": {
                                "type": "string",
                                "description": "Filter by target snapshot CRN (optional)"
                            }
                        },
                        "required": ["backup_policy_id", "region"]
                    }
                ),
                Tool(
                    name="list_backup_policy_plans",
                    description="List plans for a specific backup policy",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "backup_policy_id": {
                                "type": "string",
                                "description": "Backup policy ID"
                            },
                            "region": {
                                "type": "string",
                                "description": "Region name"
                            },
                            "name": {
                                "type": "string",
                                "description": "Filter by plan name (optional)"
                            }
                        },
                        "required": ["backup_policy_id", "region"]
                    }
                ),
                Tool(
                    name="get_backup_policy_summary",
                    description="Get comprehensive information about a backup policy including plans and recent jobs",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "backup_policy_id": {
                                "type": "string",
                                "description": "Backup policy ID"
                            },
                            "region": {
                                "type": "string",
                                "description": "Region name"
                            }
                        },
                        "required": ["backup_policy_id", "region"]
                    }
                ),
                Tool(
                    name="analyze_backup_policies",
                    description="Analyze backup policies in a region for health and compliance",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "region": {
                                "type": "string",
                                "description": "Region name"
                            },
                            "resource_group_id": {
                                "type": "string",
                                "description": "Filter by resource group ID (optional)"
                            }
                        },
                        "required": ["region"]
                    }
                ),
        Tool(
            name="list_volumes",
            description="List block storage volumes in a region with optional filtering",
            inputSchema={
                "type": "object",
                "properties": {
                    "region": {
                        "type": "string",
                        "description": "Region name"
                    },
                    "start": {
                        "type": "string",
                        "description": "Pagination start token (optional)"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results (optional)"
                    },
                    "attachment_state": {
                        "type": "string",
                        "description": "Filter by attachment state (optional: attached, unattached)"
                    },
                    "encryption": {
                        "type": "string",
                        "description": "Filter by encryption type (optional)"
                    },
                    "name": {
                        "type": "string",
                        "description": "Filter by volume name (optional)"
                    },
                    "operating_system_family": {
                        "type": "string",
                        "description": "Filter by operating system family (optional)"
                    },
                    "operating_system_architecture": {
                        "type": "string",
                        "description": "Filter by operating system architecture (optional)"
                    },
                    "tag": {
                        "type": "string",
                        "description": "Filter by tag (optional)"
                    },
                    "zone_name": {
                        "type": "string",
                        "description": "Filter by zone name (optional)"
                    }
                },
                "required": ["region"]
            }
        ),
        Tool(
            name="list_volume_profiles",
            description="List available volume profiles in a region",
            inputSchema={
                "type": "object",
                "properties": {
                    "region": {
                        "type": "string",
                        "description": "Region name"
                    },
                    "start": {
                        "type": "string",
                        "description": "Pagination start token (optional)"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results (optional)"
                    }
                },
                "required": ["region"]
            }
        ),
        Tool(
            name="get_volume",
            description="Get detailed information about a specific volume",
            inputSchema={
                "type": "object",
                "properties": {
                    "volume_id": {
                        "type": "string",
                        "description": "Volume ID"
                    },
                    "region": {
                        "type": "string",
                        "description": "Region name"
                    }
                },
                "required": ["volume_id", "region"]
            }
        ),
        Tool(
            name="analyze_storage_usage",
            description="Analyze block storage usage in a region",
            inputSchema={
                "type": "object",
                "properties": {
                    "region": {
                        "type": "string",
                        "description": "Region name"
                    }
                },
                "required": ["region"]
            }
        ),
        Tool(
            name="list_shares",
            description="List file shares in a region with optional filtering",
            inputSchema={
                "type": "object",
                "properties": {
                    "region": {
                        "type": "string",
                        "description": "Region name"
                    },
                    "start": {
                        "type": "string",
                        "description": "Pagination start token (optional)"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results (optional)"
                    },
                    "resource_group_id": {
                        "type": "string",
                        "description": "Filter by resource group ID (optional)"
                    },
                    "name": {
                        "type": "string",
                        "description": "Filter by share name (optional)"
                    },
                    "sort": {
                        "type": "string",
                        "description": "Sort order (optional)"
                    },
                    "replication_role": {
                        "type": "string",
                        "description": "Filter by replication role (optional)"
                    }
                },
                "required": ["region"]
            }
        ),
        Tool(
            name="get_share",
            description="Get detailed information about a specific file share",
            inputSchema={
                "type": "object",
                "properties": {
                    "share_id": {
                        "type": "string",
                        "description": "Share ID"
                    },
                    "region": {
                        "type": "string",
                        "description": "Region name"
                    }
                },
                "required": ["share_id", "region"]
            }
        ),
        Tool(
            name="list_share_profiles",
            description="List available file share profiles in a region",
            inputSchema={
                "type": "object",
                "properties": {
                    "region": {
                        "type": "string",
                        "description": "Region name"
                    },
                    "start": {
                        "type": "string",
                        "description": "Pagination start token (optional)"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results (optional)"
                    },
                    "sort": {
                        "type": "string",
                        "description": "Sort order (optional)"
                    }
                },
                "required": ["region"]
            }
        ),
        Tool(
            name="list_routing_tables",
            description="List routing tables in a VPC (vpc_id is required)",
            inputSchema={
                "type": "object",
                "properties": {
                    "region": {
                        "type": "string",
                        "description": "Region name"
                    },
                    "vpc_id": {
                        "type": "string",
                        "description": "VPC ID (required)"
                    },
                    "start": {
                        "type": "string",
                        "description": "Pagination start token (optional)"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results (optional)"
                    },
                    "is_default": {
                        "type": "boolean",
                        "description": "Filter by default routing table (optional)"
                    },
                    "name": {
                        "type": "string",
                        "description": "Filter by routing table name (optional)"
                    }
                },
                "required": ["region", "vpc_id"]
            }
        ),
        Tool(
            name="get_routing_table",
            description="Get detailed information about a specific routing table",
            inputSchema={
                "type": "object",
                "properties": {
                    "vpc_id": {
                        "type": "string",
                        "description": "VPC ID"
                    },
                    "routing_table_id": {
                        "type": "string",
                        "description": "Routing table ID"
                    },
                    "region": {
                        "type": "string",
                        "description": "Region name"
                    }
                },
                "required": ["vpc_id", "routing_table_id", "region"]
            }
        ),
        Tool(
            name="find_routing_table_by_name",
            description="Find a routing table by name and return its UUID and details",
            inputSchema={
                "type": "object",
                "properties": {
                    "region": {
                        "type": "string",
                        "description": "Region name"
                    },
                    "vpc_id": {
                        "type": "string",
                        "description": "VPC ID"
                    },
                    "name": {
                        "type": "string",
                        "description": "Routing table name to search for"
                    }
                },
                "required": ["region", "vpc_id", "name"]
            }
        ),
        Tool(
            name="list_snapshots",
            description="List block storage snapshots in a region with optional filtering",
            inputSchema={
                "type": "object",
                "properties": {
                    "region": {
                        "type": "string",
                        "description": "Region name"
                    },
                    "start": {
                        "type": "string",
                        "description": "Pagination start token (optional)"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results (optional)"
                    },
                    "name": {
                        "type": "string",
                        "description": "Filter by snapshot name (optional)"
                    },
                    "source_volume_id": {
                        "type": "string",
                        "description": "Filter by source volume ID (optional)"
                    },
                    "resource_group_id": {
                        "type": "string",
                        "description": "Filter by resource group ID (optional)"
                    },
                    "sort": {
                        "type": "string",
                        "description": "Sort order (optional)"
                    }
                },
                "required": ["region"]
            }
        ),
        Tool(
            name="get_snapshot",
            description="Get detailed information about a specific snapshot",
            inputSchema={
                "type": "object",
                "properties": {
                    "snapshot_id": {
                        "type": "string",
                        "description": "Snapshot ID"
                    },
                    "region": {
                        "type": "string",
                        "description": "Region name"
                    }
                },
                "required": ["snapshot_id", "region"]
            }
        ),
        Tool(
            name="analyze_snapshot_usage",
            description="Analyze snapshot usage in a region",
            inputSchema={
                "type": "object",
                "properties": {
                    "region": {
                        "type": "string",
                        "description": "Region name"
                    }
                },
                "required": ["region"]
            }
        ),
        Tool(
            name="list_vpn_gateways",
            description="List VPN gateways in a region with optional VPC filtering",
            inputSchema={
                "type": "object",
                "properties": {
                    "region": {
                        "type": "string",
                        "description": "Region name"
                    },
                    "vpc_id": {
                        "type": "string",
                        "description": "Optional VPC ID to filter gateways"
                    },
                    "limit": {
                        "type": "number",
                        "description": "Maximum number of gateways to return (default 50)"
                    },
                    "start": {
                        "type": "string", 
                        "description": "Pagination start token"
                    }
                },
                "required": ["region"]
            }
        ),
        Tool(
            name="get_vpn_gateway",
            description="Get detailed information about a specific VPN gateway",
            inputSchema={
                "type": "object",
                "properties": {
                    "vpn_gateway_id": {
                        "type": "string",
                        "description": "VPN gateway ID"
                    },
                    "region": {
                        "type": "string",
                        "description": "Region name"
                    }
                },
                "required": ["vpn_gateway_id", "region"]
            }
        ),
        Tool(
            name="list_vpn_servers",
            description="List VPN servers in a region with optional name filtering",
            inputSchema={
                "type": "object",
                "properties": {
                    "region": {
                        "type": "string",
                        "description": "Region name"
                    },
                    "limit": {
                        "type": "number",
                        "description": "Maximum number of servers to return (default 50)"
                    },
                    "start": {
                        "type": "string",
                        "description": "Pagination start token"
                    },
                    "name": {
                        "type": "string",
                        "description": "Optional name filter for servers"
                    }
                },
                "required": ["region"]
            }
        ),
        Tool(
            name="get_vpn_server", 
            description="Get detailed information about a specific VPN server",
            inputSchema={
                "type": "object",
                "properties": {
                    "vpn_server_id": {
                        "type": "string",
                        "description": "VPN server ID"
                    },
                    "region": {
                        "type": "string",
                        "description": "Region name"
                    }
                },
                "required": ["vpn_server_id", "region"]
            }
        ),
        Tool(
            name="get_ike_policy",
            description="Get detailed information about a specific IKE policy",
            inputSchema={
                "type": "object",
                "properties": {
                    "ike_policy_id": {
                        "type": "string",
                        "description": "IKE policy ID"
                    },
                    "region": {
                        "type": "string",
                        "description": "Region name"
                    }
                },
                "required": ["ike_policy_id", "region"]
            }
        ),
        Tool(
            name="get_ipsec_policy",
            description="Get detailed information about a specific IPsec policy",
            inputSchema={
                "type": "object",
                "properties": {
                    "ipsec_policy_id": {
                        "type": "string",
                        "description": "IPsec policy ID"
                    },
                    "region": {
                        "type": "string",
                        "description": "Region name"
                    }
                },
                "required": ["ipsec_policy_id", "region"]
            }
        ),
        Tool(
            name="get_vpn_server_client_configuration",
            description="Get client configuration for a VPN server",
            inputSchema={
                "type": "object",
                "properties": {
                    "vpn_server_id": {
                        "type": "string",
                        "description": "VPN server ID"
                    },
                    "region": {
                        "type": "string",
                        "description": "Region name"
                    }
                },
                "required": ["vpn_server_id", "region"]
            }
        ),
        Tool(
            name="list_vpn_server_routes",
            description="List routes for a VPN server",
            inputSchema={
                "type": "object",
                "properties": {
                    "vpn_server_id": {
                        "type": "string",
                        "description": "VPN server ID"
                    },
                    "region": {
                        "type": "string",
                        "description": "Region name"
                    },
                    "limit": {
                        "type": "number",
                        "description": "Maximum number of routes to return (default 50)"
                    },
                    "start": {
                        "type": "string",
                        "description": "Pagination start token"
                    }
                },
                "required": ["vpn_server_id", "region"]
            }
        ),
        Tool(
            name="list_vpn_server_clients",
            description="List clients connected to a VPN server",
            inputSchema={
                "type": "object",
                "properties": {
                    "vpn_server_id": {
                        "type": "string",
                        "description": "VPN server ID"
                    },
                    "region": {
                        "type": "string",
                        "description": "Region name"
                    },
                    "limit": {
                        "type": "number",
                        "description": "Maximum number of clients to return (default 50)"
                    },
                    "start": {
                        "type": "string",
                        "description": "Pagination start token"
                    },
                    "sort": {
                        "type": "string",
                        "description": "Sort field (e.g., 'created_at', 'common_name')"
                    }
                },
                "required": ["vpn_server_id", "region"]
            }
        )
    ]
    
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            try:
                # Initialize VPC manager if not already done
                if not self.vpc_manager:
                    api_key = os.environ.get('IBMCLOUD_API_KEY')
                    if not api_key:
                        raise ValueError("IBMCLOUD_API_KEY environment variable not set")
                    authenticator = IAMAuthenticator(apikey=api_key)
                    self.vpc_manager = VPCManager(authenticator)
                    self.storage_manager = StorageManager(None, authenticator)
                
                # Route to appropriate handler
                if name == "list_regions":
                    result = await self.vpc_manager.list_regions()
                elif name == "list_vpcs":
                    result = await self.vpc_manager.list_vpcs(arguments.get('region'))
                elif name == "get_vpc":
                    result = await self.vpc_manager.get_vpc(arguments['vpc_id'], arguments['region'])
                elif name == "list_subnets":
                    result = await self.vpc_manager.list_subnets(arguments['region'], arguments.get('vpc_id'))
                elif name == "list_instances":
                    result = await self.vpc_manager.list_instances(arguments['region'], arguments.get('vpc_id'))
                elif name == "list_instance_profiles":
                    result = await self.vpc_manager.list_instance_profiles(arguments['region'])
                elif name == "list_public_gateways":
                    result = await self.vpc_manager.list_public_gateways(arguments['region'], arguments.get('vpc_id'))
                elif name == "list_security_groups":
                    result = await self.vpc_manager.list_security_groups(arguments['region'], arguments.get('vpc_id'))
                elif name == "get_security_group":
                    result = await self.vpc_manager.get_security_group(arguments['security_group_id'], arguments['region'])
                elif name == "list_security_group_rules":
                    result = await self.vpc_manager.list_security_group_rules(arguments['security_group_id'], arguments['region'])
                elif name == "analyze_ssh_security_groups":
                    result = await self.vpc_manager.analyze_ssh_security_groups(arguments['region'], arguments.get('vpc_id'))
                elif name == "analyze_security_groups_by_protocol":
                    result = await self.vpc_manager.analyze_security_groups_by_protocol(
                        arguments['region'], 
                        arguments['protocol'],
                        arguments.get('port'),
                        arguments.get('source_cidr', '0.0.0.0/0'),
                        arguments.get('vpc_id')
                    )
                elif name == "list_floating_ips":
                    result = await self.vpc_manager.list_floating_ips(arguments['region'])
                elif name == "get_vpc_resources_summary":
                    result = await self.vpc_manager.get_vpc_resources_summary(arguments['vpc_id'], arguments['region'])
                # Backup Policy handlers
                elif name == "list_backup_policies":
                    result = await self.vpc_manager.list_backup_policies(
                        arguments['region'],
                        arguments.get('resource_group_id'),
                        arguments.get('name'),
                        arguments.get('tag'),
                        arguments.get('start'),
                        arguments.get('limit')
                    )
                elif name == "list_backup_policy_jobs":
                    result = await self.vpc_manager.list_backup_policy_jobs(
                        arguments['backup_policy_id'],
                        arguments['region'],
                        arguments.get('status'),
                        arguments.get('backup_policy_plan_id'),
                        arguments.get('start'),
                        arguments.get('limit'),
                        arguments.get('sort'),
                        arguments.get('source_id'),
                        arguments.get('target_snapshots_id'),
                        arguments.get('target_snapshots_crn')
                    )
                elif name == "list_backup_policy_plans":
                    result = await self.vpc_manager.list_backup_policy_plans(
                        arguments['backup_policy_id'],
                        arguments['region'],
                        arguments.get('name')
                    )
                elif name == "get_backup_policy_summary":
                    result = await self.vpc_manager.get_backup_policy_summary(
                        arguments['backup_policy_id'],
                        arguments['region']
                    )
                elif name == "analyze_backup_policies":
                    result = await self.vpc_manager.analyze_backup_policies(
                        arguments['region'],
                        arguments.get('resource_group_id')
                    )
                elif name == "list_volumes":
                    result = await self.storage_manager.list_volumes(
                        arguments['region'],
                        start=arguments.get('start'),
                        limit=arguments.get('limit'),
                        attachment_state=arguments.get('attachment_state'),
                        encryption=arguments.get('encryption'),
                        name=arguments.get('name'),
                        operating_system_family=arguments.get('operating_system_family'),
                        operating_system_architecture=arguments.get('operating_system_architecture'),
                        tag=arguments.get('tag'),
                        zone_name=arguments.get('zone_name')
                    )
                elif name == "list_volume_profiles":
                    result = await self.storage_manager.list_volume_profiles(
                        arguments['region'],
                        start=arguments.get('start'),
                        limit=arguments.get('limit')
                    )
                elif name == "get_volume":
                    result = await self.storage_manager.get_volume(
                        arguments['volume_id'],
                        arguments['region']
                    )
                elif name == "analyze_storage_usage":
                    result = await self.storage_manager.analyze_storage_usage(
                        arguments['region']
                    )
                elif name == "list_shares":
                    result = await self.storage_manager.list_shares(
                        arguments['region'],
                        start=arguments.get('start'),
                        limit=arguments.get('limit'),
                        resource_group_id=arguments.get('resource_group_id'),
                        name=arguments.get('name'),
                        sort=arguments.get('sort'),
                        replication_role=arguments.get('replication_role')
                    )
                elif name == "get_share":
                    result = await self.storage_manager.get_share(
                        arguments['share_id'],
                        arguments['region']
                    )
                elif name == "list_share_profiles":
                    result = await self.storage_manager.list_share_profiles(
                        arguments['region'],
                        start=arguments.get('start'),
                        limit=arguments.get('limit'),
                        sort=arguments.get('sort')
                    )
                elif name == "list_routing_tables":
                    result = await self.vpc_manager.list_routing_tables(
                        arguments['region'],
                        arguments['vpc_id'],
                        start=arguments.get('start'),
                        limit=arguments.get('limit'),
                        is_default=arguments.get('is_default'),
                        name=arguments.get('name')
                    )
                elif name == "get_routing_table":
                    result = await self.vpc_manager.get_routing_table(
                        arguments['vpc_id'],
                        arguments['routing_table_id'],
                        arguments['region']
                    )
                elif name == "find_routing_table_by_name":
                    result = await self.vpc_manager.find_routing_table_by_name(
                        arguments['region'],
                        arguments['vpc_id'],
                        arguments['name']
                    )
                elif name == "list_snapshots":
                    result = await self.storage_manager.list_snapshots(
                        arguments['region'],
                        start=arguments.get('start'),
                        limit=arguments.get('limit'),
                        name=arguments.get('name'),
                        source_volume_id=arguments.get('source_volume_id'),
                        resource_group_id=arguments.get('resource_group_id'),
                        sort=arguments.get('sort')
                    )
                elif name == "get_snapshot":
                    result = await self.storage_manager.get_snapshot(
                        arguments['snapshot_id'],
                        arguments['region']
                    )
                elif name == "analyze_snapshot_usage":
                    result = await self.storage_manager.analyze_snapshot_usage(
                        arguments['region']
                    )
                elif name == "list_vpn_gateways":
                    result = await self.vpc_manager.list_vpn_gateways(
                        arguments['region'],
                        arguments.get('vpc_id'),
                        arguments.get('limit', 50),
                        arguments.get('start')
                    )
                elif name == "get_vpn_gateway":
                    result = await self.vpc_manager.get_vpn_gateway(
                        arguments['vpn_gateway_id'],
                        arguments['region']
                    )
                elif name == "list_vpn_servers":
                    result = await self.vpc_manager.list_vpn_servers(
                        arguments['region'],
                        arguments.get('limit', 50),
                        arguments.get('start'),
                        arguments.get('name')
                    )
                elif name == "get_vpn_server":
                    result = await self.vpc_manager.get_vpn_server(
                        arguments['vpn_server_id'],
                        arguments['region']
                    )
                elif name == "get_ike_policy":
                    result = await self.vpc_manager.get_ike_policy(
                        arguments['ike_policy_id'],
                        arguments['region']
                    )
                elif name == "get_ipsec_policy":
                    result = await self.vpc_manager.get_ipsec_policy(
                        arguments['ipsec_policy_id'],
                        arguments['region']
                    )
                elif name == "get_vpn_server_client_configuration":
                    result = await self.vpc_manager.get_vpn_server_client_configuration(
                        arguments['vpn_server_id'],
                        arguments['region']
                    )
                elif name == "list_vpn_server_routes":
                    result = await self.vpc_manager.list_vpn_server_routes(
                        arguments['vpn_server_id'],
                        arguments['region'],
                        arguments.get('limit', 50),
                        arguments.get('start')
                    )
                elif name == "list_vpn_server_clients":
                    result = await self.vpc_manager.list_vpn_server_clients(
                        arguments['vpn_server_id'],
                        arguments['region'],
                        arguments.get('limit', 50),
                        arguments.get('start'),
                        arguments.get('sort')
                    )
                else:
                    raise ValueError(f"Unknown tool: {name}")
                
                return [TextContent(
                    type="text",
                    text=json.dumps(result, indent=2)
                )]
                
            except Exception as e:
                logger.error(f"Error executing tool {name}: {str(e)}")
                return [TextContent(
                    type="text",
                    text=f"Error: {str(e)}"
                )]
                
    async def run(self):
        """Run the MCP server"""
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options()
            )


async def main():
    server = VPCMCPServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())