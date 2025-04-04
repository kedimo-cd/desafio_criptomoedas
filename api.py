"""
Módulo responsável pela comunicação com a API externa de criptomoedas,
com retentativa em caso de erro 429, usando exponential backoff + jitter.
"""
import requests
import logging
import time
import random

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

fh = logging.FileHandler('api.log')
fh.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)

BASE_URL = "https://api.coincap.io/v2/assets"

def get_cryptos(limit=10, max_attempts=5, initial_delay=2):
    """
    Faz requisições à CoinCap para obter 'limit' criptomoedas.
    Implementa retentativa com exponential backoff + jitter em caso de erro 429.
    
    Args:
        limit (int): Quantidade de criptomoedas a buscar na API.
        max_attempts (int): Número máximo de tentativas antes de falhar.
        initial_delay (int): Tempo (em segundos) base para a primeira espera.
                             Este valor é multiplicado por (2^(tentativa-1)).
    Returns:
        data (list): Lista de dicionários com dados das criptomoedas.
    Raises:
        Exception: Se após todas as tentativas ainda falhar.
    """
    url = f"{BASE_URL}?limit={limit}"

    for attempt in range(1, max_attempts + 1):
        try:
            response = requests.get(url)
            response.raise_for_status()  # dispara exceção se status != 200
            data = response.json()["data"]
            logger.info(f"Sucesso ao obter {len(data)} criptomoedas (tentativa {attempt}).")
            return data
        except requests.exceptions.HTTPError as http_error:
            # Se erro 429, aguarda e tenta novamente, até max_attempts
            if response.status_code == 429 and attempt < max_attempts:
                # Exponential backoff + jitter
                wait_time = (initial_delay * (2 ** (attempt - 1))) + random.uniform(0, 3)
                logger.warning(
                    f"429 Too Many Requests. Tentativa {attempt}/{max_attempts}. "
                    f"Aguardando {wait_time:.1f}s antes de nova tentativa."
                )
                time.sleep(wait_time)
            else:
                logger.error(f"Erro HTTP ao obter dados da API: {http_error}")
                raise
        except Exception as e:
            logger.error(f"Erro inesperado ao chamar a API: {e}")
            raise

    # Se chegar aqui, significa que todas as tentativas falharam
    raise Exception("Falha ao obter dados da API após múltiplas tentativas.")
