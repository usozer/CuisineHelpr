import os

DEBUG = True
LOGGING_CONFIG = "config/logging/local.conf"
PORT = 5000
APP_NAME = "CuisineHelpr"
SQLALCHEMY_TRACK_MODIFICATIONS = True
HOST = "0.0.0.0"
SQLALCHEMY_ECHO = False  # If true, SQL for queries made will be printed
REDO = False

# Components of connection string
DB_HOST = os.environ.get("MYSQL_HOST")
DB_PORT = os.environ.get("MYSQL_PORT")
DB_USER = os.environ.get("MYSQL_USER")
DB_PW = os.environ.get("MYSQL_PASSWORD")
DATABASE = os.environ.get("MYSQL_DATABASE")
DB_DIALECT = "mysql+pymysql"

SQLALCHEMY_DATABASE_URI = os.environ.get("SQLALCHEMY_DATABASE_URI")

# If user provides a valid string, use it
if SQLALCHEMY_DATABASE_URI is not None:
    pass
# If environment variables are not set, default to sqlite
elif DB_HOST is None:
    SQLALCHEMY_DATABASE_URI = "sqlite:///data/kitchen.db"
    REDO = True
    SQLITE = True
# If no string is provided, and env variables are set, construct string
else:
    SQLALCHEMY_DATABASE_URI = (
        "{dialect}://{user}:{pw}@{host}:{port}/{db}".format(
            dialect=DB_DIALECT,
            user=DB_USER,
            pw=DB_PW,
            host=DB_HOST,
            port=DB_PORT,
            db=DATABASE,
        )
    )
