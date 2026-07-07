# Quick Start - Real Data Only

## 🚀 Your Dashboard Now Shows Real Applications Only!

---

## ✅ What Changed?

### Before:
```
Officer Dashboard: 429 mock businesses + real uploads
```

### After:
```
Officer Dashboard: ONLY real user uploads
Training Data: Separate analytics endpoint
```

---

## 🎯 Quick Test

### 1. Start Backend:
```bash
cd backend
python main.py
```

**Expected Output:**
```
✓ Loaded training dataset: 429 businesses (for analytics/training only)
INFO:     Started server process
INFO:     Uvicorn running on http://127.0.0.1:8000
```

### 2. Check Production Endpoint:
```bash
curl http://localhost:8000/api/portfolio
```

**Expected:** Empty array `[]` or only real applications

### 3. Check Training Endpoint:
```bash
curl http://localhost:8000/api/portfolio/analytics
```

**Expected:** 429 training businesses

### 4. Start Frontend:
```bash
npm run dev
```

### 5. Open Dashboard:
```
http://localhost:5173/officer/applications
```

**Expected:** Empty state or only real applications

---

## 📤 How to Add Real Application

### Option 1: Upload CSV
```bash
curl -X POST http://localhost:8000/api/intake \
  -F "bank_file=@indian_kirana_medium_risk.csv"
```

### Option 2: Registration Form
Visit: `http://localhost:5173/business-registration`
Fill form and submit

### Option 3: API Call
```bash
curl -X POST http://localhost:8000/api/intake/register \
  -H "Content-Type: application/json" \
  -d '{
    "business_name": "My Store",
    "owner_name": "Raj",
    "industry": "Retail",
    "loan_amount_required": 500000,
    "connect_gst": true
  }'
```

---

## ✅ Success Indicators

- ✅ Dashboard shows 0-5 applications (not 429)
- ✅ No "Test Bank" or mock businesses
- ✅ Real application IDs (GSTIN format)
- ✅ Actual upload dates (not 2026-06-30)
- ✅ Analytics endpoint returns training data

---

## 🎉 You're All Set!

Your system now:
- Shows only real applications in production
- Keeps training data separate
- Provides professional user experience
- Has clean data architecture

**Ready to process real credit applications!** 🚀
