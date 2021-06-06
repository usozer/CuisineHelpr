import logging
import csv

import pandas as pd
import sqlalchemy
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from flask_sqlalchemy import SQLAlchemy

# Set up module logger
logger = logging.getLogger(__name__)

Base = declarative_base()

table_columns = [
    "name",
    "brazilian",
    "british",
    "cajun_creole",
    "chinese",
    "filipino",
    "french",
    "greek",
    "indian",
    "irish",
    "italian",
    "jamaican",
    "japanese",
    "korean",
    "mexican",
    "moroccan",
    "russian",
    "southern_us",
    "spanish",
    "thai",
    "vietnamese",
    "ingr_sum",
]


class Ingredient(Base):
    """Create a table for ingredients"""

    __tablename__ = "ingredients"

    cuisineid = Column(Integer, primary_key=True)
    name = Column(String(100), unique=False, nullable=False)
    brazilian = Column(Integer, unique=False, nullable=False)
    british = Column(Integer, unique=False, nullable=False)
    cajun_creole = Column(Integer, unique=False, nullable=False)
    chinese = Column(Integer, unique=False, nullable=False)
    filipino = Column(Integer, unique=False, nullable=False)
    french = Column(Integer, unique=False, nullable=False)
    greek = Column(Integer, unique=False, nullable=False)
    indian = Column(Integer, unique=False, nullable=False)
    irish = Column(Integer, unique=False, nullable=False)
    italian = Column(Integer, unique=False, nullable=False)
    jamaican = Column(Integer, unique=False, nullable=False)
    japanese = Column(Integer, unique=False, nullable=False)
    korean = Column(Integer, unique=False, nullable=False)
    mexican = Column(Integer, unique=False, nullable=False)
    moroccan = Column(Integer, unique=False, nullable=False)
    russian = Column(Integer, unique=False, nullable=False)
    southern_us = Column(Integer, unique=False, nullable=False)
    spanish = Column(Integer, unique=False, nullable=False)
    thai = Column(Integer, unique=False, nullable=False)
    vietnamese = Column(Integer, unique=False, nullable=False)
    ingr_sum = Column(Integer, unique=False, nullable=False)

    # String representation
    def __repr__(self):
        return "<Ingredients %r>" % self.cuisineid


def create_db(engine):
    """Create database from provided engine string

    Args:
        engine_string (str): Engine string for DB

    Returns:
        None
    """
    try:
        Base.metadata.create_all(engine)
        logger.info("Database created.")
    except sqlalchemy.exc.ArgumentError:
        logger.error("Invalid engine string provided")
    except sqlalchemy.exc.OperationalError:
        logger.error("Connection timed out, please check VPN connection")
    except Exception as e:
        logger.error("Unknown error", e)


def delete_db(engine):
    """Delete database from provided engine string."""
    Base.metadata.drop_all(engine)
    logger.info("Database deleted")


class SessionManager:
    def __init__(self, app=None, engine_string=None):
        """
        Args:
            app: Flask - Flask app
            engine_string: str - Engine string
        """
        if app:
            self.db = SQLAlchemy(app)
            self.session = self.db.session
        elif engine_string:
            engine = sqlalchemy.create_engine(engine_string)
            Session = sessionmaker(bind=engine)
            self.session = Session()
        else:
            raise ValueError(
                "Need either an engine string or a Flask app to initialize"
            )

    def close(self) -> None:
        """Closes session
        Returns: None
        """
        self.session.close()

    def add_to_db(self, datapath):
        """Populate table with ingredients

        Args:
            list_of_values (`list`): List of arrays, each representing
            one row.

            Each array must have a value representing each of the cuisines,
            and a variable at the end that has the sum of values.
        """
        with open(datapath, "r") as f:
            rows = list(csv.reader(f))
            del rows[0]
            # print(rows)
            # print(table_columns)
        
        # Initialize empty list, populate with dicts for each entry
        all_ingr = []

        for ingr_values in rows:
            inserts = {
                table_columns[i]: ingr_values[i]
                for i in range(len(table_columns))
            }
            # print(inserts)
            # print(Ingredient(**inserts))
            all_ingr.append(Ingredient(**inserts))

        # Add all Ingredient objects to database, and commit
        self.session.add_all(all_ingr)
        self.session.commit()

    def bind_model(self, model, **kwargs):
        self.df = pd.read_sql("SELECT * FROM ingredients", self.session.bind)
        traindf = self.df.set_index(keys=self.df.name).drop(
            ["cuisineid", "name"], axis=1
        )

        model.train(traindf, **kwargs)
        self.model = model
