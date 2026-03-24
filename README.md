# 🚀 Reach11 - Lead Generation Engine (Backend)

<p align="center">
  <b>Stealth LinkedIn Lead Scraper powered by FastAPI + Selenium</b><br/>
  Generate high-quality leads in seconds ⚡
</p>

---

## 🧠 Overview

**Reach11 Backend API** is a production-ready, stealth scraping engine that:

- 🔍 Searches LinkedIn based on filters  
- 🛡️ Bypasses bot-detection using Selenium Stealth  
- 🎯 Extracts high-quality leads with recent activity  
- ⚡ Provides API-first architecture for frontend integration  

> Built for speed, stealth, and scalability.

---

## 🛠️ Tech Stack

| Category   | Tech Used |
|------------|----------|
| Framework  | FastAPI |
| Scraping   | Undetected ChromeDriver + Selenium Stealth |
| Security   | API Key (`X-API-KEY`) + `.env` |
| Runtime    | Python |

---

## ⚙️ Local Setup Guide

Follow these steps to run the backend locally:

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/reach11-backend.git
cd reach11-backend
```

---

### 2️⃣ Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate
```

---

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 4️⃣ Setup Environment Variables

Create a `.env` file in root:

```env
REACH11_API_KEY=reach11_secure_prod_key_2026
```

> ⚠️ Never commit `.env` to GitHub

---

### 5️⃣ Run the Server

```bash
python -m uvicorn main:app --reload
```

✅ Server running at:  
👉 http://127.0.0.1:8000

---

## 🔌 API Documentation

👉 Swagger UI:  
http://127.0.0.1:8000/docs

---

## 🚀 Generate Leads API

### 📍 Endpoint

```
POST /api/v1/generate-leads
```

---

### 📥 Headers

```
Content-Type: application/json
X-API-KEY: reach11_secure_prod_key_2026
```

---

### 📤 Request Body

```json
{
  "target": {
    "job_title": "Web Developer",
    "location": "Noida",
    "industry": "IT Services",
    "keywords": ["React", "Next.js", "Frontend"]
  },
  "li_at_cookie": "PASTE_YOUR_LI_AT_COOKIE_HERE",
  "user_city": "noida",
  "user_country": "in",
  "max_leads": 3
}
```

---

### 📦 Response

```json
{
  "status": "success",
  "target_searched": {
    "job_title": "Web Developer",
    "location": "Noida",
    "industry": "IT Services",
    "keywords": ["React", "Next.js", "Frontend"]
  },
  "leads": [
    {
      "name": "John Doe",
      "linkedin_url": "https://www.linkedin.com/in/johndoe",
      "recent_posts": [
        "Just launched my new Next.js portfolio!...",
        "Looking for freelance React opportunities..."
      ]
    }
  ]
}
```

---

## ⚠️ Important Notes

### 🧠 Headless Mode
- Disabled by default (for debugging)
- Chrome will open during scraping

---

### 🍪 Cookie Issue
If you get:

```json
"leads": []
```

👉 Your `li_at` cookie is expired  
👉 Get a fresh one from browser dev tools

---

### ⏳ Performance
- ~30–45 seconds for 3 leads  
- Delay ensures:
  - Human-like behavior  
  - Avoid LinkedIn bans  

---

## 🧪 Testing Tips

- Use Swagger UI for quick testing  
- Always verify cookie validity  
- Handle loading state in frontend  

---

## 🚨 Common Mistakes

- ❌ Using ```markdown wrapper in README  
- ❌ Wrong file name (`README.txt`)  
- ❌ Missing `.env` file  
- ❌ Invalid API key  

---

## ✨ Future Improvements

- Headless mode toggle  
- Proxy rotation  
- Lead export (CSV / Excel)  
- Dashboard analytics  

---

## 👨‍💻 Author

Built with ❤️ by Reach11

---

## ⭐ Support

If you found this useful:
- ⭐ Star the repo  
- 🔗 Share with others  
- 🚀 Build something amazing  