import traceback

from fastapi import HTTPException, Depends, APIRouter
from address import models
from address.database import engine, SessionLocal
from sqlalchemy.orm import Session

from address.schema import Retrive, Address
import logging

# router creation
router = APIRouter(
    tags=["Address"],
    prefix='/address'
)

# Create and configure logger
logging.basicConfig(filename="newfile.log",
                    format='%(asctime)s: %(levelname)s :-  %(message)s',
                    filemode='a+')

# Creating an object
logger = logging.getLogger()

# Setting the threshold of logger to DEBUG
logger.setLevel(logging.DEBUG)

# for first time when database is not there it will create
models.Base.metadata.create_all(bind=engine)


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


@router.get("/")
def get_address(db: Session = Depends(get_db)):
    '''

    :param db:
    :return: All the address record present in our database
    '''
    try:
        # querying the db for all records.
        logger.info("Inside get all adress")
        data = db.query(models.Address).all()
        logger.debug("Successfully fetched the records")
        return data
    except Exception as e:
        logger.error("Server error " + str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Not able to fetch data at this moment, please try after some time"
        )


@router.post("/")
def create_address(address: Address, db: Session = Depends(get_db)):
    '''
    This function will add one record of address to db
    :param address: coming from schema for validation of input
    :param db:
    :return: address data
    '''
    try:
        logger.debug("Inside creating new adress")
        # creating the instace of Address class to insert data
        address_book_model = models.Address()
        address_book_model.name = address.name
        address_book_model.zipcode = address.zipcode
        address_book_model.longitude = address.longitude
        address_book_model.latitude = address.latitude

        db.add(address_book_model)
        db.commit()
        logger.debug("Successfully added the address")
        return address
    except Exception as e:
        logger.error("Server error " + str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Not able to Add New Address at this Moment ! "
        )


@router.post("/bulk-upload-address")
def add_bulk_address(db: Session = Depends(get_db)):
    '''
    This function is used for adding all the data from dataset at single shot, where data is stored in form of
    list of tuple.
    e.g. ("Air Force Hospital", 560007, 12.963637, 77.62905)
    inside dataset data is present for karnatka city only
    :param db:
    :return:
    '''
    try:
        logger.debug("Inside Bulk upload of adress")
        # taking the data from dataset and iterate over it and insert one by one
        from address.dataset import data
        for each in data:
            address_book_model = models.Address()
            address_book_model.name = each[0]
            address_book_model.zipcode = each[1]
            address_book_model.longitude = each[2]
            address_book_model.latitude = each[3]

            db.add(address_book_model)
            db.commit()
            logger.debug("successfully upload all the records of address")
        return {"message": "Data Added successfully !!"}
    except Exception as e:
        logger.error("error while uploading the data " + str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Not able to Add New Address at this Moment ! "
        )


@router.put("/{address_id}")
def update_address(address_id: int, address: Address, db: Session = Depends(get_db)):
    '''
    This is used for updating any single record from address book
    :param address_id: id
    :param address: data to be being updated with
    :param db:
    :return: address
    '''
    try:
        logger.debug("Inside update of adress")
        # fetching the first matching records from db
        address_book_model = db.query(models.Address).filter(models.Address.id == address_id).first()

        if address_book_model is None:
            logger.error("Not able to find the specific address")
            raise HTTPException(
                status_code=404,
                detail=f"ID {address_id} : Does not exist"
            )

        address_book_model.name = address.name
        address_book_model.zipcode = address.zipcode
        address_book_model.longitude = address.longitude
        address_book_model.latitude = address.latitude

        db.add(address_book_model)
        db.commit()
        logger.debug("Successfully updated the address")
        return address
    except Exception as e:
        logger.error("error while updating the address " + str(e))
        raise HTTPException(
            status_code=404,
            detail=f"ID Does not exist"
        )


@router.delete("/{address_id}")
def delete_book(address_id: int, db: Session = Depends(get_db)):
    '''
    This function is used for deleting any records from our address record
    :param address_id: id
    :param db:
    :return: message
    '''
    try:
        logger.debug("Inside delete adress")
        book_model = db.query(models.Address).filter(models.Address.id == address_id).first()

        if book_model is None:
            logger.error("Not able to locate the address we are deleting for")
            raise HTTPException(
                status_code=404,
                detail=f"ID {address_id} : Does not exist"
            )

        # deleting the records if it is present in our db
        db.query(models.Address).filter(models.Address.id == address_id).delete()

        db.commit()
        logger.debug("successfully deleted the address")
        return {"message": "Successfully Deleted address"}
    except Exception as e:
        logger.error("Error while deleting the address " + str(e))
        raise HTTPException(
            status_code=404,
            detail=f"ID  : Does not exist"
        )


@router.post("/retrive")
def retrive_address_within_radius(input_json: Retrive, db: Session = Depends(get_db)):
    '''
    retrive function is mainly used for getting all the address from a center point within a range
    which is radius from a location
    :param input_json: comes from schema where we need radius, long, lat
    eg. radius = 5, in kms
        long = 12.813337,
        lat = 77.578951
    :param db:
    :return: All address within a limited radius.
    '''
    try:
        logger.debug("Inside retrieving all addresses nearby")

        from geopy import distance

        # querying db for all records
        addresses = db.query(models.Address).all()

        # fetching the input data
        radius = input_json.radius
        center_lat = input_json.latitude
        center_long = input_json.longitude

        final_addresses = list()
        for each in addresses:
            center_point_tuple = (each.latitude, each.longitude)
            test_point_tuple = (center_lat, center_long)

            # inbuilt function used for calculating the distance between two cordinates.
            dis = distance.distance(center_point_tuple, test_point_tuple).km
            print("Distance: {}".format(dis))

            # if it statisfies the condition we will push that specific address
            if dis <= radius:
                print("{} point is inside the {} km radius from {} coordinate".format(test_point_tuple, radius,
                                                                                      center_point_tuple))
                temp_dict = {
                    "id": each.id,
                    "name": each.name,
                    "longitude": each.longitude,
                    "latitude": each.latitude,
                    "zipcode": each.zipcode
                }
                final_addresses.append(temp_dict)
        logger.debug("successfully retrived all nearby adress")
        return final_addresses
    except Exception as e:
        logger.error("Error while retrival of nearby addr " + str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Not able to retrive Address at this Moment ! "
        )
