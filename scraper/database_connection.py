from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import Session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import *

class DatabaseConnection:
    def __init__(self, db_url: str, echo: bool = False, pool_size: int = 5):
        self.db_url = db_url
        self.echo = echo
        self.pool_size = pool_size
        self.engine = None
        self.Session = None

    def __enter__(self) -> Session:
        self.engine = create_engine(self.db_url, echo=self.echo, pool_size=self.pool_size)
        
        self.Session = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
        self.session = self.Session()
        return self.session

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            self.session.close()
