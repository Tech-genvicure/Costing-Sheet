from app.services.pipeline_service import process_drug


drug = "wegovy"

data = process_drug(drug)

print("\nFINAL OUTPUT:\n")
print(data)