<<<<<<< HEAD
# 📊 Monitoring and Analytics Setup Guide

Complete guide for setting up monitoring, analytics, and uptime tracking for your deployed applications.

## 🎯 Overview

This guide covers setting up monitoring for:
- **Render API Health Checks** - Built-in monitoring and alerts
- **UptimeRobot** - External uptime monitoring with free tier
- **Google Analytics** - User behavior tracking for web properties
- **Status Badges** - Visual uptime indicators in README files

---

## 🏥 Render Monitoring Setup

### 1. Enable Health Checks

Your FastAPI app already has health check endpoints configured:

```python
# Already implemented in job-tracker-api/middleware.py
@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "timestamp": "2024-01-15T12:00:00Z",
        "uptime": 3600.0
    }
```

### 2. Configure Render Health Checks

In your `render.yaml`:

```yaml
services:
  - type: web
    name: job-tracker-api
    healthCheckPath: "/health"  # ✅ Already configured
    # Render will check this endpoint every 30 seconds
```

### 3. Set Up Email Alerts

1. **Go to Render Dashboard**:
   - Visit [render.com](https://render.com)
   - Navigate to your service

2. **Configure Notifications**:
   ```
   Service Settings → Notifications
   ├── Email Alerts: ON
   ├── Deploy Failures: ON
   ├── Health Check Failures: ON
   └── Auto-deploy Failures: ON
   ```

3. **Add Team Members** (optional):
   - Settings → Team → Add members for alerts

### 4. Monitor Response Times

Render automatically tracks:
- ✅ Response times
- ✅ Memory usage
- ✅ CPU usage
- ✅ Request counts

Access via: **Dashboard → Your Service → Metrics**

---

## 🤖 UptimeRobot Setup (Free Tier)

### 1. Create UptimeRobot Account

1. Visit [uptimerobot.com](https://uptimerobot.com)
2. Sign up for free account (50 monitors included)
3. Verify email and log in

### 2. Add Your Services

#### Monitor 1: Job Tracker API
```
Monitor Type: HTTP(s)
Friendly Name: Job Tracker API
URL: https://your-service-name.onrender.com/health
Monitoring Interval: 5 minutes (free tier)
```

#### Monitor 2: Streamlit App
```
Monitor Type: HTTP(s)  
Friendly Name: Job Application Tracker
URL: https://your-streamlit-app.streamlit.app
Monitoring Interval: 5 minutes
```

#### Monitor 3: Portfolio Website
```
Monitor Type: HTTP(s)
Friendly Name: Portfolio Website
URL: https://your-portfolio.vercel.app
Monitoring Interval: 5 minutes
```

### 3. Configure Alerts

For each monitor:
```
Alert Contacts:
├── Email: your-email@domain.com
├── SMS: +1234567890 (optional)
└── Webhook: (for advanced integrations)

Alert Settings:
├── Send alerts when: Monitor goes DOWN
├── Send alerts when: Monitor comes back UP  
├── Alert threshold: 1 confirmation (immediate)
└── Resend notifications: Every 12 hours
```

### 4. Create Status Page (Public)

1. **Create Status Page**:
   ```
   UptimeRobot → Status Pages → Add Status Page
   ├── Page Name: "Aniket's Services Status"
   ├── Subdomain: aniket-services  
   ├── Monitors: Select all 3 monitors
   └── Make Public: YES
   ```

2. **Your Status Page URL**:
   ```
   https://stats.uptimerobot.com/aniket-services
   ```

---

## 📈 Google Analytics Setup

### 1. Create Google Analytics Account

1. Visit [analytics.google.com](https://analytics.google.com)
2. Sign in with Google account
3. Click "Start measuring"
4. Set up account and property

### 2. Create Properties

#### Property 1: Portfolio Website
```
Property Name: Aniket Kumar Portfolio
Website URL: https://your-portfolio.vercel.app
Industry Category: Technology
Business Objective: Get baseline reports
```

#### Property 2: Streamlit App (Optional)
```
Property Name: Job Application Tracker
Website URL: https://your-streamlit-app.streamlit.app
Industry Category: Technology  
Business Objective: Examine user behavior
```

### 3. Get Measurement IDs

After creating properties, copy the Measurement IDs:
- Portfolio: `GA_MEASUREMENT_ID` (e.g., G-XXXXXXXXXX)
- Streamlit: `GA_MEASUREMENT_ID_STREAMLIT`

### 4. Implement Analytics

#### For Portfolio Website
Replace `GA_MEASUREMENT_ID` in both HTML files:

**index.html & projects.html**:
```html
<!-- Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);} 
  gtag('js', new Date());
  gtag('config', 'G-XXXXXXXXXX');
</script>
```

#### For Streamlit App
Set environment variable in Streamlit deployment:
```bash
# In Streamlit Cloud or locally
export GA_MEASUREMENT_ID="G-XXXXXXXXXX"
```

The analytics code is already implemented in `app.py`.

### 5. Track API Usage Patterns

Add analytics to your FastAPI app (optional):

```python
# In job-tracker-api/middleware.py
import httpx

class AnalyticsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Track API usage to Google Analytics
        response = await call_next(request)
        
        # Send event to GA4 (async, non-blocking)
        if GA_MEASUREMENT_ID:
            asyncio.create_task(self.track_api_usage(request, response))
        
        return response
```

---

## 📋 Status Badges Setup

### 1. Update README Badges

#### Job Tracker API README

Replace placeholders in `job-tracker-api/README.md`:

```markdown
[![API Status](https://img.shields.io/website?down_color=red&down_message=offline&up_color=green&up_message=online&url=https%3A%2F%2Fyour-service-name.onrender.com%2Fhealth)](https://your-service-name.onrender.com/health)
[![Uptime](https://img.shields.io/uptimerobot/ratio/m123456789?label=uptime)](https://stats.uptimerobot.com/aniket-services)
[![Response Time](https://img.shields.io/badge/response%20time-track%20via%20%2Fmetrics-blue)](https://your-service-name.onrender.com/metrics)
```

#### Portfolio README

Replace placeholders in `portfolio-website/README.md`:

```markdown
[![Website Status](https://img.shields.io/website?down_color=red&down_message=offline&up_color=green&up_message=online&url=https%3A%2F%2Fyour-portfolio.vercel.app)](https://your-portfolio.vercel.app)
[![Uptime](https://img.shields.io/uptimerobot/ratio/m123456789?label=uptime)](https://stats.uptimerobot.com/aniket-services)
```

### 2. Get UptimeRobot Monitor IDs

1. **Find Monitor ID**:
   ```
   UptimeRobot Dashboard → Select Monitor → Settings
   Monitor ID: m123456789-xxxxxxxxxx
   ```

2. **Update Badge URLs**:
   Replace `m123456789` with your actual monitor ID.

### 3. Add Custom Status Section

Add to your main `README.md`:

```markdown
## 🚦 Live Status

| Service | Status | Uptime | Response Time |
|---------|--------|---------|---------------|
| [Job Tracker API](https://your-api.onrender.com) | [![Status](https://img.shields.io/website?url=https%3A%2F%2Fyour-api.onrender.com%2Fhealth)](https://your-api.onrender.com/health) | [![Uptime](https://img.shields.io/uptimerobot/ratio/m123456789)](https://stats.uptimerobot.com/your-page) | [View Metrics](https://your-api.onrender.com/metrics) |
| [Streamlit App](https://your-app.streamlit.app) | [![Status](https://img.shields.io/website?url=https%3A%2F%2Fyour-app.streamlit.app)](https://your-app.streamlit.app) | [![Uptime](https://img.shields.io/uptimerobot/ratio/m987654321)](https://stats.uptimerobot.com/your-page) | N/A |
| [Portfolio](https://your-portfolio.vercel.app) | [![Status](https://img.shields.io/website?url=https%3A%2F%2Fyour-portfolio.vercel.app)](https://your-portfolio.vercel.app) | [![Uptime](https://img.shields.io/uptimerobot/ratio/m555666777)](https://stats.uptimerobot.com/your-page) | N/A |

🔗 **[View Detailed Status Page →](https://stats.uptimerobot.com/your-page)**
```

---

## 📊 Monitoring Dashboard

### 1. API Metrics Endpoint

Your API now exposes metrics at `/metrics`:

```json
{
  "total_requests": 1234,
  "last_request_ts": "2024-01-15T12:00:00Z",
  "endpoints": {
    "/api/applications": {
      "count": 456,
      "avg_response_time_sec": 0.1234
    },
    "/health": {
      "count": 789,
      "avg_response_time_sec": 0.0045
    }
  }
}
```

### 2. Create Custom Dashboard

Use tools like:
- **Grafana** (free tier)
- **Datadog** (limited free tier)
- **Custom dashboard** with JavaScript

Example custom dashboard:
```html
<div id="metrics-dashboard">
  <h3>Live API Metrics</h3>
  <div id="metrics-data">Loading...</div>
</div>

<script>
async function loadMetrics() {
  const response = await fetch('/metrics');
  const data = await response.json();
  document.getElementById('metrics-data').innerHTML = `
    <p>Total Requests: ${data.total_requests}</p>
    <p>Last Request: ${new Date(data.last_request_ts).toLocaleString()}</p>
  `;
}

setInterval(loadMetrics, 30000); // Update every 30 seconds
loadMetrics();
</script>
```

---

## 🔔 Alert Configuration

### 1. Email Alerts

Set up alerts for:
- ❌ **Service Down** (immediate)
- ✅ **Service Restored** (immediate)  
- ⚠️ **High Response Time** (>5 seconds)
- 📊 **Weekly Uptime Report**

### 2. SMS Alerts (Optional)

For critical services only:
- API completely down for >2 minutes
- Database connection failures

### 3. Slack/Discord Integration

UptimeRobot webhook for team notifications:
```
Webhook URL: https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK
Content Type: JSON
POST Value:
{
  "text": "*alertTypeFriendlyName* - *monitorFriendlyName* is *alertType*",
  "channel": "#alerts"
}
```

---

## 🎯 Analytics Goals

### 1. Website Goals (Portfolio)

Track conversions for:
- ✅ Contact form submissions
- ✅ Project demo clicks
- ✅ GitHub profile visits
- ✅ Resume downloads

### 2. App Goals (Streamlit)

Track user engagement:
- ✅ Applications added
- ✅ Analytics page views
- ✅ Export actions
- ✅ Session duration

### 3. API Goals

Monitor usage patterns:
- ✅ Endpoint popularity
- ✅ Response times
- ✅ Error rates
- ✅ User retention

---

## 📋 Quick Setup Checklist

### ✅ Render Monitoring
- [ ] Health check endpoint working
- [ ] Email alerts configured  
- [ ] Team notifications set up
- [ ] Response time monitoring enabled

### ✅ UptimeRobot
- [ ] Account created
- [ ] 3 monitors added (API, App, Portfolio)
- [ ] Email alerts configured
- [ ] Public status page created
- [ ] Monitor IDs noted for badges

### ✅ Google Analytics
- [ ] GA account created
- [ ] Properties set up (Portfolio + App)
- [ ] Measurement IDs obtained
- [ ] Analytics code implemented
- [ ] Goals configured

### ✅ Status Badges
- [ ] README files updated with badges
- [ ] UptimeRobot monitor IDs added
- [ ] Status table created in main README
- [ ] Links tested and working

### ✅ Documentation
- [ ] Monitoring guide created
- [ ] Team access documented  
- [ ] Alert procedures established
- [ ] Metrics interpretation guide

---

## 🚀 Next Steps

1. **Deploy Changes**: Push analytics code to production
2. **Test Monitoring**: Verify all health checks work
3. **Configure Alerts**: Set up appropriate notification levels
4. **Create Dashboard**: Build custom monitoring dashboard
5. **Document Process**: Share monitoring setup with team

---

## 📞 Troubleshooting

### Health Check Issues
```bash
# Test health endpoint
curl -i https://your-service-name.onrender.com/health

# Check logs
render logs your-service-name
```

### Analytics Not Working
```javascript
// Check if GA is loading
console.log(window.gtag);
console.log(window.dataLayer);
```

### UptimeRobot False Alerts
- Increase check interval (5→10 minutes)
- Set confirmation threshold to 2
- Check for maintenance windows

### Badge Not Updating
- Verify monitor ID is correct
- Check if service is public
- Clear browser cache

---

**🎉 Congratulations!** Your applications now have comprehensive monitoring and analytics set up for professional-grade deployment tracking.
=======
# 📊 Monitoring and Analytics Setup Guide

Complete guide for setting up monitoring, analytics, and uptime tracking for your deployed applications.

## 🎯 Overview

This guide covers setting up monitoring for:
- **Render API Health Checks** - Built-in monitoring and alerts
- **UptimeRobot** - External uptime monitoring with free tier
- **Google Analytics** - User behavior tracking for web properties
- **Status Badges** - Visual uptime indicators in README files

---

## 🏥 Render Monitoring Setup

### 1. Enable Health Checks

Your FastAPI app already has health check endpoints configured:

```python
# Already implemented in job-tracker-api/middleware.py
@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "timestamp": "2024-01-15T12:00:00Z",
        "uptime": 3600.0
    }
```

### 2. Configure Render Health Checks

In your `render.yaml`:

```yaml
services:
  - type: web
    name: job-tracker-api
    healthCheckPath: "/health"  # ✅ Already configured
    # Render will check this endpoint every 30 seconds
```

### 3. Set Up Email Alerts

1. **Go to Render Dashboard**:
   - Visit [render.com](https://render.com)
   - Navigate to your service

2. **Configure Notifications**:
   ```
   Service Settings → Notifications
   ├── Email Alerts: ON
   ├── Deploy Failures: ON
   ├── Health Check Failures: ON
   └── Auto-deploy Failures: ON
   ```

3. **Add Team Members** (optional):
   - Settings → Team → Add members for alerts

### 4. Monitor Response Times

Render automatically tracks:
- ✅ Response times
- ✅ Memory usage
- ✅ CPU usage
- ✅ Request counts

Access via: **Dashboard → Your Service → Metrics**

---

## 🤖 UptimeRobot Setup (Free Tier)

### 1. Create UptimeRobot Account

1. Visit [uptimerobot.com](https://uptimerobot.com)
2. Sign up for free account (50 monitors included)
3. Verify email and log in

### 2. Add Your Services

#### Monitor 1: Job Tracker API
```
Monitor Type: HTTP(s)
Friendly Name: Job Tracker API
URL: https://your-service-name.onrender.com/health
Monitoring Interval: 5 minutes (free tier)
```

#### Monitor 2: Streamlit App
```
Monitor Type: HTTP(s)  
Friendly Name: Job Application Tracker
URL: https://your-streamlit-app.streamlit.app
Monitoring Interval: 5 minutes
```

#### Monitor 3: Portfolio Website
```
Monitor Type: HTTP(s)
Friendly Name: Portfolio Website
URL: https://your-portfolio.vercel.app
Monitoring Interval: 5 minutes
```

### 3. Configure Alerts

For each monitor:
```
Alert Contacts:
├── Email: your-email@domain.com
├── SMS: +1234567890 (optional)
└── Webhook: (for advanced integrations)

Alert Settings:
├── Send alerts when: Monitor goes DOWN
├── Send alerts when: Monitor comes back UP  
├── Alert threshold: 1 confirmation (immediate)
└── Resend notifications: Every 12 hours
```

### 4. Create Status Page (Public)

1. **Create Status Page**:
   ```
   UptimeRobot → Status Pages → Add Status Page
   ├── Page Name: "Aniket's Services Status"
   ├── Subdomain: aniket-services  
   ├── Monitors: Select all 3 monitors
   └── Make Public: YES
   ```

2. **Your Status Page URL**:
   ```
   https://stats.uptimerobot.com/aniket-services
   ```

---

## 📈 Google Analytics Setup

### 1. Create Google Analytics Account

1. Visit [analytics.google.com](https://analytics.google.com)
2. Sign in with Google account
3. Click "Start measuring"
4. Set up account and property

### 2. Create Properties

#### Property 1: Portfolio Website
```
Property Name: Aniket Kumar Portfolio
Website URL: https://your-portfolio.vercel.app
Industry Category: Technology
Business Objective: Get baseline reports
```

#### Property 2: Streamlit App (Optional)
```
Property Name: Job Application Tracker
Website URL: https://your-streamlit-app.streamlit.app
Industry Category: Technology  
Business Objective: Examine user behavior
```

### 3. Get Measurement IDs

After creating properties, copy the Measurement IDs:
- Portfolio: `GA_MEASUREMENT_ID` (e.g., G-XXXXXXXXXX)
- Streamlit: `GA_MEASUREMENT_ID_STREAMLIT`

### 4. Implement Analytics

#### For Portfolio Website
Replace `GA_MEASUREMENT_ID` in both HTML files:

**index.html & projects.html**:
```html
<!-- Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);} 
  gtag('js', new Date());
  gtag('config', 'G-XXXXXXXXXX');
</script>
```

#### For Streamlit App
Set environment variable in Streamlit deployment:
```bash
# In Streamlit Cloud or locally
export GA_MEASUREMENT_ID="G-XXXXXXXXXX"
```

The analytics code is already implemented in `app.py`.

### 5. Track API Usage Patterns

Add analytics to your FastAPI app (optional):

```python
# In job-tracker-api/middleware.py
import httpx

class AnalyticsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Track API usage to Google Analytics
        response = await call_next(request)
        
        # Send event to GA4 (async, non-blocking)
        if GA_MEASUREMENT_ID:
            asyncio.create_task(self.track_api_usage(request, response))
        
        return response
```

---

## 📋 Status Badges Setup

### 1. Update README Badges

#### Job Tracker API README

Replace placeholders in `job-tracker-api/README.md`:

```markdown
[![API Status](https://img.shields.io/website?down_color=red&down_message=offline&up_color=green&up_message=online&url=https%3A%2F%2Fyour-service-name.onrender.com%2Fhealth)](https://your-service-name.onrender.com/health)
[![Uptime](https://img.shields.io/uptimerobot/ratio/m123456789?label=uptime)](https://stats.uptimerobot.com/aniket-services)
[![Response Time](https://img.shields.io/badge/response%20time-track%20via%20%2Fmetrics-blue)](https://your-service-name.onrender.com/metrics)
```

#### Portfolio README

Replace placeholders in `portfolio-website/README.md`:

```markdown
[![Website Status](https://img.shields.io/website?down_color=red&down_message=offline&up_color=green&up_message=online&url=https%3A%2F%2Fyour-portfolio.vercel.app)](https://your-portfolio.vercel.app)
[![Uptime](https://img.shields.io/uptimerobot/ratio/m123456789?label=uptime)](https://stats.uptimerobot.com/aniket-services)
```

### 2. Get UptimeRobot Monitor IDs

1. **Find Monitor ID**:
   ```
   UptimeRobot Dashboard → Select Monitor → Settings
   Monitor ID: m123456789-xxxxxxxxxx
   ```

2. **Update Badge URLs**:
   Replace `m123456789` with your actual monitor ID.

### 3. Add Custom Status Section

Add to your main `README.md`:

```markdown
## 🚦 Live Status

| Service | Status | Uptime | Response Time |
|---------|--------|---------|---------------|
| [Job Tracker API](https://your-api.onrender.com) | [![Status](https://img.shields.io/website?url=https%3A%2F%2Fyour-api.onrender.com%2Fhealth)](https://your-api.onrender.com/health) | [![Uptime](https://img.shields.io/uptimerobot/ratio/m123456789)](https://stats.uptimerobot.com/your-page) | [View Metrics](https://your-api.onrender.com/metrics) |
| [Streamlit App](https://your-app.streamlit.app) | [![Status](https://img.shields.io/website?url=https%3A%2F%2Fyour-app.streamlit.app)](https://your-app.streamlit.app) | [![Uptime](https://img.shields.io/uptimerobot/ratio/m987654321)](https://stats.uptimerobot.com/your-page) | N/A |
| [Portfolio](https://your-portfolio.vercel.app) | [![Status](https://img.shields.io/website?url=https%3A%2F%2Fyour-portfolio.vercel.app)](https://your-portfolio.vercel.app) | [![Uptime](https://img.shields.io/uptimerobot/ratio/m555666777)](https://stats.uptimerobot.com/your-page) | N/A |

🔗 **[View Detailed Status Page →](https://stats.uptimerobot.com/your-page)**
```

---

## 📊 Monitoring Dashboard

### 1. API Metrics Endpoint

Your API now exposes metrics at `/metrics`:

```json
{
  "total_requests": 1234,
  "last_request_ts": "2024-01-15T12:00:00Z",
  "endpoints": {
    "/api/applications": {
      "count": 456,
      "avg_response_time_sec": 0.1234
    },
    "/health": {
      "count": 789,
      "avg_response_time_sec": 0.0045
    }
  }
}
```

### 2. Create Custom Dashboard

Use tools like:
- **Grafana** (free tier)
- **Datadog** (limited free tier)
- **Custom dashboard** with JavaScript

Example custom dashboard:
```html
<div id="metrics-dashboard">
  <h3>Live API Metrics</h3>
  <div id="metrics-data">Loading...</div>
</div>

<script>
async function loadMetrics() {
  const response = await fetch('/metrics');
  const data = await response.json();
  document.getElementById('metrics-data').innerHTML = `
    <p>Total Requests: ${data.total_requests}</p>
    <p>Last Request: ${new Date(data.last_request_ts).toLocaleString()}</p>
  `;
}

setInterval(loadMetrics, 30000); // Update every 30 seconds
loadMetrics();
</script>
```

---

## 🔔 Alert Configuration

### 1. Email Alerts

Set up alerts for:
- ❌ **Service Down** (immediate)
- ✅ **Service Restored** (immediate)  
- ⚠️ **High Response Time** (>5 seconds)
- 📊 **Weekly Uptime Report**

### 2. SMS Alerts (Optional)

For critical services only:
- API completely down for >2 minutes
- Database connection failures

### 3. Slack/Discord Integration

UptimeRobot webhook for team notifications:
```
Webhook URL: https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK
Content Type: JSON
POST Value:
{
  "text": "*alertTypeFriendlyName* - *monitorFriendlyName* is *alertType*",
  "channel": "#alerts"
}
```

---

## 🎯 Analytics Goals

### 1. Website Goals (Portfolio)

Track conversions for:
- ✅ Contact form submissions
- ✅ Project demo clicks
- ✅ GitHub profile visits
- ✅ Resume downloads

### 2. App Goals (Streamlit)

Track user engagement:
- ✅ Applications added
- ✅ Analytics page views
- ✅ Export actions
- ✅ Session duration

### 3. API Goals

Monitor usage patterns:
- ✅ Endpoint popularity
- ✅ Response times
- ✅ Error rates
- ✅ User retention

---

## 📋 Quick Setup Checklist

### ✅ Render Monitoring
- [ ] Health check endpoint working
- [ ] Email alerts configured  
- [ ] Team notifications set up
- [ ] Response time monitoring enabled

### ✅ UptimeRobot
- [ ] Account created
- [ ] 3 monitors added (API, App, Portfolio)
- [ ] Email alerts configured
- [ ] Public status page created
- [ ] Monitor IDs noted for badges

### ✅ Google Analytics
- [ ] GA account created
- [ ] Properties set up (Portfolio + App)
- [ ] Measurement IDs obtained
- [ ] Analytics code implemented
- [ ] Goals configured

### ✅ Status Badges
- [ ] README files updated with badges
- [ ] UptimeRobot monitor IDs added
- [ ] Status table created in main README
- [ ] Links tested and working

### ✅ Documentation
- [ ] Monitoring guide created
- [ ] Team access documented  
- [ ] Alert procedures established
- [ ] Metrics interpretation guide

---

## 🚀 Next Steps

1. **Deploy Changes**: Push analytics code to production
2. **Test Monitoring**: Verify all health checks work
3. **Configure Alerts**: Set up appropriate notification levels
4. **Create Dashboard**: Build custom monitoring dashboard
5. **Document Process**: Share monitoring setup with team

---

## 📞 Troubleshooting

### Health Check Issues
```bash
# Test health endpoint
curl -i https://your-service-name.onrender.com/health

# Check logs
render logs your-service-name
```

### Analytics Not Working
```javascript
// Check if GA is loading
console.log(window.gtag);
console.log(window.dataLayer);
```

### UptimeRobot False Alerts
- Increase check interval (5→10 minutes)
- Set confirmation threshold to 2
- Check for maintenance windows

### Badge Not Updating
- Verify monitor ID is correct
- Check if service is public
- Clear browser cache

---

**🎉 Congratulations!** Your applications now have comprehensive monitoring and analytics set up for professional-grade deployment tracking.
>>>>>>> 409cb991133140d112bd4125da7948b5dacb035f
