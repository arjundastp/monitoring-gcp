# CloudSQL P99 CPU Monitor Setup Guide

## 1. Install Dependencies
```bash
pip install -r requirements.txt
```

## 2. Setup Google Cloud Service Account

### Step 1: Create Service Account
1. Go to Google Cloud Console → IAM & Admin → Service Accounts
2. Click "Create Service Account"
3. Name: "cloudsql-monitor"
4. Grant Role: "Monitoring Viewer"

### Step 2: Download Key File
1. Click on your service account
2. Go to "Keys" tab
3. Click "Add Key" → "Create New Key" → JSON
4. Download and save as `service-account-key.json` in this directory

## 3. Setup Email Configuration

### For Gmail:
1. Enable 2-Factor Authentication on your Gmail account
2. Generate App Password:
   - Go to Google Account Settings → Security → 2-Step Verification → App passwords
   - Generate password for "Mail"
3. Update the script with your credentials:
   ```python
   EMAIL_FROM = "your-email@gmail.com"
   EMAIL_PASSWORD = "your-16-digit-app-password"
   ```

## 4. Configuration

### Step 1: Setup Environment Variables
1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` file with your actual values:
   ```env
   PROJECT_ID=fantacode-services
   EMAIL_FROM=your-email@gmail.com
   EMAIL_PASSWORD=your-16-digit-app-password
   EMAIL_TO=aejundastp3@gmail.com
   SERVICE_ACCOUNT_FILE=service-account-key.json
   ```

### Step 2: Secure Your Files
- Never commit `.env` or `service-account-key.json` to version control
- The `.gitignore` file is already configured to exclude these files

## 5. Run the Script
```bash
python test.py
```

## 6. Schedule (Optional)

### Windows Task Scheduler:
```bash
schtasks /create /tn "CloudSQL-Monitor" /tr "python C:\path\to\test.py" /sc daily /st 09:00
```

### Linux Cron:
```bash
# Add to crontab (runs daily at 9 AM)
0 9 * * * /usr/bin/python3 /path/to/test.py
```

## Troubleshooting

### Authentication Issues:
- Verify service account has "Monitoring Viewer" role
- Check `service-account-key.json` file exists and is valid
- Ensure project ID is correct

### Email Issues:
- Verify Gmail app password (not regular password)
- Check 2FA is enabled on Gmail account
- Verify SMTP settings

### No Data Issues:
- Check CloudSQL instances exist in the project
- Verify instances are running
- Check time range (script looks at last 24 hours)