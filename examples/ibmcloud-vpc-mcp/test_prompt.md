# VPC MCP Server Test Prompt

Use this prompt with Claude Desktop or Claude Code to test multiple VPC MCP tools in a comprehensive scenario.

## Test Prompt

```
I need to perform a comprehensive security audit of my IBM Cloud VPC infrastructure across all regions. Please help me with the following analysis:

1. **Infrastructure Discovery**:
   - List all regions where I have VPC resources
   - For each region, show me all VPCs and their basic information
   - For the first VPC you find, list all subnets and instances

2. **Security Analysis**:
   - Check for any instances that are exposed to SSH (port 22) from the internet (0.0.0.0/0)
   - Check for any instances that are exposed to RDP (port 3389) from the internet
   - Show me the security groups and their rules for any exposed instances

3. **Network Infrastructure Review**:
   - List all public gateways across regions
   - Show floating IPs and what they're attached to
   - If you find any routing tables, show me their details

4. **Storage and Backup Assessment**:
   - List block storage volumes and show their usage patterns
   - Check backup policies and their health status
   - Show any snapshots and analyze their storage usage

5. **VPN Configuration Review** (if applicable):
   - List any VPN gateways and their configuration
   - Show VPN servers and their client configurations
   - List connected VPN clients if any exist

6. **Summary Report**:
   - Provide a security risk summary highlighting any concerning findings
   - Recommend specific actions to improve security posture
   - Identify any unused or underutilized resources

Please be thorough and show me the actual data for each step, not just confirmations that you've checked. If you encounter any errors or missing permissions, please let me know what additional access might be needed.
```

## Expected Tool Usage

This prompt should exercise these MCP tools:

### Core Infrastructure
- `list_regions`
- `list_vpcs` 
- `list_subnets`
- `list_instances`

### Security Analysis
- `check_ssh_exposure`
- `check_rdp_exposure`
- `list_security_groups`
- `get_security_group_rules`

### Network Resources
- `list_public_gateways`
- `list_floating_ips`
- `list_routing_tables`
- `get_routing_table` (if routing tables exist)

### Storage and Backups
- `list_volumes`
- `analyze_volume_usage`
- `list_backup_policies`
- `check_backup_policy_health`
- `list_snapshots`
- `analyze_snapshot_usage`

### VPN (if applicable)
- `list_vpn_gateways`
- `get_vpn_gateway`
- `list_vpn_servers`
- `get_vpn_server`
- `list_vpn_server_clients`

## Alternative Shorter Test

For a quicker test, use this condensed version:

```
Please help me get an overview of my IBM Cloud VPC security posture:

1. List all my VPCs across regions
2. Check for SSH exposure (port 22) from internet across all regions  
3. Show me any security groups with concerning rules
4. List my backup policies and their health status
5. Show storage volume usage patterns

Provide specific findings and security recommendations.
```

## Usage Notes

- Ensure your `IBMCLOUD_API_KEY` environment variable is set before testing
- The tools will work across multiple regions automatically
- Some tools may return empty results if you don't have those resource types
- Error messages about missing resources or permissions are normal and expected
- The analysis should take 30-60 seconds depending on your infrastructure size