from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float

engine = create_engine("postgresql://admin:password@localhost/testdb")
Base = declarative_base()


class Restaurant(Base):
    __tablename__ = 'restaurants'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    longitude = Column(Float)
    latitude = Column(Float)
    description = Column(String, nullable=True)


def import_restaurant():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    sess = Session(engine)
    sess.add(Restaurant(id=1, name='ff', longitude=5.2, latitude=2.3))
    sess.commit()
