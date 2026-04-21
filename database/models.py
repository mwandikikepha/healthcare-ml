from sqlalchemy import Column, Integer, String, Float, DateTime
from .db_connection import Base

class CleanedHealthcare(Base):
    __tablename__ = "cleaned_healthcare_data"

    # Primary key is important for SQL best practices
    id = Column(Integer, primary_key=True, autoincrement=True)
    age = Column(Integer)
    gender = Column(String)
    blood_type = Column(String)
    medical_condition = Column(String)
    insurance_provider = Column(String)
    admission_type = Column(String)
    medication = Column(String)
    test_results = Column(String)
    days_hospitalized = Column(Integer)
    billing_amount = Column(Float)