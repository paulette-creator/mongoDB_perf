import os
from pymongo import MongoClient
from dotenv import load_dotenv


class MongoTest:
    def __init__(self):
        load_dotenv()
        self.uri = os.getenv("MONGO_URI")
        self.db_name = os.getenv("MONGO_DB")

        if not self.uri or not self.db_name:
            raise ValueError("Missing MongoDB config")

    def test(self):
        try:
            client = MongoClient(self.uri, serverSelectionTimeoutMS=3000)
            client.admin.command("ping")          # test connexion
            client[self.db_name].list_collection_names()  # test accès DB
            print("✅ MongoDB connected & DB accessible")
        except Exception as e:
            print(f"❌ MongoDB test failed: {e}")
        finally:
            client.close()


if __name__ == "__main__":
    MongoTest().test()
