"""
Script principal que orquestra a coleta e armazenamento no banco.
Implementa as boas práticas de logging e retentativas.
"""
import logging
from datetime import datetime

from database import init_db, SessionLocal, Criptomoeda, HistoricoPreco
from api import get_cryptos

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

fh = logging.FileHandler('main.log')
fh.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)

def insert_data():
    """
    Inicializa o DB, obtém dados de criptomoedas e as insere/atualiza.
    """
    init_db()
    session = SessionLocal()
    try:
        logger.info("Coletando dados de criptomoedas (limit=10)...")
        
        # Ajuste 'limit', 'max_attempts', 'initial_delay' conforme necessidade
        cryptos = get_cryptos(limit=10, max_attempts=5, initial_delay=2)
        
        logger.info("Dados coletados. Iniciando inserção no banco.")
        for crypto in cryptos:
            cripto_obj = Criptomoeda(
                id=crypto['id'],
                symbol=crypto['symbol'],
                name=crypto['name'],
                price_usd=float(crypto['priceUsd']),
                market_cap_usd=float(crypto['marketCapUsd']),
                volume_usd_24hr=float(crypto['volumeUsd24Hr']),
                change_percent_24hr=float(crypto['changePercent24Hr']),
                last_updated=datetime.now()
            )
            session.merge(cripto_obj)

            historico = HistoricoPreco(
                crypto_id=crypto['id'],
                price_usd=float(crypto['priceUsd']),
                timestamp=datetime.now()
            )
            session.add(historico)

        session.commit()
        logger.info("Inserção finalizada com sucesso.")
    except Exception as e:
        session.rollback()
        logger.error(f"Erro durante a inserção de dados: {e}")
        raise
    finally:
        session.close()
        logger.info("Conexão com o banco encerrada.")

if __name__ == "__main__":
    try:
        insert_data()
    except Exception as e:
        logger.critical(f"Falha crítica no fluxo principal: {e}")
