from sqlalchemy import *
from sqlalchemy.orm import sessionmaker

from .models import BaseDocument

from contextlib import contextmanager
from loguru import logger


class DatabaseConnection:
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
    """
    
    def __init__(self, db_url: str, echo: bool = False, pool_size: int = 5):
        """
        Initialize database connection settings.
        
        Args:
            db_url (str): Database URL connection string
            echo (bool): Whether to enable SQLAlchemy engine logging (default: False)
            pool_size (int): Number of connections in the connection pool (default: 5)
        """
        self.logger = logger
        self.db_url = db_url
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
    
    @contextmanager
    def session_scope(self):
        """
        Context manager for database session handling.
        
        Ensures proper transaction management and session cleanup.
        
        Yields:
            Session: SQLAlchemy session object
            
        Raises:
            Exception: Any exception occurring during session operations
        """
        session = self.Session()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def create_table(self, model_class) -> None:
        """
        Create a database table if it doesn't exist.
        
        Args:
            model_class: SQLAlchemy model class containing __tablename__
            
        Raises:
            ValueError: If model_class doesn't have __tablename__ attribute
            Exception: If table creation fails
            
        Notes:
            Uses atomic transactions for thread safety and maintains an internal
            tracking of created tables to prevent duplicate creation attempts.
        """
        if not hasattr(model_class, "__tablename__"):
            raise ValueError("Model must have __tablename__ attribute")
        
        table_name = model_class.__tablename__
        if table_name in self._tables:
            self.logger.debug(f"Table {table_name} already exists")
            return
        
        try:
            with self.engine.connect() as conn:
                context = conn.begin()
                try:
                    # Check if table exists
                    conn.execute(text(f"""
                        SELECT name FROM sqlite_master 
                        WHERE type='table' AND name=:table_name
                    """), {"table_name": table_name})
                    
                    if not conn.execute(text("""
                        SELECT name FROM sqlite_master 
                        WHERE type='table' AND name=:table_name
                    """), {"table_name": table_name}).fetchone():
                        BaseDocument.metadata.create_all(conn, tables=[model_class.__table__])
                        self._tables[table_name] = True
                        self.logger.debug(f"Table {table_name} created successfully")
                    context.commit()
                except Exception as e:
                    context.rollback()
                    self.logger.error(f"Error creating table {table_name}: {str(e)}")
                    raise
        except Exception as e:
            self.logger.error(f"Error connecting to database: {str(e)}")
            raise