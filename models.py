from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
from sqlalchemy import Column, Integer, String


class Learner(Base):
    __tablename__ = "learners"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)  
    credentials = relationship("Credential", back_populates="learner")  # connect to Credential

class Credential(Base):
    __tablename__ = "credentials"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    learner_id = Column(Integer, ForeignKey("learners.id"))
    learner = relationship("Learner", back_populates="credentials")
