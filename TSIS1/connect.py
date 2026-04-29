import psycopg2
from config import config


def get_connection():
    params = config()
    return psycopg2.connect(**params)
