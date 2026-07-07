# Real-Time Data Implementation

## 🎯 Overview

The Officer Dashboard now displays **ONLY real user-uploaded applications**, not the static mock dataset. The static dataset (429 businesses from CSV files) is now reserved exclusively for training and analytics purposes.

---

## ✅ Changes Made

### 1. **Modified `/api/portfolio` Endpoint**

**Before:**
```python
# Loaded static CSV dataset
merged = FEAT_DF.merge(LBL_DF[...])

# Added custom businesses
for c in custom_list:
    rows.append(...)

# Added all 429 static dataset rows ❌
for _, row in merged.iterrows():
    rows.append(...)
```

**After:**
```python
# ONLY returns custom businesses (real user uploads)
custom_list = get_custom_businesses()
for c in custom_list:
    rows.append(...)

# Static dataset NOT included ✅
# Comment explains it's for training only
```

**Result:** Officer Dashboard shows 0 applications initially, only shows applications after users upload data.

---

### 2. **Created `/api/portfolio/analytics` Endpoint**

New dedicated endpoint for accessing training data:

```python
@app.get("/api/portfolio/analytics")
def portfolio_analytics():
    """
    Returns the static training dataset for analytics 
    and model training purposes only.
    """
```

**Purpose:**
- Access training data for analytics
- Model training and validation
- Data science research
- NOT displayed in production UI

**Response Format:**
```json
{
  "count": 429,
  "data": [
    {
      "business_id": "MSME_UP_9212",
      "name": "Test Bank",
      "score": 70,
      "purpose": "TRAINING_DATA_ONLY"
    }
  ],
  "note": "This is static training data, not real applications"
}
```

---

### 3. **Graceful CSV Loading**

**Before:**
```python
# Would crash if CSV files missing ❌
FEAT_DF = pd.read_csv(...)
LBL_DF = pd.read_csv(...)
```

**After:**
```python
# Gracefully handles missing files ✅
try:
    FEAT_DF = pd.read_csv(...)
    LBL_DF = pd.read_csv(...)
    print("✓ Loaded training dataset (for analytics only)")
except FileNotFoundError:
    print("⚠ Training dataset not found - production still works")
    FEAT_DF = pd.DataFrame()
    LBL_DF = pd.DataFrame()
```

**Benefit:** Production features work even if training data is unavailable.

---

## 📊 Data Flow

### Production Flow (What Officers See):

```
User Uploads Application
         ↓
   /api/intake OR
/api/intake/register OR
   /api/v1/evaluate
         ↓
Saved to custom_businesses table
         ↓
   /api/portfolio
         ↓
Officer Dashboard (Real Applications Only)
```

### Training/Analytics Flow:

```
Static CSV Files (Dataset/)
         ↓
Loaded at server startup
         ↓
/api/portfolio/analytics
         ↓
Data Science Tools / Model Training
```

---

## 🔄 How to Add Applications

### Method 1: Quick Registration Form
```http
POST /api/intake/register
Content-Type: application/json

{
  "business_name": "My Kirana Store",
  "owner_name": "Raj Patel",
  "industry": "Retail",
  "loan_amount_required": 500000,
  "connect_gst": true,
  "connect_aa": true
}
```

### Method 2: File Upload (CSV)
```http
POST /api/intake
Content-Type: multipart/form-data

bank_file: <bank_statement.csv>
gst_file: <gst_returns.csv> (optional)
```

### Method 3: Full Data Evaluation
```http
POST /api/v1/evaluate
Content-Type: application/json

{
  "gstin": "27ABCDE1234F1Z5",
  "pan": "ABCDE1234F",
  "gst_data": {...},
  "account_aggregator_data": {...}
}
```

**Result:** All three methods save to `custom_businesses` table → Appears in Officer Dashboard

---

## 📍 Database Structure

### custom_businesses Table:
```sql
CREATE TABLE custom_businesses (
    id INTEGER PRIMARY KEY,
    business_id TEXT UNIQUE,
    name TEXT,
    industry TEXT,
    score INTEGER,
    band TEXT,
    data_json TEXT,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**What Gets Stored:**
- Real business information
- Credit score and risk band
- Full evaluation report (JSON)
- Application timestamp

---

## 🧪 Testing the Changes

### 1. Check Empty Dashboard:
```bash
# Start backend
cd backend
python main.py

# Check portfolio (should be empty or very few items)
curl http://localhost:8000/api/portfolio
```

**Expected:** `[]` or only real uploaded applications

### 2. Check Training Data:
```bash
# Access analytics endpoint
curl http://localhost:8000/api/portfolio/analytics
```

**Expected:** 429 static dataset businesses with `"purpose": "TRAINING_DATA_ONLY"`

### 3. Upload Test Application:
```bash
# Use existing CSV file
curl -X POST http://localhost:8000/api/intake \
  -F "bank_file=@indian_kirana_medium_risk.csv"
```

**Expected:** New application appears in dashboard

---

## 🎯 Expected Behavior

### Initial State:
- **Officer Dashboard**: Empty (0 applications) or very few
- **Message**: "No pending applications found"
- **Action Required**: Users must upload applications

### After Uploads:
- **Officer Dashboard**: Shows real uploaded applications
- **Each Application**: Has unique business_id (GSTIN or MSME_UP_*)
- **Status**: All start as "Pending"
- **Real Data**: Actual metrics from uploaded files

---

## 🔧 Configuration

### To Re-enable Mock Data (Testing Only):

In `backend/main.py`, uncomment this section:

```python
# Uncomment to show static dataset in dashboard (testing only)
if FEAT_DF.empty or LBL_DF.empty:
    pass
else:
    merged = FEAT_DF.merge(LBL_DF[...])
    for _, row in merged.iterrows():
        rows.append({
            "business_id": row["Business_ID"],
            "name": row["Business_Name"],
            # ... rest of data
        })
```

**Warning:** Only use for testing/development, not production!

---

## 📚 API Endpoints Summary

| Endpoint | Purpose | Returns |
|----------|---------|---------|
| `/api/portfolio` | **Production** - Real applications only | User uploads |
| `/api/portfolio/analytics` | **Training** - Static dataset | 429 mock businesses |
| `/api/intake` | Upload bank statement CSV | Creates new application |
| `/api/intake/register` | Quick registration form | Creates new application |
| `/api/v1/evaluate` | Full data evaluation | Creates new application |
| `/api/business/{id}` | Get application details | Full business profile |

---

## 🚨 Important Notes

### For Officers:
- ✅ Dashboard shows only real applications
- ✅ No more mock/test data cluttering the view
- ✅ Empty state means no pending applications (as expected)
- ✅ Applications appear immediately after user upload

### For Developers:
- ✅ Static dataset still available via `/api/portfolio/analytics`
- ✅ Training workflows unchanged
- ✅ Model training can still use CSV data
- ✅ Production and training data clearly separated

### For Data Scientists:
- ✅ Training data accessible via analytics endpoint
- ✅ 429 businesses available for model training
- ✅ Can compare real vs. training data
- ✅ Performance metrics can use both datasets

---

## 🔄 Migration Guide

### If You Have Existing Mock Data Decisions:

The `officer_decisions` table might have decisions for mock businesses:

```sql
-- Check decisions for mock data
SELECT * FROM officer_decisions 
WHERE business_id LIKE 'MSME%' 
AND business_id NOT LIKE 'MSME_UP_%';

-- Optional: Clean up mock data decisions
DELETE FROM officer_decisions 
WHERE business_id IN (
  SELECT Business_ID FROM engineered_features
);
```

### If You Need to Reset Everything:

```sql
-- Clear all custom businesses
DELETE FROM custom_businesses;

-- Clear all decisions
DELETE FROM officer_decisions;

-- Restart with clean slate
```

---

## 📊 Expected vs. Actual Data

### Old Behavior (Before):
```
Officer Dashboard:
- 429 mock businesses from CSV
- 3 real uploaded applications
Total: 432 applications ❌
```

### New Behavior (After):
```
Officer Dashboard:
- 0 mock businesses
- 3 real uploaded applications
Total: 3 applications ✅

Analytics Endpoint:
- 429 training businesses ✅
```

---

## ✅ Verification Checklist

- [ ] Backend starts without errors
- [ ] `/api/portfolio` returns empty or only real applications
- [ ] `/api/portfolio/analytics` returns 429 training businesses
- [ ] Officer Dashboard shows empty state or real applications only
- [ ] New uploads appear in dashboard immediately
- [ ] No mock data (Test Bank, Test Cotton Mills, etc.) visible
- [ ] Statistics cards show correct counts
- [ ] Application details page works for real uploads

---

## 🎉 Benefits

### 1. **Cleaner Production UI**
- Officers see only real work
- No confusion with test data
- Better focus and efficiency

### 2. **Clear Data Separation**
- Training data isolated
- Production data distinct
- No mixing of concerns

### 3. **Realistic Experience**
- Dashboard reflects actual workload
- Empty state when no applications (expected)
- Real business metrics only

### 4. **Flexible Development**
- Training data still accessible
- Can re-enable mock data for testing
- Graceful handling of missing files

---

## 🚀 Next Steps

1. **Test with Real Uploads**: Upload actual bank statements to populate dashboard
2. **User Training**: Inform officers about the new real-time only view
3. **Monitor Usage**: Track number of real applications vs. training data usage
4. **Analytics Integration**: Use `/api/portfolio/analytics` for reporting
5. **Performance Testing**: Ensure fast loading even with many real applications

---

## 📞 Troubleshooting

### Issue: Dashboard is empty
**Expected Behavior:** This is correct if no users have uploaded applications yet.

**Solution:** Upload test applications using:
- Business Registration form
- CSV file upload
- API evaluation endpoint

### Issue: Can't access training data
**Check:**
```bash
# Verify CSV files exist
ls -la Dataset/engineered_features.csv
ls -la Dataset/credit_labels.csv

# Test analytics endpoint
curl http://localhost:8000/api/portfolio/analytics
```

### Issue: Old mock data still showing
**Solution:**
```bash
# Restart backend server
# Ctrl+C to stop
python backend/main.py
```

---

## 📈 Metrics

### Before Change:
- Portfolio endpoint: 429 static + N real = 429+ businesses
- Dashboard load time: Slower (large dataset)
- Confusion: High (mock data mixed with real)

### After Change:
- Portfolio endpoint: N real businesses only
- Dashboard load time: Faster (smaller dataset)
- Clarity: High (production data only)
- Training data: Separate endpoint

---

## ✨ Summary

**What Changed:**
1. ❌ Removed static dataset from `/api/portfolio`
2. ✅ Created `/api/portfolio/analytics` for training data
3. ✅ Dashboard shows only real user uploads
4. ✅ Clear separation between production and training data

**Result:** Clean, professional, real-time application queue that reflects actual business operations! 🎉
