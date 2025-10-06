from pydantic import BaseModel

class LearnerCreate(BaseModel):
    name: str
    email: str
    password: str  

class LearnerRead(BaseModel):
    id: int
    name: str
    email: str
    class Config:
        orm_mode = True

class CredentialCreate(BaseModel):
    title: str
    learner_id: int

class CredentialRead(BaseModel):
    id: int
    title: str
    learner_id: int
    class Config:
        orm_mode = True

# schemas.py
from pydantic import BaseModel

class LoginRequest(BaseModel):
    email: str
    password: str  

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
