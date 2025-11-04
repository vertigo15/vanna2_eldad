# Docker Setup Guide

## Current Status

✅ Docker is installed (v28.0.4)  
✅ Docker Compose is installed (v2.34.0)  
✅ Docker image built successfully  
⚠️ Docker Desktop needs to be started

## Steps to Run in Docker

### 1. Start Docker Desktop

**Option A: Via Start Menu**
- Press Windows key
- Search for "Docker Desktop"
- Click to open

**Option B: Via Command**
```powershell
Start-Process "C:\Program Files\Docker\Docker\Docker Desktop.exe"
```

Wait for Docker Desktop to fully start (whale icon in system tray should be steady)

### 2. Verify Docker is Running

```powershell
docker ps
```

You should see a list of containers (may be empty).

### 3. Start the Vanna Application

```powershell
docker-compose up -d
```

Expected output:
```
[+] Running 2/2
 ✔ Network vanna2_eldad_vanna-network  Created
 ✔ Container vanna2-app                Started
```

### 4. Check Container Status

```powershell
docker-compose ps
```

You should see:
```
NAME                IMAGE                        STATUS
vanna2-app          vanna2_eldad-vanna-app       Up X seconds
```

### 5. View Logs

```powershell
docker-compose logs -f
```

Look for these messages:
```
INFO:__main__:✓ Azure OpenAI configured: gpt-4o
INFO:__main__:✓ Data source configured: jeen-pg-dev-weu.postgres.database.azure.com/AdventureWorksDW
INFO:__main__:✓ Tools registered
INFO:__main__:✓ Using in-memory conversation storage
INFO:vanna.core.agent.agent:Initialized Agent
INFO:__main__:✓ Vanna 2.0 application started successfully
INFO:     Uvicorn running on http://0.0.0.0:8000
```

Press `Ctrl+C` to exit logs (container keeps running).

### 6. Access the Application

- **Web Interface**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## Useful Docker Commands

### Stop the Container
```powershell
docker-compose down
```

### Restart the Container
```powershell
docker-compose restart
```

### View Real-time Logs
```powershell
docker-compose logs -f vanna-app
```

### Execute Commands Inside Container
```powershell
docker-compose exec vanna-app bash
```

### Rebuild After Code Changes
```powershell
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Check Container Resource Usage
```powershell
docker stats vanna2-app
```

## Troubleshooting

### Port 8000 Already in Use
```powershell
# Find process using port 8000
netstat -ano | findstr :8000

# Stop the process (replace PID with actual process ID)
Stop-Process -Id <PID> -Force

# Try starting again
docker-compose up -d
```

### Docker Desktop Not Starting
1. Check if virtualization is enabled in BIOS
2. Restart your computer
3. Run Docker Desktop as Administrator

### Container Keeps Restarting
```powershell
# Check detailed logs
docker-compose logs --tail=100 vanna-app

# Common issues:
# - Missing environment variables in .env file
# - Database connection issues
# - Azure OpenAI credentials invalid
```

### Image Not Found After Build
```powershell
# List all images
docker images

# Rebuild
docker-compose build --no-cache
```

## Environment Variables

The container reads from your `.env` file automatically via docker-compose.yml.

Make sure these are set:
- `AZURE_OPENAI_API_KEY`
- `AZURE_OPENAI_ENDPOINT`
- `AZURE_OPENAI_API_VERSION`
- `AZURE_OPENAI_DEPLOYMENT_NAME`
- `DATA_SOURCE_HOST`
- `DATA_SOURCE_PORT`
- `DATA_SOURCE_DB`
- `DATA_SOURCE_USER`
- `DATA_SOURCE_PASSWORD`

## Health Check

The container has a built-in health check that runs every 30 seconds:

```powershell
docker inspect vanna2-app --format='{{.State.Health.Status}}'
```

Should return: `healthy`

## Next Steps

Once the container is running successfully:

1. Test the API endpoints
2. Send natural language queries
3. Monitor logs for errors
4. Check database connectivity
5. Verify Azure OpenAI integration

## Production Notes

For production deployment:
- Use orchestration (Kubernetes, Azure Container Apps)
- Add load balancing
- Configure persistent storage volumes
- Set up monitoring and alerting
- Use secrets management (Azure Key Vault)
- Enable HTTPS/TLS
- Configure CORS appropriately
