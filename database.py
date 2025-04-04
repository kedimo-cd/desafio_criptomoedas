"""
Módulo responsável pela configuração do banco de dados e pelos modelos.
"""
import os
import logging
from sqlalchemy import create_engine, Column, String, Float, TIMESTAMP, ForeignKey, Integer
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

load_dotenv()

# Configura logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

fh = logging.FileHandler('database.log')
fh.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)

DB_USER = os.getenv('DB_USER')
DB_PASS = os.getenv('DB_PASS')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_NAME = os.getenv('DB_NAME')

DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class Criptomoeda(Base):
    __tablename__ = 'criptomoedas'
    id = Column(String(100), primary_key=True)
    symbol = Column(String(20))
    name = Column(String(100))
    price_usd = Column(Float)
    market_cap_usd = Column(Float)
    volume_usd_24hr = Column(Float)
    change_percent_24hr = Column(Float)
    last_updated = Column(TIMESTAMP)

class HistoricoPreco(Base):
    __tablename__ = 'historico_precos'
    id = Column(Integer, primary_key=True, autoincrement=True)
    crypto_id = Column(String(100), ForeignKey('criptomoedas.id'))
    price_usd = Column(Float)
    timestamp = Column(TIMESTAMP)

def init_db():
    """
    Inicializa o banco de dados, criando as tabelas se não existirem.
    """
    try:
        Base.metadata.create_all(engine)
        logger.info("Banco de dados inicializado ou já existente.")
    except Exception as e:
        logger.error(f"Erro ao criar tabelas: {e}")
        raise
