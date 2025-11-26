from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
# Necessário para criptografar senhas de forma segura
import bcrypt 

# ----------------- CONFIGURAÇÃO BASE -----------------
app = Flask(__name__)
# Configura o banco de dados SQLite (cria o arquivo 'site.db')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'uma_chave_secreta_muito_segura' # Chave para criptografar sessões
db = SQLAlchemy(app)

# ----------------- MODELO DO BANCO DE DADOS -----------------
# Classe 'User' representa a tabela no banco de dados.
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    # Vamos armazenar o HASH da senha, e NÃO a senha pura!
    password_hash = db.Column(db.String(128), nullable=False) 
    
    def __repr__(self):
        return f'User("{self.username}")'


class Noticia(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    def __repr__(self):
        return f'Noticia("{self.title}")'

# ----------------- FUNÇÃO DE CRIPTOGRAFIA DE SENHA -----------------
def hash_password(password):
    # Gera um "salt" (valor aleatório) para garantir a segurança.
    salt = bcrypt.gensalt()
    # Codifica a senha em bytes e a hasheia
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password.decode('utf-8') # Decodifica de volta para string

# ----------------- ROTAS DA APLICAÇÃO -----------------

# Rota para a página de perfil (acesso restrito)
@app.route('/perfil')
def perfil():
    # Verifica se o ID do usuário está na sessão. Se não estiver, redireciona.
    if 'user_id' not in session:
        return redirect(url_for('index'))
    
    # Busca o objeto User pelo ID armazenado na sessão
    user = User.query.get(session['user_id'])
    user_count = User.query.count()
    # Renderiza a página do perfil com um painel bonito
    return render_template('perfil.html', user=user, user_count=user_count)


@app.route('/perfil/editar', methods=['POST'])
def editar_perfil():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    user = User.query.get(session['user_id'])
    new_username = request.form.get('new_username')
    if not new_username:
        return redirect(url_for('perfil'))
    # Evita duplicação de username
    if User.query.filter_by(username=new_username).first():
        return 'Erro: nome de usuário já existe.', 409
    try:
        user.username = new_username
        db.session.commit()
        return redirect(url_for('perfil'))
    except Exception as e:
        db.session.rollback()
        return f'Erro ao atualizar: {e}', 500

# Rota para deslogar o usuário
@app.route('/logout')
def logout():
    session.pop('user_id', None) # Remove 'user_id' da sessão
    return redirect(url_for('index'))


@app.route('/criar_noticia', methods=['POST'])
def criar_noticia():
    title = request.form.get('title')
    content = request.form.get('content')
    # Only admin (username 'admin') can create news
    if 'user_id' not in session:
        user_logged = None
        noticias = Noticia.query.order_by(Noticia.created_at.desc()).limit(10).all()
        return render_template('cadastro.html', user_logged=user_logged, error_msg='Apenas administradores podem publicar notícias.', noticias=noticias)
    user = User.query.get(session['user_id'])
    if user.username != 'admin':
        noticias = Noticia.query.order_by(Noticia.created_at.desc()).limit(10).all()
        return render_template('cadastro.html', user_logged=user, error_msg='Apenas administradores podem publicar notícias.', noticias=noticias)
    if not title or not content:
        # Re-render index with an error
        user_logged = None
        if 'user_id' in session:
            user_logged = User.query.get(session['user_id'])
        noticias = Noticia.query.order_by(Noticia.created_at.desc()).limit(10).all()
        return render_template('cadastro.html', user_logged=user_logged, error_msg='Preencha título e conteúdo!', noticias=noticias)
    try:
        n = Noticia(title=title, content=content)
        db.session.add(n)
        db.session.commit()
        user_logged = None
        if 'user_id' in session:
            user_logged = User.query.get(session['user_id'])
        noticias = Noticia.query.order_by(Noticia.created_at.desc()).limit(10).all()
        return render_template('cadastro.html', user_logged=user_logged, success_msg='Notícia publicada!', noticias=noticias)
    except Exception as e:
        db.session.rollback()
        user_logged = None
        if 'user_id' in session:
            user_logged = User.query.get(session['user_id'])
        noticias = Noticia.query.order_by(Noticia.created_at.desc()).limit(10).all()
        return render_template('cadastro.html', user_logged=user_logged, error_msg='Erro ao publicar notícia.', noticias=noticias)

# Rota de visualização inicial e cadastro
@app.route('/')
def index():
    # Verifica se o usuário já está logado para passar essa informação para o template
    user_logged = None
    if 'user_id' in session:
        user_logged = User.query.get(session['user_id'])
    # Fetch latest noticias to show on the page
    noticias = None
    try:
        noticias = Noticia.query.order_by(Noticia.created_at.desc()).limit(10).all()
    except Exception:
        noticias = []
    # Passa o objeto do usuário logado (ou None) para o template
    return render_template('cadastro.html', user_logged=user_logged, noticias=noticias)

# Rota que recebe os dados do formulário de cadastro (POST)
@app.route('/cadastrar', methods=['POST'])
def cadastrar():
    username = request.form.get('username')
    password = request.form.get('password')

    # 1. Validação básica
    if not username or not password:
        user_logged = None
        if 'user_id' in session:
            user_logged = User.query.get(session['user_id'])
        noticias = Noticia.query.order_by(Noticia.created_at.desc()).limit(10).all()
        return render_template('cadastro.html', user_logged=user_logged, error_msg='Preencha todos os campos!', noticias=noticias)

    # 2. Verifica se o usuário já existe
    if User.query.filter_by(username=username).first():
        user_logged = None
        if 'user_id' in session:
            user_logged = User.query.get(session['user_id'])
        noticias = Noticia.query.order_by(Noticia.created_at.desc()).limit(10).all()
        return render_template('cadastro.html', user_logged=user_logged, error_msg=f'Erro: O usuário "{username}" já está cadastrado.', noticias=noticias)

    # 3. Criptografa a senha antes de salvar
    hashed_pw = hash_password(password)
    
    # 4. Cria e salva o novo usuário
    novo_usuario = User(username=username, password_hash=hashed_pw)
    
    try:
        db.session.add(novo_usuario)
        db.session.commit()
        # Em vez de redirecionar, renderizamos a mesma tela com uma mensagem de sucesso
        user_logged = None
        if 'user_id' in session:
            user_logged = User.query.get(session['user_id'])
        noticias = Noticia.query.order_by(Noticia.created_at.desc()).limit(10).all()
        return render_template('cadastro.html', user_logged=user_logged, success_msg='Conta criada com sucesso! Você já pode fazer login.', noticias=noticias)
    except Exception as e:
        db.session.rollback()
        user_logged = None
        if 'user_id' in session:
            user_logged = User.query.get(session['user_id'])
        noticias = Noticia.query.order_by(Noticia.created_at.desc()).limit(10).all()
        return render_template('cadastro.html', user_logged=user_logged, error_msg=f'Erro no banco de dados: {e}', noticias=noticias)

# Rota que recebe os dados do formulário de login (POST)
@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password_tentativa = request.form.get('password')

    user = User.query.filter_by(username=username).first()

    if user and bcrypt.checkpw(password_tentativa.encode('utf-8'), user.password_hash.encode('utf-8')):
        # 🟢 SUCESSO: Salva o ID do usuário na sessão
        session['user_id'] = user.id 
        return redirect(url_for('perfil')) # Redireciona para a nova página de perfil
    else:
        user_logged = None
        if 'user_id' in session:
            user_logged = User.query.get(session['user_id'])
        noticias = Noticia.query.order_by(Noticia.created_at.desc()).limit(10).all()
        return render_template('cadastro.html', user_logged=user_logged, login_error='Login falhou: Usuário ou Senha incorretos.', noticias=noticias)
    
# ----------------- EXECUÇÃO -----------------
if __name__ == '__main__':
    # Cria o banco de dados e as tabelas (se ainda não existirem)
    with app.app_context():
        db.create_all()
        
    app.run(debug=True)