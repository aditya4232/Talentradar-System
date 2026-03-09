# 🔑 **GET YOUR FREE API KEYS - STEP BY STEP GUIDE**

Follow these steps to get **LinkedIn + Naukri + 10x more jobs!**

---

## **KEY 1: Adzuna API** 
### ➡️ Get Naukri + Monster + Indeed India

### **Steps to Get Key:**

1. **Open this link:** https://developer.adzuna.com/signup

2. **Fill the signup form:**
   ```
   First Name: [Your name]
   Last Name: [Your last name]
   Email: [Your email]
   Company: TalentRadar (or your company)
   Purpose: Job aggregation
   ```

3. **Click "Sign Up"**

4. **Check your email** → Click confirmation link

5. **Login to Adzuna dashboard:** https://developer.adzuna.com/

6. **You'll see TWO keys on the dashboard:**
   ```
   Application ID:    12345678
   Application Key:   abc123def456ghi789...
   ```

7. **Copy both keys!**

---

## **KEY 2: JSearch RapidAPI**
### ➡️ Get LinkedIn + Glassdoor + Indeed

### **Steps to Get Key:**

1. **Open this link:** https://rapidapi.com/letscrape-6bRBa3QguO5/api/jsearch

2. **Click "Sign Up" (top right)** 
   - OR faster: Click "Log in with Google" or "Log in with GitHub"

3. **Once logged in, you'll be on the JSearch API page**

4. **Click the blue "Subscribe to Test" button**

5. **Select the FREE plan:**
   - Plan name: **"Basic"**
   - Price: **$0/month**
   - Requests: **2,500/month**
   - Click **"Subscribe"**

6. **After subscribing, scroll down** to "Code Snippets" section

7. **Look for this line:**
   ```
   'X-RapidAPI-Key': 'abc123def456ghi789jkl012...'
   ```

8. **Copy the key** (the long string after `X-RapidAPI-Key`)

---

## **NOW ADD THE KEYS TO YOUR SYSTEM**

### **Option 1: Direct Edit (Easiest)**

1. **Open file:** `backend\.env`

2. **Replace these lines:**
   ```env
   ADZUNA_APP_ID=PASTE_YOUR_APP_ID_HERE
   ADZUNA_API_KEY=PASTE_YOUR_API_KEY_HERE
   RAPIDAPI_KEY=PASTE_YOUR_RAPIDAPI_KEY_HERE
   ```

3. **With your actual keys:**
   ```env
   ADZUNA_APP_ID=12345678
   ADZUNA_API_KEY=abc123def456ghi789...
   RAPIDAPI_KEY=xyz789abc456def123...
   ```

4. **Save the file** (Ctrl+S)

### **Option 2: Tell Me the Keys (In Chat)**

Just paste them here and I'll add them to the `.env` file automatically!

Format:
```
Adzuna App ID: [paste here]
Adzuna API Key: [paste here]
RapidAPI Key: [paste here]
```

---

## **RESTART BACKEND**

After adding keys:

1. **Stop the backend** (press Ctrl+C in the backend terminal)
2. **Start it again:**
   ```powershell
   cd backend
   .\.venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

---

## **VERIFY IT'S WORKING**

Run this test:
```powershell
cd backend
.\.venv\Scripts\python.exe verify_complete_system.py
```

**Expected result:**
```
✅ Got 50-150 jobs (instead of just 2!)
✅ Sources will show: Remotive, Adzuna, JSearch
✅ You'll see LinkedIn, Naukri, Indeed jobs!
```

---

## **WHAT YOU'LL GET**

### **Before (Without Keys):**
- 2-10 jobs per query from Remotive only
- ~100-500 jobs per full scrape

### **After (With Both Keys):**
- 80-190 jobs per query from 6+ sources!
- ~4,000-9,500 jobs per full scrape
- **LinkedIn India jobs** ✅
- **Naukri jobs** ✅
- **Indeed India jobs** ✅
- **Glassdoor jobs** ✅
- **Monster India jobs** ✅
- **ZipRecruiter jobs** ✅

---

## **TROUBLESHOOTING**

### **If Adzuna doesn't work:**
- Make sure you used the **India-specific** endpoint (code already configured)
- Check you copied BOTH the App ID AND API Key
- Verify no extra spaces in the `.env` file

### **If JSearch doesn't work:**
- Make sure you **subscribed** to the free plan (not just logged in)
- Check you copied the full key (it's long, ~50 characters)
- Verify the key is on the same line as `RAPIDAPI_KEY=`

### **Still having issues?**
- Paste the error message in chat
- Or take a screenshot of your RapidAPI dashboard
- I'll help you debug!

---

## **TIME INVESTMENT vs REWARD**

| Time | What You Get |
|------|--------------|
| **3 minutes** | Adzuna → +5,000 jobs from Naukri/Monster/Indeed |
| **+2 minutes** | JSearch → +3,000 jobs from LinkedIn/Glassdoor |
| **= 5 minutes total** | **10x more jobs from major job boards!** |

---

## **READY TO GO?**

1. ✅ Open https://developer.adzuna.com/signup
2. ✅ Open https://rapidapi.com/letscrape-6bRBa3QguO5/api/jsearch
3. ✅ Get both keys (5 minutes)
4. ✅ Paste them in `backend\.env` (or tell me in chat!)
5. ✅ Restart backend
6. ✅ Run scraper → **Watch thousands of jobs pour in!** 🚀

---

**Questions? Just ask!** I'm here to help! 😊
