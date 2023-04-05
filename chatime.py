from dotenv import load_dotenv
load_dotenv()

import os

from supabase import create_client

import requests

import json

from datetime import datetime
import pytz

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")

supabase = create_client(url, key)

status_logs = json.loads(supabase.table("StoreStatusLogs").select("*").eq("brand", "chatime").execute().json())["data"]

store_data = requests.get("https://chatime.redcatcloud.com.au/api/v1/stores").json()["data"]

melbourne_timezone = pytz.timezone("Australia/Melbourne")
current_time = datetime.now(melbourne_timezone)

for location in store_data:
    if location["StoreStatus"] == "Online":
        id = next((log for log in status_logs if log["storeId"] == location["StoreID"]), None)

        if next((log for log in status_logs if log["storeId"] == location["StoreID"]), None):
            supabase.table("StoreStatusLogs").update({
                "lastOnline": str(current_time)
            }).eq("id", id["id"]).execute()
        else:
            supabase.table("StoreStatusLogs").insert({
                "brand": "chatime",
                "storeId": location["StoreID"],
                "lastOnline": str(current_time)
            }).execute()