from migrate import SchemaMigrator
from models import Customer

def test_nested_json_parsing():
    """Test that the migrator correctly handles the nested 'columns' JSON structure."""
    migrator = SchemaMigrator()
    
    mock_bq_columns = [
        {"name": "id", "type": "STRING", "mode": "REQUIRED"},
        {"name": "name", "type": "STRING", "mode": "REQUIRED"},
        {"name": "email", "type": "STRING", "mode": "REQUIRED"},
        {"name": "tier", "type": "STRING", "mode": "REQUIRED"},
        {"name": "is_active", "type": "BOOLEAN", "mode": "REQUIRED"},
        {"name": "created_at", "type": "TIMESTAMP", "mode": "REQUIRED"},
        # 'annual_revenue' is missing from this mock list --- A/S - 4/13/2026
    ]
    
    ddl, _ = migrator.compare(Customer, mock_bq_columns)
    
    # Verify logic detects the missing 'annual_revenue' from models.py --- A/S - 4/13/2026
    assert any("ADD COLUMN annual_revenue FLOAT64" in stmt for stmt in ddl)

def test_type_normalization():
    """Test that 'BOOLEAN' in JSON is correctly compared to 'BOOL' in Model."""
    migrator = SchemaMigrator()
    
    # In JSON is_active is 'BOOLEAN', in Model it is 'BOOL' --- A/S - 4/13/2026
    mock_columns = [{"name": "is_active", "type": "BOOLEAN", "mode": "REQUIRED"}]
    
    _, warnings = migrator.compare(Customer, mock_columns)
    assert not any("TYPE MISMATCH: 'is_active'" in w for w in warnings)