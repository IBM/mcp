# IBM MCP

A collection of Model Context Protocol (MCP) servers, MCP Clients and Developer Tools by IBM. Connect your IBM products to any AI Agent or AI application.

## What is MCP?

MCP is an open-source protocol designed to enable AI models to securely interact with local and remote resources through standardized server implementations. This collection of IBM MCP services focuses on both production-ready and experimental MCP servers that enhance AI capabilities by providing file access, database connections, API integrations, and additional contextual services.

## Available MCP Servers

#### Automation

- [IBM Decision Intelligence MCP Server](https://github.com/DecisionsDev/decision-intelligence-mcp-server) - This MCP server provides tools to invoke decision services deployed by [IBM Decision Intelligence](https://www.ibm.com/products/decision-intelligence) or [IBM Automation Decision Services](https://www.ibm.com/products/automation-decision-services)
- [IBM MQ Server](https://github.com/ibm-messaging/mq-mcp-server) - Provides access to IBM MQ queue managers health checks, and to run any MQSC command against a specific queue manager.
- [IBM ODM MCP Server](https://github.com/DecisionsDev/decision-mcp-server) - An MCP Server enabling integration with IBM Decision Server Runtime to retrieve and invoke decision services.

#### Data & Analytics

- [DataStax Astra DB](https://github.com/datastax/astra-db-mcp) - An MCP server for Astra DB workloads.
- [Docling MCP Server](https://github.com/docling-project/docling-mcp) - Turn unstructured data into structured data using Docling, with tools for document conversion, processing and generation.
- [IBM watsonx.data Document Retrieval MCP Server](https://github.com/IBM/ibm-watsonxdata-dl-retrieval-mcp-server) - Query document libraries from watsonx.data using conversational language and receive human-readable responses.
  
#### Infrastructure & Deployment

- [IBM Cloud MCP Server](https://ibm-cloud.github.io/mcp/) - Enhance your LLM with tools from IBM Cloud.
- [IBM Cloud Code Engine MCP Server](https://github.com/greyhoundforty/code-engine-mcp) - This MCP server provides tools to list and inspect Code Engine projects, applications, revisions, domain mappings, and secrets. 
- [IBM Cloud Docs MCP Server (community)](https://github.com/sankalpmukim/ibm-cloud-docs-mcp-server) - This MCP server wraps the IBM Cloud Official Documentation, and provides the tools to search and read documentation.
- [IBM Cloud VPC MCP Server](https://github.com/greyhoundforty/ibmcloud-vpc-mcp) - Provides access to IBM Cloud VPC resources and security analysis capabilities, enabling AI agents to interact with cloud infrastructure, backups, and security policies.
- [Terraform MCP Server](https://github.com/hashicorp/terraform-mcp-server) - Provides seamless integration with Terraform ecosystem, enabling advanced automation and interaction capabilities for Infrastructure as Code (IaC) development.

#### Observability & Monitoring

- [IBM Instana MCP Server](https://github.com/instana/mcp-instana) - This MCP server provides tools to list and inspect IBM Instana resources, including applications, infrastructure resources etc.
- [IBM Storage Insights MCP Server](https://github.com/IBM/ibm-storageinsights-mcpserver) - Leverage key IBM Storage Insights monitoring capabilities via an MCP interface.

#### Security

- [Vault Radar MCP Server](https://developer.hashicorp.com/hcp/docs/vault-radar/mcp-server/overview) - Provides access to HCP Vault Radar data sources, secret risks, and events, enabling LLMs to query and analyze security information using natural language.

#### 🛠️ Developer Tools

- [BeeAI Framework](https://framework.beeai.dev/integrations/mcp) - BeeAI Framework is an open-source framework for building production-grade multi-agent systems, supporting both Python and TypeScript. It integrates with the Model Context Protocol (MCP) as a MCP client, and is hosted by the Linux Foundation under open governance.
- [ContextForge MCP Gateway](https://github.com/IBM/mcp-context-forge) - MCP server, feature-rich gateway, and proxy that federates MCP and REST services-delivering unified discovery, authentication, rate-limiting, observability, multi-transport protocols, and an optional HTMX-powered admin UI through a single endpoint.
- [IBM API Connect for GraphQL](https://www.ibm.com/docs/en/api-connect-graphql/saas?topic=directives-directive-tool) - Turn any GraphQL schema into a MCP server incl. authentication.
- [Langflow](https://github.com/langflow-ai/langflow) - Langflow is an open-source visual builder that lets developers rapidly prototype and build AI applications, it integrates with the Model Context Protocol (MCP) as both an MCP server and an MCP client.
- [MCP Composer](https://pypi.org/project/mcp-composer/) - FastMCP based library to manages multiple MCP servers & tools with dynamic registration, authentication, and unified interface.. Supports multiple tool types, such as OpenAPI (REST), GraphQL, CLI-based tools, client SDKs, and nested MCP servers.
- [WxMCPServer](https://github.com/IBM/WxMCPServer) - IBM webMethods Hybrid Integration (IWHI) based MCP server, that enables existing APIs to be used as MCP tools.

## MCP Clients

We recommend using [Langflow](https://github.com/langflow-ai/langflow) or your IDE of choice as MCP client.

## 💬 Community

Participate in the [Discord community](https://discord.com/invite/NzCQQWm7Xs).

## 🤝 Contributing

Everyone is invited to contribute to this repository, see [CONTRIBUTING.md](./CONTRIBUTING.md) for information.

Thanks to all of our amazing contributors!

<a href="https://github.com/ibm/mcp/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=ibm/mcp" />
</a>

## ⭐ Support

If you find these IBM MCP servers useful please consider starring the repository and contributing new servers, examples or improvements!
