# IBM MCP

A collection of Model Context Protocol (MCP) servers, MCP Clients and Developer Tools by IBM. Connect your IBM products to any AI Agent or AI application.

## What is MCP?

MCP is an open-source protocol designed to enable AI models to securely interact with local and remote resources through standardized server implementations. This collection of IBM MCP services focuses on both production-ready and experimental MCP servers that enhance AI capabilities by providing file access, database connections, API integrations, and additional contextual services.

## Available MCP Servers

#### ⚙️ Automation

| Server name | Description | Usage |
|---|---|---|
| [IBM MQ Server](https://github.com/ibm-messaging/mq-mcp-server) | Provides access to IBM MQ queue managers health checks, and to run any MQSC command against a specific queue manager. | *see link for instructions* |
| [K* Planner](https://github.com/IBM/kstar/tree/main/mcp) | K* MCP Server provides a containerized deployment of Top-K and Top-Q planners from the KStar repository as Model Checking Problem (MCP) tools. | *see link for instructions* |

#### 💼 Business Automation

| Server name | Description | Usage |
|---|---|---|
| [IBM Business Automation Workflow MCP Server](https://github.com/ibmbpm/ibm-baw-mcp-server) | The IBM® Business Automation Workflow MCP Server is a local Model Control Protocol (MCP) server that supports integration of AI agents with IBM® Business Automation Workflow through the Model Context Protocol. | [![Install in VS Code](https://img.shields.io/badge/VS_Code-Install-0098FF?style=flat-square&logo=visualstudiocode&logoColor=ffffff)](https://insiders.vscode.dev/redirect?url=vscode:mcp/install?%7B%22name%22%3A%22ibm-baw-mcp-server%22%2C%22type%22%3A%22stdio%22%2C%22command%22%3A%22uvx%22%2C%22args%22%3A%5B%22--from%22%2C%22git%2Bhttps%3A%2F%2Fgithub.com%2Fibmbpm%2Fibm-baw-mcp-server%22%2C%22ibm-baw-mcp-server%22%5D%2C%22env%22%3A%7B%22ENDPOINT%22%3A%22YOUR_WORKFLOW_ENDPOINT%22%2C%22USERID%22%3A%22YOUR_WORKFLOW_USERNAME%22%2C%22PASSWORD%22%3A%22YOUR_WORKFLOW_PASWORD%22%7D%7D) |
| [IBM Core Content Services MCP Server](https://github.com/ibm-ecm/ibm-content-services-mcp-server) | Provides tools to interact with IBM FileNet Content Manager (FNCM) repositories, enabling document management, folder operations, search capabilities and more. | [![Install in VS Code](https://img.shields.io/badge/VS_Code-Install-0098FF?style=plastic&logo=visualstudiocode&logoColor=ffffff)](vscode:mcp/install?%7B%22name%22%3A%22core-cs-mcp-server%22%2C%22type%22%3A%22stdio%22%2C%22command%22%3A%22uvx%22%2C%22args%22%3A%5B%22--from%22%2C%22git%2Bhttps%3A%2F%2Fgithub.com%2Fibm-ecm%2Fibm-content-services-mcp-server%22%2C%22core-cs-mcp-server%22%5D%2C%22env%22%3A%7B%22SERVER_URL%22%3A%22https%3A%2F%2Fyour-graphql-server%2Fcontent-services-graphql%2Fgraphql%22%2C%22OBJECT_STORE%22%3A%22your_object_store%22%2C%22USERNAME%22%3A%22username%22%2C%22PASSWORD%22%3A%22password%22%7D%7D) |
| [IBM Decision Intelligence MCP Server](https://github.com/DecisionsDev/decision-intelligence-mcp-server) | This MCP server provides tools to invoke decision services deployed by [IBM Decision Intelligence](https://www.ibm.com/products/decision-intelligence) or [IBM Automation Decision Services](https://www.ibm.com/products/automation-decision-services) | [![Install in VS Code](https://img.shields.io/badge/VS_Code-Install-0098FF?style=plastic&logo=visualstudiocode&logoColor=ffffff)](https://insiders.vscode.dev/redirect?url=vscode:mcp/install?%7B%22name%22%3A%22ibm-decision-intelligence-mcp-server%22%2C%22type%22%3A%22stdio%22%2C%22command%22%3A%22npx%22%2C%22args%22%3A%5B%22-y%22%2C%22di-mcp-server%22%5D%2C%22env%22%3A%7B%22APIKEY%22%3A%22%3CAPIKEY%3E%22%2C%22URL%22%3A%22https%3A%2F%2F%3CTENANT_NAME%3E.decision-prod-us-south.decision.saas.ibm.com%2Fads%2Fruntime%2Fapi%2Fv1%22%7D%7D) |
| [IBM ODM MCP Server](https://github.com/DecisionsDev/ibm-odm-decision-mcp-server) | An MCP Server enabling integration with IBM Decision Server Runtime to retrieve and invoke decision services. | [![Install in VS Code](https://img.shields.io/badge/VS_Code-Install-0098FF?style=plastic&logo=visualstudiocode&logoColor=ffffff)](https://insiders.vscode.dev/redirect?url=vscode:mcp/install?%7B%22name%22%3A%22ibm-odm-mcp-server%22%2C%22type%22%3A%22stdio%22%2C%22command%22%3A%22uvx%22%2C%22args%22%3A%5B%22--from%22%2C%22git%2Bhttps%3A%2F%2Fgithub.com%2FDecisionsDev%2Fdecision-mcp-server%22%2C%22decision-mcp-server%22%5D%7D) |
| [IBM Process Mining](https://www.ibm.com/docs/en/process-mining/2.1.0?topic=menu-generating-mcp-rest-api-tokens) | Provides access to processes and Data Analyst features. | *see link for instructions* |

#### 🧠 Data & Analytics

| Server name | Description | Usage |
|---|---|---|
| [IBM OpenPages MCP Server](https://github.com/IBM/ibm-openpages-local-mcp-server) | An experimental local Model Context Protocol (MCP) server that enables AI agents to securely interact with IBM OpenPages GRC platform through a standardized interface. | *see link for instructions* |
| [DataStax Astra DB](https://github.com/datastax/astra-db-mcp) | An MCP server for Astra DB workloads. | [![Install in VS Code](https://img.shields.io/badge/VS_Code-Install-0098FF?style=plastic&logo=visualstudiocode&logoColor=ffffff)](https://insiders.vscode.dev/redirect?url=vscode:mcp/install?%7B%22name%22%3A%22astra-db-mcp%22%2C%22type%22%3A%22stdio%22%2C%22command%22%3A%22npx%22%2C%22args%22%3A%5B%22-y%22%2C%22%40datastax%2Fastra-db-mcp-server%22%5D%2C%22env%22%3A%7B%22ASTRA_DB_APPLICATION_TOKEN%22%3A%22your_astra_db_token%22%2C%22ASTRA_DB_API_ENDPOINT%22%3A%22your_astra_db_endpoint%22%7D%7D) |
| [Docling MCP Server](https://github.com/docling-project/docling-mcp) | Turn unstructured data into structured data using Docling, with tools for document conversion, processing and generation. | [![Install in VS Code](https://img.shields.io/badge/VS_Code-Install-0098FF?style=plastic&logo=visualstudiocode&logoColor=ffffff)](https://insiders.vscode.dev/redirect?url=vscode:mcp/install?%7B%22name%22%3A%22docling-mcp-server%22%2C%22type%22%3A%22stdio%22%2C%22command%22%3A%22uvx%22%2C%22args%22%3A%5B%22--from%3Ddocling-mcp%22%2C%22docling-mcp-server%22%5D%7D) |
| [IBM watsonx.data MCP Server](https://github.com/IBM/ibm-watsonxdata-mcp-server) | Enables AI assistants to interact with IBM watsonx.data lakehouses using natural language. Provides tools for querying lakehouse data with SQL, exploring data catalogs and metadata, inspecting table schemas, and monitoring engines. | *see link for instructions* |
| [IBM watsonx.data Document Library Retrieval MCP Server](https://github.com/IBM/ibm-watsonxdata-dl-retrieval-mcp-server) | Query document libraries from watsonx.data using conversational language and receive human-readable responses using local MCP server. | *see link for instructions* |
| [IBM watsonx.data Document Library Retrieval MCP Server (Remote)](https://www.ibm.com/docs/en/watsonxdata/saas?topic=service-watsonxdata-remote-model-context-protocol-mcp-server) | Query document libraries from watsonx.data using conversational language and receive human-readable responses using remote MCP server hosted in IBM infrastructure. | *see link for instructions* |
| [IBM watsonx.data intelligence MCP Server](https://github.com/IBM/data-intelligence-mcp-server) | MCP Server to interact with watsonx.data intelligence on-prem or on SaaS environment. | *see link for instructions* |
| [IBM MDM MCP Server](https://github.com/IBM/mdm-mcp-server) | This MCP server enables AI assistants like Claude to interact with IBM MDM services(formarly known as IBM Match 360), allowing users to search records, retrieve data models, and manage master data through natural language conversations. The server acts as a bridge between AI assistants and IBM MDM, exposing enterprise data management capabilities through the Model Context Protocol. | *see link for instructions* |

#### 👩🏻‍💻 Developer Productivity

| Server name | Description | Usage |
|---|---|---|
| [Carbon MCP](https://github.com/carbon-design-system/carbon-mcp) | Provides tools to explore Carbon Design System components, tokens, and icons, answer documentation questions, and generate consistent UI code. | *Cloud server access [instructions.](https://pages.github.ibm.com/carbon/ibm-products/developing/carbon-mcp/overview/)* |
| [IBM Developer for z/OS on VS Code MCP Server](https://www.ibm.com/docs/en/developer-for-zos/17.0.x?topic=overview-agent-mode) | MCP server that runs as part of IBM's z/OS enterprise application development editor for COBOL, PL/I, REXX, JCL, and Assembler. Enable your AI Chat in VS Code with access to your local workspace as well as your remote z/OS development environment. Interact with z/OS retrieving or updating data sets, submitting jobs and fetching job info and spool files, retrieving files from your z/OS UNIX home directory and open it in the editor, building you application and analyzing problems with guidance for how to fix them, and much more. | [![Install in VS Code](https://img.shields.io/badge/VS_Code-Install-0098FF?style=plastic&logo=visualstudiocode&logoColor=ffffff)](https://insiders.vscode.dev/redirect?url=vscode:extension/IBM.zopeneditor) |

#### 🏗️ Infrastructure & Deployment

| Server name | Description | Usage |
|---|---|---|
| [IBM Cloud MCP Server](https://ibm-cloud.github.io/mcp/) | Enhance your LLM with tools from IBM Cloud. | *see link for instructions* |
| [Terraform IBM Modules (TIM) MCP Server](https://github.com/terraform-ibm-modules/tim-mcp) | The TIM-MCP server provides structured access to the Terraform IBM Modules(TIM) ecosystem, enabling intelligent provisioning of IBM Cloud infrastructure resources as code. | *see link for instructions* |
| [IBM Cloud Code Engine MCP Server](https://github.com/greyhoundforty/code-engine-mcp) | This MCP server provides tools to list and inspect Code Engine projects, applications, revisions, domain mappings, and secrets. | *see link for instructions* |
| [IBM Cloud VPC MCP Server](https://github.com/greyhoundforty/ibmcloud-vpc-mcp) | Provides access to IBM Cloud VPC resources and security analysis capabilities, enabling AI agents to interact with cloud infrastructure, backups, and security policies. | *see link for instructions* |
| [IBM i MCP Server](https://github.com/IBM/ibmi-mcp-server) | MCP server for IBM i systems that enables AI agents to interact securely with IBM i through SQL-based tools. It provides a flexible framework for building custom agentic tools for tasks such as performance monitoring, security auditing, storage analysis, database administration and more. | [![Install in VS Code](https://img.shields.io/badge/VS_Code-Install-0098FF?style=flat-square&logo=visualstudiocode&logoColor=ffffff)](https://insiders.vscode.dev/redirect?url=vscode:mcp/install?%7B%22name%22%3A%22ibmi-mcp-server%22%2C%22type%22%3A%22stdio%22%2C%22command%22%3A%22npx%22%2C%22args%22%3A%5B%22-y%22%2C%22%40ibm%2Fibmi-mcp-server%40latest%22%5D%7D) |
| [IBM Power Virtual Server MCP Server](https://github.com/IBM/powervs-mcp-server) | Brings to AI-Agents seamless observability and diagnosis of their virtual machines registered with IBM Power Virtual Server  | *see link for instructions* |
| [Terraform MCP Server](https://github.com/hashicorp/terraform-mcp-server) | Provides seamless integration with Terraform ecosystem, enabling advanced automation and interaction capabilities for Infrastructure as Code (IaC) development. | [![Install in VS Code](https://img.shields.io/badge/VS_Code-Install-0098FF?style=plastic&logo=visualstudiocode&logoColor=ffffff)](https://insiders.vscode.dev/redirect?url=vscode:mcp/install?%7B%22name%22%3A%22terraform-mcp-server%22%2C%22type%22%3A%22stdio%22%2C%22command%22%3A%22docker%22%2C%22args%22%3A%5B%22run%22%2C%22-i%22%2C%22--rm%22%2C%22hashicorp%2Fterraform-mcp-server%22%5D%7D) |

#### 📊 Observability & Monitoring

| Server name | Description | Usage |
|---|---|---|
| [IBM Instana MCP Server](https://github.com/instana/mcp-instana) | This MCP server provides tools to list and inspect IBM Instana resources, including applications, infrastructure resources etc. | *see link for instructions* |
| [IBM Storage Insights MCP Server](https://github.com/IBM/ibm-storageinsights-mcpserver) | Leverage key IBM Storage Insights monitoring capabilities via an MCP interface. | *see link for instructions* |

#### 📡 Networking

| Server name | Description | Usage |
|---|---|---|
| [Consul MCP Server](https://hub.docker.com/r/hashicorp/consul-mcp-server) |This MCP server acts as a bridge, giving AI models the ability to execute Consul operations via APIs. | [![Install in VS Code](https://img.shields.io/badge/VS_Code-Install-0098FF?style=plastic&logo=visualstudiocode&logoColor=ffffff)](vscode:mcp/install?%7B%22name%22%3A%22consul%22%2C%22type%22%3A%22stdio%22%2C%22command%22%3A%22docker%22%2C%22args%22%3A%5B%22run%22%2C%22-i%22%2C%22--rm%22%2C%22-e%22%2C%22CONSUL_HTTP_ADDR%3Dhttp%3A%2F%2Fhost.docker.internal%3A8500%22%2C%22-e%22%2C%22CONSUL_HTTP_TOKEN%3D%24%7BCONSUL_DC1_TOKEN%7D%22%2C%22hashicorp%2Fconsul-mcp-server%22%5D%7D) |

#### 🔬 Research

| Server name                                                                                  | Description                                                                                                                                                                                                                                                                                                                                                                                                                                | Usage |
|----------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---|
| [MAMMAL-MCP](https://github.com/BiomedSciAI/biomed-multi-alignment/tree/main/mammal_mcp) | MAMMAL (ibm/biomed.omics.bl.sm.ma-ted-458m) is a 'biomedical foundation model' (BMFM) that has been trained by IBM and the details can be found here -> https://github.com/BiomedSciAI/biomed-multi-alignment. This MCP server can be used to enable AI Agent systems to use some of the MAMMAL model tasks, such as: 'Protein-Protein interaction prediction', 'Protein solubility prediction' and 'Drug-Protein interaction prediction'. | *see link for instructions* |


#### 🔐 Security

| Server name | Description | Usage |
|---|---|---|
| [QRadar SIEM MCP Server](https://github.com/IBM/qradar-mcp-server) | Access 728+ IBM QRadar REST API endpoints through 4 intelligent MCP tools — search offenses, run AQL queries, manage reference sets, and investigate security incidents. | *[see link for instructions](https://github.com/IBM/qradar-mcp-server)* |
| [Guardium Cryptography Manager MCP Server](https://github.com/IBM/gcm-mcp-server) | Access 292 IBM Guardium Cryptography Manager API endpoints through 3 intelligent MCP tools — manage encryption keys, run discovery scans, enforce crypto policies, and monitor compliance. | *[see link for instructions](https://github.com/IBM/gcm-mcp-server)* |
| [IBM Security Verify MCP Server](https://github.com/IBM/verify-mcp-server) | Access 210 IBM Security Verify REST API endpoints through 4 intelligent MCP tools — discover APIs, manage users, configure SSO, and orchestrate identity workflows. | *[see link for instructions](https://github.com/IBM/verify-mcp-server)* |
| [Vault MCP Server](https://developer.hashicorp.com/hcp/docs/vault-radar/mcp-server/overview) |This MCP server acts as a bridge, giving AI models the ability to execute kv, pki, and mount operations in Vault via APIs. | [![Install in VS Code](https://img.shields.io/badge/VS_Code-Install-0098FF?style=plastic&logo=visualstudiocode&logoColor=ffffff)](vscode:mcp/install?%7B%22name%22%3A%22vault-mcp-server%22%2C%22type%22%3A%22stdio%22%2C%22command%22%3A%22docker%22%2C%22args%22%3A%5B%22run%22%2C%22--rm%22%2C%22-i%22%2C%22-e%22%2C%22VAULT_ADDR%3D%3CVault%20Address%3E%22%2C%22-e%22%2C%22VAULT_TOKEN%3D%3CVault%20Token%3E%22%2C%22-e%22%2C%22VAULT_NAMESPACE%3D%3CVault%20Namespace%3E%22%2C%22hashicorp%2Fvault-mcp-server%22%5D%7D) |
| [Vault Radar MCP Server](https://developer.hashicorp.com/hcp/docs/vault-radar/mcp-server/overview) |Provides access to HCP Vault Radar data sources, secret risks, and events, enabling LLMs to query and analyze security information using natural language. | [![Install in VS Code](https://img.shields.io/badge/VS_Code-Install-0098FF?style=plastic&logo=visualstudiocode&logoColor=ffffff)](https://insiders.vscode.dev/redirect?url=vscode:mcp/install?%7B%22name%22%3A%22vault-radar%22%2C%22type%22%3A%22stdio%22%2C%22command%22%3A%22docker%22%2C%22args%22%3A%5B%22run%22%2C%22--rm%22%2C%22-i%22%2C%22-e%22%2C%22HCP_PROJECT_ID%3D%3CHCP%20Project%20ID%3E%22%2C%22-e%22%2C%22HCP_CLIENT_ID%3D%3CHCP%20Service%20Principal%20Client%20ID%3E%22%2C%22-e%22%2C%22HCP_CLIENT_SECRET%3D%3CHCP%20Service%20Principal%20Client%20Secret%3E%22%2C%22hashicorp%2Fvault-radar-mcp-server%3A%3Ctag%3E%22%5D%7D) |


#### 🛠️ Developer Tools

- [BeeAI Framework](https://framework.beeai.dev/integrations/mcp) - BeeAI Framework is an open-source framework for building production-grade multi-agent systems, supporting both Python and TypeScript. It integrates with the Model Context Protocol (MCP) as a MCP client, and is hosted by the Linux Foundation under open governance.
- [ContextForge MCP Gateway](https://github.com/IBM/mcp-context-forge) - MCP server, feature-rich gateway, and proxy that federates MCP and REST services-delivering unified discovery, authentication, rate-limiting, observability, multi-transport protocols, and an optional HTMX-powered admin UI through a single endpoint.
- [IBM API Connect for GraphQL](https://www.ibm.com/docs/en/api-connect-graphql/saas?topic=directives-directive-tool) - Turn any GraphQL schema into a MCP server incl. authentication.
- [Langflow](https://github.com/langflow-ai/langflow) - Langflow is an open-source visual builder that lets developers rapidly prototype and build AI applications, it integrates with the Model Context Protocol (MCP) as both an MCP server and an MCP client.
- [MCP Composer](https://pypi.org/project/mcp-composer/) - FastMCP based library to manages multiple MCP servers & tools with dynamic registration, authentication, and unified interface.. Supports multiple tool types, such as OpenAPI (REST), GraphQL, CLI-based tools, client SDKs, and nested MCP servers.
- [WxMCPServer](https://github.com/IBM/WxMCPServer) - IBM webMethods Hybrid Integration (IWHI) based MCP server, that enables existing APIs to be used as MCP tools.
- [z/OS Connect](https://www.ibm.com/docs/en/zos-connect/3.0.0?topic=connect-what-is-mcp) - z/OS Connect based MCP server, that enables existing APIs to be used as MCP tools.

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
