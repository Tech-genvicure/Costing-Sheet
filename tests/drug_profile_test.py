import sys
from pathlib import Path
from pprint import pprint

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app.services.drug_profile_builders import DrugProfileBuilder

builder = DrugProfileBuilder()

profile = builder.build(appl_no="215256")

pprint(profile)

builder.close()