from typing import List, Optional, Dict
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime

class InstagramAccount(BaseModel):
    username: str
    password: str
    is_active: bool = True
    last_login: Optional[datetime] = None
    login_status: str = "pending"
    error_message: Optional[str] = None

class Template(BaseModel):
    id: Optional[str] = None
    name: str
    content: str
    variables: List[str] = []
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class DMRequest(BaseModel):
    template_id: str
    csv_data: List[Dict[str, str]]
    instagram_account_username: Optional[str] = None  # If None, system will choose an available account

class AutoReplyConfig(BaseModel):
    is_enabled: bool = False
    template_id: Optional[str] = None
    conditions: Dict[str, str] = {}  # e.g., {"contains": "price"}

class DMResponse(BaseModel):
    success: bool
    message: str
    details: Optional[Dict] = None
    timestamp: datetime = Field(default_factory=datetime.now)

class DMCampaignStatus(BaseModel):
    campaign_id: str
    total_messages: int
    sent_messages: int
    failed_messages: int
    status: str  # "running", "completed", "failed"
    errors: List[Dict[str, str]] = []
    start_time: datetime
    end_time: Optional[datetime] = None

class TokenData(BaseModel):
    username: str
    exp: Optional[datetime] = None

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

# API Response Models
class APIResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict] = None
    errors: Optional[List[Dict[str, str]]] = None

class TemplateList(BaseModel):
    templates: List[Template]
    total: int

class AccountList(BaseModel):
    accounts: List[InstagramAccount]
    total: int

class CampaignList(BaseModel):
    campaigns: List[DMCampaignStatus]
    total: int
