from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Properties(Base):
    __tablename__ = 'properties'
    id = Column(Integer, primary_key=True)
    adress = Column(String)
    # available = Column(String)
    # property_type= Column(String)
    # estimate_value= Column(String)
    # img= Column(String)
    # listing_price= Column(String)
    # unit= Column(String)
    # bedrooms= Column(String)
    # coordinating= Column(String)
    # listing_status= Column(String)
    # bathrooms= Column(String)
    # living_area= Column(String)
    
if __name__ == '__main__':
    engine = create_engine('sqlite:///properties.db')
    Base.metadata.create_all(engine)
