from flask import Flask, render_template, request, redirect, session, flash
from flask_sqlalchemy import SQLAlchemy
import os
from werkzeug.security import generate_password_hash, check_password_hash

# Configuração do Flask e do banco de dados
project_dir = os.path.dirname(os.path.abspath(__file__))
database_file = "sqlite:///{}".format(os.path.join(project_dir, "bookdatabase.db"))

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = database_file
app.secret_key = os.urandom(24)  # Necessário para sessões
db = SQLAlchemy(app)

# Modelos de banco de dados
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return f"<User {self.username}>"

class Book(db.Model):
    title = db.Column(db.String(80), unique=True, nullable=False, primary_key=True)

    def __repr__(self):
        return "<Title: {}>".format(self.title)

with app.app_context():
    db.create_all()  # Criação das tabelas no banco de dados

# Rota inicial (redirecionar para cadastro ou lista de livros)
@app.route("/", methods=["GET", "POST"])
def home():
    if "user_id" not in session:
        return redirect("/register")  # Redireciona para a tela de cadastro se não estiver logado
    
    books = None
    if request.form:
        try:
            book = Book(title=request.form.get("title"))
            db.session.add(book)
            db.session.commit()
        except Exception as e:
            print("Falha ao adicionar livro")
            print(e)
    books = Book.query.all()
    return render_template("index.html", books=books)

# Rota de cadastro
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        
        # Criptografando a senha
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        
        new_user = User(username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash("Usuário cadastrado com sucesso!", "success")
        return redirect("/login")
    
    return render_template("register.html")

# Rota de login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session["user_id"] = user.id
            session["username"] = user.username
            flash("Login realizado com sucesso!", "success")
            return redirect("/")
        else:
            flash("Credenciais inválidas. Tente novamente.", "danger")
    
    return render_template("login.html")

# Rota de logout
@app.route("/logout")
def logout():
    session.clear()
    flash("Você saiu com sucesso!", "success")
    return redirect("/login")

# Rota de atualização de livro
@app.route("/update", methods=["POST"])
def update():
    try:
        newtitle = request.form.get("newtitle")
        oldtitle = request.form.get("oldtitle")
        book = Book.query.filter_by(title=oldtitle).first()
        if book:
            book.title = newtitle
            db.session.commit()
        else:
            print("Livro não encontrado")
    except Exception as e:
        print("Falha ao atualizar título do livro")
        print(e)
    return redirect("/")

# Rota de exclusão de livro
@app.route("/delete", methods=["POST"])
def delete():
    title = request.form.get("title")
    book = Book.query.filter_by(title=title).first()
    if book:
        db.session.delete(book)
        db.session.commit()
    else:
        print("Livro não encontrado")
    return redirect("/")

# Rota para ver detalhes do jogo (livro)
@app.route("/jogo/<title>", methods=["GET"])
def jogo(title):
    book = Book.query.filter_by(title=title).first()  
    if book:
        return render_template("jogo.html", book=book)
    else:
        return "Jogo não encontrado", 404

# Inicializando o servidor
if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
