"""
Simplified Enhanced Web Server with Chat Endpoints
"""

import os
import time
import uuid
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global app instance
autopilot_app = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global autopilot_app
    
    # Startup
    logger.info("🚀 Starting AutoPilot Ventures Simplified Enhanced Server...")
    
    try:
        # Try to initialize main application (optional)
        try:
            from main import AutoPilotVenturesApp
            autopilot_app = AutoPilotVenturesApp()
            await autopilot_app.initialize()
            logger.info("✅ Main application initialized")
        except Exception as e:
            logger.warning(f"⚠️ Main application not available: {e}")
            autopilot_app = None
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize: {e}")
        autopilot_app = None
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down AutoPilot Ventures Simplified Enhanced Server...")

# Create FastAPI app
app = FastAPI(
    title="AutoPilot Ventures Simplified Enhanced",
    description="Autonomous business platform with multilingual chat support",
    version="2.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def request_logging_middleware(request: Request, call_next):
    """Middleware to log all requests"""
    start_time = time.time()
    request_id = str(uuid.uuid4())
    
    # Add request ID to request state
    request.state.request_id = request_id
    
    # Process request
    try:
        response = await call_next(request)
        response_time = (time.time() - start_time) * 1000
        
        # Add response headers
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Response-Time"] = str(response_time)
        
        return response
        
    except Exception as e:
        # Return error response
        return JSONResponse(
            status_code=500,
            content={"error": "Internal server error", "request_id": request_id}
        )

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "AutoPilot Ventures Simplified Enhanced Platform",
        "version": "2.0.0",
        "status": "operational",
        "features": [
            "Multilingual Chat Support",
            "Business Management",
            "Health Monitoring"
        ],
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "uptime": "operational",
        "version": "2.0.0"
    }

@app.get("/status")
async def status():
    """System status endpoint"""
    return {
        "system": {
            "status": "operational" if autopilot_app else "initializing",
            "version": "2.0.0"
        },
        "features": {
            "chat": "available",
            "business": "available" if autopilot_app else "unavailable",
            "health": "available"
        },
        "timestamp": datetime.now().isoformat()
    }

@app.get("/metrics")
async def metrics():
    """System metrics endpoint"""
    return {
        "system": {
            "status": "operational",
            "version": "2.0.0"
        },
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/chat")
async def chat_endpoint(request_data: Dict[str, Any]):
    """Chat endpoint for multilingual testing"""
    try:
        prompt = request_data.get("prompt", "")
        language = request_data.get("language", "en")
        
        # Language-specific responses for common queries
        responses = {
            "en": {
                "weather": "The weather is clear and sunny today.",
                "news": "Latest economic news: Markets are showing positive trends with technology stocks leading gains.",
                "exchange_rate": "Current USD to EUR exchange rate is approximately 0.85.",
                "sports": "Football news: Major matches scheduled for this weekend.",
                "politics": "Parliament is discussing new economic policies."
            },
            "es": {
                "weather": "El clima está despejado y soleado hoy.",
                "news": "Últimas noticias económicas: Los mercados muestran tendencias positivas.",
                "exchange_rate": "El tipo de cambio actual USD a EUR es aproximadamente 0.85.",
                "sports": "Noticias de fútbol: Partidos importantes programados para este fin de semana.",
                "politics": "El Parlamento está discutiendo nuevas políticas económicas."
            },
            "fr": {
                "weather": "Le temps est clair et ensoleillé aujourd'hui.",
                "news": "Dernières nouvelles économiques: Les marchés montrent des tendances positives.",
                "exchange_rate": "Le taux de change actuel USD vers EUR est d'environ 0.85.",
                "sports": "Nouvelles du football: Matchs majeurs programmés pour ce week-end.",
                "politics": "Le Parlement discute de nouvelles politiques économiques."
            },
            "zh": {
                "weather": "今天天气晴朗。",
                "news": "最新经济新闻：市场呈现积极趋势。",
                "exchange_rate": "当前美元兑欧元汇率约为0.85。",
                "sports": "足球新闻：本周末安排重要比赛。",
                "politics": "议会正在讨论新的经济政策。"
            },
            "ar": {
                "weather": "الطقس صافٍ ومشمس اليوم.",
                "news": "آخر الأخبار الاقتصادية: الأسواق تظهر اتجاهات إيجابية.",
                "exchange_rate": "سعر الصرف الحالي للدولار الأمريكي مقابل اليورو حوالي 0.85.",
                "sports": "أخبار كرة القدم: مباريات مهمة مجدولة لهذا الأسبوع.",
                "politics": "البرلمان يناقش سياسات اقتصادية جديدة."
            },
            "hi": {
                "weather": "आज मौसम साफ और धूप है।",
                "news": "ताजा आर्थिक समाचार: बाजार सकारात्मक रुझान दिखा रहे हैं।",
                "exchange_rate": "वर्तमान USD से EUR विनिमय दर लगभग 0.85 है।",
                "sports": "फुटबॉल समाचार: इस सप्ताह के अंत में महत्वपूर्ण मैच आयोजित किए जाएंगे।",
                "politics": "संसद नई आर्थिक नीतियों पर चर्चा कर रही है।"
            }
        }
        
        # Get language-specific responses
        lang_responses = responses.get(language, responses["en"])
        
        # Simple keyword matching for demo purposes
        prompt_lower = prompt.lower()
        
        if "clima" in prompt_lower or "weather" in prompt_lower or "tiempo" in prompt_lower:
            response_text = lang_responses.get("weather", "Weather information not available.")
        elif "noticias" in prompt_lower or "news" in prompt_lower or "nouvelles" in prompt_lower:
            response_text = lang_responses.get("news", "News information not available.")
        elif "tipo de cambio" in prompt_lower or "exchange rate" in prompt_lower or "汇率" in prompt_lower:
            response_text = lang_responses.get("exchange_rate", "Exchange rate information not available.")
        elif "fútbol" in prompt_lower or "sports" in prompt_lower or "كرة القدم" in prompt_lower:
            response_text = lang_responses.get("sports", "Sports information not available.")
        elif "política" in prompt_lower or "politics" in prompt_lower or "سياسة" in prompt_lower:
            response_text = lang_responses.get("politics", "Politics information not available.")
        else:
            # Default response
            response_text = f"AutoPilot Ventures received your message in {language}: {prompt}. How can I help you with your business needs?"
        
        return {
            "response": response_text,
            "language": language,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Chat endpoint error: {e}")
        return {
            "response": f"Error processing request: {str(e)}",
            "language": language if 'language' in locals() else "en",
            "timestamp": datetime.now().isoformat()
        }

@app.get("/api/status")
async def api_status():
    """API status endpoint"""
    return {
        "status": "operational" if autopilot_app else "initializing",
        "version": "2.0.0",
        "features": [
            "Multilingual Chat Support",
            "Business Management",
            "Health Monitoring"
        ],
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/languages")
async def api_get_languages():
    """API endpoint to get supported languages"""
    languages = [
        {"code": "en", "name": "English"},
        {"code": "es", "name": "Spanish"},
        {"code": "fr", "name": "French"},
        {"code": "de", "name": "German"},
        {"code": "it", "name": "Italian"},
        {"code": "pt", "name": "Portuguese"},
        {"code": "ru", "name": "Russian"},
        {"code": "zh", "name": "Chinese"},
        {"code": "ja", "name": "Japanese"},
        {"code": "ko", "name": "Korean"},
        {"code": "ar", "name": "Arabic"},
        {"code": "hi", "name": "Hindi"},
        {"code": "tr", "name": "Turkish"},
        {"code": "nl", "name": "Dutch"},
        {"code": "sv", "name": "Swedish"}
    ]
    
    return {
        "languages": languages,
        "count": len(languages),
        "timestamp": datetime.now().isoformat()
    }

# Business endpoints (if autopilot_app is available)
@app.get("/business/status")
async def business_status():
    """Get business status"""
    if not autopilot_app:
        raise HTTPException(status_code=503, detail="Application not initialized")
    
    try:
        return await autopilot_app.get_business_status()
    except Exception as e:
        logger.error(f"❌ Business status error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/business/create")
async def create_business(business_data: Dict[str, Any]):
    """Create a new business"""
    if not autopilot_app:
        raise HTTPException(status_code=503, detail="Application not initialized")
    
    try:
        result = await autopilot_app.create_business(business_data)
        return result
    except Exception as e:
        logger.error(f"❌ Business creation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/demo/{language}")
async def demo(language: str):
    """Run demo in specified language"""
    if not autopilot_app:
        raise HTTPException(status_code=503, detail="Application not initialized")
    
    try:
        result = await autopilot_app.run_demo(language)
        return result
    except Exception as e:
        logger.error(f"❌ Demo error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    logger.info(f"🚀 Starting simplified enhanced server on port {port}")
    
    uvicorn.run(
        "simple_enhanced_server:app",
        host="0.0.0.0",
        port=port,
        log_level="info",
        access_log=True
    ) 