import logging
import os


def get_logger():
    APP_NAME = os.getenv('APP_NAME', 'nsj_multi_database_lib')
    return logging.getLogger(APP_NAME)

def get_crypt_key():
    if CRYPT_KEY is None:
        raise Exception('Faltando chave de criptografia')
    
    return CRYPT_KEY.encode()

CRYPT_KEY = os.getenv('CRYPT_KEY', None)
if CRYPT_KEY is None:
    get_logger().warning('Faltando chave de criptografia na variável de ambiente: CRYPT_KEY')
