from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Usamos SQLite. Esto creará un archivo llamado "upway_comercios.db" en tu servidor.
# El día de mañana, si quieres pasar a un servidor gigante de PostgreSQL, 
# literalmente solo cambias esta línea de abajo.
SQLALCHEMY_DATABASE_URL = "sqlite:///./upway_comercios.db"

# connect_args={"check_same_thread": False} es necesario solo para SQLite en FastAPI
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# Esta es la fábrica de sesiones (cada vez que un cliente escriba, abrimos una sesión)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Esta es la clase base de la que heredarán nuestras tablas
Base = declarative_base()