import os
from dotenv import load_dotenv
from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS
import pymysql

# Load environment variables
load_dotenv()

class DBConnection:
    def __init__(self):
        # MySQL Configuration
        self.username = os.getenv('DB_USER')
        self.password = os.getenv('DB_PASSWORD')
        self.database = os.getenv('DB_NAME')
        self.host = os.getenv('DB_HOST')
        self.port = os.getenv('DB_PORT')

        db_url = f"mysql+pymysql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"
        self.engine = create_engine(db_url, echo=False)
        self.SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=self.engine))

        # InfluxDB Configuration
        self.influx_client = InfluxDBClient(
            url=os.getenv('INFLUXDB_URL'),
            token=os.getenv('TOKEN'),
            org=os.getenv('ORG')
        )
        self.write_api = self.influx_client.write_api(write_options=SYNCHRONOUS)
        self.query_api = self.influx_client.query_api()

    @contextmanager
    def session_scope(self):
        """Provide a transactional scope around a series of operations."""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()

    def close_connections(self):
        """Close all database connections."""
        self.SessionLocal.remove()
        self.influx_client.close()
