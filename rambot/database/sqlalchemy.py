from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker

from .models import BaseDocument

from contextlib import contextmanager
from loguru import logger

class SQLAlchemyConnection:
    """
    Manages database connections and operations using SQLAlchemy.
    
    This class handles database engine creation, session management, and table operations.
    It implements proper connection pooling and transaction handling with comprehensive error logging.
    
    Attributes:
        db_url (str): Database URL connection string
        echo (bool): Whether to enable SQLAlchemy engine logging
        pool_size (int): Number of connections in the connection pool
        engine: SQLAlchemy engine instance
        Session: Session maker bound to the engine
        metadata: SQLAlchemy MetaData object for table operations
        _tables (dict): Internal tracking of created tables
    
    Example:
        ```python
        database = SQLAlchemyConnection(url="sqlite:///example.db")
        ```
    """
    
    def __init__(self, url: str, echo: bool = False, pool_size: int = 5):
        """
        Initialize database connection settings.
        
        Args:
            db_url (str): Database URL connection string
            echo (bool): Whether to enable SQLAlchemy engine logging (default: False)
            pool_size (int): Number of connections in the connection pool (default: 5)
        """
        self.logger = logger
        
        self.db_url = url
        self.echo = echo
        self.pool_size = pool_size
        self.engine = create_engine(
            self.db_url,
            echo=self.echo,
            pool_size=self.pool_size,
            pool_timeout=30,
            pool_recycle=3600,
            connect_args={
                'check_same_thread': False
            }
        )
        self.Session = sessionmaker(
            bind=self.engine,
            autocommit=False,
            autoflush=True,
            expire_on_commit=False
        )
        self.metadata = MetaData()
        self._tables = {}
        
        self.logger.debug(f"Database connection established with URL: {self.db_url}")
    
    @contextmanager
    def session(self):
        """
        Context manager for handling database sessions.
        
        Ensures proper transaction management and session cleanup.
        It automatically creates tables if they do not exist and provides
        a session to interact with the database. The session is committed 
        if no exceptions occur and rolled back if an exception is raised.
        
        Yields:
            Session: SQLAlchemy session object to perform database operations.
            
        Raises:
            Exception: Any exception occurring during session operations, 
            which will cause the session to be rolled back.
        
        Example:
        ```python
        with database.session() as session:
            ...
        ```
        """
        try:
            BaseDocument.metadata.create_all(self.engine)
            self.logger.debug("Tables initiated successfully.")
        except Exception as e:
            self.logger.error(f"Error while creating tables: {str(e)}")
            raise
        
        self.logger.debug("Starting new database session.")
        session = self.Session()
        
        try:
            yield session
            
            session.commit()
            self.logger.debug("Transaction committed successfully.")
        except Exception as e:
            self.logger.error(f"Error during session operation: {str(e)}. Rolling back transaction.")
            session.rollback()
            raise
        finally:
            session.close()
            self.logger.debug("Session closed.")