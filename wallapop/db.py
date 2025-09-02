import os
import logging

from time import sleep
from sqlalchemy import create_engine, Column, String, Integer, Float, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import SQLAlchemyError, OperationalError

logger = logging.getLogger("wallapop")


DB_USER = os.environ.get("DATABASE_USER", "user")
DB_PASS = os.environ.get("DATABASE_PASSWORD", "password")
DB_HOST = os.environ.get("DATABASE_HOST", "127.0.0.1")
DB_NAME = os.environ.get("DATABASE_NAME", "wallapop")

DATABASE_URL = f"mariadb+mariadbconnector://{DB_USER}:{DB_PASS}@{DB_HOST}:3306/{DB_NAME}"

Base = declarative_base()


# class BaseProduct(Base):
#     __tablename__ = DB_NAME

#     title = Column(String(255))
#     price = Column(Float)
#     item_url = Column(String(255), primary_key=True)
#     description = Column(String(1024)) 
#     location = Column(String(255)) 
#     date = Column(DateTime)
#     user_id = Column(String(32))
#     user_reviews = Column(Integer)

def create_product_class(tablename):
    ProductClass = type(tablename, (Base,), {
        '__tablename__': tablename,
        '__table_args__': {'extend_existing': True},

        'title': Column(String(255)),
        'price': Column(Float),
        'item_url': Column(String(255), primary_key=True),
        'description': Column(String(1024)), 
        'location': Column(String(255)), 
        'date': Column(DateTime),
        'user_id': Column(String(32)),
        'user_reviews': Column(Integer)
    })
    return ProductClass

def insert_items(tablename, items):

    engine = create_engine(DATABASE_URL)
    tablename = tablename.lower()
    tablename = tablename.replace(" ", "_")
    ProductClass = create_product_class(tablename)

    try:
        Base.metadata.create_all(engine)
    except SQLAlchemyError as e:
        logger.error(f"Error creating database tables: {e}")
        sleep(5)
        return
    except OperationalError as e:
        logger.error(f"Database connection error: {e}")
        sleep(5)
        return
    Session = sessionmaker(bind=engine)
    session = Session()

    new_items = []

    for item in items:

        new_item = ProductClass(
            title = item['title'],
            price = item['price'],
            item_url = item['item_url'],
            description = item['description'],
            location = item['location'],
            date = item['date'], 
            user_id = item['user_id'],
            user_reviews = item['user_reviews']
        )

        new_item_in_db = session.query(ProductClass).filter_by(item_url=item['item_url']).first()
        if not new_item_in_db:
            try:
                new_items.append(item)
                session.add(new_item)
                session.commit()
            except SQLAlchemyError as e:
                logger.error(f"Error inserting Item: {e}")
                session.rollback()
                return
            except OperationalError as e:
                logger.error(f"Database connection error: {e}")
                session.rollback()
                return
            
            logger.debug(f"Inserted new Item: {item['title']}")
        else:
            if new_item_in_db.price != item['price']:
                new_item_in_db.price == item['price']
                logger.info(f"Item with title '{item['title']}' has changed its price from {new_item_in_db.price} to {item['price']}.")

            else:
                logger.debug(f"Item '{item['title']}' already exists. Skipping insertion.")
    
    session.commit()
    session.close()

    return new_items