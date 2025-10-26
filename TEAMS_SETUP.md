# Microsoft Teams Integration Setup Guide

## How to Setup Teams Webhook for CloudSQL Monitoring

### Step 1: Create Teams Incoming Webhook

1. **Open Microsoft Teams**
2. **Go to your target channel** (where you want to receive notifications)
3. **Click on the 3 dots (...)** next to the channel name
4. **Select "Connectors"**
5. **Find "Incoming Webhook"** and click **"Configure"**
6. **Enter Details:**
   - Name: `CloudSQL Monitoring`
   - Description: `CloudSQL P99 CPU monitoring alerts`
   - Upload an icon (optional)
7. **Click "Create"**
8. **Copy the webhook URL** (looks like: `https://your-org.webhook.office.com/webhookb2/...`)

### Step 2: Add Webhook URL to Environment

1. **Edit your `.env` file**
2. **Add the webhook URL:**
   ```env
   TEAMS_WEBHOOK_URL=https://your-org.webhook.office.com/webhookb2/your-actual-webhook-url
   ```

### Step 3: Test the Integration

Run your monitoring script:
```bash
python test.py
```

You should see both:
- ✅ Email report sent to your email
- ✅ Teams message sent successfully

### Teams Message Features

The Teams message includes:
- 🎨 **Color-coded cards**: Red (High), Orange (Moderate), Green (Normal)
- 📊 **Instance data**: Each instance with P99 CPU percentage
- 🔗 **Quick link**: Direct link to Google Cloud Console
- 📱 **Mobile-friendly**: Works on Teams mobile app

### Troubleshooting

**If Teams message fails:**
1. Verify webhook URL is correct and active
2. Check if webhook was deleted from Teams channel
3. Ensure network connectivity
4. Check firewall/proxy settings

**Common Issues:**
- Webhook URL expires if not used for 90 days
- Channel deletion removes the webhook
- Wrong webhook URL format

### Advanced: Power Automate Alternative

If you prefer Power Automate:
1. Create a new Flow in Power Automate
2. Use "When a HTTP request is received" trigger
3. Add "Post message in a chat or channel" action
4. Use the HTTP trigger URL in TEAMS_WEBHOOK_URL

The script will work with both approaches!