from flask import Flask, request, render_template, jsonify, redirect, url_for
from flask_cors import CORS
import json
import time

from config import Config
from database import DatabaseHandler
from performance import PerformanceMonitor

app = Flask(__name__)
CORS(app) # Habilita CORS para comunicação entre frontend e backend

# Configuração do banco de dados
db_config = {
    'host': Config.MYSQL_HOST,
    'user': Config.MYSQL_USER,
    'password': Config.MYSQL_PASSWORD,
    'database': Config.MYSQL_DATABASE,
    'port': Config.MYSQL_PORT
}

# Inicializa o manipulador do banco e o monitor de performance
db_handler = DatabaseHandler(db_config)
perf_monitor = PerformanceMonitor()

# Dicionário em memória (Tabela Hash) para simular a estrutura de dados rápida
# Vamos popular com os mesmos dados do banco de dados na inicialização
hash_table = {}

# Conecta ao banco e cria as tabelas
db_connection = db_handler.connect()

def carregar_hash_table():
    """Carrega todos os dados do banco de dados para a hash table."""
    global hash_table
    hash_table.clear()
    usuarios = db_handler.get_all_usuarios()
    for usuario in usuarios:
        hash_table[usuario['cpf']] = usuario
    print(f"Hash table carregada com {len(hash_table)} usuários.")

# Tenta carregar a hash table se a conexão foi bem-sucedida
if db_connection:
    carregar_hash_table()
else:
    print("Erro: Não foi possível conectar ao banco de dados. A hash table não foi carregada.")

# --- ROTAS DA APLICAÇÃO ---

@app.route('/')
def index():
    """Página inicial (Dashboard)."""
    return render_template('index.html')

@app.route('/cadastro')
def cadastro():
    """Página de cadastro de usuários."""
    return render_template('cadastro.html')

@app.route('/gerenciar')
def gerenciar():
    """Página de gerenciamento de usuários."""
    return render_template('gerenciar.html')

# --- API ENDPOINTS (COMUNICAÇÃO FRONTEND <-> BACKEND) ---

@app.route('/api/cadastrar', methods=['POST'])
def api_cadastrar():
    """API para cadastrar um novo usuário."""
    data = request.get_json()
    nome = data.get('nome')
    email = data.get('email')
    cpf = data.get('cpf')

    if not all([nome, email, cpf]):
        return jsonify({'success': False, 'message': 'Todos os campos são obrigatórios.'}), 400

    # Insere no banco de dados (B-Tree)
    user_id = db_handler.insert_usuario(nome, email, cpf)

    if user_id:
        # Insere na hash table também (para manter a consistência)
        novo_usuario = {'id': user_id, 'nome': nome, 'email': email, 'cpf': cpf}
        hash_table[cpf] = novo_usuario
        return jsonify({'success': True, 'message': 'Usuário cadastrado com sucesso!'})
    else:
        return jsonify({'success': False, 'message': 'Erro ao cadastrar usuário. CPF ou e-mail podem já existir.'}), 500

@app.route('/api/buscar', methods=['GET'])
def api_buscar():
    """API para buscar um usuário pelo CPF, comparando Hash Table vs MySQL."""
    cpf = request.args.get('cpf')
    if not cpf:
        return jsonify({'error': 'CPF não fornecido'}), 400

    # 1. BUSCA NA HASH TABLE (em memória)
    hash_result = hash_table.get(cpf)
    hash_time = -1
    hash_memory = -1
    if hash_result:
        # Mede tempo e memória da busca na hash table
        def busca_hash():
            return hash_table.get(cpf)
        resultado_hash, tempo_hash, memoria_hash = perf_monitor.measure_time_and_memory(busca_hash)
        hash_time = tempo_hash
        hash_memory = memoria_hash
        db_handler.log_performance(cpf, 'hash_table', hash_time, hash_memory)

    # 2. BUSCA NO MySQL (B-Tree)
    # Mede tempo e memória da busca no MySQL
    def busca_mysql():
        return db_handler.get_usuario_by_cpf(cpf)
    resultado_mysql, tempo_mysql, memoria_mysql = perf_monitor.measure_time_and_memory(busca_mysql)
    db_handler.log_performance(cpf, 'mysql_btree', tempo_mysql, memoria_mysql)

    # Prepara a resposta para o frontend
    response = {
        'hash_result': hash_result,
        'hash_time': hash_time,
        'hash_memory': hash_memory,
        'mysql_result': resultado_mysql,
        'mysql_time': tempo_mysql,
        'mysql_memory': memoria_mysql
    }

    return jsonify(response)

@app.route('/api/usuarios', methods=['GET'])
def api_listar_usuarios():
    """API para listar todos os usuários."""
    usuarios = db_handler.get_all_usuarios()
    return jsonify(usuarios)

@app.route('/api/deletar/<int:user_id>', methods=['DELETE'])
def api_deletar_usuario(user_id):
    """API para deletar um usuário pelo ID."""
    # Primeiro, busca o usuário para pegar o CPF e remover da hash table
    all_users = db_handler.get_all_usuarios()
    cpf_to_remove = None
    for user in all_users:
        if user['id'] == user_id:
            cpf_to_remove = user['cpf']
            break

    # Deleta do banco de dados
    success = db_handler.delete_usuario(user_id)
    if success and cpf_to_remove:
        # Remove da hash table também
        hash_table.pop(cpf_to_remove, None)
        return jsonify({'success': True, 'message': 'Usuário deletado com sucesso!'})
    else:
        return jsonify({'success': False, 'message': 'Erro ao deletar usuário.'}), 500

@app.route('/api/logs', methods=['GET'])
def api_logs():
    """API para obter os logs de desempenho."""
    logs = db_handler.get_performance_logs()
    return jsonify(logs)

if __name__ == '__main__':
    app.run(debug=True, port=5000)