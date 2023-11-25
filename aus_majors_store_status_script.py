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

brands = json.loads(supabase.table("AustralianMajorBrands").select("title").execute().json())["data"]

for brand in brands:
    status_logs = json.loads(supabase.table("AusMajorsStoreStatusLogs").select("*").eq("brand", brand["title"]).execute().json())["data"]

    store_data = requests.get("https://" + brand["title"] + ".redcatcloud.com.au/api/v1/stores").json()["data"]

    melbourne_timezone = pytz.timezone("Australia/Melbourne")
    current_time = datetime.now(melbourne_timezone)

    for location in store_data:
        id = next((log for log in status_logs if log["storeId"] == location["StoreID"]), None)

        if location["StoreStatus"] == "Online":
            if next((log for log in status_logs if log["storeId"] == location["StoreID"]), None):
                supabase.table("AusMajorsStoreStatusLogs").update({
                    "lastOnline": str(current_time),
                    "phone": location["Phone"],
                    "status": location["StoreStatus"],
                    "locationName": location["LocationName"],
                    "openNow": location["OpenNow"]
                }).eq("id", id["id"]).execute()
            else:
                supabase.table("AusMajorsStoreStatusLogs").insert({
                    "brand": brand["title"],
                    "storeId": location["StoreID"],
                    "lastOnline": str(current_time),
                    "phone": location["Phone"],
                    "status": location["StoreStatus"],
                    "locationName": location["LocationName"],
                    "openNow": location["OpenNow"]
                }).execute()
        else:
            if next((log for log in status_logs if log["storeId"] == location["StoreID"]), None):
                supabase.table("AusMajorsStoreStatusLogs").update({
                    "phone": location["Phone"],
                    "status": location["StoreStatus"],
                    "locationName": location["LocationName"],
                    "openNow": location["OpenNow"]
                }).eq("id", id["id"]).execute()