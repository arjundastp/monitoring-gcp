import requests
from datetime import datetime, timedelta
import numpy as np
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from google.auth.transport.requests import Request
from google.oauth2 import service_account
import json
import os

# Load .env on local only
if os.path.exists(".env"):
    from dotenv import load_dotenv
    load_dotenv()

PROJECT_ID = os.getenv('PROJECT_ID')
EMAIL_TO = os.getenv('EMAIL_TO')
EMAIL_FROM = os.getenv('EMAIL_FROM')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
TEAMS_WEBHOOK_URL = os.getenv('TEAMS_WEBHOOK_URL')

GOOGLE_SERVICE_ACCOUNT_EMAIL = os.getenv('GOOGLE_SERVICE_ACCOUNT_EMAIL')
GOOGLE_PRIVATE_KEY = os.getenv('GOOGLE_PRIVATE_KEY')
GOOGLE_PRIVATE_KEY_ID = os.getenv('GOOGLE_PRIVATE_KEY_ID')
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
SCOPES = ['https://www.googleapis.com/auth/monitoring.read']


def get_access_token():
    try:
        sa = {
            "type": "service_account",
            "project_id": PROJECT_ID,
            "private_key_id": GOOGLE_PRIVATE_KEY_ID,
            "private_key": GOOGLE_PRIVATE_KEY.replace("\\n", "\n"),
            "client_email": GOOGLE_SERVICE_ACCOUNT_EMAIL,
            "client_id": GOOGLE_CLIENT_ID,
            "token_uri": "https://oauth2.googleapis.com/token"
        }
        creds = service_account.Credentials.from_service_account_info(sa, scopes=SCOPES)
        creds.refresh(Request())
        return creds.token
    except Exception as e:
        print("Auth error", e)
        return None


def send_email_report(subject, body):
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_FROM
        msg['To'] = EMAIL_TO
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_FROM, EMAIL_PASSWORD)
        server.sendmail(EMAIL_FROM, EMAIL_TO, msg.as_string())
        server.quit()
    except Exception as e:
        print("Email error", e)


def send_teams_message(text):
    if not TEAMS_WEBHOOK_URL:
        return
    try:
        requests.post(TEAMS_WEBHOOK_URL, json={"text": text})
    except:
        pass


def get_instances(token):
    url = f"https://monitoring.googleapis.com/v3/projects/{PROJECT_ID}/timeSeries"
    params = {
        "filter": 'metric.type="cloudsql.googleapis.com/database/cpu/utilization" AND resource.type="cloudsql_database"',
        "interval.startTime": (datetime.utcnow() - timedelta(hours=1)).isoformat() + "Z",
        "interval.endTime": datetime.utcnow().isoformat() + "Z"
    }
    r = requests.get(url, headers={"Authorization": f"Bearer {token}"}, params=params)
    inst = []
    for ts in r.json().get("timeSeries", []):
        iid = ts["resource"]["labels"].get("database_id", "")
        if ":" in iid: inst.append(iid.split(":")[-1])
    return inst


def get_cpu(token, inst):
    url = f"https://monitoring.googleapis.com/v3/projects/{PROJECT_ID}/timeSeries"
    params = {
        "filter": f'metric.type="cloudsql.googleapis.com/database/cpu/utilization" AND resource.labels.database_id="{PROJECT_ID}:{inst}"',
        "interval.startTime": (datetime.utcnow() - timedelta(days=1)).isoformat() + "Z",
        "interval.endTime": datetime.utcnow().isoformat() + "Z"
    }
    r = requests.get(url, headers={"Authorization": f"Bearer {token}"}, params=params)
    vals = []
    for ts in r.json().get("timeSeries", []):
        for p in ts.get("points", []):
            v = p.get("value", {}).get("doubleValue")
            if v is not None: vals.append(v)
    return np.percentile(vals, 99) * 100 if vals else 25.0


def run_job():
    token = get_access_token()
    if not token:
        return False

    insts = get_instances(token)
    if not insts:
        return False

    logs = []
    for inst in insts:
        cpu = get_cpu(token, inst)
        logs.append(f"{inst}: {cpu:.1f}% CPU")

    report = "\n".join(logs)
    send_email_report("Cloud SQL CPU Report", report)
    send_teams_message(report)
    return True


# ✅ Vercel handler
def handler(request, context):
    ok = run_job()
    return {
        "statusCode": 200,
        "body": json.dumps({"success": ok, "time": datetime.utcnow().isoformat()})
    }


# ✅ local run
if __name__ == "__main__":
    print("Running locally...")
    run_job()
