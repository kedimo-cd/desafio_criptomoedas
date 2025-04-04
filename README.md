# Desafio Técnico - Coleta e Armazenamento de Dados de Criptomoedas

Este projeto tem como objetivo consumir dados de criptomoedas da **API pública da CoinCap**, armazenar as informações em um **banco de dados MySQL** e disponibilizar um esquema que permita análise em ferramentas de Business Intelligence (BI), como **Looker**, **Power BI** ou **Tableau**.

---

## 1. O que este projeto faz?

- **Consulta** a API da CoinCap em busca de informações sobre criptomoedas (preço atual, capitalização de mercado, volume, etc.).
- **Gerencia possíveis limitações** de acesso da API (código 429 - Too Many Requests), usando retentativas.
- **Armazena** esses dados em duas tabelas relacionadas no **MySQL**:
- **criptomoedas**: dados principais de cada cripto.
- **historico_precos**: histórico de preços com timestamp.
- **Gera logs** em arquivos separados para facilitar o monitoramento de cada etapa do processo (coleta, inserção e possíveis erros).

---

## 2. Como usar este projeto?

### Passo 1: Clonar o repositório

1. Abra seu terminal na pasta onde deseja clonar o projeto.
2. Execute:
   ```bash
   git clone <Uhttps://github.com/kedimo-cd/desafio_criptomoedas.git>
   cd <NOME_DA_PASTA_CLONADA>
   ```

### 2: Configurar o Ambiente Virtual

1. **Crie e ative** o ambiente virtual (você deve ter o Python instalado):
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
2. **Instale as dependências** listadas em `requirements.txt`:
   ```bash
   pip install -r requirements.txt
   ```

---

## 3: Preparar o Banco de Dados MySQL

- Verifique se o MySQL está instalado ou use Docker Compose.
- Entre no MySQL como root:
  ```bash
  sudo mysql -u root
  ```
- Crie o banco e o usuário:
  ```sql
  CREATE DATABASE crypto_db;
  CREATE USER 'crypto_user'@'localhost' IDENTIFIED BY 'Km12345';
  GRANT ALL PRIVILEGES ON crypto_db.* TO 'crypto_user'@'localhost';
  FLUSH PRIVILEGES;
  EXIT;
  ```
- **OBS**: Caso utilize Docker Compose para subir o MySQL, verifique o nome do host e da porta no `docker-compose.yml` e atualize no `.env`, se necessário.

---

## 4: Executar o Script de Coleta

Na raiz do projeto, com o ambiente virtual **ativo**:
```bash
python main.py
```
- Se tudo ocorrer bem, o script se conectará à API, criará as tabelas e armazenará os dados no MySQL.

## Passo 5: Conferir Logs e Dados

- Arquivos de log como `main.log`, `api.log` e `database.log` são gerados para cada módulo.
- Se o script rodar sem erros, eles incluirão mensagens de sucesso; se houver falhas, aparecerão mensagens de aviso ou erro.

Para verificar manualmente no MySQL:
```sql
USE crypto_db;
SELECT * FROM criptomoedas;
SELECT * FROM historico_precos;
```

---

## 3. Estrutura do Projeto

A pasta raiz do projeto contém:

- **`main.py`**: script principal que inicia a coleta e armazenagem.
- **`api.py`**: funções para acessar a API da CoinCap com retentativas (lida com erro 429).
- **`database.py`**: configuração do SQLAlchemy, modelos de tabelas e criação do banco.
- **`.env`**: variáveis de ambiente para credenciais do banco.
- **`requirements.txt`**: dependências do projeto.
- **`docker-compose.yml`** (opcional): subir o MySQL via Docker.
- **Arquivos de log** (criados após a execução).

---

## 4. Modelagem do Banco

### `criptomoedas`
- **id** (PK)  
- **symbol**, **name**, **price_usd**, **market_cap_usd**, **volume_usd_24hr**, **change_percent_24hr**, **last_updated**

### `historico_precos`
- **id** (PK auto-increment)  
- **crypto_id** (FK para `criptomoedas.id`)  
- **price_usd**, **timestamp**

Essa estrutura cria um relacionamento **1 -> N** (uma criptomoeda pode ter vários registros de histórico). Assim, no campo **`crypto_id`** de `historico_precos`, armazenamos qual cripto aquele histórico representa. Esse modelo garante:

- **Integridade referencial**: não pode existir um histórico sem uma criptomoeda correspondente.
- **Escalabilidade**: podemos registrar quantos registros de histórico quisermos, sem duplicar dados da cripto.

---

## 5. Estratégia Contra Erros 429

No arquivo **`api.py`**, foi implementada uma lógica de **retentativas** caso a API retorne código **429 Too Many Requests**. Isso inclui:

- **Exponential Backoff**: aumento progressivo do tempo de espera a cada tentativa falha.
- **Jitter**: adição de um intervalo aleatório, evitando que várias requisições fiquem sincronizadas.

Se você receber muitas vezes o erro 429, experimente:

- **Diminuir a frequência** de execução do script (por exemplo, rodar de hora em hora).
- **Reduzir o número de criptomoedas** requisitadas.
- **Aguardar** alguns minutos antes de rodar novamente.

---

## Dicas Adicionais

- **Automatização**: Use o `cron` (Linux) ou `Task Scheduler` (Windows) para agendar o comando `python main.py` e coletar dados regularmente, semelhante ao que seria o cloud scheduler no GCP.
- **Dashboard**: É possivel conectar uma ferramenta de BI (Looker, Power BI) ao banco para criar visualizações e relatórios.
- **Outros Bancos**: Se desejar usar outro SGBD (PostgreSQL, por exemplo), basta alterar a URL de conexão no `database.py`.

---

**Muito Obrigado!**

