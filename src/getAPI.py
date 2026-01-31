import os
import time
from typing import Any, Dict, List

import requests
from dotenv import load_dotenv
from pymongo import MongoClient, UpdateOne


class ApiToMongo:
    def __init__(self):
        load_dotenv()
        self.uri = os.getenv("MONGO_URI")
        self.db_name = os.getenv("MONGO_DB")
        self.col_name = os.getenv("MONGO_COLLECTION")
        self.api_url = os.getenv("api_url")

        if not all([self.uri, self.db_name, self.col_name, self.api_url]):
            raise ValueError("Missing .env vars: MONGO_URI, MONGO_DB, MONGO_COLLECTION, api_url")

    @staticmethod
    def _extract_records(payload: Any) -> List[Dict[str, Any]]:
        """
        Essaie d'extraire une liste de documents depuis différents formats d'API:
        - payload = {"data": {"stations": [...]}}
        - payload = {"stations": [...]}
        - payload = [...]
        - payload = {"records": [...]}
        """
        if isinstance(payload, list):
            return [x for x in payload if isinstance(x, dict)]

        if isinstance(payload, dict):
            # essais fréquents
            candidates = [
                payload.get("data", {}).get("stations") if isinstance(payload.get("data"), dict) else None,
                payload.get("stations"),
                payload.get("results"),
                payload.get("data"),
            ]
            for c in candidates:
                if isinstance(c, list):
                    return [x for x in c if isinstance(x, dict)]

        # rien trouvé -> 0 records
        return []

    @staticmethod
    def _make_key(doc: Dict[str, Any]) -> str | None:
        """Définit une clé unique (si possible) pour faire un upsert propre."""
        for k in ("station_id", "id", "stationCode", "station_code", "code"):
            v = doc.get(k)
            if v is not None and str(v).strip() != "":
                return str(v)
        return None

    def run(self) -> None:
        t0 = time.time()

        # 1) Fetch API
        r = requests.get(self.api_url, timeout=10)
        r.raise_for_status()
        payload = r.json()

        # 2) Extract records
        records = self._extract_records(payload)
        if not records:
            print("⚠️ No records found in API response (format inattendu).")
            return

        # 3) Connect + bulk upsert
        client = MongoClient(self.uri, serverSelectionTimeoutMS=3000)
        try:
            client.admin.command("ping")
            col = client[self.db_name][self.col_name]

            ops = []
            for doc in records:
                key = self._make_key(doc)
                if key:
                    ops.append(
                        UpdateOne(
                            {"_id": key},                 # on force un id stable
                            {"$set": {"raw": doc}},       # on stocke brut au début
                            upsert=True
                        )
                    )
                else:
                    # si pas de clé, on insère brut (risque de doublons, mais on garde simple)
                    ops.append(UpdateOne({"raw": doc}, {"$setOnInsert": {"raw": doc}}, upsert=True))

            result = col.bulk_write(ops, ordered=False)

            dt = time.time() - t0
            print(
                "✅ Sync done | "
                f"fetched={len(records)} | "
                f"upserted={result.upserted_count} | "
                f"modified={result.modified_count} | "
                f"time={dt:.2f}s"
            )

        finally:
            client.close()


if __name__ == "__main__":
    ApiToMongo().run()
