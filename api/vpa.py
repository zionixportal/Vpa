import json
import requests
from urllib.parse import urlparse, parse_qs

HALFBLOOD_URL = "https://halfblood.famapp.in/vpa/verifyExt"
IFSC_SRC = "https://encore.toxictanji0503.workers.dev/ifsc?id="

HALFBLOOD_HEADERS = {
    "user-agent": "2312DRAABI | Android 15 | Dalvik/2.1.0 | gold | 2EF4F924D8CD3764269BD3548C4E7BF4FA070E7B | 3.11.5 (Build 525) | U78TN5J23U",
    "x-device-details": "2312DRAABI | Android 15 | Dalvik/2.1.0 | gold | 2EF4F924D8CD3764269BD3548C4E7BF4FA070E7B | 3.11.5 (Build 525) | U78TN5J23U",
    "x-app-version": "525",
    "x-platform": "1",
    "device-id": "adb84e9925c4f17a",
    "authorization": "Token eyJlbmMiOiJBMjU2Q0..."
}

def fetch_ifsc_details(ifsc_code: str):
    try:
        resp = requests.get(IFSC_SRC + ifsc_code, timeout=12)
        try:
            return resp.json()
        except ValueError:
            return {"raw": resp.text}
    except Exception as e:
        return {"error": str(e)}

def extract_ifsc(data):
    try:
        resp = data.get("data", {}).get("verify_vpa_resp", {})
        return resp.get("ifsc")
    except:
        return None


class handler:
    def __init__(self, event, context):
        self.event = event
        self.context = context

    def __call__(self):
        # Get `num` parameter
        query = self.event.get("queryStringParameters") or {}
        number = query.get("num") or query.get("number")

        if not number:
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": "Missing number"})
            }

        payload = {"upi_number": number}

        try:
            resp = requests.post(
                HALFBLOOD_URL,
                headers=HALFBLOOD_HEADERS,
                json=payload,
                timeout=12
            )
            data = resp.json()
        except Exception as e:
            return {
                "statusCode": 502,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": "HalfBlood request failed", "details": str(e)})
            }

        ifsc_code = extract_ifsc(data)
        data["ifsc_details"] = fetch_ifsc_details(ifsc_code) if ifsc_code else {"error": "IFSC not found"}

        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(data)
        }
