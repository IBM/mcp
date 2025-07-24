FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY vpc_mcp_server.py .
COPY utils.py .
COPY storage.py .

# Create non-root user
RUN useradd -m -u 1000 mcpuser && chown -R mcpuser:mcpuser /app
USER mcpuser

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV MCP_SERVER_NAME="ibm-vpc-mcp"

# The MCP server uses stdio, so we don't expose ports
# Instead, it will communicate via stdin/stdout

ENTRYPOINT ["python", "vpc_mcp_server.py"]
