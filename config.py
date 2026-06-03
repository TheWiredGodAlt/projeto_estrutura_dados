# config.py

# Configurações da aplicação Flask
class Config:
    # MySQL configurations - Troque 'senha' pela senha que você definiu durante a instalação!
    MYSQL_HOST = 'localhost'
    MYSQL_USER = 'root'
    MYSQL_PASSWORD = 'minhasenhasegura'  # 🔴 COLOCA A SENHA QUE VOCÊ DEFINIU PRA INSTALAÇÃO DO MYSQL 🔴
    MYSQL_DATABASE = 'estruturas_db'
    MYSQL_PORT = 3306
    MYSQL_DSN = f"mysql+mysqlconnector://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"