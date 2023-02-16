from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine('sqlite:///data.db')

db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

Base = declarative_base()

Base.query = db_session.query_property()

def init_db():

    #TODO Here must define the modules that might define de models

    Base.metadata.create_all(bind=engine)
