from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from sqlalchemy.orm import Session
from typing import List
from . import models
from .database import get_db
from .  import schemas
from sqlalchemy.exc import SQLAlchemyError


router=APIRouter()


import logging

logger = logging.getLogger(__name__)

@router.get("/branchCustomer", status_code=status.HTTP_200_OK) 
def get_branch_customer(branch_code:int,db: Session = Depends(get_db)):
    try:
        customers = db.query(models.CustomerList).filter(
            models.CustomerList.cust_id == branch_code
        ).first()
        
        if not customers:
            raise HTTPException(status_code=404, detail="No customers found with the given branch code and loan status")
        
        return customers

    except SQLAlchemyError as e:
        logger.error(f"Database query failed: {e}")
        raise HTTPException(status_code=500, detail="Database query failed")
    except Exception as e:
        logger.error(f"An unexpected error occurred:{e}")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred")
    

@router.post("/activeBranchCustomer", status_code=status.HTTP_200_OK)
def get_active_branch_customer(branchData:schemas.BranchCustomer, db:Session=Depends(get_db)):
    try:
        branchStatCustomer= db.query(models.CustomerList).filter(
            models.CustomerList.branch_code.in_(branchData.branch_code),
            models.CustomerList.loan_status==branchData.loan_status
        ).all()

        if not branchStatCustomer:
            raise HTTPException(status_code=404, detail="Data doesn't exist")
        return branchStatCustomer
    except SQLAlchemyError as error:
        logger.error(f"Data base query failed: {str(error)}")

        raise HTTPException(status_code=500, detail="Data base query is failed")
    except Exception as e:
        logger.error(f"Something went wrong: {str(e)}" )
        raise HTTPException (status_code=500, detail=f"Something went wrong")
    

@router.post("/collection", status_code=status.HTTP_200_OK)
def addCollection(collectionData: schemas.addCollection, db: Session = Depends(get_db)):
    try:
        db_collection = models.updatingData( **collectionData.dict())

        db.add(db_collection)
        db.commit()
        db.refresh(db_collection)

        return {"success": True, "message": "Collection added successfully"}
        
    except SQLAlchemyError as e:
        logger.error(f"Database query failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Database query failed")
    except Exception as e:
        logger.error(f"The error:,{str(e)}")
        raise HTTPException(status_code=500, detail=f"Something went wrong: {str(e)}")





@router.post("/collectionDatas", status_code=status.HTTP_200_OK)
def get_collected_data(branch_codes: List[str]=Body(...), db: Session = Depends(get_db)):
    try:
        # Query for multiple branch codes using the `in_` clause
        collection_datas = db.query(models.updatingData).filter(models.updatingData.branch_code.in_(branch_codes)).all()

        if not collection_datas:
            raise HTTPException(status_code=404, detail="No collection data found for the given branch codes")

        return collection_datas

    except SQLAlchemyError as e:
        logger.error(f"Data query failed: {str(e)}")
        raise HTTPException(status_code=500, detail="An internal error occurred")

    except Exception as e:
        logger.error(f"An unexpected error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")

    


@router.patch("/collectionConfirmation", status_code=status.HTTP_200_OK)
def update_collection_data(data: schemas.confirmCollection, db: Session = Depends(get_db)):

    try:
        updating_data = db.query(models.updatingData).filter(models.updatingData.collectionID == data.collectionID).first()
        update_customer_list = db.query(models.CustomerList).filter(models.CustomerList.cust_id == data.cust_id).first()

        if not updating_data or not update_customer_list:
            raise HTTPException(status_code=404, detail="Unable to find the data with the given information")

        
        updating_data.collectionStatus = data.collectionStatus
        updating_data.loan_status = data.loan_status
        updating_data.remark = data.remark
        updating_data.oustanding_total=data.oustanding_total

        update_customer_list.loan_status = data.loan_status
        update_customer_list.oustanding_total = data.oustanding_total

        print("The data to be updated_____------__", data)
        db.commit()
        db.refresh(updating_data)

        return updating_data

    except SQLAlchemyError as e:
        logger.error(f"Database error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

    except Exception as e:
        logger.error(f"An unexpected error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail="Something went wrong")
    