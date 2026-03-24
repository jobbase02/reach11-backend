from fastapi import FastAPI, HTTPException, Security, Depends
from fastapi.security.api_key import APIKeyHeader
from pydantic import BaseModel
from typing import Optional, List
from fastapi.middleware.cors import CORSMiddleware
import os
import logging
from dotenv import load_dotenv
from scraper import reach11_lead_engine, reach11_post_lead_engine

# Load environment variables from .env file
load_dotenv()

# Production Logging Configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [%(levelname)s] - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Reach11 Production API")

# --- CORS SETUP ADD KARO ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"], # Aapka Next.js frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
#

# API Security Setup
API_KEY_NAME = "X-API-KEY"
# Fetches from .env, fails securely if missing in production
REACH11_API_KEY = os.getenv("REACH11_API_KEY") 
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=True)

def verify_api_key(api_key: str = Security(api_key_header)):
    if not REACH11_API_KEY:
        logger.error("API Key not configured in environment variables.")
        raise HTTPException(status_code=500, detail="Server Configuration Error")
    if api_key != REACH11_API_KEY:
        logger.warning("Unauthorized API access attempt blocked.")
        raise HTTPException(status_code=403, detail="Forbidden: Invalid API Key")
    return api_key

# Request Models
class TargetType(BaseModel):
    job_title: str
    location: str
    industry: Optional[str] = ""
    keywords: Optional[List[str]] = [] 

class LeadRequest(BaseModel):
    target: TargetType
    li_at_cookie: str
    user_city: str       
    user_country: str    
    max_leads: int = 3   


# =====================================================================
# ENDPOINT 1: TRADITIONAL PROFILE SCRAPER (Purana wala - Untouched)
# =====================================================================
@app.post("/api/v1/generate-leads")
async def generate_leads(request: LeadRequest, api_key: str = Depends(verify_api_key)):
    try:
        logger.info(f"Lead generation request received | Target: {request.target.job_title} | Location: {request.target.location}")
        
        # Call the scraper engine
        leads_data = reach11_lead_engine(
            target=request.target,
            li_at=request.li_at_cookie,
            proxy_url=None, # Keep None for local testing. In Prod, replace with OS Env Proxy.
            lead_count=request.max_leads
        )
        
        # Safe dict conversion
        target_dict = request.target.model_dump() if hasattr(request.target, 'model_dump') else request.target.dict()
        
        logger.info(f"Lead generation successful | Leads extracted: {len(leads_data)}")
        
        return {
            "status": "success", 
            "target_searched": target_dict,
            "leads": leads_data
        }

    except Exception as e:
        logger.error(f"Critical error in generate_leads endpoint: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error during scraping execution")


# =====================================================================
# ENDPOINT 2: HIGH-INTENT POST SCRAPER (Naya wala)
# =====================================================================
@app.post("/api/v1/generate-leads-from-posts")
async def generate_leads_from_posts(request: LeadRequest, api_key: str = Depends(verify_api_key)):
    try:
        logger.info(f"Post-based lead generation request received | Keywords: {request.target.keywords} | Location: {request.target.location}")
        
        # Call the new post scraper engine
        leads_data = reach11_post_lead_engine(
            target=request.target,
            li_at=request.li_at_cookie,
            proxy_url=None, # Keep None for local testing. In Prod, replace with OS Env Proxy.
            lead_count=request.max_leads
        )
        
        # Safe dict conversion
        target_dict = request.target.model_dump() if hasattr(request.target, 'model_dump') else request.target.dict()
        
        logger.info(f"Post-based lead generation successful | Leads extracted: {len(leads_data)}")
        
        return {
            "status": "success", 
            "intent_type": "post_author",
            "target_searched": target_dict,
            "leads": leads_data
        }

    except Exception as e:
        logger.error(f"Critical error in generate_leads_from_posts endpoint: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error during post scraping execution")