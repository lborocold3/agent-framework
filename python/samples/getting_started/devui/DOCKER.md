# Docker Setup Guide for DevUI Agents

Successfully built Docker image: `devui-agents:latest` (424MB)

## Running the Container

### Option 1: Using Docker Compose (Recommended)

```bash
# Copy .env file if you have environment variables
cp .env.example .env
# Edit .env with your Azure AI Foundry credentials

# Start the container
docker-compose up

# Access the DevUI at http://localhost:8080
```

### Option 2: Using Docker CLI

```bash
# Run with environment variables
docker run -it \
  -p 8080:8080 \
  -p 8090:8090 \
  -e AZURE_AI_PROJECT_ENDPOINT="https://your-project.ai.azure.com" \
  -e FOUNDRY_MODEL_DEPLOYMENT_NAME="your-deployment" \
  devui-agents:latest

# Or run in-memory mode instead
docker run -it \
  -p 8090:8090 \
  devui-agents:latest \
  python in_memory_mode.py
```

## Environment Variables

Set these in your `.env` file or pass as `-e` flags:

- `AZURE_AI_PROJECT_ENDPOINT`: Your Azure AI Foundry project endpoint
- `FOUNDRY_MODEL_DEPLOYMENT_NAME`: Your model deployment name

## Authentication

The container uses `DefaultAzureCredential()` from Azure SDK, which supports:
- Azure CLI (`az login`)
- Managed Identity (in Azure)
- Environment variables (`AZURE_CLIENT_ID`, `AZURE_CLIENT_SECRET`, etc.)
- Service Principal

## Exposed Ports

- **8080**: DevUI with directory discovery mode
- **8090**: DevUI with in-memory mode (if running `python in_memory_mode.py`)

## Building the Image

```bash
docker build -t devui-agents:latest .
```

## Multi-stage Build

The Dockerfile uses a multi-stage build to minimize image size:
1. **Builder stage**: Installs all dependencies
2. **Runtime stage**: Copies only the compiled packages, reducing final image to 424MB

## Troubleshooting

### Azure Authentication Issues

If you get authentication errors:
1. Ensure you're logged in: `az login`
2. Set the correct subscription: `az account set --subscription <id>`
3. Or provide Azure credentials via environment variables

### Port Already in Use

If ports 8080/8090 are in use:
```bash
docker run -p 8081:8080 -p 8091:8090 devui-agents:latest
```

### View Logs

```bash
docker logs <container-id>
docker logs -f <container-id>  # Follow logs
```
