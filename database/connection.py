from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import *
from sqlalchemy.orm import sessionmaker

from loguru import logger

import typing

from contextlib import contextmanager

Base = declarative_base()

class DatabaseConnection:
    def __init__(self, db_url: str, echo: bool = False, pool_size: int = 5):
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
                'check_same_thread': False  # Pour SQLite
            }
        )
        
        self.Session = sessionmaker(
            bind=self.engine,
            autocommit=False,
            autoflush=True,
            expire_on_commit=False
        )
        
        self.metadata = MetaData()
        self._tables = {}  # Cache des tables créées

    @contextmanager
    def session_scope(self):
        """Context manager pour la gestion des sessions."""
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
        Crée une table si elle n'existe pas dans la base de données.
        
        Args:
            model_class: Classe modèle SQLAlchemy à créer
            
        Raises:
            ValueError: Si le modèle n'a pas d'attribut __tablename__
        """
        if not hasattr(model_class, "__tablename__"):
            raise ValueError("Le modèle doit avoir un attribut __tablename__")
            
        table_name = model_class.__tablename__
        
        # Vérification si la table est déjà créée
        if table_name in self._tables:
            self.logger.debug(f"Table {table_name} déjà créée")
            return
            
        try:
            with self.engine.connect() as conn:
                context = conn.begin()
                try:
                    # Vérification si la table existe déjà dans la base
                    conn.execute(text(f"""
                        SELECT name FROM sqlite_master 
                        WHERE type='table' AND name=:table_name
                    """), {"table_name": table_name})
                    
                    # Création de la table si elle n'existe pas
                    if not conn.execute(text("""
                        SELECT name FROM sqlite_master 
                        WHERE type='table' AND name=:table_name
                    """), {"table_name": table_name}).fetchone():
                        Base.metadata.create_all(conn, tables=[model_class.__table__])
                        self._tables[table_name] = True
                        self.logger.info(f"Table {table_name} créée avec succès")
                    
                    context.commit()
                except Exception as e:
                    context.rollback()
                    self.logger.error(f"Erreur lors de la création de la table {table_name}: {str(e)}")
                    raise
        except Exception as e:
            self.logger.error(f"Erreur lors de la connexion à la base de données: {str(e)}")
            raise