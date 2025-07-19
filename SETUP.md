# 🚀 AutoPilot Ventures - Quick Setup Guide

## ⚡ 5-Minute Setup

### 1. Prerequisites
- Python 3.11+
- OpenAI API key
- Internet connection

### 2. Installation

```bash
# Clone or download the project
cd autopilot-ventures

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp env.example .env

# Edit .env with your OpenAI API key
# OPENAI_SECRET_KEY=your_actual_api_key_here
```

### 3. Quick Start

```bash
# Run the quick start script
python start.py

# Or run the demo to see it in action
python demo.py

# Or start the platform directly
python main.py start --goals productivity wellness technology
```

### 4. Access Dashboard

- **Web Dashboard**: http://localhost:8501
- **CLI Status**: `python main.py status`

## 🎯 What You Get

### Autonomous Agents
- **Niche Discovery**: Finds profitable market opportunities
- **Idea Generation**: Creates validated business ideas
- **MVP Development**: Builds and deploys products
- **Launch & Marketing**: Handles marketing campaigns
- **Operations**: Manages ongoing business operations
- **Optimization**: Makes strategic decisions and pivots

### Platform Features
- **Multi-Startup Management**: Handle 10-50 concurrent ventures
- **Real-time Monitoring**: Comprehensive dashboard and metrics
- **Budget Control**: Automated cost management
- **Security**: Built-in ethical safeguards
- **Scalability**: Cloud-ready architecture

## 🔧 Configuration

### Essential Settings (in .env)
```env
OPENAI_SECRET_KEY=your_openai_api_key
MONTHLY_BUDGET=500.0
STARTUP_BUDGET=100.0
MAX_CONCURRENT_STARTUPS=20
```

### Optional APIs (enhance functionality)
```env
STRIPE_SECRET_KEY=your_stripe_key          # Payment processing
SERPAPI_KEY=your_serpapi_key              # Market research
TWITTER_API_KEY=your_twitter_key          # Social marketing
GODADDY_API_KEY=your_godaddy_key          # Domain registration
```

## 🚀 Deployment Options

### Local Development
```bash
python main.py start --goals productivity wellness technology
```

### Docker Deployment
```bash
docker-compose up -d
```

### Cloud Deployment
- **AWS EC2**: Use Docker Compose
- **DigitalOcean**: Deploy with Docker
- **Google Cloud**: Use Compute Engine
- **Azure**: Deploy to Container Instances

## 📊 Monitoring

### Dashboard Features
- **Overview**: Platform status and metrics
- **Startups**: Individual startup management
- **Niches**: Market opportunity analysis
- **Analytics**: Revenue trends and ROI
- **Settings**: Configuration management

### CLI Commands
```bash
python main.py status          # Check platform status
python main.py dashboard       # Launch web dashboard
python main.py test --full     # Run comprehensive tests
python main.py backup          # Create platform backup
python main.py stop            # Graceful shutdown
```

## 🎮 Demo Mode

Run the demo to see the platform in action:

```bash
python demo.py
```

This will simulate:
1. Niche discovery
2. Idea generation
3. MVP development
4. Launch & marketing
5. Operations & monetization
6. Performance optimization

## 🔒 Security & Ethics

### Built-in Safeguards
- **Content Filtering**: Automatic detection of harmful content
- **Domain Restrictions**: Whitelist of allowed business domains
- **Budget Controls**: Automated spending limits
- **Kill Switch**: Emergency stop mechanism

### Ethical Guidelines
- No adult or harmful content
- No financial or medical advice
- No illegal activities
- Respect for user privacy

## 📈 Performance Metrics

The platform tracks:
- **Revenue Metrics**: Total revenue, per-startup revenue, conversion rates
- **Operational Metrics**: User counts, engagement rates, uptime
- **Financial Metrics**: ROI, cost per acquisition, profit margins
- **Agent Performance**: Success rates, processing times, error rates

## 🆘 Troubleshooting

### Common Issues

1. **"OpenAI API key not found"**
   - Add your API key to the .env file
   - Ensure the key is valid and has credits

2. **"Database connection failed"**
   - Check if SQLite is working
   - Ensure write permissions in the data directory

3. **"Dependencies not installed"**
   - Run `pip install -r requirements.txt`
   - Check Python version (3.11+ required)

4. **"Dashboard not loading"**
   - Check if port 8501 is available
   - Install Streamlit: `pip install streamlit`

### Getting Help

- **Documentation**: Check the README.md for detailed guides
- **Tests**: Run `python main.py test --full` to diagnose issues
- **Logs**: Check logs/autopilot.log for error details

## 🎯 Next Steps

1. **Start Small**: Begin with 1-2 startups to test the platform
2. **Monitor Performance**: Use the dashboard to track metrics
3. **Adjust Budgets**: Modify spending limits based on results
4. **Scale Up**: Increase startup count as you gain confidence
5. **Customize**: Add your own APIs and integrations

## ⚠️ Important Notes

- **API Costs**: Monitor your OpenAI API usage and costs
- **Legal Compliance**: Ensure compliance with local laws
- **Data Privacy**: Handle user data responsibly
- **Financial Responsibility**: Set appropriate budget limits

---

**Ready to launch your autonomous startup empire? 🚀**

Start with: `python start.py` 