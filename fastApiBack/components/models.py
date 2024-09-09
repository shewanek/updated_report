from sqlalchemy import Column, Integer, String, Float, Date, DateTime, UUID, Text, func, Enum, DECIMAL, Text, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base
import uuid

from sqlalchemy.dialects.mysql import CHAR

import enum
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


# Enums
class GenderEnum(str, enum.Enum):
    Male = 'Male'
    Female = 'Female'

class MaritalStatusEnum(str, enum.Enum):
    Unmarried = 'Unmarried'
    Married = 'Married'
    Divorced = 'Divorced'
    Widowed = 'Widowed'

class Kiyya(Base):
    __tablename__ = 'kiyya_customer'

    kiyya_id = Column(CHAR(36), primary_key=True)
    userId = Column(String(36))
    fullName = Column(String(255))
    phone_number = Column(String(36))
    account_number = Column(String(36))
    customer_ident_type = Column(String(255))
    gender = Column(Enum(GenderEnum))
    marital_status = Column(Enum(MaritalStatusEnum))
    date_of_birth = Column(Date)
    region = Column(String(255))
    zone_subcity = Column(String(255))
    woreda = Column(String(255))
    educational_level = Column(String(255))
    economic_sector = Column(String(255))
    line_of_business = Column(String(255))
    initial_working_capital = Column(DECIMAL(15, 2))
    source_of_initial_capital = Column(String(100))
    daily_sales = Column(DECIMAL(15, 2))
    purpose_of_loan = Column(Text)
    registered_date = Column(TIMESTAMP)
