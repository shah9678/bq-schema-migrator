import json
import logging
import sqlalchemy
from typing import Dict, Any, List, Tuple, Type
from sqlmodel import SQLModel
from models import Customer, Product, Order, OrderItem, InventorySnapshot

# --- Logging Configuration ---
logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("SchemaMigrator")

MODELS = [Customer, Product, Order, OrderItem, InventorySnapshot]
SCHEMA_PATH = "data/bigquery_schema.json"
DATASET = "production"

TYPE_MAP: Dict[str, str] = {
    "VARCHAR": "STRING",
    "STRING": "STRING",
    "INTEGER": "INT64",
    "BIGINTEGER": "INT64",
    "FLOAT": "FLOAT64",
    "BOOLEAN": "BOOL",
    "DATETIME": "DATETIME",
    "TIMESTAMP": "TIMESTAMP",
    "DATE": "DATE",
    "JSON": "JSON",
}

NORMALIZE_MAP = {
    "BOOLEAN": "BOOL",
    "INTEGER": "INT64",
}

class SchemaMigrator:
    def get_bq_type(self, sa_column: sqlalchemy.Column) -> str:
        sa_type_str = str(sa_column.type).upper()
        for sa_key, bq_val in TYPE_MAP.items():
            if sa_key in sa_type_str:
                return bq_val
        return "STRING"

    def normalize_type(self, bq_type: str) -> str:
        t = bq_type.upper()
        return NORMALIZE_MAP.get(t, t)

    def compare(self, model: Type[SQLModel], bq_columns_list: List[Dict[str, Any]]) -> Tuple[List[str], List[str]]:
        table_name = model.__tablename__
        desired_columns = model.__table__.columns
        existing_columns = {col["name"]: col for col in bq_columns_list}
        
        ddl: List[str] = []
        warnings: List[str] = []

        for col_name, col_info in desired_columns.items():
            desired_type = self.get_bq_type(col_info)
            desired_nullable = col_info.nullable

            if col_name not in existing_columns:
                ddl.append(f"ALTER TABLE `{DATASET}.{table_name}` ADD COLUMN {col_name} {desired_type}")
                if col_info.default:
                    warnings.append(f"Column '{col_name}' has a default. BQ requires manual backfill.")
            else:
                curr = existing_columns[col_name]
                curr_type = self.normalize_type(curr["type"])
                curr_is_nullable = curr.get("mode", "NULLABLE") == "NULLABLE"

                if desired_type != curr_type:
                    warnings.append(f"TYPE MISMATCH in '{table_name}.{col_name}': {curr_type} (BQ) vs {desired_type} (Model).")
                
                if curr_is_nullable and not desired_nullable:
                    warnings.append(f"DESTRUCTIVE CHANGE in '{table_name}.{col_name}': Changing from NULLABLE to REQUIRED.")
                elif not curr_is_nullable and desired_nullable:
                    ddl.append(f"ALTER TABLE `{DATASET}.{table_name}` ALTER COLUMN {col_name} DROP NOT NULL")

        for bq_col_name in existing_columns:
            if bq_col_name not in desired_columns:
                warnings.append(f"EXTRA COLUMN in BQ: '{table_name}.{bq_col_name}' exists in BigQuery but not in Python model.")

        return ddl, warnings

def main():
    try:
        with open(SCHEMA_PATH, "r") as f:
            bigquery_schema = json.load(f)
    except FileNotFoundError:
        logger.error(f"Schema file not found at path: {SCHEMA_PATH}")
        return
    except json.JSONDecodeError:
        logger.error(f"Failed to decode JSON from {SCHEMA_PATH}")
        return

    migrator = SchemaMigrator()
    logger.info(f"Starting schema migration comparison for dataset: {DATASET}")

    for model in MODELS:
        table_name = model.__tablename__
        table_data = bigquery_schema.get(table_name, {})
        current_bq_cols = table_data.get("columns", [])
        
        ddl, warnings = migrator.compare(model, current_bq_cols)

        if not ddl and not warnings:
            logger.info(f"Table '{table_name}': In sync.")
            continue

        # Log Warnings --- A/S - 4/13/2026
        for warn in warnings:
            logger.warning(f"Table '{table_name}': {warn}")

        # Log DDL --- A/S - 4/13/2026
        for stmt in ddl:
            logger.info(f"Table '{table_name}' Suggested DDL: {stmt};")

if __name__ == "__main__":
    main()