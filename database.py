import mysql.connector
from mysql.connector import Error

class DatabaseHandler:
    def __init__(self, config):
        """
        Construtor da classe DatabaseHandler.
        Args:
            config (dict): Dicionário com as configurações de conexão do banco.
        """
        self.config = config
        self.connection = None
        self.cursor = None

    def connect(self):
        """Estabelece conexão com o MySQL e cria o banco e tabelas se não existirem."""
        try:
            # Configuração detalhada para conexão
            self.connection = mysql.connector.connect(
                host=self.config['host'],
                user=self.config['user'],
                password=self.config['password'],
                database=self.config['database'],
                port=self.config['port']
            )
            if self.connection.is_connected():
                self.cursor = self.connection.cursor(dictionary=True) # dictionary=True retorna resultados como dicionários, fica mais fácil de usar
                print("Conectado ao MySQL com sucesso!")
                self._setup_database() # Chama o método que cria as tabelas
                return self.connection
        except Error as e:
            print(f"Erro ao conectar ao MySQL: {e}")
            return None

    def _setup_database(self):
        """Cria as tabelas 'usuarios', 'logs_performance' e 'enderecos' se elas não existirem."""
        # Criação da tabela 'usuarios'
        create_usuarios_table = """
        CREATE TABLE IF NOT EXISTS usuarios (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nome VARCHAR(255) NOT NULL,
            email VARCHAR(255) NOT NULL UNIQUE,
            cpf VARCHAR(14) NOT NULL UNIQUE,
            data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        # Criação da tabela 'logs_performance'
        create_logs_performance_table = """
        CREATE TABLE IF NOT EXISTS logs_performance (
            id INT AUTO_INCREMENT PRIMARY KEY,
            cpf_buscado VARCHAR(14) NOT NULL,
            estrutura_usada VARCHAR(50) NOT NULL,
            tempo_segundos FLOAT NOT NULL,
            memoria_mb FLOAT NOT NULL,
            data_busca TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        # Criação da tabela 'enderecos' (para deixar nosso trabalho mais robusto)
        create_enderecos_table = """
        CREATE TABLE IF NOT EXISTS enderecos (
            id INT AUTO_INCREMENT PRIMARY KEY,
            usuario_id INT NOT NULL,
            logradouro VARCHAR(255) NOT NULL,
            numero VARCHAR(20),
            cidade VARCHAR(100) NOT NULL,
            estado VARCHAR(2) NOT NULL,
            cep VARCHAR(9),
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
        )
        """

        try:
            self.cursor.execute(create_usuarios_table)
            self.cursor.execute(create_logs_performance_table)
            self.cursor.execute(create_enderecos_table)
            self.connection.commit()
            print("Tabelas verificadas/criadas com sucesso!")
        except Error as e:
            print(f"Erro ao criar tabelas: {e}")

    def insert_usuario(self, nome, email, cpf):
        """Insere um novo usuário na tabela 'usuarios'."""
        query = "INSERT INTO usuarios (nome, email, cpf) VALUES (%s, %s, %s)"
        try:
            self.cursor.execute(query, (nome, email, cpf))
            self.connection.commit()
            return self.cursor.lastrowid
        except Error as e:
            print(f"Erro ao inserir usuário: {e}")
            self.connection.rollback()
            return None

    def get_usuario_by_cpf(self, cpf):
        """Busca um usuário na tabela 'usuarios' pelo CPF."""
        query = "SELECT * FROM usuarios WHERE cpf = %s"
        try:
            self.cursor.execute(query, (cpf,))
            return self.cursor.fetchone()
        except Error as e:
            print(f"Erro ao buscar usuário: {e}")
            return None

    def get_all_usuarios(self):
        """Retorna todos os usuários da tabela 'usuarios'."""
        query = "SELECT * FROM usuarios ORDER BY nome"
        try:
            self.cursor.execute(query)
            return self.cursor.fetchall()
        except Error as e:
            print(f"Erro ao listar usuários: {e}")
            return []

    def delete_usuario(self, user_id):
        """Deleta um usuário da tabela 'usuarios' pelo ID."""
        query = "DELETE FROM usuarios WHERE id = %s"
        try:
            self.cursor.execute(query, (user_id,))
            self.connection.commit()
            return self.cursor.rowcount > 0
        except Error as e:
            print(f"Erro ao deletar usuário: {e}")
            self.connection.rollback()
            return False

    def log_performance(self, cpf_buscado, estrutura_usada, tempo_segundos, memoria_mb):
        """Insere um log de desempenho na tabela 'logs_performance'."""
        query = """
        INSERT INTO logs_performance (cpf_buscado, estrutura_usada, tempo_segundos, memoria_mb)
        VALUES (%s, %s, %s, %s)
        """
        try:
            self.cursor.execute(query, (cpf_buscado, estrutura_usada, tempo_segundos, memoria_mb))
            self.connection.commit()
            return True
        except Error as e:
            print(f"Erro ao inserir log de performance: {e}")
            return False

    def get_performance_logs(self):
        """Retorna todos os logs de desempenho."""
        query = "SELECT * FROM logs_performance ORDER BY data_busca DESC"
        try:
            self.cursor.execute(query)
            return self.cursor.fetchall()
        except Error as e:
            print(f"Erro ao buscar logs de performance: {e}")
            return []

    def close(self):
        """Fecha a conexão com o banco de dados."""
        if self.cursor:
            self.cursor.close()
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("Conexão com MySQL encerrada.")