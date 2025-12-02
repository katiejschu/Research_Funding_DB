# neo4j_conn.py

from neo4j import GraphDatabase
import streamlit as st

# Use Streamlit's cache so we don't reconnect on every interaction
@st.cache_resource
def get_driver():
    """
    Create and cache a Neo4j driver.
    For Neo4j Desktop, the default URI is usually bolt://localhost:7687.
    """
    uri = "neo4j+s://da53f87f.databases.neo4j.io"  # <-- change if your port is different
    user = "neo4j"                 # <-- your Neo4j username
    password = "W5EjzWxQIIOAG3m-ShKBnz4TGAsWmOLK-j27eQxcwWs"  # <-- put your Desktop DB password

    driver = GraphDatabase.driver(uri, auth=(user, password))
    return driver


def run_cypher(query: str, params: dict | None = None, database="neo4j") -> list[dict]:
    driver = get_driver()
    with driver.session(database=database) as session:
        result = session.run(query, params or {})
        return [record.data() for record in result]

    """
    Run a Cypher query and return a list of dicts.
    Each dict is a row with column names as keys.
    """
    driver = get_driver()
    with driver.session() as session:
        result = session.run(query, params or {})
        return [record.data() for record in result]
