import os
from dotenv import load_dotenv

load_dotenv()

print("VNOC_USERNAME:", os.getenv("VNOC_USERNAME"))
print("VNOC_PASSWORD:", os.getenv("VNOC_PASSWORD"))
