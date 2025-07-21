from sqlalchemy import create_engine, Column, Float, Integer, DateTime # Importar DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func

# Definición de la base declarativa
Base = declarative_base()

# Modelo de la tabla para las coordenadas
class DBCoordinate(Base):
    """
    Modelo de la base de datos para almacenar coordenadas.
    Se mapea a la tabla 'coordinates'.
    """
    __tablename__ = "coordinates"
    id = Column(Integer, primary_key=True, index=True)
    lat = Column(Float, nullable=False)
    lng = Column(Float, nullable=False)
    # Corregido: El primer argumento de Column debe ser el tipo de dato (DateTime)
    # func.now() se usa como el valor por defecto
    created_at = Column(DateTime, nullable=False, default=func.now())

# Configuración de la URL de la base de datos SQLite
# El archivo 'coordinates.db' se creará dentro de 'app/core/'
DATABASE_URL = "sqlite:///./app/core/coordinates.db"

# Crea un motor de base de datos. 'check_same_thread=False' es necesario para SQLite
# cuando se usa con FastAPI, ya que SQLite por defecto permite una sola thread a la vez.
engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)

# Crea una instancia de sesión para interactuar con la base de datos
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_db_tables():
    """
    Crea las tablas de la base de datos si no existen.
    Esta función debe llamarse al inicio de la aplicación.
    """
    print("Creando tablas de la base de datos...")
    Base.metadata.create_all(bind=engine)
    print("Tablas de la base de datos creadas/verificadas.")

def get_db():
    """
    Dependencia para obtener una sesión de base de datos.
    Cierra la sesión después de que la solicitud haya sido procesada.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

