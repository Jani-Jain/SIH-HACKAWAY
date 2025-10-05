# main.py
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timedelta
from jose import JWTError, ExpiredSignatureError

from database import engine, Base, SessionLocal
from models import Learner, Credential
from schemas import LearnerCreate, LearnerRead, CredentialCreate, CredentialRead, LoginRequest, TokenResponse

# ------------------ FastAPI app ------------------
app = FastAPI()
@app.get("/")
def root():
    return {"status": "Server is running!"}

# ------------------ Create tables ------------------
Base.metadata.create_all(bind=engine)

# ------------------ Database dependency ------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ------------------ JWT setup ------------------
SECRET_KEY = "your-super-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def create_access_token(data: dict, expires_delta: timedelta |None = None):
    to_encode = data.copy()
    if expires_delta is None:
        expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return token

def get_current_learner(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
       payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
       learner_id = payload.get("sub")
       if learner_id is None:
        raise HTTPException(status_code=401, detail="Invalid token")
       learner_id = str(learner_id)  # force it to str for downstream usage

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    learner = db.query(Learner).filter(Learner.id == int(learner_id)).first()
    if learner is None:
        raise HTTPException(status_code=401, detail="Learner not found")
    return learner

# ------------------ Learner endpoints ------------------
@app.post("/learners/", response_model=LearnerRead)
def create_learner(learner: LearnerCreate, db: Session = Depends(get_db)):
    db_learner = Learner(name=learner.name, email=learner.email)
    db.add(db_learner)
    db.commit()
    db.refresh(db_learner)
    return db_learner

@app.get("/learners/{learner_id}", response_model=LearnerRead)
def read_learner(learner_id: int, db: Session = Depends(get_db)):
    return db.query(Learner).filter(Learner.id == learner_id).first()

# ------------------ Credential endpoints ------------------
@app.post("/credentials/", response_model=CredentialRead)
def create_credential(cred: CredentialCreate, db: Session = Depends(get_db)):
    db_cred = Credential(title=cred.title, learner_id=cred.learner_id)
    db.add(db_cred)
    db.commit()
    db.refresh(db_cred)
    return db_cred

@app.get("/credentials/{cred_id}", response_model=CredentialRead)
def read_credential(cred_id: int, db: Session = Depends(get_db)):
    return db.query(Credential).filter(Credential.id == cred_id).first()

@app.get("/learners/{learner_id}/credentials", response_model=list[CredentialRead])
def read_credentials_for_learner(learner_id: int, db: Session = Depends(get_db)):
    return db.query(Credential).filter(Credential.learner_id == learner_id).all()

# ------------------ JWT Login ------------------
@app.post("/login/", response_model=TokenResponse)
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    learner = db.query(Learner).filter(Learner.email == login_data.email).first()
    if not learner:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email")
    token = create_access_token({"sub": str(learner.id)})
    return {"access_token": token, "token_type": "bearer"}

# ------------------ Protected endpoint ------------------
@app.get("/me/credentials", response_model=list[CredentialRead])
def read_my_credentials(current_learner: Learner = Depends(get_current_learner), db: Session = Depends(get_db)):
    return db.query(Credential).filter(Credential.learner_id == current_learner.id).all()
