import os

SERVICE_MAIN_URL = 'http://{}:8000'
SECRET = os.environ.get('SECRET', None)
ALGORITHM = os.environ.get('ALGORITHM', 'HS256')
ISSUER = os.environ.get('ISSUER')

TOKEN_HEADER_TYPES = ('Bearer', 'JWT')
