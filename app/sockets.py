import json
from flask import session, current_app
from flask_socketio import emit
from . import socketio
from .database import conectar_db

@socketio.on('connect')
def handle_connect():
    conn = conectar_db()
    c = conn.cursor()
    # Cargamos el historial
    c.execute("SELECT data FROM trazos")
    filas = c.fetchall()
    conn.close()
    
    historial = [json.loads(fila[0]) for fila in filas]
    emit('cargar_historial', historial)

@socketio.on('draw_line')
def handle_draw(data):
    # Identificamos al dueño del trazo
    owner_email = session.get('user', {}).get('email', 'desconocido')
    obj_id = data.get('id', 'sin_id')
    
    conn = conectar_db()
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO trazos (id, data, owner_email) VALUES (?, ?, ?)", 
              (obj_id, json.dumps(data), owner_email))
    conn.commit()
    conn.close()
    
    emit('draw_line', data, broadcast=True, include_self=False)

@socketio.on('report_object')
def handle_report(data):
    emit('notify_admin_report', {'id': data.get('id')}, broadcast=True)

@socketio.on('delete_object')
def handle_delete_object(data):
    obj_id = data.get('id')
    user_email = session.get('user', {}).get('email')
    is_admin = (user_email == current_app.config['ADMIN_EMAIL'])
    
    conn = conectar_db()
    c = conn.cursor()
    
    # Validacion de Propiedad
    c.execute("SELECT owner_email FROM trazos WHERE id=?", (obj_id,))
    resultado = c.fetchone()
    
    if resultado:
        owner = resultado[0]
        # Solo borra si eres el admin o si tu lo dibujaste
        if is_admin or owner == user_email:
            c.execute("DELETE FROM trazos WHERE id=?", (obj_id,))
            conn.commit()
            emit('object_deleted', {'id': obj_id}, broadcast=True)
    
    conn.close()

@socketio.on('clear_board')
def handle_clear_board(data):
    # Ya no dependemos del prompt 'admin123', validamos directo con la sesion del servidor
    user_email = session.get('user', {}).get('email')
    
    if user_email == current_app.config['ADMIN_EMAIL']:
        conn = conectar_db()
        c = conn.cursor()
        c.execute("DELETE FROM trazos")
        conn.commit()
        conn.close()
        emit('board_cleared', broadcast=True)
    else:
        emit('admin_error', {'message': 'Violacion de seguridad: Permisos insuficientes'})