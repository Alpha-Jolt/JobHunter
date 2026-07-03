from pydantic import BaseModel
from typing import List, Optional


class StartDiscoveryRequest(BaseModel):
    role: str
    location: str
    experience: str = "fresher"
    salary: Optional[str] = None


class BootstrapRequest(BaseModel):
    sources: List[str] = ["all"]


class StartCareerScrapeRequest(BaseModel):
    company_id: Optional[str] = None
