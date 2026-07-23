import sys
from pathlib import Path

# Add project root to Python path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app.database.repository import DrugRepository

repo = DrugRepository()

results = repo.search_drug("semaglutide")

print(f"Found {len(results)} results")

for row in results:
    print(row)

repo.close()