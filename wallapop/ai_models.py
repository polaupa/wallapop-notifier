from pydantic import BaseModel, ValidationError
from typing import Optional
from datetime import datetime, time

def ModelPlatform(MODEL):
    if MODEL == "deepseek-chat":
        return "DeepSeek"
    elif MODEL in ["sonar", "r1-1776", "sonar-pro"]:
        return "Perplexity"
    elif MODEL in ["gemini-2.5-flash", "gemini-2.5-pro"]:
        return "Gemini"
    elif MODEL in ["mistral-large-2411", "mistral-large-latest", "mistral-medium-2505", "magistral-medium-2506"]:
        return "Mistral"
    else:
        return None

class Product(BaseModel):
    title: str
    max_price: int
    analysis: str
    score: int
    item_url: str

class Products(BaseModel):
    products: list[Product]

class CombinedProduct(BaseModel):
    title: str
    price: float
    max_price: Optional[float] = None 
    analysis: Optional[str] = None
    description: str
    location: str
    date: datetime
    user_id: str
    user_reviews: int 
    score: Optional[int] = None
    item_url: str

class BaseProduct(BaseModel):
    title: str
    price: float
    item_url: str
    description: str 
    location: str 
    date: datetime
    user_id: str