import aiohttp
import urllib.parse
import json
import hmac
import hashlib
import random
import base64
import requests
import os


from urllib.parse import urljoin
from sqlalchemy import select, insert
from typing import Tuple, Union

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import declarative_base, sessionmaker

from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy_utils import database_exists


host = os.environ['DB_HOST']
user = os.environ['DB_USER']
password = os.environ['DB_PASSWORD']
db = os.environ['DB_DATABASE']

def table_exists(engine,name):
    ins = inspect(engine)
    ret = ins.dialect.has_table(engine.connect(),name)
    print('Table "{}" exists: {}'.format(name, ret))
    return ret


def create_tables(host, user, password, database):  # pragma: no cover
    """
    create tables
    """
    engine = create_engine(
        "postgresql+psycopg2://{user}:{pwd}@{host}:5432/{db}".format(
            user=user, host=host, pwd=password, db=database
        )
    )
    conn = engine.connect()
    # Session = sessionmaker(bind = engine)
    # session = Session()

    create_card_table = text("CREATE TABLE node_cards (commons_name VARCHAR(255), card JSONB, PRIMARY KEY (commons_name))")

    try:
        conn.execute(create_card_table)
        print("WE HAVE CREATED THE TABLE")
        conn.commit()
    except Exception:
        print("Unable to create table")
        raise
    finally:
        conn.close()



engine = create_engine(f'postgresql+psycopg2://{user}:{password}@{host}:5432/{db}')
Session = sessionmaker(bind = engine)
session = Session()



if not table_exists(engine, "node_cards"):
    create_tables(host, user, password, db)


Base = declarative_base()




class Cards(Base):
    __tablename__ = "node_cards"

    commons_name = Column(String, primary_key=True)
    card = Column(JSONB)


class NodeCard():
    commons_name: str
    card: dict

example_node_card = {
    "card_type": "node",
    "id": "BioData-Catalyst",
    "meshcard_version": "1.0.0",
    "description": "BioData Catalyst data commons",
    "node_url": "https://gen3.biodatacatalyst.nhlbi.nih.gov",
    "mesh_metadata_api": {
        "standard": "gen3_MDS",
        "version": "4.0.5",
        "endpoint": "gen3.biodatacatalyst.nhlbi.nih.gov/mds/metadata/"
    },
    "node_metadata_api": {
        "standard": "gen3_sheepdog",
        "version": "1.0.0",
        "endpoint": "gen3.biodatacatalyst.nhlbi.nih.gov/v0/submission/"
    },
    "authz_api": {
        "standard": "fence",
        "version": "1.0",
        "endpoint": "example.com/ga4gh/passports/"
    },
    "data_api": {
        "standard": "DRS",
        "version": "1.5",
        "endpoint": "gen3.biodatacatalyst.nhlbi.nih.gov/ga4gh/drs/"
    },
    "metadata_adapters": {
        "BRH": {
            "mds_url": "https://gen3.biodatacatalyst.nhlbi.nih.gov/",
            "commons_url" : "gen3.biodatacatalyst.nhlbi.nih.gov",
            "adapter": "gen3",
            "config" : {
                "guid_type": "discovery_metadata",
                "study_field": "gen3_discovery"
            },
            "keep_original_fields": False,
            "field_mappings" : {
                "authz": "path:authz",
                "tags": "path:tags",
                "_unique_id": "path:study_id",
                "study_id": "path:study_id",
                "study_description": "path:study_description",
                "full_name": "path:full_name",
                "short_name": "path:short_name",
                "commons": "BioData Catalyst",
                "study_url": "path:dbgap_url",
                "_subjects_count" : {"path":"_subjects_count", "default" : 0 },
                "__manifest": "path:__manifest",
                "commons_url" : "gen3.biodatacatalyst.nhlbi.nih.gov"
            }
        }
    }
}


class CardClient(object):
    """Client for getting information about mesh or node cards deployed"""

    def __init__(self):
        self.meshcard = {
            "mesh_name": "Test mesh",
            "data_apis": ["DRS", "indexd"],
            "metadata_apis": ["mds"],
            "auth_apis": ["oidc", "keycloak"]
        }

    async def return_meshcard(self):
        return 200, self.meshcard

    async def get_card(self, commons):
        stmt = select(Cards).where(Cards.commons_name == commons)
        result = session.execute(stmt)

        for r in result.scalars():
            ret_card = r.card

        return 200, ret_card

    async def get_all_cards(self):
        stmt = select(Cards)
        result = session.execute(stmt)

        ret = []

        for r in result.scalars():
            ret.append(r.card)

        return 200, ret

    async def validate_nodecard(self, nodecard):
        """ 
        This function validates a node card against a mesh card to ensure that all endpoints are compatiable with the mesh

        Input:
            nodecard: JSON format of a nodecard
        """
        
        malformed_nodecard_message = "There is was an error parsing your nodecare please insure that your card is formatted correctly"

        # first we need to ensure that all of the basics of the nodecard are there, this includes data, metadata, and auth
        if not "data_api" in nodecard or not "metadata_api" in nodecard or not "auth_api" in nodecard or not "node_name" in nodecard or "node_url" not in nodecard:
            return 400, malformed_nodecard_message


        # Ensure URL for node is correct and working
        url = nodecard.get("node_url")
        url_get = requests.get(url)

        if url_get.status_code != 200:
            return 400, "URL for node was un reachable, ensure that the URL is correct"


        # Ensure data API is accepted by mesh and URL for data API is working
        data_api = nodecard.get("data_api")
        if data_api not in self.meshcard.get("data_apis"):
            return 400, "Data API for node is not supported by this mesh"

        data_api_endpoint = nodecard.get("data_api_endpoint")
        data_api_url = urljoin(url, data_api_endpoint)
        data_get = requests.get(data_api_url)

        if data_get.status_code != 200:
            return 400, "Unable to reach data API, ensure that data API endpoint is correct"

        # Ensure metadata API is accepted by mesh and URL for metadata API is working
        metadata_api = nodecard.get("metadata_api")
        if metadata_api not in self.meshcard.get("metadata_apis"):
            return 400, "Metadata API for node is not supported by this mesh"

        metadata_api_endpoint = nodecard.get("metadata_api_endpoint")
        metadata_api_url = urljoin(url, metadata_api_endpoint)
        metadata_get = requests.get(metadata_api_url)

        if metadata_get.status_code != 200:
            return 400, "Unable to reach metadata API, ensure that your metadata API endpoint is correct"


        # Ensure Auth api is accepted by mesh and URL for auth is working
        auth_api = nodecard.get("auth_api")
        if auth_api not in self.meshcard.get("auth_apis"):
            return 400, "Auth API for node is not supported by this mesh"

        oidc_well_known = "/.well-known/openid-configuration"
        auth_api_endpoint = nodecard.get("auth_api_endpoint")
        auth_api_url = urljoin(url, oidc_well_known)
        auth_get = requests.get(auth_api_url)

        if auth_get.status_code != 200:
            return 400, "Unable to reach Auth API, ensure that your Auth API endpoint is correct"


        # If code has gotten to here then the submitted nodecard is valid!
        return 200, "OK!"

    async def insert_nodecard(self, nodecard):
        node_id = nodecard.get("id")

        stmt = insert(Cards).values(commons_name=node_id, card=nodecard)

        result = session.execute(stmt)

        return 200, "Node Card Inserted"






        
