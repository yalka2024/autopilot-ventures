# 🌐 Web Server Deployment Guide - AutoPilot Ventures

## **Overview**

The AutoPilot Ventures platform now includes a web server wrapper (`web_server.py`) that enables the platform to run on Google Cloud Run. This provides a REST API interface for the autonomous business creation platform.

## **🔧 Web Server Features**

### **REST API Endpoints**
- **GET /** - Platform information and available endpoints
- **GET /health** - Health check for Cloud Run
- **GET /status** - Platform status and metrics
- **POST /business/create** - Create a new business
- **POST /workflow/run** - Run complete workflow with all agents
- **POST /agent/run** - Run a single agent
- **GET /demo/{language}** - Multilingual demonstration
- **GET /master/status** - Master agent status
- **GET /income/report** - Income projection report
- **POST /autonomous/start** - Start autonomous operation
- **GET /metrics** - Prometheus metrics

### **Cloud Run Compatibility**
- **Port Configuration**: Automatically uses Cloud Run's PORT environment variable
- **Health Checks**: Proper health check endpoint for Cloud Run
- **Graceful Shutdown**: Proper cleanup on container shutdown
- **Error Handling**: Comprehensive error handling and logging

## **🚀 Deployment Steps**

### **1. Verify Web Server**
```bash
# Test the web server locally
python test_web_server.py
```

### **2. Deploy to Google Cloud Run**
```bash
# Use the existing deployment script
.\deploy-simple.ps1
```

### **3. Verify Deployment**
```bash
# Get the service URL
gcloud run services describe autopilot-ventures --region=us-central1 --format="value(status.url)"

# Test the health endpoint
curl https://your-service-url/health
```

## **📋 API Usage Examples**

### **Health Check**
```bash
curl https://your-service-url/health
```

### **Platform Status**
```bash
curl https://your-service-url/status
```

### **Create Business**
```bash
curl -X POST "https://your-service-url/business/create" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "AI-Powered E-commerce",
    "description": "Automated online store",
    "niche": "Technology",
    "language": "en"
  }'
```

### **Run Workflow**
```bash
curl -X POST "https://your-service-url/workflow/run" \
  -H "Content-Type: application/json" \
  -d '{
    "workflow_config": {
      "steps": ["niche_research", "mvp_design", "marketing_strategy"]
    },
    "language": "en"
  }'
```

### **Start Autonomous Operation**
```bash
curl -X POST "https://your-service-url/autonomous/start" \
  -H "Content-Type: application/json" \
  -d '{
    "autonomy_mode": "full"
  }'
```

## **🔍 Troubleshooting**

### **Container Startup Issues**
If the container fails to start:

1. **Check Logs**:
   ```bash
   gcloud logs read --project=autopilot-ventures-core --filter="resource.type=cloud_run_revision"
   ```

2. **Verify Environment Variables**:
   - Ensure all required environment variables are set
   - Check that API keys are valid

3. **Test Locally**:
   ```bash
   python web_server.py
   ```

### **Health Check Failures**
If health checks fail:

1. **Check Application Initialization**:
   - Verify all dependencies are installed
   - Check database connections
   - Ensure API keys are working

2. **Review Logs**:
   ```bash
   gcloud run services logs read autopilot-ventures --region=us-central1
   ```

### **Port Configuration**
The web server automatically:
- Uses Cloud Run's PORT environment variable (default: 8080)
- Listens on 0.0.0.0 for all interfaces
- Provides proper health check endpoint

## **📊 Monitoring**

### **Health Monitoring**
- **Health Endpoint**: `/health` for Cloud Run health checks
- **Status Endpoint**: `/status` for platform status
- **Metrics Endpoint**: `/metrics` for Prometheus metrics

### **Logging**
- **Application Logs**: Available in Cloud Run logs
- **Error Logging**: Comprehensive error logging
- **Performance Logging**: Request/response logging

## **🔒 Security**

### **CORS Configuration**
- **Allow All Origins**: Configured for development
- **Customizable**: Can be restricted for production

### **Authentication**
- **API Key Validation**: Validates OpenAI API key
- **Environment Variables**: Secure handling of secrets
- **Error Handling**: No sensitive information in error responses

## **🚀 Performance**

### **Optimizations**
- **Async Processing**: All endpoints are async
- **Background Tasks**: Autonomous operation runs in background
- **Connection Pooling**: Database connection optimization
- **Caching**: Redis caching for performance

### **Scaling**
- **Auto-scaling**: Cloud Run automatically scales
- **Resource Limits**: Configurable CPU and memory
- **Concurrent Requests**: Handles multiple requests

## **🎯 Next Steps**

### **After Deployment**
1. **Test All Endpoints**: Verify all API endpoints work
2. **Monitor Performance**: Check response times and errors
3. **Start Autonomous Operation**: Begin business creation
4. **Monitor Income**: Track business creation and revenue

### **Production Considerations**
1. **Custom Domain**: Set up custom domain for the API
2. **SSL Certificate**: Ensure HTTPS is enabled
3. **Rate Limiting**: Implement rate limiting if needed
4. **Monitoring**: Set up comprehensive monitoring

## **✅ Success Indicators**

### **Deployment Success**
- ✅ Container starts successfully
- ✅ Health checks pass
- ✅ All endpoints respond correctly
- ✅ Platform status shows "operational"

### **Platform Ready**
- ✅ Web server running on Cloud Run
- ✅ API endpoints accessible
- ✅ Autonomous operation can be started
- ✅ Business creation ready

**Your AutoPilot Ventures platform is now ready to generate income through the web API!** 🚀💰 