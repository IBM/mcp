#!/usr/bin/env python3
"""
Simple MCP client to test storage tools without Claude Desktop
"""
import os
import json
import asyncio
import subprocess
from typing import Dict, Any

class SimpleMCPClient:
    """Simple MCP client for testing"""
    
    def __init__(self):
        self.process = None
    
    async def start_server(self):
        """Start the MCP server process"""
        env = os.environ.copy()
        if 'IBMCLOUD_API_KEY' not in env:
            raise ValueError("IBMCLOUD_API_KEY environment variable not set")
        
        self.process = await asyncio.create_subprocess_exec(
            'python', 'vpc_mcp_server.py',
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=env
        )
        
        # Initialize MCP protocol
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {}
                },
                "clientInfo": {
                    "name": "test-client",
                    "version": "1.0.0"
                }
            }
        }
        
        await self.send_request(init_request)
        response = await self.read_response()
        print(f"Initialize response: {response}")
        
        # Send initialized notification
        initialized_notification = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized"
        }
        await self.send_request(initialized_notification)
    
    async def send_request(self, request: Dict[str, Any]):
        """Send a request to the MCP server"""
        message = json.dumps(request) + "\n"
        self.process.stdin.write(message.encode())
        await self.process.stdin.drain()
    
    async def read_response(self):
        """Read a response from the MCP server"""
        line = await self.process.stdout.readline()
        if line:
            return json.loads(line.decode().strip())
        return None
    
    async def list_tools(self):
        """List available tools"""
        request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list"
        }
        
        await self.send_request(request)
        response = await self.read_response()
        return response
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]):
        """Call a specific tool"""
        request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        }
        
        await self.send_request(request)
        response = await self.read_response()
        return response
    
    async def close(self):
        """Close the MCP server"""
        if self.process:
            self.process.terminate()
            await self.process.wait()

async def test_storage_tools():
    """Test storage tools via MCP protocol"""
    client = SimpleMCPClient()
    
    try:
        print("Starting MCP server...")
        await client.start_server()
        
        print("\\nListing available tools...")
        tools_response = await client.list_tools()
        if tools_response and 'result' in tools_response:
            tools = tools_response['result']['tools']
            new_tools = [t for t in tools if 'routing' in t['name'] or 'snapshot' in t['name']]
            print(f"Found {len(new_tools)} new tools:")
            for tool in new_tools:
                print(f"  - {tool['name']}: {tool['description']}")
        
        # First get a VPC ID for routing table tests
        print("\\n" + "="*50)
        print("Getting VPC ID for routing table tests...")
        vpc_response = await client.call_tool("list_vpcs", {
            "region": "us-south",
            "limit": 1
        })
        
        vpc_id = None
        if vpc_response and 'result' in vpc_response:
            content = vpc_response['result']['content'][0]['text']
            vpc_data = json.loads(content)
            if vpc_data.get('count', 0) > 0:
                vpc_id = vpc_data['vpcs'][0]['id']
                print(f"Using VPC ID: {vpc_id}")
        
        if vpc_id:
            # Test list_routing_tables
            print("\\n" + "="*50)
            print("Testing list_routing_tables tool...")
            routing_response = await client.call_tool("list_routing_tables", {
                "region": "us-south",
                "vpc_id": vpc_id,
                "limit": 5
            })
            
            if routing_response and 'result' in routing_response:
                print("✅ list_routing_tables succeeded")
                content = routing_response['result']['content'][0]['text']
                data = json.loads(content)
                print(f"Found {data.get('count', 0)} routing tables")
                if 'error' in data:
                    print(f"❌ Error: {data['error']}")
            else:
                print("❌ list_routing_tables failed")
                print(f"Response: {routing_response}")
        else:
            print("❌ No VPC ID available for routing table tests")
        
        # Test list_snapshots
        print("\\n" + "="*50)
        print("Testing list_snapshots tool...")
        snapshots_response = await client.call_tool("list_snapshots", {
            "region": "us-south",
            "limit": 5
        })
        
        if snapshots_response and 'result' in snapshots_response:
            print("✅ list_snapshots succeeded")
            content = snapshots_response['result']['content'][0]['text']
            data = json.loads(content)
            print(f"Found {data.get('count', 0)} snapshots")
            if 'error' in data:
                print(f"❌ Error: {data['error']}")
        else:
            print("❌ list_snapshots failed")
            print(f"Response: {snapshots_response}")
        
        # Test analyze_snapshot_usage
        print("\\n" + "="*50)
        print("Testing analyze_snapshot_usage tool...")
        usage_response = await client.call_tool("analyze_snapshot_usage", {
            "region": "us-south"
        })
        
        if usage_response and 'result' in usage_response:
            print("✅ analyze_snapshot_usage succeeded")
            content = usage_response['result']['content'][0]['text']
            data = json.loads(content)
            if 'error' in data:
                print(f"❌ Error: {data['error']}")
            else:
                print(f"Usage analysis: {data.get('summary', {}).get('total_snapshots', 0)} snapshots")
        else:
            print("❌ analyze_snapshot_usage failed")
            print(f"Response: {usage_response}")
    
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(test_storage_tools())