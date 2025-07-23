# AutoPilot Ventures - Comprehensive Setup Guide

## 🚀 Overview

AutoPilot Ventures is a Python-based AI platform with 10 autonomous agents for business creation, featuring multilingual support for 10 languages, SQLAlchemy database, and comprehensive testing capabilities.

## 📋 Prerequisites

- **Python 3.8+**
- **OpenAI API Key** (required)
- **DeepL API Key** (for translations)
- **Internet connection** (for API calls)

## 🛠️ Quick Setup

### 1. Clone and Navigate
```bash
git clone <repository-url>
cd autopilot-ventures
```

### 2. Run Comprehensive Setup
```bash
python setup.py
```

This will:
- ✅ Install all dependencies from `requirements.txt`
- ✅ Create `.env` file with API key placeholders
- ✅ Initialize SQLAlchemy database (`phase1_memory.db`)
- ✅ Test all 10 agents
- ✅ Test multilingual functionality
- ✅ Update README with local testing steps

### 3. Configure API Keys
Edit the `.env` file and add your actual API keys:
```env
OPENAI_SECRET_KEY=your_actual_openai_key_here
DEEPL_API_KEY=your_actual_deepl_key_here
```

## 🤖 Agent Overview

The platform includes **10 specialized AI agents**:

| Agent | Purpose | Multilingual |
|-------|---------|--------------|
| 1. **Niche Research Agent** | Market research and niche identification | ✅ |
| 2. **MVP Design Agent** | Product design and prototyping | ✅ |
| 3. **Marketing Strategy Agent** | Marketing planning and execution | ✅ |
| 4. **Content Creation Agent** | Content generation and management | ✅ |
| 5. **Analytics Agent** | Data analysis and insights | ✅ |
| 6. **Operations Monetization Agent** | Business operations and revenue | ✅ |
| 7. **Funding Investor Agent** | Investment and funding strategies | ✅ |
| 8. **Legal Compliance Agent** | Legal documentation and compliance | ✅ |
| 9. **HR Team Building Agent** | Team building and hiring | ✅ |
| 10. **Customer Support Scaling Agent** | Customer support optimization | ✅ |

## 🌍 Multilingual Support

**Supported Languages (10 total):**
- 🇺🇸 English (en)
- 🇪🇸 Spanish (es)
- 🇨🇳 Chinese (zh)
- 🇫🇷 French (fr)
- 🇩🇪 German (de)
- 🇸🇦 Arabic (ar)
- 🇵🇹 Portuguese (pt)
- 🇮🇳 Hindi (hi)
- 🇷🇺 Russian (ru)
- 🇯🇵 Japanese (ja)

## 🧪 Testing

### Quick Test
```bash
python run_tests.py
```

### Comprehensive Agent Testing
```bash
python test_agents.py
```

### Individual Agent Test
```python
import asyncio
from agents import NicheResearchAgent
from utils import generate_id

async def test_agent():
    startup_id = generate_id('test')
    agent = NicheResearchAgent(startup_id)
    result = await agent.execute(
        niche="AI productivity tools",
        market_data="Growing market"
    )
    print(f"Success: {result.success}")
    print(f"Data: {result.data}")

asyncio.run(test_agent())
```

## 🚀 Running the Platform

### Basic Usage
```bash
python main.py
```

### With Language Specification
```bash
# English
python main.py --language en --niche "AI productivity tools"

# Spanish
python main.py --language es --niche "Herramientas de productividad IA"

# Chinese
python main.py --language zh --niche "AI生产力工具"
```

### Business Creation Example
```python
import asyncio
from main import AutoPilotVenturesApp

async def create_business():
    app = AutoPilotVenturesApp()
    
    # English business
    result_en = await app.create_business(
        name="AI Productivity Platform",
        description="AI-powered task management for remote teams",
        niche="Productivity Software",
        language="en"
    )
    
    # Spanish business
    result_es = await app.create_business(
        name="Plataforma de Productividad IA",
        description="Gestión de tareas impulsada por IA para equipos remotos",
        niche="Software de Productividad",
        language="es"
    )
    
    print(f"English: {result_en}")
    print(f"Spanish: {result_es}")

asyncio.run(create_business())
```

## 🗄️ Database

### SQLAlchemy Configuration
- **Database**: SQLite (`phase1_memory.db`)
- **ORM**: SQLAlchemy
- **Auto-initialization**: On first run
- **Backup**: Automatic

### Database Schema
```python
# Key tables
- startups: Business information
- agents: Agent metadata and performance
- transactions: Financial tracking
- content: Generated content storage
- analytics: Performance metrics
```

## 🔧 Configuration

### Environment Variables
```env
# Required
OPENAI_SECRET_KEY=your_openai_key

# Optional but recommended
DEEPL_API_KEY=your_deepl_key
FERNET_KEY=auto_generated_encryption_key
DATABASE_URL=sqlite:///phase1_memory.db

# Payment processing (optional)
STRIPE_SECRET_KEY=your_stripe_key
STRIPE_PUBLISHABLE_KEY=your_stripe_publishable_key
```

### Configuration Classes
```python
from config import config

# AI Configuration
print(config.ai.model_name)  # 'gpt-4'
print(config.ai.max_tokens)  # 4000

# Multilingual Configuration
print(config.multilingual.supported_languages)  # 10 languages
print(config.multilingual.default_language)     # 'en'

# Security Configuration
print(config.security.fernet_key)  # Auto-generated encryption key
```

## 📊 Monitoring and Logging

### Metrics
- **Agent performance** tracking
- **Cost monitoring** per operation
- **Success rates** by agent type
- **Multilingual accuracy** metrics

### Logging
```python
import logging
logger = logging.getLogger(__name__)

# Structured logging with context
logger.info("Agent execution started", extra={
    'agent_type': 'niche_research',
    'language': 'en',
    'startup_id': startup_id
})
```

## 🔒 Security Features

- **Fernet encryption** for sensitive data
- **Content safety filtering**
- **API key management**
- **Secure agent communication**
- **Input validation** and sanitization

## 🧪 Unit Testing

### Run All Tests
```bash
python -m pytest test_setup.py -v
```

### Test Specific Components
```bash
# Test multilingual support
python -m pytest test_setup.py::TestMultilingualSupport -v

# Test agent coordination
python -m pytest test_setup.py::TestAgentCoordination -v

# Test configuration
python -m pytest test_setup.py::TestConfiguration -v
```

## 🐛 Troubleshooting

### Common Issues

#### 1. API Key Errors
```bash
# Check .env file exists and has correct keys
cat .env

# Verify OpenAI key format
echo $OPENAI_SECRET_KEY
```

#### 2. Database Issues
```bash
# Reset database
rm phase1_memory.db
python setup.py
```

#### 3. Import Errors
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

#### 4. Multilingual Issues
```bash
# Check DeepL API key
echo $DEEPL_API_KEY

# Test translation service
python -c "from config import config; print(config.multilingual.translation_service)"
```

### Debug Mode
```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
python main.py
```

## 📈 Performance Optimization

### Agent Optimization
- **Concurrent execution** for multiple agents
- **Caching** for repeated operations
- **Rate limiting** for API calls
- **Resource pooling** for database connections

### Memory Management
- **Connection pooling** for database
- **Garbage collection** optimization
- **Memory monitoring** and alerts

## 🔄 Continuous Integration

### GitHub Actions
```yaml
# .github/workflows/test.yml
name: Test Platform
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.8
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: python run_tests.py
```

## 📚 API Documentation

### Agent API
```python
# All agents follow the same interface
async def execute(self, **kwargs) -> AgentResult:
    """
    Execute agent task with multilingual support
    
    Returns:
        AgentResult: Success status, data, message, and cost
    """
```

### Main Application API
```python
class AutoPilotVenturesApp:
    async def create_business(self, name: str, description: str, 
                            niche: str, language: str = "en") -> Dict[str, Any]
    
    async def run_workflow(self, workflow_config: Dict[str, Any], 
                          language: str = "en") -> Dict[str, Any]
    
    async def health_check(self) -> Dict[str, Any]
```

## 🎯 Next Steps

1. **Configure API keys** in `.env` file
2. **Run comprehensive tests**: `python test_agents.py`
3. **Test multilingual support** with different languages
4. **Create your first business** using `main.py`
5. **Monitor performance** and costs
6. **Scale operations** as needed

## 📞 Support

- **Documentation**: Check this README and inline code comments
- **Issues**: Create GitHub issues for bugs or feature requests
- **Testing**: Use the comprehensive test suite for validation

---

**🎉 Your AutoPilot Ventures platform is now ready for autonomous business creation!** 