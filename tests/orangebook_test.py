import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app.database.repository import DrugRepository

repo = DrugRepository()

appl_no = "215256"  # Wegovy

print("=" * 70)
print("ORANGE PRODUCT")
print("=" * 70)

print(repo.get_orange_product(appl_no))

print("\n" + "=" * 70)
print("PATENTS")
print("=" * 70)

patents = repo.get_patents(appl_no)

print(f"Found {len(patents)} patents")

for patent in patents:
    print(patent)

print("\n" + "=" * 70)
print("EXCLUSIVITIES")
print("=" * 70)

exclusivities = repo.get_exclusivities(appl_no)

print(f"Found {len(exclusivities)} exclusivities")

for item in exclusivities:
    print(item)

repo.close()