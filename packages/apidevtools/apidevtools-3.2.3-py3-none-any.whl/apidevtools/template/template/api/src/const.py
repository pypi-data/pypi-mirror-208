from dotenv import load_dotenv
from os import getenv
from apidevtools import PostgreSQL


# assert load_dotenv('api/.env')
assert load_dotenv('apidevtools/template/template/api/.env')

DB_NAME: str = getenv('DB_NAME')
DB_HOST: str = getenv('DB_HOST')
DB_PORT: int = int(getenv('DB_PORT'))
DB_USER: str = getenv('DB_USER')
DB_PASS: str = getenv('DB_PASS')

API_HOST: str = getenv('API_HOST', '127.0.0.1')
API_PORT: int = int(getenv('API_PORT', 8000))

API_TITLE: str = getenv('API_TITLE')
API_DESCRIPTION: str = getenv('API_DESCRIPTION')
API_VERSION: str = getenv('API_VERSION')
API_CONTACT_NAME: str = getenv('API_CONTACT_NAME')
API_CONTACT_URL: str = getenv('API_CONTACT_URL')
API_CONTACT_EMAIL: str = getenv('API_CONTACT_EMAIL')

API_CORS_ORIGINS: list[str] = getenv('API_CORS_ORIGINS', '*').split(',')
API_CORS_ALLOW_CREDENTIALS: bool = getenv('API_CORS_ALLOW_CREDENTIALS', 'Y') == 'Y'
API_CORS_METHODS: list[str] = getenv('API_CORS_METHODS', '*').split(',')
API_CORS_HEADERS: list[str] = getenv('API_CORS_HEADERS', '*').split(',')

JWT_SECRET_KEY: str = getenv('JWT_SECRET_KEY')

db = PostgreSQL(database=DB_NAME, host=DB_HOST, port=DB_PORT, user=DB_USER, password=DB_PASS)
