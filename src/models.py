from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import declarative_base, Session


# engine = create_engine('postgresql+psycopg2://user:postgres@/card_test')

Base = declarative_base()

class Cards(Base):
	__tablename__ = "node_cards"

	commons_name = Column(String, primary_key=True)
	card = Column(JSONB)