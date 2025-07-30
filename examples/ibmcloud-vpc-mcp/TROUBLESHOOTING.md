# Troubleshooting Guide

## Common Issues

### Authentication Errors

**Problem**: API authentication failures or permission denied errors

**Solutions**:
```bash
# Verify API key is set
echo $IBMCLOUD_API_KEY

# Test API key validity
ibmcloud iam api-key-get your-key-name

# Check API key permissions
ibmcloud iam user-policy-list your-email@domain.com
```

**Required Permissions**:
- VPC Infrastructure Services: Reader or Administrator
- Resource Groups: Viewer (minimum)
- IAM Identity Services: Viewer (for service-to-service auth)

### Docker Issues

**Problem**: Container fails to start or crashes

**Solutions**:
```bash
# Clean rebuild
mise run docker:clean
mise run docker:build

# Manual cleanup
docker system prune -f
docker build --no-cache -t ibmcloud-vpc-mcp:latest .

# Check container logs
docker logs vpc-mcp-server

# Run in debug mode
docker run -it --rm -e IBMCLOUD_API_KEY="${IBMCLOUD_API_KEY}" \
  -e LOG_LEVEL=DEBUG ibmcloud-vpc-mcp:latest
```

### Permission Errors

**Problem**: Access denied to specific VPC resources

**Solutions**:
- Ensure API key has VPC Reader/Administrator permissions
- Check IBM Cloud IAM policies for resource group access
- Verify region-specific permissions if using cross-region operations

### Tool-Specific Issues

#### Routing Table Tools

**Problem**: `list_routing_tables` fails with "function not available"

**Solution**: Ensure you're providing the required `vpc_id` parameter:
```bash
# Correct usage
list_routing_tables --region us-south --vpc_id vpc-12345

# This will fail (missing vpc_id)
list_routing_tables --region us-south
```

#### Storage Tools

**Problem**: `list_volumes` or `list_shares` return "status" errors

**Solution**: This was fixed in recent versions. Update to the latest container image:
```bash
# Build latest version
mise run build-and-update

# Or manually update
docker pull ibmcloud-vpc-mcp:latest
```

#### Backup Policy Tools

**Problem**: Empty results or "resource not found" errors

**Solution**: 
- Backup policies are region-specific
- Some regions may not have backup policies enabled
- Check if backup policies exist in your account:
```bash
# List policies in different regions
list_backup_policies --region us-south
list_backup_policies --region us-east
```

### Network Connectivity Issues

**Problem**: Timeouts or connection errors to IBM Cloud APIs

**Solutions**:
- Check internet connectivity
- Verify corporate firewall/proxy settings
- Try different regions (some may have temporary issues)
- Increase timeout values in environment variables

### Container Image Issues

**Problem**: Using old container image with missing features

**Solutions**:
```bash
# Check current image timestamp
docker images | grep ibmcloud-vpc-mcp

# Build new image with timestamp
mise run build-container

# Update Claude Desktop config
mise run build-and-update
```

### Performance Issues

**Problem**: Slow response times or timeouts

**Solutions**:
- Use pagination with `limit` parameter for large result sets
- Filter results using available filter parameters
- Consider regional proximity (use regions closer to your location)

### MCP Protocol Issues

**Problem**: Tools not appearing in Claude Desktop

**Solutions**:
1. Restart Claude Desktop application
2. Check container is running: `docker ps`
3. Verify MCP configuration in Claude Desktop settings
4. Check container logs: `docker logs vpc-mcp-server`

### Data Consistency Issues

**Problem**: Stale or inconsistent data

**Solutions**:
- IBM Cloud API data is eventually consistent
- Some resources may take time to appear after creation
- Try refreshing the query after a few seconds

## Environment Variables

| Variable | Purpose | Default | Notes |
|----------|---------|---------|-------|
| `IBMCLOUD_API_KEY` | IBM Cloud authentication | Required | Must have VPC permissions |
| `LOG_LEVEL` | Logging verbosity | INFO | Use DEBUG for troubleshooting |
| `PYTHONUNBUFFERED` | Python output buffering | False | Set to 1 for container logs |

## Debugging Steps

### 1. Basic Connectivity Test
```bash
# Test basic tool
list_regions

# Should return list of IBM Cloud regions
```

### 2. Authentication Test
```bash
# Test VPC access
list_vpcs --region us-south

# Should return VPCs in your account
```

### 3. New Feature Test
```bash
# Test new routing table functionality
list_routing_tables --vpc_id vpc-12345 --region us-south

# Test new snapshot functionality
list_snapshots --region us-south
```

### 4. Error Analysis
```bash
# Run with debug logging
docker run -it --rm -e LOG_LEVEL=DEBUG \
  -e IBMCLOUD_API_KEY="${IBMCLOUD_API_KEY}" \
  ibmcloud-vpc-mcp:latest
```

## Getting Help

### Resources
- **IBM Cloud VPC Documentation**: [https://cloud.ibm.com/docs/vpc](https://cloud.ibm.com/docs/vpc)
- **MCP Protocol**: [https://modelcontextprotocol.io](https://modelcontextprotocol.io)
- **IBM Cloud CLI**: [https://cloud.ibm.com/docs/cli](https://cloud.ibm.com/docs/cli)

### Support Channels
- **Issues**: Create an issue in this repository
- **IBM Cloud Support**: For API-related issues
- **Community**: Stack Overflow with tags `ibm-cloud` and `vpc`

### Diagnostic Information to Include

When reporting issues, include:
1. Container image version/timestamp
2. IBM Cloud region being used
3. Tool name and parameters
4. Full error message
5. Docker logs (`docker logs vpc-mcp-server`)
6. MCP client being used (Claude Desktop, etc.)

## Known Limitations

- Some tools require specific permissions that may not be available to all users
- Cross-region operations may have higher latency
- Large result sets may need pagination
- Some resources are region-specific and won't appear in global queries
- Backup policies are not available in all regions
- File shares are not available in all regions