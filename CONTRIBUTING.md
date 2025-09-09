# Contributing

Thank you for your interest in contributing to the repository! This document provides guidelines and instructions for contributing.

## Getting Started

1. Fork the repository

2. Clone your fork:

   ```bash
   git clone https://github.com/your-username/mcp.git
   ```
3. Add the upstream remote:

   ```bash
   git remote add upstream https://github.com/ibm/mcp.git
   ```
4. Create a branch:

   ```bash
   git checkout -b my-feature
   ```

## Add a new MCP server

1. Find the right category for your MCP server
2. Create a new row in any of the tables:

   ```md
   | [IBM Storage Insights MCP Server](https://github.com/IBM/ibm-storageinsights-mcpserver) | Leverage key IBM Storage Insights monitoring capabilities via an MCP interface. | *see link for instructions* |
   ```

   If your MCP server can be run using `uvx`, `npx` or `docker` you can use [this tool](https://vscodemcp.com/) to generate a button for one-click installation in VSCode (or other MCP Clients).

3. Add the MCP Client configuration instructions to [`mcp.json`](./mcp.json)

## Development Guidelines

### Code Style
- Follow the existing code style in the repository
- Include appropriate type definitions
- Add comments for complex logic

### Documentation
- Include a detailed README.md in your server directory
- Document all configuration options
- Provide setup instructions
- Include usage examples

### Security
- Follow security best practices
- Implement proper input validation
- Handle errors appropriately
- Document security considerations

## Submitting Changes

1. Commit your changes:
   ```bash
   git add .
   git commit -m "Description of changes"
   ```
2. Push to your fork:
   ```bash
   git push origin my-feature
   ```
3. Create a Pull Request through GitHub

### Pull Request Guidelines

- Thoroughly test your changes
- Fill out the pull request template completely
- Link any related issues
- Provide clear description of changes
- Include any necessary documentation updates
- Add screenshots for UI changes
- List any breaking changes

## 💬 Questions

Participate in the [Discord community](https://discord.com/invite/NzCQQWm7Xs).

Thank you for contributing to IBM MCP Servers!