import logging
import csv

import pandas as pd
import sqlalchemy
from sqlalchemy.exc import ArgumentError
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

    # String representation, displays primary key
    def __repr__(self):
        return "<Ingredients %r>" % self.cuisineid


def create_db(engine_string, engine=None):
    """Create db at the specified engine.

    Args:
        engine_string (str): URI to engine
        engine (`sqlalchemy.engine.Engine`): specified engine object, optional
    """
    try:
        if not engine:
            engine = sqlalchemy.create_engine(engine_string)
        Base.metadata.create_all(engine)
        logger.info("Database created at %s.", engine)
    except sqlalchemy.exc.ArgumentError:
        logger.error("Invalid engine string provided")
    # except sqlalchemy.exc.OperationalError:
    #     logger.error("Connection timed out, please check VPN connection")
    except Exception as e:
        logger.error("Unknown error", e)


def delete_db(engine_string, engine=None):
    """Delete database from provided engine.x

    Args:
        engine_string (str): URI to engine
        engine (`sqlalchemy.engine.Engine`): specified engine object, optional
    """
    try:
        if not engine:
            engine = sqlalchemy.create_engine(engine_string)
        Base.metadata.drop_all(engine)
        logger.info("Database deleted at %s.", engine)
    except sqlalchemy.exc.ArgumentError:
        logger.error("Invalid engine string provided")
    except sqlalchemy.exc.OperationalError:
        logger.error("Connection timed out, please check VPN connection")
    except Exception as e:
        logger.error("Unknown error", e)


class SessionManager:
    def __init__(self, app=None, engine_string=None):
        """
        Args:
            app: Flask - Flask app
            engine_string: str - Engine string
        """
        if app:
            # If app is given, then get db bound to Flask
            self.db = SQLAlchemy(app)
            self.session = self.db.session
        elif engine_string:
            # If engine string is given, then create
            # new SQLAlchemy engine object
            try:
                engine = sqlalchemy.create_engine(engine_string)
                Session = sessionmaker(bind=engine)
                self.session = Session()
            except sqlalchemy.exc.ArgumentError:
                logger.error(
                    "Could not parse engine URL from %s", engine_string
                )
            except sqlalchemy.exc.OperationalError:
                logger.error(
                    "Timed out, check to see if DB configuration \
                    is passed as env variables"
                )
        else:
            raise ValueError(
                "Need either an engine string or a Flask app to initialize"
            )

    def close(self):
        """Closes session
        Returns: None
        """
        self.session.close()

    def add_to_db(self, datapath, header=True):
        """Populate table with ingredients.

        Args:
            datapath (`str`): path to cleaned dataset (full)
            header (bool, optional): If true, csv file has
            a header row. True by default.

            Each row of the table must have a value representing each
            of the cuisines, and a variable at the end that
            has the sum of values.
        """
        with open(datapath, "r") as f:
            logger.info("Opened csv file at %s", datapath)
            # Turn csv file into list of lists
            rows = list(csv.reader(f))
            logger.info("Obtained %i records", len(rows))

        if header:
            del rows[0]
            logger.debug("Removed header row")

        # Initialize empty list, populate with dicts for each entry
        all_ingr = []

        for ingr_values in rows:
            try:
                inserts = {
                    table_columns[i]: ingr_values[i]
                    for i in range(len(table_columns))
                }
                all_ingr.append(Ingredient(**inserts))
            except IndexError:
                logger.warning(
                    "Row length %i do not match up number of columns %i",
                    len(table_columns),
                    len(ingr_values),
                )

        # Add all Ingredient objects to database, and commit
        try:
            logger.info("Attempting to insert records")
            self.session.add_all(all_ingr)
            logger.info("Added %i records", len(all_ingr))
            self.session.commit()
            logger.info("Changes committed to db %s", self.session.bind)
        except sqlalchemy.exc.DatabaseError:
            logger.error("Connection timed out!")

    def bind_model(self, model, **kwargs):
        """Bind a model object to session manager

        Args:
            model (any): Generic model object
        """
        # Get train df from `ingredients` table
        try:
            self.df = pd.read_sql(
                "SELECT * FROM ingredients", self.session.bind
            )
        except ArgumentError:
            logger.error(
                "Invalid DB, please reset the db %s", self.session.bind
            )
            return None

        # Prepare for training
        traindf = self.df.set_index(keys=self.df.name).drop(
            ["cuisineid", "name"], axis=1
        )

        model.train(traindf, **kwargs)
        self.model = model
        logger.info("Assigned a new model to subject of type %s", type(model))
