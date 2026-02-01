import os
import time
from typing import Any, Dict, List

import requests
from dotenv import load_dotenv
from pymongo import MongoClient, UpdateOne

import uuid
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime


class ApiToMongo:
    def __init__(self):
        # load_dotenv()
      
        BASE_DIR = os.path.dirname(os.path.dirname(__file__))  # dossier racine
        load_dotenv(os.path.join(BASE_DIR, ".env"))
        print("POSTGRES_PASSWORD =", os.getenv("POSTGRES_PASSWORD"))

        self.uri = os.getenv("MONGO_URI")
        self.db_name = os.getenv("MONGO_DB")
        self.col_name = os.getenv("MONGO_COLLECTION")
        self.api_url = os.getenv("api_url")

        self.postgres_host = os.getenv("POSTGRES_HOST")
        self.postgres_db = os.getenv("POSTGRES_DB")
        self.postgres_user = os.getenv("POSTGRES_USER")
        self.postgres_password = os.getenv("POSTGRES_PASSWORD")
        self.postgres_port = os.getenv("POSTGRES_PORT", "5434")

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
    def _make_key() -> str:
        """Définit une clé unique pour faire un upsert propre."""
        return str(uuid.uuid1())

    def run(self) -> None:
        t0 = time.time()

        # 1) Fetch API
        r = requests.get(self.api_url, timeout=10)
        r.raise_for_status()
        payload = r.json()

        t1 = time.time()
        t_fetch = t1 - t0

        # 2) Extract records
        records = self._extract_records(payload)
        if not records:
            print("⚠️ No records found in API response (format inattendu).")
            return
        
        t2 = time.time()
        t_extract = t2 - t1

        # 3) MongoDB : Connect + bulk upsert
        try:
            client = MongoClient(self.uri, serverSelectionTimeoutMS=5000)
            client.admin.command("ping")
            db = client[self.db_name]
            col = db[self.col_name]

            ops = []
            for doc in records:
                key = self._make_key()
                ops.append(
                    UpdateOne(
                        {"_id": key},                 # on force un id stable
                        {"$set": {"raw": doc}},       # on stocke brut au début
                        upsert=True
                    )
                )

            result = col.bulk_write(ops, ordered=False)

            t3 = time.time()
            t_mongo = t3 - t2

            coll_stats = db.command("collStats", self.col_name)
            mongo_disk_size_mb = coll_stats.get("storageSize", 0) / (1024 * 1024)

        finally:
            client.close()

        # 4) Postgres : Connect + upsert
        try:
            t4 = time.time()

            # Establish connection
            # Ensure you have your connection string (e.g., "dbname=db user=user password=pw host=host")
            conn = psycopg2.connect(
                dbname=self.postgres_db,
                user=self.postgres_user,
                password=self.postgres_password,
                host=self.postgres_host,
                port=self.postgres_port
            )
            cur = conn.cursor(cursor_factory=RealDictCursor)

            for doc in records:
                # --- 1. Insert or fetch site ---
                # Using ON CONFLICT allows us to handle the "fetch or insert" in one trip to the DB
                cur.execute("""
                    INSERT INTO sites (identifiant, nom, date_installation, longitude, latitude)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (identifiant) DO UPDATE SET identifiant = EXCLUDED.identifiant
                    RETURNING id;
                """, (
                    doc["id"], 
                    doc["name"], 
                    doc["installation_date"], 
                    doc["coordinates"]["lon"], 
                    doc["coordinates"]["lat"]
                ))
                site_id = cur.fetchone()['id']

                # --- 2. Insert or fetch compteur ---
                cur.execute("""
                    INSERT INTO compteurs (identifiant, nom, site_id)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (identifiant) DO UPDATE SET identifiant = EXCLUDED.identifiant
                    RETURNING id;
                """, (
                    doc["id_compteur"], 
                    doc["nom_compteur"], 
                    site_id
                ))
                compteur_id = cur.fetchone()['id']

                # --- 3. Insert comptage ---
                cur.execute("""
                    INSERT INTO comptages (date, comptage_horaire, photos, compteur_id)
                    VALUES (%s, %s, %s, %s);
                """, (
                    doc["date"], 
                    doc["sum_counts"], 
                    doc["photos"], 
                    compteur_id
                ))

            # Commit all changes at once for better performance
            conn.commit()
            
            t5 = time.time()
            t_postgres = t5 - t4

            cur.execute("SELECT pg_size_pretty(pg_database_size(current_database()));")
            postgres_disk_size_mb = cur.fetchone().get("pg_size_pretty")

        except Exception as e:
            if conn:
                conn.rollback()
            print(f"Error: {e}")

        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()


        # 5) Print summary
        print(
            "✅ Sync done | "
            f"fetched={len(records)} | "
            f"time_fetch={t_fetch:.2f}s | "
            f"time_extract={t_extract:.2f}s | "
            f"time_mongo={t_mongo:.2f}s | "
            f"time_postgres={t_postgres:.2f}s | "
            f"mongo_disk_size={mongo_disk_size_mb:.2f}MB | "
            f"postgres_disk_size={postgres_disk_size_mb}"
        )


if __name__ == "__main__":
    ApiToMongo().run()
