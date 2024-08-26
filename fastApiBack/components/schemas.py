from pydantic import BaseModel
from typing import List, Optional
from datetime import date, datetime

class CustomerList(BaseModel):
    cust_id: int
    branch_code: str
    customer_number: str
    customer_name: str
    gender: str
    phone_number: str
    saving_account: str
    business_tin: str
    application_status: str
    michu_loan_product: str
    approved_amount: float
    approved_date: date
    expiry_date: date
    oustanding_total: float
    arrears_start_date: Optional[date]
    loan_status: str
    created_date: datetime

    class Config:
        orm_mode = True


class addCollection(BaseModel):
    branch_code: str
    cust_id:int
    customer_name: str
    phone_number: str
    saving_account: str
    application_status: str
    michu_loan_product: str
    approved_amount: float
    approved_date: date
    expiry_date: date
    oustanding_total: float
    paid_amount:float
    # arrears_start_date: Optional[date]
    loan_status: str
    collectionStatus:str
    remark:str
    created_date: datetime

    class Config:
        orm_mode = True

class CollectionDetail(BaseModel):
    branch_code: str
    loan_status: str


class BranchCustomer(BaseModel):
    branch_code:list
    loan_status:str

class confirmCollection(BaseModel):
    collectionID:int
    cust_id:int
    oustanding_total:float
    collectionStatus:str
    loan_status:str
    remark:str


class apprilSchemas(BaseModel):
    # userId : str
    # customerName : str
    # customerPhone:int
    # customerAccount:str
    # callResponce : str
    # paymentStatus:str
    # payedAmount:float
    # date:date


    userId: str
    customerName: str = None
    customerPhone: int = None
    customerAccount: str = None
    callResponce: str =None
    paymentStatus: str =None
    payedAmount: float = None
    date: str 
    # createdAt:datetime
    # updatedAt:datetime