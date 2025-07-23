# 🚀 AutoPilot Ventures - Personal Income Generation Platform

An autonomous AI-powered platform for creating, managing, and scaling businesses for personal income generation with multilingual support, advanced security, and comprehensive analytics.

## ✨ Features

### 🤖 **AI Agents**
- **Niche Research Agent**: Market analysis and opportunity identification
- **MVP Design Agent**: Product development and technical planning
- **Marketing Strategy Agent**: Campaign planning and audience targeting
- **Content Creation Agent**: Copywriting and content generation
- **Analytics Agent**: Data analysis and insights generation
- **Operations Agent**: Business optimization and monetization
- **Funding & Investor Agent**: Investment strategy and funding optimization
- **Legal & Compliance Agent**: Legal compliance and risk management
- **HR & Team Building Agent**: Team management and human resources
- **Customer Support & Scaling Agent**: Customer service and business scaling

### 🌍 **Multilingual Support**
- **10 Languages**: English, Spanish, Mandarin, French, German, Arabic, Portuguese, Hindi, Russian, Japanese
- **Cultural Adaptation**: Context-aware content generation
- **Translation Services**: Google Translate and DeepL integration

### 🔒 **Security & Compliance**
- **Fernet Encryption**: End-to-end data encryption
- **Content Safety**: Detoxify integration for toxicity detection
- **Input Sanitization**: Bleach-based HTML sanitization
- **Access Control**: Domain whitelisting and blacklisting
- **GDPR Compliance**: Data protection and privacy controls

### 📊 **Analytics & Monitoring**
- **Real-time Metrics**: Performance tracking and ROI calculation
- **Budget Management**: Cost tracking and spending limits
- **Health Checks**: Comprehensive system monitoring
- **Database Statistics**: Startup and agent performance metrics

### 🗄️ **Database Management**
- **SQLAlchemy ORM**: Robust data modeling and relationships
- **PostgreSQL Support**: Scalable database with connection pooling
- **Automatic Backups**: Scheduled database backups
- **Data Cleanup**: Automated old data removal
- **Redis Caching**: High-performance caching layer

## 🛠️ Installation

### Prerequisites
- Python 3.8+
- pip package manager
- OpenAI API key

### Quick Start

1. **Clone the repository**
```bash
git clone <repository-url>
cd autopilot-ventures
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Generate Fernet key**
```bash
python generate_fernet_key.py --save-env
```

4. **Configure environment variables**
```bash
# Copy example environment file
cp env.example .env

# Edit .env file with your API keys
nano .env
```

5. **Run health check**
```bash
python main.py --health-check --verbose
```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
# OpenAI Configuration
OPENAI_SECRET_KEY=your_openai_api_key_here

# Security
FERNET_KEY=your_fernet_key_here

# Optional: SerpAPI for enhanced research
SERPAPI_KEY=your_serpapi_key_here

# Database (optional)
DATABASE_URL=sqlite:///autopilot_ventures.db
```

### Configuration Classes

The platform uses dataclass-based configuration:

```python
from config import config

# Access AI settings
print(config.ai.model_name)  # gpt-4
print(config.ai.max_tokens)  # 4000

# Access security settings
print(config.security.content_safety_threshold)  # 0.7

# Access budget settings
print(config.budget.initial_budget)  # 500.0
```

## 🚀 Usage

### Command Line Interface

#### Health Check
```bash
# Basic health check
python main.py --health-check

# Verbose health check with details
python main.py --health-check --verbose
```

#### Multilingual Demo
```bash
# Demo in Hindi
python main.py --demo --languages hi

# Demo in multiple languages
python main.py --demo --languages en es fr de hi
```

#### Platform Metrics
```bash
# View platform statistics
python main.py --metrics
```

### Python API

#### Basic Usage
```python
import asyncio
from main import AutoPilotVentures

async def main():
    # Initialize platform
    app = AutoPilotVentures()
    
    # Create startup
    startup_result = await app.create_startup(
        name="My Startup",
        description="A revolutionary product",
        niche="technology",
        languages=["en", "es"]
    )
    
    # Run niche research
    research_result = await app.run_niche_research("AI productivity tools")
    
    # Run MVP design
    design_result = await app.run_mvp_design(
        niche="AI productivity tools",
        target_audience="developers"
    )
    
    # Run marketing strategy
    marketing_result = await app.run_marketing_strategy(
        product="AI Productivity Suite",
        target_audience="developers",
        budget=1000.0
    )

# Run the application
asyncio.run(main())
```

#### Advanced Usage
```python
import asyncio
from main import AutoPilotVentures

async def comprehensive_startup_creation():
    app = AutoPilotVentures()
    
    # Create startup with multilingual support
    startup = await app.create_startup(
        name="Wellness App",
        description="Holistic wellness application",
        niche="health and wellness",
        languages=["hi", "en"]  # Hindi and English
    )
    
    if startup['success']:
        # Run all agents for comprehensive analysis
        tasks = [
            app.run_niche_research("wellness apps"),
            app.run_mvp_design("wellness apps", "health-conscious individuals"),
            app.run_marketing_strategy("Wellness App", "health-conscious individuals", 1000.0),
            app.run_content_creation("Wellness benefits", "health enthusiasts"),
            app.run_analytics("User engagement data", "conversion metrics"),
            app.run_operations_optimization("Current operations", "revenue data")
        ]
        
        results = await asyncio.gather(*tasks)
        
        # Process results
        for i, result in enumerate(results):
            if result['success']:
                print(f"✅ Task {i+1} completed: {result['message']}")
            else:
                print(f"❌ Task {i+1} failed: {result['error']}")

# Run comprehensive startup creation
asyncio.run(comprehensive_startup_creation())
```

## 🧪 Testing

### Run All Tests
```bash
# Run basic tests
pytest tests/test_basic.py -v

# Run with coverage
pytest tests/ --cov=. --cov-report=html

# Run specific test class
pytest tests/test_basic.py::TestConfig -v
```

### Test Categories
- **Configuration Tests**: Config validation and structure
- **Utility Tests**: Helper functions and security
- **Database Tests**: CRUD operations and relationships
- **Agent Tests**: AI agent functionality
- **Application Tests**: Main app integration

### Test Fixtures
The test suite includes fixtures for:
- Temporary database setup
- Mock API keys
- Fernet key generation
- Sample data creation

## 🔧 Development

### Project Structure
```
autopilot-ventures/
├── config.py              # Configuration management
├── utils.py               # Utility functions
├── database.py            # Database models and management
├── agents.py              # AI agents implementation
├── main.py                # Main application
├── generate_fernet_key.py # Key generation utility
├── requirements.txt       # Dependencies
├── tests/                 # Test suite
│   ├── test_basic.py     # Basic functionality tests
│   └── test_enhanced.py  # Advanced feature tests
├── backups/              # Database backups
├── logs/                 # Application logs
└── exports/              # Data exports
```

### Code Style
The project follows PEP 8 standards:
- Line length: ≤ 79 characters
- Type hints: Required for all functions
- Docstrings: Comprehensive documentation
- Import organization: Standard library, third-party, local

### Adding New Features

#### 1. New AI Agent
```python
from agents import BaseAgent, AgentResult

class NewAgent(BaseAgent):
    def __init__(self, startup_id: str):
        super().__init__('new_agent', startup_id)
        
        self.prompt_template = PromptTemplate(
            input_variables=["input_data"],
            template="Your prompt template here: {input_data}"
        )
    
    async def execute(self, input_data: str) -> AgentResult:
        # Implementation here
        pass
```

#### 2. New Configuration
```python
from config import dataclass, field

@dataclass
class NewConfig:
    setting1: str = field(default="default_value")
    setting2: int = field(default=100)
```

#### 3. New Database Model
```python
from database import Base, Column, String, Integer

class NewModel(Base):
    __tablename__ = 'new_models'
    
    id = Column(String(50), primary_key=True)
    name = Column(String(100), nullable=False)
    value = Column(Integer, default=0)
```

## 📊 Monitoring & Analytics

### Health Checks
The platform provides comprehensive health monitoring:

```python
# Run health check
results = await app.health_check(verbose=True)

# Check specific components
print(f"Database: {results['checks']['database']['status']}")
print(f"Configuration: {results['checks']['configuration']['status']}")
print(f"Agents: {results['checks']['agents']['status']}")
print(f"Budget: {results['checks']['budget']['status']}")
print(f"Security: {results['checks']['security']['status']}")
```

### Metrics Collection
```python
# Get platform metrics
metrics = app.get_metrics()

print(f"Startups: {metrics['database']['startups']}")
print(f"Agents: {metrics['database']['agents']}")
print(f"Remaining Budget: ${metrics['budget']['remaining']}")
print(f"Daily Spent: ${metrics['budget']['daily_spent']}")
```

## 🔒 Security Features

### Encryption
```python
from utils import security_utils

# Encrypt sensitive data
encrypted = security_utils.encrypt_data("sensitive information")

# Decrypt data
decrypted = security_utils.decrypt_data(encrypted)
```

### Content Safety
```python
# Check content safety
safety_result = security_utils.check_content_safety("user content")

if safety_result['toxicity'] > 0.7:
    print("Content flagged as potentially unsafe")
```

### Input Sanitization
```python
from utils import sanitize_html

# Sanitize HTML content
clean_html = sanitize_html("<script>alert('xss')</script><p>Safe content</p>")
# Result: "<p>Safe content</p>"
```

## 🌍 Multilingual Support

### Supported Languages
- **en**: English
- **es**: Spanish
- **zh**: Mandarin/Chinese
- **fr**: French
- **de**: German
- **ar**: Arabic
- **pt**: Portuguese
- **hi**: Hindi
- **ru**: Russian
- **ja**: Japanese

### Cultural Context
The platform automatically adapts content based on cultural context:

```python
# Create startup with Hindi support
startup = await app.create_startup(
    name="Wellness App",
    description="Holistic wellness application",
    niche="health and wellness",
    languages=["hi"]  # Hindi
)

# Content will be culturally adapted for Indian market
```

## 🚀 Deployment

### Docker Deployment
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["python", "main.py"]
```

### Environment Setup
```bash
# Production environment variables
export OPENAI_SECRET_KEY="your_production_key"
export FERNET_KEY="your_production_fernet_key"
export DATABASE_URL="postgresql://user:pass@host:port/db"
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

### Development Setup
```bash
# Clone your fork
git clone https://github.com/yourusername/autopilot-ventures.git

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -r requirements.txt
pip install pytest pytest-cov flake8

# Run tests
pytest tests/ -v

# Run linting
flake8 . --exclude=venv,.env
```

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

### Common Issues

#### Fernet Key Issues
```bash
# Generate new key
python generate_fernet_key.py --save-env

# Validate existing key
python generate_fernet_key.py --validate "your_key_here"
```

#### Database Issues
```bash
# Check database health
python main.py --health-check --verbose

# Backup database
python -c "from database import db_manager; db_manager.backup_database('backup.db')"
```

#### API Key Issues
```bash
# Verify OpenAI key
python -c "import openai; openai.api_key='your_key'; print('Key valid')"
```

### Getting Help
- Check the health check output for specific issues
- Review the test suite for usage examples
- Ensure all environment variables are properly set
- Verify API keys have sufficient credits

## 🎯 Roadmap

### Upcoming Features
- [ ] Web dashboard interface
- [ ] Real-time collaboration
- [ ] Advanced analytics dashboard
- [ ] Integration with external APIs
- [ ] Mobile application
- [ ] Advanced AI model support
- [ ] Automated deployment pipelines
- [ ] Enhanced security features

### Version History
- **v1.0.0**: Initial release with core AI agents
- **v1.1.0**: Added multilingual support
- [ ] Enhanced security and monitoring
- [ ] Improved testing and documentation

---

**AutoPilot Ventures Platform** - Personal income generation through autonomous business creation and management. 