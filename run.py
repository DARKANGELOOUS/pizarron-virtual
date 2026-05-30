from app import create_app, socketio

# Instanciamos la fabrica de la aplicacion
app = create_app()

if __name__ == '__main__':
    print("Iniciando Pizarron Virtual Modular en http://127.0.0.1:5000")
    socketio.run(app, debug=True, port=5000)