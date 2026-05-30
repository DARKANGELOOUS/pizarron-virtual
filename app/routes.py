from flask import Blueprint, render_template, redirect, url_for, session, current_app
from . import oauth

# Creamos el "plano" de rutas
main = Blueprint('main', __name__)

@main.route('/login')
def login():
    redirect_uri = url_for('main.authorize', _external=True)
    return oauth.google.authorize_redirect(redirect_uri)

@main.route('/callback')
def authorize():
    token = oauth.google.authorize_access_token()
    resp = oauth.google.get('https://openidconnect.googleapis.com/v1/userinfo')
    user_info = resp.json()
    correo = user_info['email']

    dominio = current_app.config['DOMINIO_AUTORIZADO']
    if correo.endswith(dominio) or correo == "tu_correo_personal_de_prueba@gmail.com":
        session['user'] = user_info
        return redirect('/')
    else:
        return render_template('login.html', error=f"Acceso denegado. Se requiere un correo de {dominio}")

@main.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')

@main.route('/')
def index():
    if 'user' not in session:
        return redirect('/login')
    
    user_info = session['user']
    es_admin = (user_info['email'] == current_app.config['ADMIN_EMAIL'])
    return render_template('index.html', usuario=user_info['name'], is_admin=es_admin)

@main.route('/sw.js')
def sw():
    return current_app.send_static_file('sw.js')