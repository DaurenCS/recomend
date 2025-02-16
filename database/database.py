from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base



DATABASE_URL = "postgresql://neondb_owner:npg_MQ2kgJfDh6CK@ep-summer-snowflake-a2wqcz10-pooler.eu-central-1.aws.neon.tech/neondb"
engine = create_engine(DATABASE_URL)

Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
session = Session()




Base = declarative_base()


Base.metadata.create_all(engine)