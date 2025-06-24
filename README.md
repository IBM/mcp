# IBM MCP Servers

A collection of Model Context Protocol (MCP) servers by IBM, to connect your IBM products to any AI Agent or AI application.

## What is MCP?

MCP is an open-source protocol designed to enable AI models to securely interact with local and remote resources through standardized server implementations. This collection of IBM MCP services focuses on both production-ready and experimental MCP servers that enhance AI capabilities by providing file access, database connections, API integrations, and additional contextual services.

## Available servers

### Terraform MCP Server

The [Terraform MCP Server](https://github.com/hashicorp/terraform-mcp-server) provides seamless integration with Terraform ecosystem, enabling advanced automation and interaction capabilities for Infrastructure as Code (IaC) development. The use cases include

- Automating Terraform provider, policy and module discovery
- Extracting detailed information about provider resources, data sources, user guides and functions
- Exploring and utilizing Terraform modules

### IBM API Connect for GraphQL

Any GraphQL endpoint server by API Connect for GraphQL SaaS also supports an MCP stateless HTTP server supporting `tools/list` and `tools/call`.

Tools can be defined within a GraphQL schema using [`@tool` directive](https://www.ibm.com/docs/en/api-connect-graphql/saas?topic=directives-directive-tool).

A *GraphQL tool* is a subset of the schema that the LLM generates a valid GraphQL request against.

 - [`tools/list`](https://www.ibm.com/docs/en/api-connect-graphql/saas?topic=directives-directive-tool#accessing-tool-descriptions__title__1)
 - [`tools/call`](https://www.ibm.com/docs/en/api-connect-graphql/saas?topic=directives-directive-tool#making-tool-calls__title__1)

### IBM W3 OAuth

- [Link](https://github.ibm.com/Luke-Harrison1/mcp-w3-oauth)

### ContextForge MCP Gateway

- [ContextForge MCP Gateway](https://github.com/IBM/mcp-context-forge) is an MCP server, feature-rich gateway, and proxy that federates MCP and REST services-delivering unified discovery, authentication, rate-limiting, observability, multi-transport protocols, and an optional HTMX-powered admin UI through a single endpoint; It lets you create **Virtual MCP Servers** combining tools and resources across multiple servers, and it can be installed via PyPI (`pip install mcp-contextforge-gateway`) or deployed as a cli, API or UI as a container - and scales horizontally across Kubernetes clusters with Redis-backed federation and caching.

## 💬 Community

Participate in the [Discord community](https://discord.com/invite/NzCQQWm7Xs).

## 🤝 Contributing

Everyone is invited to contribute to this repository, see CONTRIBUTING.md for information.

## ⭐ Support

If you find these IBM MCP servers useful please consider starring the repository and contributing new servers, examples or improvements!
