# Production Automation Setup Guide

## For Daily Automated Scripts (Cron/Task Scheduler)

This setup is perfect for **automated daily scripts** that run without human interaction using service accounts and environment variables.

## ✅ Why This Approach?

- **🤖 Fully Automated**: No browser interaction required
- **🔒 Secure**: Uses environment variables instead of JSON files  
- **📅 Cron/Scheduler Ready**: Works with Windows Task Scheduler, Linux cron, Docker containers
- **☁️ Cloud Native**: Works in GCP, AWS, Azure, Kubernetes
- **🔄 Self-Refreshing**: Tokens refresh automatically

## 🚀 Production Deployment Options

### Option 1: Environment Variables (Recommended)
```bash
# Current working setup - just set environment variables
python test.py
```

### Option 2: Google Cloud Application Default Credentials (Best for GCP)
If running on Google Cloud (Compute Engine, Cloud Run, Cloud Functions):

1. **Remove JSON file dependency**:
```bash
rm keydev.json  # Remove the JSON file
```

2. **Use Application Default Credentials** (modify test.py):
```python
from google.auth import default

def get_access_token():
    """Get access token using Application Default Credentials (GCP)"""
    try:
        credentials, project = default(scopes=SCOPES)
        credentials.refresh(Request())
        return credentials.token
    except Exception as e:
        print(f"ADC authentication failed: {e}")
        return None
```

### Option 3: Workload Identity (Kubernetes on GCP)
For Kubernetes deployments with Workload Identity:

```yaml
# kubernetes-service-account.yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: cloudsql-monitor
  annotations:
    iam.gke.io/gcp-service-account: gmp-test-sa@feebak-dev-394405.iam.gserviceaccount.com
```

## 🔧 Current Setup (Working Solution)

Your current approach with environment variables is **perfect for automation**! Here's why:

### ✅ Advantages:
- Works everywhere (Windows, Linux, Docker, Kubernetes)  
- No interactive authentication needed
- Secure (no files to manage)
- Already implemented and working

### 📋 Files Needed:
1. **`.env`** - Contains all credentials (already configured)
2. **`test.py`** - Main script (already working)
3. **Task Scheduler/Cron** - For daily execution

## 🕐 Daily Automation Setup

### Windows Task Scheduler
```powershell
# Create a daily task
schtasks /create /tn "CloudSQL Monitor" /tr "python \"C:\path\to\test.py\"" /sc daily /st 09:00
```

### Linux Cron
```bash
# Add to crontab (daily at 9 AM)
0 9 * * * cd /path/to/monitoring && python test.py
```

### Docker Container
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# Run daily via cron inside container
RUN echo "0 9 * * * cd /app && python test.py" | crontab -
CMD ["crond", "-f"]
```

### Kubernetes CronJob
```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: cloudsql-monitor
spec:
  schedule: "0 9 * * *"  # Daily at 9 AM
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: monitor
            image: your-image:latest
            command: ["python", "test.py"]
            envFrom:
            - secretRef:
                name: monitoring-secrets
          restartPolicy: OnFailure
```

## 🛡️ Security Best Practices

### Current Setup (Already Secure):
✅ Environment variables (not hardcoded)  
✅ Base64 encoded private key  
✅ No JSON files in production  
✅ Minimal IAM permissions (Monitoring Viewer)  

### Additional Hardening:
```bash
# 1. Use secret management
# GCP Secret Manager
gcloud secrets create monitoring-private-key --data-file=<(echo $GOOGLE_PRIVATE_KEY_B64)

# 2. Rotate service account keys regularly
gcloud iam service-accounts keys create new-key.json --iam-account=gmp-test-sa@feebak-dev-394405.iam.gserviceaccount.com

# 3. Monitor service account usage
gcloud logging read "protoPayload.authenticationInfo.principalEmail=gmp-test-sa@feebak-dev-394405.iam.gserviceaccount.com"
```

## 🧪 Testing Automation

### Test Script Execution:
```powershell
# Test environment variables are loaded
cd "C:\Users\ArjunDasTP\Desktop\fantacode files\monitoring"
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print(f'PROJECT_ID: {os.getenv(\"PROJECT_ID\")}')"

# Test full script
python test.py
```

### Expected Output:
```
🔐 Getting access token via Service Account...
   ✅ Using service account from environment variables
   📧 Service Account: gmp-test-sa@feebak-dev-394405.iam.gserviceaccount.com
   🔓 Decoding private key...
   🔐 Creating credentials from service account info...
   🔄 Refreshing credentials to get access token...
   ✅ Successfully obtained access token!
   ⏰ Token valid until: 2024-10-26 10:45:32+00:00
```

## 📈 Monitoring & Alerting

### Add Health Check:
```python
def health_check():
    """Add health check endpoint for monitoring"""
    try:
        token = get_access_token()
        return {"status": "healthy", "has_token": bool(token)}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}
```

### Log to File:
```python
import logging
logging.basicConfig(
    filename='monitor.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
```

## 🎯 Production Checklist

- [x] ✅ Service account credentials in environment variables
- [x] ✅ No JSON files in production code  
- [x] ✅ Auto-refreshing tokens
- [x] ✅ Error handling and logging
- [x] ✅ Email and Teams notifications working
- [ ] 🔲 Set up daily cron job/task scheduler
- [ ] 🔲 Add monitoring/alerting for script failures
- [ ] 🔲 Set up log rotation
- [ ] 🔲 Test disaster recovery

---

**🎉 Your current setup is production-ready for automation!**  
The service account approach with environment variables is the **standard way** to run automated scripts in production.