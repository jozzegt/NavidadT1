from flask import Flask, render_template, redirect, url_for, request, flash, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
from datetime import datetime

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
ALLOWED_EXT = {'png', 'jpg', 'jpeg', 'gif'}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-change-me')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASE_DIR, 'wishlist.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
db = SQLAlchemy(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    link = db.Column(db.String(1000))
    image = db.Column(db.String(1000))  # Either URL or local path
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    owner = db.relationship('User', backref=db.backref('items', lazy=True))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Helpers
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXT

def save_uploaded_file(file):
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S%f')
        filename = f"{timestamp}_{filename}"
        path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(path)
        # Return relative path to use in templates
        return url_for('static', filename=f'uploads/{filename}')
    return None

# Routes
@app.route('/')
def home():
    if current_user.is_authenticated:
        return redirect(url_for('my_items'))
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('my_items'))
    if request.method == 'POST':
        username = request.form.get('username').strip()
        password = request.form.get('password')
        if not username or not password:
            flash('Usuario y contraseña son requeridos.', 'warning')
            return redirect(url_for('register'))
        if User.query.filter_by(username=username).first():
            flash('El nombre de usuario ya existe.', 'warning')
            return redirect(url_for('register'))
        user = User(username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash('Cuenta creada. Inicia sesión.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('my_items'))
    if request.method == 'POST':
        username = request.form.get('username').strip()
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            flash('Sesión iniciada.', 'success')
            return redirect(url_for('my_items'))
        flash('Usuario o contraseña incorrectos.', 'danger')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Sesión cerrada.', 'info')
    return redirect(url_for('home'))

@app.route('/add', methods=['GET', 'POST'])
@login_required
def add_item():
    if request.method == 'POST':
        name = request.form.get('name').strip()
        link = request.form.get('link').strip()
        image_url = request.form.get('image_url').strip()
        image_file = request.files.get('image_file')

        if not name:
            flash('El nombre del item es requerido.', 'warning')
            return redirect(url_for('add_item'))

        image = None
        # Prefer uploaded file if present
        if image_file and image_file.filename != '':
            saved = save_uploaded_file(image_file)
            if saved:
                image = saved
            else:
                flash('Formato de imagen no permitido.', 'warning')
                return redirect(url_for('add_item'))
        elif image_url:
            image = image_url

        item = Item(name=name, link=link or None, image=image, owner_id=current_user.id)
        db.session.add(item)
        db.session.commit()
        flash('Item añadido.', 'success')
        return redirect(url_for('my_items'))
    return render_template('add_item.html')

@app.route('/my')
@login_required
def my_items():
    items = Item.query.filter_by(owner_id=current_user.id).order_by(Item.created_at.desc()).all()
    return render_template('my_items.html', items=items)

@app.route('/others')
@login_required
def other_items():
    items = Item.query.filter(Item.owner_id != current_user.id).order_by(Item.created_at.desc()).all()
    return render_template('other_items.html', items=items)

# Optional: delete an item (only owner)
@app.route('/delete/<int:item_id>', methods=['POST'])
@login_required
def delete_item(item_id):
    item = Item.query.get_or_404(item_id)
    if item.owner_id != current_user.id:
        flash('No tienes permiso para borrar este item.', 'danger')
        return redirect(url_for('my_items'))
    # If local file, optionally remove from disk (skipped for simplicity)
    db.session.delete(item)
    db.session.commit()
    flash('Item eliminado.', 'info')
    return redirect(url_for('my_items'))

if __name__ == '__main__':
    # Create DB tables if not exist
    with app.app_context():
        db.create_all()
    app.run(debug=True)
