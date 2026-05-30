import os
from dotenv import load_dotenv

# Carga las variables del archivo .env al entorno del sistema
load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'clave_insegura_por_defecto')
    GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
    GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
    ADMIN_EMAIL = os.getenv('ADMIN_EMAIL')
    DOMINIO_AUTORIZADO = os.getenv('DOMINIO_AUTORIZADO')