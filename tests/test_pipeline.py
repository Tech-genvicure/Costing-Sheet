from app.services.pipeline_service import (
    process_drug
)

result = process_drug("WEGOVY")

print(result)