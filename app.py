import sqlite3
import json
from flask import Flask, render_template, redirect, url_for, session, request
from flask_socketio import SocketIO, emit
from authlib.integrations.flask_client import OAuth

app = Flask(__name__)
app.config['SECRET_KEY'] = 'clave_secreta_pizarron_2026'

# --- CONFIGURACION OAUTH (GOOGLE) ---
oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id='674895961793-00s62uii12cldr9t4hpf47ooreq6o1tg.apps.googleusercontent.com',
    client_secret='sexo',
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'}
)

DOMINIO_AUTORIZADO = "@uteq.edu.mx"
ADMIN_EMAIL = "2025110063@uteq.edu.mx"

socketio = SocketIO(app, cors_allowed_origins="*")

# --- Optimizacion de Base de Datos ---
def conectar_db():
    return sqlite3.connect('pizarron_v2.db', timeout=15)

def init_db():
    conn = conectar_db()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS trazos
                 (id TEXT PRIMARY KEY, data TEXT)''')
    conn.commit()
    conn.close()

init_db()

@app.route('/login')
def login():
    redirect_uri = url_for('authorize', _external=True)
    return google.authorize_redirect(redirect_uri)

@app.route('/callback')
def authorize():
    token = google.authorize_access_token()
    resp = google.get('https://openidconnect.googleapis.com/v1/userinfo')
    user_info = resp.json()
    correo = user_info['email']

    if correo.endswith(DOMINIO_AUTORIZADO) or correo == "ortizangelomar2726@gmail.com":
        session['user'] = user_info
        return redirect('/')
    else:
        return render_template('login.html', error=f"Acceso denegado. Se requiere un correo de {DOMINIO_AUTORIZADO}")

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')

@app.route('/')
def index():
    if 'user' not in session:
        return redirect('/login')
    
    user_info = session['user']
    es_admin = (user_info['email'] == ADMIN_EMAIL)
    return render_template('index.html', usuario=user_info['name'], is_admin=es_admin)

@app.route('/sw.js')
def sw():
    return app.send_static_file('sw.js')

# --- EVENTOS SOCKET.IO ---
@socketio.on('connect')
def handle_connect():
    conn = conectar_db()
    c = conn.cursor()
    c.execute("SELECT data FROM trazos")
    filas = c.fetchall()
    conn.close()
    
    historial = [json.loads(fila[0]) for fila in filas]
    emit('cargar_historial', historial)

@socketio.on('draw_line')
def handle_draw(data):
    obj_id = data.get('id', 'sin_id')
    conn = conectar_db()
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO trazos (id, data) VALUES (?, ?)", (obj_id, json.dumps(data)))
    conn.commit()
    conn.close()
    emit('draw_line', data, broadcast=True, include_self=False)

@socketio.on('report_object')
def handle_report(data):
    obj_id = data.get('id')
    emit('notify_admin_report', {'id': obj_id}, broadcast=True)

@socketio.on('delete_object')
def handle_delete_object(data):
    obj_id = data.get('id')
    conn = conectar_db()
    c = conn.cursor()
    c.execute("DELETE FROM trazos WHERE id=?", (obj_id,))
    conn.commit()
    conn.close()
    emit('object_deleted', {'id': obj_id}, broadcast=True)

@socketio.on('clear_board')
def handle_clear_board(data):
    password = data.get('password')
    if password == 'admin123':
        conn = conectar_db()
        c = conn.cursor()
        c.execute("DELETE FROM trazos")
        conn.commit()
        conn.close()
        emit('board_cleared', broadcast=True)
    else:
        emit('admin_error', {'message': 'Contrasena incorrecta'})

if __name__ == '__main__':
    socketio.run(app, debug=True, port=5000)    