from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class KnowledgeBaseRead(BaseModel):
    id: int
    category: str
    title: str
    content: str
    keywords: str
    is_active: bool
    usage_count: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class KnowledgeBaseCreate(BaseModel):
    category: str = Field(min_length=2, max_length=80)
    title: str = Field(min_length=3, max_length=180)
    content: str = Field(min_length=10, max_length=5000)
    keywords: str = Field(min_length=3, max_length=1000)
    is_active: bool = True


class KnowledgeBaseUpdate(BaseModel):
    category: str | None = Field(default=None, min_length=2, max_length=80)
    title: str | None = Field(default=None, min_length=3, max_length=180)
    content: str | None = Field(default=None, min_length=10, max_length=5000)
    keywords: str | None = Field(default=None, min_length=3, max_length=1000)
    is_active: bool | None = None
