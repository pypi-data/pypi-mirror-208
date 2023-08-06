import os

SERVICE_MAIN_URL = 'http://{}:8000'
ALGORITHM = os.environ.get('ALGORITHM', 'HS256')

TOKEN_HEADER_TYPES = ('Bearer', 'JWT')
