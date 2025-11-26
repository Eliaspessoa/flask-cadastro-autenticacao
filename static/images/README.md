🔒 Sistema de Autenticação Segura com Flask, SQLAlchemy e Bcrypt

🌟 Visão Geral do Projeto

Este projeto é uma aplicação web minimalista desenvolvida em Python com o framework Flask. Seu objetivo principal é demonstrar a implementação de um sistema de autenticação robusto e seguro, utilizando as boas práticas do mercado para cadastro, login e gerenciamento de sessões.

Tecnologias Utilizadas

Backend: Python 3.x e Flask

Banco de Dados: SQLite (com SQLAlchemy ORM)

Segurança: Bcrypt (para hash de senhas)

Frontend: HTML com Jinja2 (Templates) e CSS básico

UX/Engajamento: Implementação de Mensagens Flash e Sistema de Notícias/Changelog.

🔑 Funcionalidades de Segurança

O coração deste projeto é a segurança. As seguintes funcionalidades foram implementadas:

Criptografia de Senha (Hashing): Todas as senhas são armazenadas no banco de dados usando o algoritmo Bcrypt, que adiciona um "salt" (valor aleatório) para garantir que as senhas nunca sejam armazenadas em texto simples.

Validação de Login: O login é verificado usando bcrypt.checkpw(), garantindo que a senha fornecida seja validada contra o hash armazenado.

Gerenciamento de Sessão: O estado de login do usuário é gerenciado de forma segura usando o objeto session do Flask, que é criptografado por uma SECRET_KEY.

⚙️ Como Executar o Projeto Localmente

Siga estes passos para configurar e rodar a aplicação em sua máquina.

Pré-requisitos

Certifique-se de ter o Python 3.x instalado.

1. Clonar o Repositório

git clone [https://github.com/elliaspessoa/flask-cadastro-autenticacao.git](https://github.com/elliaspessoa/flask-cadastro-autenticacao.git)
cd flask-cadastro-autenticacao


2. Criar e Ativar o Ambiente Virtual

É uma boa prática isolar as dependências do projeto.

# Cria o ambiente (para Windows/Linux/macOS)
python -m venv venv

# Ativação no Windows
.\venv\Scripts\activate

# Ativação no Linux/macOS
source venv/bin/activate


3. Instalar Dependências

Instale todas as bibliotecas necessárias (Flask, Flask-SQLAlchemy, Bcrypt).

pip install Flask Flask-SQLAlchemy bcrypt


4. Rodar a Aplicação

Execute o script principal do Flask. O banco de dados site.db será criado automaticamente.

python app.py


Acesse a aplicação no seu navegador: http://127.0.0.1:5000/

📢 Sistema de Novidades (Changelog)

O projeto inclui um sistema de notícias básicas para engajamento do usuário:

A rota /add-news (restrita a usuários logados) permite que o administrador publique novas atualizações.

A rota / (home) exibe essas atualizações para todos os visitantes.

🤝 Contribuição e Licença

Este projeto foi desenvolvido com o objetivo de estudo e demonstração de habilidades. Sinta-se à vontade para fazer fork e sugerir melhorias.