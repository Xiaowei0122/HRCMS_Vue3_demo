"""Reset MongoDB test database - drop hrcms_test so seed data re-runs on next backend start"""
from pymongo import MongoClient

URI = "mongodb://admin:123456@127.0.0.1:27017"
DB_NAME = "hrcms_test"

print(f"Connecting to {URI} ...")
client = MongoClient(URI, serverSelectionTimeoutMS=5000)

try:
    client.admin.command("ping")
    print("[OK] MongoDB connected")
except Exception as e:
    print(f"[ERROR] Cannot connect: {e}")
    exit(1)

print(f"Dropping database: {DB_NAME} ...")
client.drop_database(DB_NAME)
print(f"[OK] Database '{DB_NAME}' dropped. All collections removed.")

client.close()
print()
print("Next step: restart backend (python main.py) to auto-create tables and seed data.")
