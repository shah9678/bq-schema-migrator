"""
BigQuery Schema Migration Tool — Entry Point

Compare the SQLModel definitions in models.py against the BigQuery schema
in data/bigquery_schema.json, and generate safe migration DDL.
"""

import json
from models import Customer, Product, Order, OrderItem, InventorySnapshot

MODELS = [Customer, Product, Order, OrderItem, InventorySnapshot]
SCHEMA_PATH = "data/bigquery_schema.json"
DATASET = "production"


def main():
    with open(SCHEMA_PATH) as f:
        bigquery_schema = json.load(f)

    # Your implementation here


if __name__ == "__main__":
    main()
