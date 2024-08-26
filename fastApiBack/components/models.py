from sqlalchemy import Column, Integer, String, Float, Date, DateTime, UUID, Text, func
from sqlalchemy.ext.declarative import declarative_base
import uuid
from .database import Base

# Base = declarative_base()

class CustomerList(Base):
    __tablename__ = 'customer_list'
    cust_id = Column(Integer, primary_key=True, autoincrement=True)
    branch_code = Column(String(36))  # `char(36)` in MySQL
    customer_number = Column(String(255))  # `varchar(255)` in MySQL
    customer_name = Column(String(255))  # `varchar(255)` in MySQL
    gender = Column(String(255))  # `varchar(255)` in MySQL
    phone_number = Column(String(255))  # `varchar(255)` in MySQL
    saving_account = Column(String(255))  # `varchar(255)` in MySQL
    business_tin = Column(String(255))  # `varchar(255)` in MySQL
    application_status = Column(String(255))  # `varchar(255)` in MySQL
    michu_loan_product = Column(String(255))  # `varchar(255)` in MySQL
    approved_amount = Column(Float)  # `float` in MySQL
    approved_date = Column(Date)  # `date` in MySQL
    expiry_date = Column(Date)  # `date` in MySQL
    oustanding_total = Column(Float)  # `float` in MySQL
    arrears_start_date = Column(Date)  # `date` in MySQL
    loan_status = Column(String(255))  # `varchar(255)` in MySQL
    created_date = Column(DateTime)  # `timestamp` in MySQL




class updatingData(Base):
    __tablename__="branchCollectionData"

    collectionID = Column(Integer, primary_key=True, autoincrement=True)
    cust_id= Column(Integer, nullable=False)
    branch_code = Column(String(36))  # `char(36)` in MySQL
    customer_name = Column(String(255))  # `varchar(255)` in MySQL
    phone_number = Column(String(255))  # `varchar(255)` in MySQL
    saving_account = Column(String(255))  # `varchar(255)` in MySQL
    application_status = Column(String(255))  # `varchar(255)` in MySQL
    michu_loan_product = Column(String(255))  # `varchar(255)` in MySQL
    approved_amount = Column(Float)  # `float` in MySQL
    approved_date = Column(Date)  # `date` in MySQL
    expiry_date = Column(Date)  # `date` in MySQL
    oustanding_total = Column(Float)  # `float` in MySQL
    paid_amount=Column(Float)
    loan_status = Column(String(255))  # `varchar(255)` in MySQL
    collectionStatus=Column(String(255))
    remark=Column(String(255), default="No remark given")
    created_date = Column(DateTime)  # `timestamp` in MySQL



# class AprilCollection(Base):
#     __tablename__ = 'apprilCollection'
    
#     collectionId = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
#     userId = Column(String(36))
#     customerName = Column(Text, nullable=True)
#     customerPhone = Column(Text, nullable=True)
#     customerAccount = Column(Text, nullable=True)
#     callResponce = Column(String(255))
#     paymentStatus = Column(String(255))
#     payedAmount = Column(Float)
#     date = Column(Date)

#     createdAt=Column(DateTime, default=func.now())
#     updatedAt=Column(DateTime, default=func.now())