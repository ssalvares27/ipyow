# -*- coding: utf-8 -*-
""" config.py """

import os


class Config:
    SECRET_KEY = os.urandom(24)  # Chave secreta gerada dinamicamente
    SQLALCHEMY_DATABASE_URI = 'sqlite:///app.db'  # Usando SQLite para simplicidade
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = False  # Modo de debug desativado por padrão
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_USERNAME = os.getenv('MAIL_USERNAME', 'contatoipyow@gmail.com')
    # Coloque a senha do app aqui
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD', 'lyfq soah kzam letf')
    MAIL_DEFAULT_SENDER = os.getenv(
        'MAIL_DEFAULT_SENDER', 'contatoipyow@gmail.com')
    MERCADOPAGO_ACCESS_TOKEN = 'APP_USR-7494560022086392-020614-e3bd198fae9aa4ae957e72bdbbf8adff-2255004884'
    MELHOR_ENVIO_TOKEN = "SEU_TOKEN_AQUI"
