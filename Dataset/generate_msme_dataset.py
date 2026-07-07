"""
MSME Synthetic Financial Dataset Generator
==========================================
Generates institution-quality synthetic data for MSME credit scoring:
  1. businesses.csv
  2. bank_transactions.csv
  3. gst_summary.csv
  4. engineered_features.csv
  5. credit_labels.csv

All math reconciles: running balances, GST-revenue alignment, and
labels derived from underwriting logic (NOT random).
"""

import csv
import math
import os
import random
from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Dict, List, Tuple

# ---------------------------------------------------------------------------
# Reproducibility
# ---------------------------------------------------------------------------
SEED = 20260707
random.seed(SEED)

OUT_DIR = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------------------
# Reference data (Indian context)
# ---------------------------------------------------------------------------
CITIES = [
    ("Mumbai", "Maharashtra"), ("Pune", "Maharashtra"), ("Nagpur", "Maharashtra"),
    ("Ahmedabad", "Gujarat"), ("Surat", "Gujarat"), ("Rajkot", "Gujarat"),
    ("Bengaluru", "Karnataka"), ("Mysuru", "Karnataka"),
    ("Chennai", "Tamil Nadu"), ("Coimbatore", "Tamil Nadu"), ("Madurai", "Tamil Nadu"),
    ("Hyderabad", "Telangana"), ("Warangal", "Telangana"),
    ("Delhi", "Delhi"),
    ("Jaipur", "Rajasthan"), ("Jodhpur", "Rajasthan"),
    ("Lucknow", "Uttar Pradesh"), ("Kanpur", "Uttar Pradesh"), ("Varanasi", "Uttar Pradesh"),
    ("Kolkata", "West Bengal"),
    ("Indore", "Madhya Pradesh"), ("Bhopal", "Madhya Pradesh"),
    ("Kochi", "Kerala"), ("Thiruvananthapuram", "Kerala"),
    ("Chandigarh", "Chandigarh"), ("Ludhiana", "Punjab"),
    ("Patna", "Bihar"), ("Bhubaneswar", "Odisha"),
    ("Guwahati", "Assam"), ("Dehradun", "Uttarakhand"),
]

FIRST_NAMES = [
    "Rajesh", "Sunita", "Amit", "Priya", "Vikram", "Anita", "Suresh", "Meena",
    "Ramesh", "Kavita", "Deepak", "Neha", "Manoj", "Pooja", "Sanjay", "Ritu",
    "Arun", "Shweta", "Naveen", "Divya", "Karthik", "Lakshmi", "Ganesh", "Radha",
    "Farhan", "Ayesha", "Iqbal", "Zaira",
]
LAST_NAMES = [
    "Kumar", "Sharma", "Patel", "Iyer", "Reddy", "Nair", "Shah", "Gupta", "Singh",
    "Mehta", "Verma", "Bansal", "Chaudhary", "Jain", "Menon", "Rao", "Das",
    "Bose", "Mukherjee", "Khan", "Ansari", "Pillai",
]

VENDOR_NAMES = [
    "SHREE ENTERPRISES", "BALAJI TRADERS", "ANNAPURNA SUPPLIES", "MAHALAXMI AGENCY",
    "RAM TRADING CO", "GANESH DISTRIBUTORS", "SIDDHI VINAYAK ENTP", "OM SAI TRADERS",
    "KRISHNA IMPEX", "AMBEY WHOLESALE", "JAI HIND TRADERS", "NEW BHARAT AGENCY",
    "ROYAL TRADING", "STAR ENTERPRISES", "GLOBAL SUPPLY CHAIN", "METRO WHOLESALE",
    "SANGAM MARKETING", "PRATAP TRADERS", "VISHNU AGENCY", "DURGA DISTRIBUTORS",
]

CUSTOMER_UPI_TAGS = [
    "PAYTM", "PHONEPE", "GPAY", "BHIM", "AMAZONPAY", "MOBIKWIK", "CRED",
    "RAZORPAY", "PAYU", "INSTAMOJO",
]

# ---------------------------------------------------------------------------
# Industry archetypes
# Each: baseline monthly revenue range, cash share, digital share, seasonality,
# expense ratio band, receivable style, volatility.
# ---------------------------------------------------------------------------
INDUSTRY_PROFILES = {
    "Grocery Store": dict(
        rev_range=(350_000, 900_000), cash=0.55, digital=0.40, cheque=0.05,
        expense_ratio=(0.78, 0.87), volatility=0.06, seasonal="festival",
        avg_ticket=(120, 800), tx_density_per_day=(4, 8),
        vendor_mix=["Raw Material", "Vendor Payment"], gst_slab=0.05,
    ),
    "Pharmacy": dict(
        rev_range=(400_000, 1_100_000), cash=0.30, digital=0.65, cheque=0.05,
        expense_ratio=(0.70, 0.80), volatility=0.05, seasonal="mild",
        avg_ticket=(150, 1500), tx_density_per_day=(4, 8),
        vendor_mix=["Raw Material", "Vendor Payment"], gst_slab=0.12,
    ),
    "Medical Shop": dict(
        rev_range=(300_000, 850_000), cash=0.35, digital=0.60, cheque=0.05,
        expense_ratio=(0.72, 0.82), volatility=0.05, seasonal="mild",
        avg_ticket=(200, 1200), tx_density_per_day=(3, 7),
        vendor_mix=["Raw Material", "Vendor Payment"], gst_slab=0.12,
    ),
    "Restaurant": dict(
        rev_range=(500_000, 1_400_000), cash=0.35, digital=0.60, cheque=0.05,
        expense_ratio=(0.78, 0.88), volatility=0.10, seasonal="weekend",
        avg_ticket=(400, 2200), tx_density_per_day=(5, 10),
        vendor_mix=["Raw Material", "Vendor Payment", "Fuel"], gst_slab=0.05,
    ),
    "Bakery": dict(
        rev_range=(200_000, 550_000), cash=0.50, digital=0.45, cheque=0.05,
        expense_ratio=(0.75, 0.85), volatility=0.08, seasonal="festival",
        avg_ticket=(80, 700), tx_density_per_day=(4, 8),
        vendor_mix=["Raw Material", "Vendor Payment"], gst_slab=0.05,
    ),
    "Textile Shop": dict(
        rev_range=(600_000, 1_700_000), cash=0.25, digital=0.45, cheque=0.30,
        expense_ratio=(0.72, 0.82), volatility=0.18, seasonal="wedding",
        avg_ticket=(1500, 12000), tx_density_per_day=(2, 5),
        vendor_mix=["Raw Material", "Vendor Payment"], gst_slab=0.05,
    ),
    "Garment Store": dict(
        rev_range=(400_000, 1_200_000), cash=0.30, digital=0.55, cheque=0.15,
        expense_ratio=(0.73, 0.83), volatility=0.16, seasonal="festival",
        avg_ticket=(600, 5000), tx_density_per_day=(3, 6),
        vendor_mix=["Raw Material", "Vendor Payment"], gst_slab=0.12,
    ),
    "Hardware Store": dict(
        rev_range=(350_000, 1_100_000), cash=0.30, digital=0.45, cheque=0.25,
        expense_ratio=(0.75, 0.85), volatility=0.12, seasonal="construction",
        avg_ticket=(400, 6000), tx_density_per_day=(3, 6),
        vendor_mix=["Raw Material", "Vendor Payment"], gst_slab=0.18,
    ),
    "Electronics Shop": dict(
        rev_range=(500_000, 1_500_000), cash=0.15, digital=0.65, cheque=0.20,
        expense_ratio=(0.80, 0.88), volatility=0.14, seasonal="festival",
        avg_ticket=(2500, 30000), tx_density_per_day=(2, 5),
        vendor_mix=["Raw Material", "Vendor Payment"], gst_slab=0.18,
    ),
    "Furniture Manufacturer": dict(
        rev_range=(700_000, 2_000_000), cash=0.10, digital=0.35, cheque=0.55,
        expense_ratio=(0.72, 0.83), volatility=0.20, seasonal="wedding",
        avg_ticket=(8000, 60000), tx_density_per_day=(2, 4),
        vendor_mix=["Raw Material", "Salary", "Vendor Payment"], gst_slab=0.18,
    ),
    "Mobile Shop": dict(
        rev_range=(400_000, 1_200_000), cash=0.20, digital=0.70, cheque=0.10,
        expense_ratio=(0.82, 0.90), volatility=0.13, seasonal="festival",
        avg_ticket=(3000, 25000), tx_density_per_day=(2, 5),
        vendor_mix=["Raw Material", "Vendor Payment"], gst_slab=0.18,
    ),
    "Dairy": dict(
        rev_range=(500_000, 1_300_000), cash=0.60, digital=0.35, cheque=0.05,
        expense_ratio=(0.83, 0.92), volatility=0.05, seasonal="mild",
        avg_ticket=(60, 500), tx_density_per_day=(5, 10),
        vendor_mix=["Raw Material", "Fuel", "Vendor Payment"], gst_slab=0.05,
    ),
    "Agriculture Supply": dict(
        rev_range=(400_000, 1_400_000), cash=0.35, digital=0.35, cheque=0.30,
        expense_ratio=(0.75, 0.85), volatility=0.22, seasonal="agri",
        avg_ticket=(800, 8000), tx_density_per_day=(2, 5),
        vendor_mix=["Raw Material", "Vendor Payment"], gst_slab=0.05,
    ),
    "Printing Press": dict(
        rev_range=(300_000, 900_000), cash=0.10, digital=0.50, cheque=0.40,
        expense_ratio=(0.70, 0.82), volatility=0.14, seasonal="exam",
        avg_ticket=(2500, 40000), tx_density_per_day=(2, 4),
        vendor_mix=["Raw Material", "Salary", "Vendor Payment"], gst_slab=0.12,
    ),
    "Transport Service": dict(
        rev_range=(400_000, 1_300_000), cash=0.20, digital=0.35, cheque=0.45,
        expense_ratio=(0.78, 0.88), volatility=0.16, seasonal="mild",
        avg_ticket=(2000, 25000), tx_density_per_day=(2, 4),
        vendor_mix=["Fuel", "Salary", "Maintenance"], gst_slab=0.05,
    ),
    "Logistics Company": dict(
        rev_range=(700_000, 2_200_000), cash=0.05, digital=0.30, cheque=0.65,
        expense_ratio=(0.78, 0.88), volatility=0.14, seasonal="festival",
        avg_ticket=(5000, 80000), tx_density_per_day=(2, 4),
        vendor_mix=["Fuel", "Salary", "Maintenance"], gst_slab=0.18,
    ),
    "Hotel": dict(
        rev_range=(600_000, 1_800_000), cash=0.25, digital=0.65, cheque=0.10,
        expense_ratio=(0.72, 0.85), volatility=0.20, seasonal="tourist",
        avg_ticket=(1800, 15000), tx_density_per_day=(3, 6),
        vendor_mix=["Vendor Payment", "Salary", "Electricity"], gst_slab=0.12,
    ),
    "Cafe": dict(
        rev_range=(250_000, 700_000), cash=0.25, digital=0.72, cheque=0.03,
        expense_ratio=(0.78, 0.88), volatility=0.09, seasonal="weekend",
        avg_ticket=(180, 900), tx_density_per_day=(5, 9),
        vendor_mix=["Raw Material", "Vendor Payment"], gst_slab=0.05,
    ),
    "Automobile Workshop": dict(
        rev_range=(300_000, 950_000), cash=0.35, digital=0.45, cheque=0.20,
        expense_ratio=(0.72, 0.84), volatility=0.13, seasonal="mild",
        avg_ticket=(700, 15000), tx_density_per_day=(3, 6),
        vendor_mix=["Raw Material", "Salary", "Maintenance"], gst_slab=0.18,
    ),
    "Construction Contractor": dict(
        rev_range=(800_000, 2_500_000), cash=0.10, digital=0.25, cheque=0.65,
        expense_ratio=(0.75, 0.88), volatility=0.28, seasonal="lumpy",
        avg_ticket=(15000, 250000), tx_density_per_day=(1, 3),
        vendor_mix=["Raw Material", "Salary", "Vendor Payment"], gst_slab=0.18,
    ),
    "Manufacturing Unit": dict(
        rev_range=(900_000, 2_500_000), cash=0.05, digital=0.30, cheque=0.65,
        expense_ratio=(0.75, 0.86), volatility=0.15, seasonal="mild",
        avg_ticket=(10000, 150000), tx_density_per_day=(2, 4),
        vendor_mix=["Raw Material", "Salary", "Electricity", "Vendor Payment"], gst_slab=0.18,
    ),
}

# 25 businesses spread across archetypes (some industries repeated with variation)
# Industry weights: how frequently each industry appears in a real MSME
# portfolio. Retail-heavy (grocery/pharmacy/restaurant/textile) dominates,
# manufacturing/construction is thinner. Weights are approximate but reflect
# rough national MSME distribution.
INDUSTRY_WEIGHTS = {
    "Grocery Store": 12,
    "Pharmacy": 6,
    "Medical Shop": 4,
    "Restaurant": 8,
    "Cafe": 4,
    "Bakery": 5,
    "Textile Shop": 6,
    "Garment Store": 6,
    "Hardware Store": 5,
    "Electronics Shop": 4,
    "Furniture Manufacturer": 3,
    "Mobile Shop": 5,
    "Dairy": 4,
    "Agriculture Supply": 5,
    "Printing Press": 3,
    "Transport Service": 5,
    "Logistics Company": 3,
    "Hotel": 3,
    "Automobile Workshop": 5,
    "Construction Contractor": 5,
    "Manufacturing Unit": 4,
}

def build_business_roster(n: int) -> list:
    """Sample n industries with proportional representation. Uses weighted
    round-robin so each industry appears roughly weight/sum_weights * n times,
    then shuffles to remove any ordering bias."""
    industries = list(INDUSTRY_WEIGHTS.keys())
    weights = [INDUSTRY_WEIGHTS[i] for i in industries]
    total_w = sum(weights)
    # Allocate integer counts proportionally, distribute remainder by residuals.
    exact = [w / total_w * n for w in weights]
    counts = [int(x) for x in exact]
    residuals = [(exact[i] - counts[i], i) for i in range(len(exact))]
    remaining = n - sum(counts)
    residuals.sort(reverse=True)
    for _, idx in residuals[:remaining]:
        counts[idx] += 1
    roster = []
    for ind, c in zip(industries, counts):
        roster.extend([ind] * c)
    random.shuffle(roster)
    return roster

# Financial personalities — assigned to businesses to ensure diversity
PERSONALITIES = [
    "very_stable", "rapidly_growing", "seasonal_festival", "cash_heavy",
    "digitally_driven", "debt_stressed", "high_emi", "declining",
    "recovery_phase", "expansion_phase", "inventory_intensive",
    "service_based", "manufacturing_based",
]

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def r2(x: float) -> float:
    """Round to 2 decimals."""
    return round(float(x), 2)

def jitter(base: float, pct: float) -> float:
    return base * (1.0 + random.uniform(-pct, pct))

def month_start(y: int, m: int) -> date:
    return date(y, m, 1)

def month_days(y: int, m: int) -> int:
    if m == 12:
        return (date(y + 1, 1, 1) - date(y, m, 1)).days
    return (date(y, m + 1, 1) - date(y, m, 1)).days

def business_name(industry: str, owner_first: str, city: str, idx: int) -> str:
    prefixes = [
        f"{owner_first}", "Sri", "Shree", "New", "Royal", "Star", "Ganesh",
        "Balaji", "Krishna", "Om Sai", "Annapurna", "Bharat", city,
    ]
    suffix_map = {
        "Grocery Store": ["Kirana", "Provisions", "General Store"],
        "Pharmacy": ["Pharmacy", "Medicals", "Medi Store"],
        "Medical Shop": ["Medicals", "Medi Plus", "Health Care"],
        "Restaurant": ["Restaurant", "Family Dhaba", "Kitchen"],
        "Bakery": ["Bakery", "Bakers", "Confectionery"],
        "Textile Shop": ["Textiles", "Sarees", "Fabrics"],
        "Garment Store": ["Garments", "Fashions", "Apparels"],
        "Hardware Store": ["Hardware", "Sanitary & Hardware", "Tools"],
        "Electronics Shop": ["Electronics", "Digital World", "Home Appliances"],
        "Furniture Manufacturer": ["Furniture Works", "Wood Craft", "Interiors"],
        "Mobile Shop": ["Mobiles", "Telecom", "Mobile World"],
        "Dairy": ["Dairy", "Milk Products", "Doodh Bhandar"],
        "Agriculture Supply": ["Agri Centre", "Krishi Kendra", "Farm Supplies"],
        "Printing Press": ["Printers", "Offset Press", "Digital Press"],
        "Transport Service": ["Transport", "Roadways", "Carriers"],
        "Logistics Company": ["Logistics", "Cargo Movers", "Freight Services"],
        "Hotel": ["Hotel", "Lodge", "Residency"],
        "Cafe": ["Cafe", "Coffee House", "Bistro"],
        "Automobile Workshop": ["Motors", "Auto Garage", "Service Point"],
        "Construction Contractor": ["Constructions", "Builders", "Infra"],
        "Manufacturing Unit": ["Industries", "Manufacturing", "Products"],
    }
    pfx = random.choice(prefixes)
    sfx = random.choice(suffix_map[industry])
    return f"{pfx} {sfx}"

# ---------------------------------------------------------------------------
# Business generation
# ---------------------------------------------------------------------------
@dataclass
class Business:
    business_id: str
    business_name: str
    industry: str
    city: str
    state: str
    business_age: int
    owner_age: int
    owner_first: str
    owner_last: str
    employee_count: int
    monthly_operating_days: int
    average_daily_customers: int
    annual_turnover: float
    gst_registered: str
    existing_loan: str
    existing_emi: float
    working_capital: float
    credit_limit: float
    business_category: str  # Micro / Small / Medium
    personality: str
    opening_balance: float
    profile: dict = field(default_factory=dict)

def classify_msme(annual_turnover: float) -> str:
    # Approx MSME categorisation (post-2020 revised, turnover-based, INR)
    if annual_turnover < 50_000_000:  # < ₹5 Cr
        return "Micro"
    if annual_turnover < 500_000_000:  # < ₹50 Cr
        return "Small"
    return "Medium"

def generate_businesses(count: int = 25, start_id: int = 1) -> List[Business]:
    businesses: List[Business] = []
    used_names = set()
    roster = build_business_roster(count)
    # personality pool sized to match count, cycled evenly
    reps = (count // len(PERSONALITIES)) + 1
    personality_pool = (PERSONALITIES * reps)[:count]
    random.shuffle(personality_pool)

    for offset, industry in enumerate(roster):
        i = start_id + offset
        profile = INDUSTRY_PROFILES[industry]
        city, state = random.choice(CITIES)
        first = random.choice(FIRST_NAMES)
        last = random.choice(LAST_NAMES)

        # ensure unique names
        for _ in range(10):
            name = business_name(industry, first, city, i)
            if name not in used_names:
                used_names.add(name)
                break
        else:
            name = f"{first} {industry} #{i}"

        personality = personality_pool[offset]

        # Estimate baseline monthly revenue for turnover
        base_rev = random.uniform(*profile["rev_range"])
        # personality tweaks
        pmul = 1.0
        if personality == "rapidly_growing":
            pmul = 0.9  # starts a bit lower, grows
        elif personality == "expansion_phase":
            pmul = 1.0
        elif personality == "declining":
            pmul = 1.15
        elif personality == "debt_stressed":
            pmul = 1.0
        base_rev *= pmul

        annual_turnover = base_rev * 12 * random.uniform(0.95, 1.05)
        category = classify_msme(annual_turnover)

        biz_age = random.randint(2, 22)
        owner_age = random.randint(28, 62)
        employees = max(1, int(math.sqrt(base_rev / 40_000)) + random.randint(-1, 3))
        op_days = 30 if industry in ("Dairy", "Restaurant", "Cafe", "Hotel") else random.choice([25, 26, 27, 28, 30])
        ticket_lo, ticket_hi = profile["avg_ticket"]
        avg_ticket = (ticket_lo + ticket_hi) / 2
        daily_customers = max(5, int(base_rev / (op_days * avg_ticket)))

        gst_registered = "Yes" if (base_rev * 12 > 4_000_000 or random.random() < 0.9) else "No"

        # Loan / EMI
        loan_prob = {
            "debt_stressed": 0.95, "high_emi": 0.98, "recovery_phase": 0.85,
            "expansion_phase": 0.75, "rapidly_growing": 0.55, "declining": 0.7,
        }.get(personality, 0.5)
        existing_loan = "Yes" if random.random() < loan_prob else "No"
        if existing_loan == "Yes":
            emi_multiplier = {
                "high_emi": 0.28, "debt_stressed": 0.22, "recovery_phase": 0.15,
                "expansion_phase": 0.12, "rapidly_growing": 0.10, "declining": 0.20,
            }.get(personality, 0.10)
            emi = r2(base_rev * emi_multiplier * random.uniform(0.85, 1.15))
        else:
            emi = 0.0

        working_capital = r2(base_rev * random.uniform(0.35, 0.9))
        credit_limit = r2(base_rev * random.uniform(0.5, 1.6))
        opening_balance = r2(base_rev * random.uniform(0.20, 0.55))

        bid = f"MSME{i:03d}"
        businesses.append(Business(
            business_id=bid, business_name=name, industry=industry,
            city=city, state=state, business_age=biz_age, owner_age=owner_age,
            owner_first=first, owner_last=last, employee_count=employees,
            monthly_operating_days=op_days, average_daily_customers=daily_customers,
            annual_turnover=r2(annual_turnover), gst_registered=gst_registered,
            existing_loan=existing_loan, existing_emi=emi,
            working_capital=working_capital, credit_limit=credit_limit,
            business_category=category, personality=personality,
            opening_balance=opening_balance, profile=profile,
        ))
    return businesses

# ---------------------------------------------------------------------------
# Seasonality & growth
# ---------------------------------------------------------------------------
def seasonality_multiplier(month: int, seasonal: str) -> float:
    # month: 1..12 corresponds to Jul-2025 .. Jun-2026 depending on index; we use calendar-month cycle
    # We'll pass calendar month directly
    m = month
    if seasonal == "festival":
        # Oct/Nov peak, mild dip in Feb
        table = {1:0.95,2:0.90,3:0.95,4:1.00,5:1.00,6:0.95,7:0.95,8:1.05,9:1.10,10:1.25,11:1.20,12:1.05}
    elif seasonal == "wedding":
        table = {1:1.05,2:1.10,3:1.05,4:1.10,5:1.15,6:0.95,7:0.90,8:0.95,9:1.05,10:1.15,11:1.30,12:1.20}
    elif seasonal == "agri":
        table = {1:0.85,2:0.90,3:0.95,4:1.05,5:1.15,6:1.20,7:1.10,8:1.05,9:1.00,10:1.15,11:1.10,12:0.95}
    elif seasonal == "construction":
        table = {1:1.05,2:1.10,3:1.10,4:1.10,5:1.15,6:0.85,7:0.75,8:0.80,9:1.00,10:1.10,11:1.15,12:1.10}
    elif seasonal == "tourist":
        table = {1:1.15,2:1.10,3:1.05,4:0.95,5:0.85,6:0.80,7:0.85,8:0.90,9:0.95,10:1.05,11:1.15,12:1.25}
    elif seasonal == "exam":
        table = {1:1.10,2:1.20,3:1.15,4:1.05,5:1.00,6:0.95,7:0.95,8:1.00,9:1.00,10:1.00,11:1.05,12:1.00}
    elif seasonal == "weekend":
        table = {i:1.00 for i in range(1,13)}
    elif seasonal == "lumpy":
        # will be handled at transaction level with big invoices
        table = {i:1.00 for i in range(1,13)}
    else:
        table = {i:1.00 for i in range(1,13)}
    return table[m]

def personality_growth(personality: str, month_idx: int) -> float:
    # month_idx: 0..11 within 12-month window
    if personality == "rapidly_growing":
        return 1.0 + 0.020 * month_idx  # +2%/mo compound-ish additive
    if personality == "expansion_phase":
        return 1.0 + 0.012 * month_idx
    if personality == "declining":
        return max(0.5, 1.0 - 0.018 * month_idx)
    if personality == "recovery_phase":
        # dip then recover
        return 1.0 + (0.03 * (month_idx - 3)) if month_idx > 3 else (1.0 - 0.02 * (3 - month_idx))
    if personality == "debt_stressed":
        return 1.0 - 0.005 * month_idx
    if personality == "very_stable":
        return 1.0
    return 1.0 + random.uniform(-0.005, 0.008)

# ---------------------------------------------------------------------------
# Transaction generation
# ---------------------------------------------------------------------------
DATE_START_YEAR = 2025
DATE_START_MONTH = 7  # data window: Jul-2025 .. Jun-2026
MONTHS = [(DATE_START_YEAR + (DATE_START_MONTH - 1 + i) // 12,
           ((DATE_START_MONTH - 1 + i) % 12) + 1) for i in range(12)]

def choose_payment_mode(profile: dict, is_credit: bool) -> str:
    if is_credit:
        # Sales inflow modes
        r = random.random()
        cash_p = profile["cash"]
        dig_p = profile["digital"]
        cheque_p = profile["cheque"]
        if r < cash_p:
            return "Cash Deposit"
        elif r < cash_p + dig_p:
            return random.choices(["UPI", "IMPS", "NEFT"], weights=[0.55, 0.25, 0.20])[0]
        else:
            return random.choice(["Cheque", "RTGS"])
    else:
        # Debit modes
        r = random.random()
        if r < 0.40:
            return random.choices(["UPI", "IMPS"], weights=[0.75, 0.25])[0]
        elif r < 0.70:
            return random.choice(["NEFT", "RTGS"])
        elif r < 0.85:
            return "Cheque"
        else:
            return "Cash Withdrawal"

def make_desc(category: str, mode: str) -> str:
    if category == "Sales":
        if mode in ("UPI", "IMPS"):
            tag = random.choice(CUSTOMER_UPI_TAGS)
            return f"{mode} CR/{tag}/CUST{random.randint(1000,9999)}"
        if mode == "Cash Deposit":
            return f"CASH DEP CDM/{random.randint(100000,999999)}"
        if mode == "NEFT":
            return f"NEFT CR/{random.choice(VENDOR_NAMES)}/INV{random.randint(1000,9999)}"
        if mode == "RTGS":
            return f"RTGS CR/{random.choice(VENDOR_NAMES)}/PO{random.randint(10000,99999)}"
        if mode == "Cheque":
            return f"CHQ DEP/{random.randint(100000,999999)}/CLG"
    if category == "Vendor Payment":
        return f"{mode} DR/{random.choice(VENDOR_NAMES)}/BILL{random.randint(1000,9999)}"
    if category == "Salary":
        return f"SALARY CR EMP {random.randint(101, 199)}"
    if category == "Rent":
        return f"RENT PAYMENT/{random.choice(['SHOP','GODOWN','OFFICE'])}"
    if category == "Electricity":
        return f"ELEC BILL/{random.choice(['MSEB','BESCOM','TSSPDCL','KSEB','TPDDL','GEB'])}"
    if category == "Internet":
        return f"INTERNET/{random.choice(['ACT','JIO FIBER','AIRTEL XSTREAM','BSNL'])}"
    if category == "GST":
        return f"GST PAYMENT CHALLAN {random.randint(1000000,9999999)}"
    if category == "Fuel":
        return f"FUEL/{random.choice(['HP','IOCL','BPCL','SHELL'])} PUMP"
    if category == "Raw Material":
        return f"{mode} DR/{random.choice(VENDOR_NAMES)}/RM PURCHASE"
    if category == "Office Supplies":
        return f"OFFICE SUP/{random.choice(['STAPLES','DTDC','KIRAN STAT'])}"
    if category == "Insurance":
        return f"INS PREM/{random.choice(['HDFC ERGO','ICICI LOMBARD','LIC','TATA AIG'])}"
    if category == "Maintenance":
        return f"MAINTENANCE/{random.choice(['AMC','REPAIR','SERVICE'])}"
    if category == "Loan EMI":
        return f"LOAN EMI DR/{random.choice(['HDFC','ICICI','SBI','AXIS','KOTAK','BOB'])}"
    if category == "Interest":
        return f"INTEREST DR/{random.choice(['CC ACCT','OD ACCT'])}"
    if category == "Miscellaneous":
        return f"MISC/{random.choice(['POS SWIPE','ATM WDL','SUBSCRIPTION','COURIER'])}"
    return category.upper()

def month_events(business: Business, cal_month: int, month_idx: int) -> Dict[str, bool]:
    """Return event flags for the month based on personality & seasonality."""
    ev = {"cheque_bounce": False, "festival_spike": False, "unexpected_expense": False,
          "equipment_purchase": False, "revenue_drop": False, "gst_delay_days": 0,
          "loan_repay_lump": False, "working_capital_short": False}
    p = business.personality
    seasonal = business.profile["seasonal"]

    if seasonal == "festival" and cal_month in (10, 11):
        if random.random() < 0.7:
            ev["festival_spike"] = True

    if p == "debt_stressed":
        if random.random() < 0.35: ev["cheque_bounce"] = True
        if random.random() < 0.40: ev["gst_delay_days"] = random.randint(3, 18)
        if random.random() < 0.35: ev["working_capital_short"] = True
    if p == "high_emi":
        if random.random() < 0.25: ev["cheque_bounce"] = True
        if random.random() < 0.30: ev["gst_delay_days"] = random.randint(1, 10)
    if p == "declining":
        if month_idx > 5 and random.random() < 0.4: ev["revenue_drop"] = True
        if random.random() < 0.20: ev["gst_delay_days"] = random.randint(1, 12)
    if p == "expansion_phase":
        if month_idx in (2, 5, 8) and random.random() < 0.55:
            ev["equipment_purchase"] = True
    if p == "recovery_phase":
        if random.random() < 0.25 and month_idx < 4: ev["working_capital_short"] = True
    if random.random() < 0.06:
        ev["unexpected_expense"] = True
    if business.existing_loan == "Yes" and random.random() < 0.08:
        ev["loan_repay_lump"] = True
    return ev

def generate_business_transactions(biz: Business, biz_seq: List[dict]) -> Tuple[List[dict], List[dict]]:
    """
    Generate 12 months of transactions.
    Returns (transactions, monthly_summary_rows).
    Uses biz_seq to keep global txn ordering deterministic per business.
    """
    profile = biz.profile
    txns: List[dict] = []
    monthly_rows: List[dict] = []
    balance = biz.opening_balance
    tx_counter = 0

    # Sanity anchor for monthly revenue targeting
    base_monthly_rev = random.uniform(*profile["rev_range"])

    for m_idx, (yr, mo) in enumerate(MONTHS):
        # Target revenue for this month
        seas = seasonality_multiplier(mo, profile["seasonal"])
        growth = personality_growth(biz.personality, m_idx)
        volatility_pct = profile["volatility"]
        vol = random.uniform(1 - volatility_pct, 1 + volatility_pct)
        target_rev = base_monthly_rev * seas * growth * vol

        events = month_events(biz, mo, m_idx)
        if events["festival_spike"]:
            target_rev *= random.uniform(1.20, 1.45)
        if events["revenue_drop"]:
            target_rev *= random.uniform(0.55, 0.75)

        # Expense ratio
        er_lo, er_hi = profile["expense_ratio"]
        expense_ratio = random.uniform(er_lo, er_hi)
        if biz.personality == "debt_stressed":
            expense_ratio = min(0.95, expense_ratio + 0.05)
        target_expense = target_rev * expense_ratio

        # Number of sales transactions
        n_days = month_days(yr, mo)
        density_lo, density_hi = profile["tx_density_per_day"]
        sales_txn_count = int(n_days * random.uniform(density_lo, density_hi))
        sales_txn_count = max(30, min(140, sales_txn_count))

        # Determine day distribution — weekends may boost sales for restaurants/cafes
        day_weights = []
        for d in range(1, n_days + 1):
            wd = date(yr, mo, d).weekday()  # 0=Mon
            w = 1.0
            if profile["seasonal"] == "weekend" and wd in (4, 5, 6):
                w = 1.6
            day_weights.append(w)

        # Sales side ---------------------------------------------------------
        sales_amounts = []
        remaining = target_rev
        for i in range(sales_txn_count):
            # Log-normal-ish ticket
            lo, hi = profile["avg_ticket"]
            base_ticket = random.uniform(lo, hi)
            # Occasional big invoice
            if biz.industry in ("Construction Contractor", "Furniture Manufacturer",
                                "Manufacturing Unit", "Logistics Company"):
                if random.random() < 0.05:
                    base_ticket *= random.uniform(3, 8)
            sales_amounts.append(base_ticket)
        # Scale to target
        s_sum = sum(sales_amounts)
        if s_sum <= 0:
            sales_amounts = [target_rev / sales_txn_count] * sales_txn_count
            s_sum = sum(sales_amounts)
        factor = target_rev / s_sum
        sales_amounts = [a * factor for a in sales_amounts]

        # Assign dates
        sales_days = random.choices(range(1, n_days + 1), weights=day_weights, k=sales_txn_count)

        sales_records = []
        for amt, day in zip(sales_amounts, sales_days):
            mode = choose_payment_mode(profile, is_credit=True)
            desc = make_desc("Sales", mode)
            sales_records.append((day, amt, mode, desc))

        # Expense side -------------------------------------------------------
        expense_records: List[Tuple[int, float, str, str, str]] = []  # day, amt, mode, cat, desc

        # 1. Salary — one lump on day ~1-3
        salary_amt = target_expense * random.uniform(0.20, 0.32)
        if biz.industry in ("Furniture Manufacturer", "Manufacturing Unit",
                            "Construction Contractor", "Logistics Company",
                            "Printing Press", "Automobile Workshop"):
            salary_amt = target_expense * random.uniform(0.25, 0.38)
        elif biz.industry in ("Dairy", "Grocery Store"):
            salary_amt = target_expense * random.uniform(0.10, 0.18)
        # Split into a few employee payments
        per_emp = salary_amt / max(1, biz.employee_count)
        sal_day = random.randint(1, 5)
        for _ in range(biz.employee_count):
            amt = per_emp * random.uniform(0.85, 1.15)
            expense_records.append((sal_day + random.randint(0, 2),
                                    amt,
                                    random.choice(["NEFT", "IMPS"]),
                                    "Salary",
                                    make_desc("Salary", "NEFT")))

        # 2. Rent — day 3-7
        rent_amt = target_expense * random.uniform(0.05, 0.12)
        if biz.industry in ("Hotel", "Restaurant", "Cafe", "Textile Shop", "Electronics Shop"):
            rent_amt = target_expense * random.uniform(0.07, 0.14)
        expense_records.append((random.randint(3, 7), rent_amt,
                                random.choice(["NEFT", "UPI"]), "Rent",
                                make_desc("Rent", "NEFT")))

        # 3. Electricity
        elec_amt = target_expense * random.uniform(0.02, 0.05)
        if biz.industry in ("Manufacturing Unit", "Furniture Manufacturer",
                            "Hotel", "Restaurant", "Bakery", "Dairy"):
            elec_amt = target_expense * random.uniform(0.04, 0.08)
        expense_records.append((random.randint(8, 12), elec_amt,
                                "NEFT", "Electricity",
                                make_desc("Electricity", "NEFT")))

        # 4. Internet
        expense_records.append((random.randint(10, 15),
                                random.uniform(999, 4500),
                                "UPI", "Internet",
                                make_desc("Internet", "UPI")))

        # 5. Fuel (transport/logistics/dairy/restaurant deliveries)
        if biz.industry in ("Transport Service", "Logistics Company", "Dairy",
                            "Restaurant", "Automobile Workshop"):
            fuel_share = {
                "Transport Service": 0.28, "Logistics Company": 0.30, "Dairy": 0.08,
                "Restaurant": 0.05, "Automobile Workshop": 0.06,
            }[biz.industry]
            fuel_total = target_expense * fuel_share
            n_fuel = random.randint(6, 14)
            for _ in range(n_fuel):
                expense_records.append((random.randint(1, n_days),
                                        fuel_total / n_fuel * random.uniform(0.7, 1.3),
                                        random.choice(["UPI", "Cash Withdrawal"]),
                                        "Fuel", make_desc("Fuel", "UPI")))

        # 6. Raw Material / Vendor payments — the bulk of expenses
        remaining_exp = target_expense - sum(r[1] for r in expense_records)
        if remaining_exp < 0:
            remaining_exp = target_expense * 0.3
        n_vendor = random.randint(12, 28)
        vendor_amounts = [random.uniform(0.4, 2.0) for _ in range(n_vendor)]
        vs = sum(vendor_amounts)
        vendor_amounts = [a * remaining_exp / vs for a in vendor_amounts]
        for amt in vendor_amounts:
            cat = random.choice(profile["vendor_mix"])
            if cat == "Salary":  # avoid double-count
                cat = "Vendor Payment"
            mode = choose_payment_mode(profile, is_credit=False)
            if mode == "Cash Deposit":
                mode = "Cash Withdrawal"
            expense_records.append((random.randint(1, n_days), amt, mode, cat,
                                    make_desc(cat, mode)))

        # 7. GST payment (if registered) — ~20th of month
        if biz.gst_registered == "Yes":
            gst_slab = profile["gst_slab"]
            gst_out = target_rev * gst_slab / (1 + gst_slab)  # tax component
            # Input credit approx 55-75% of output
            itc_ratio = random.uniform(0.55, 0.75)
            gst_pay = max(0, gst_out * (1 - itc_ratio))
            base_gst_day = 20
            if events["gst_delay_days"]:
                base_gst_day += events["gst_delay_days"]
            base_gst_day = min(base_gst_day, n_days)
            expense_records.append((base_gst_day, gst_pay,
                                    "NEFT", "GST",
                                    make_desc("GST", "NEFT")))

        # 8. Loan EMI
        if biz.existing_emi > 0:
            emi_day = random.randint(3, 8)
            emi_amt = biz.existing_emi
            if events["loan_repay_lump"]:
                emi_amt += biz.existing_emi * random.uniform(1, 2)
            expense_records.append((emi_day, emi_amt, "NEFT", "Loan EMI",
                                    make_desc("Loan EMI", "NEFT")))
            # Also add interest debit for CC/OD
            if random.random() < 0.5:
                expense_records.append((random.randint(25, n_days),
                                        biz.working_capital * random.uniform(0.008, 0.014),
                                        "NEFT", "Interest",
                                        make_desc("Interest", "NEFT")))

        # 9. Insurance (occasional)
        if random.random() < 0.35:
            expense_records.append((random.randint(1, n_days),
                                    random.uniform(2500, 18000),
                                    "NEFT", "Insurance",
                                    make_desc("Insurance", "NEFT")))

        # 10. Office supplies + maintenance
        for cat in ("Office Supplies", "Maintenance", "Miscellaneous"):
            n_k = random.randint(1, 4)
            for _ in range(n_k):
                expense_records.append((random.randint(1, n_days),
                                        random.uniform(500, 6000),
                                        random.choice(["UPI", "Cash Withdrawal"]),
                                        cat, make_desc(cat, "UPI")))

        # 11. Equipment purchase (event)
        if events["equipment_purchase"]:
            expense_records.append((random.randint(5, 20),
                                    target_expense * random.uniform(0.25, 0.55),
                                    "RTGS", "Vendor Payment",
                                    f"RTGS DR/EQUIPMENT PURCHASE/PO{random.randint(10000,99999)}"))

        # 12. Unexpected expense
        if events["unexpected_expense"]:
            expense_records.append((random.randint(1, n_days),
                                    target_expense * random.uniform(0.05, 0.12),
                                    "Cheque", "Miscellaneous",
                                    "MISC/UNEXPECTED EXP"))

        # Merge and order by date
        combined: List[Tuple[int, str, float, str, str, str]] = []
        for day, amt, mode, desc in sales_records:
            combined.append((day, "credit", amt, mode, "Sales", desc))
        for day, amt, mode, cat, desc in expense_records:
            combined.append((day, "debit", amt, mode, cat, desc))
        # Add a random ordering seed within each day
        combined.sort(key=lambda x: (x[0], random.random()))

        # Now write with running balance
        # month_sales_credit_total = ONLY Sales-category credits (used for GST)
        # month_credit_total       = ALL credits (used for cash-flow features)
        month_credit_total = 0.0
        month_sales_credit_total = 0.0
        month_debit_total = 0.0
        bounce_count_this_month = 0
        # Randomly pick one cheque txn to bounce if event
        bounce_target_idx = None
        if events["cheque_bounce"]:
            cheque_debit_indices = [i for i, r in enumerate(combined)
                                    if r[3] == "Cheque" and r[1] == "debit"]
            if cheque_debit_indices:
                bounce_target_idx = random.choice(cheque_debit_indices)

        # Negative-balance policy per personality.
        # safe_floor = the level below which we PRE-EMPTIVELY inject an OD
        # credit BEFORE writing the next debit, so recorded balance never dips
        # beneath it. Stressed personalities allowed to sit below zero to
        # reflect real distress; others held at a small positive cushion.
        neg_ok_personalities = {"debt_stressed", "high_emi", "declining", "recovery_phase"}
        if biz.personality in neg_ok_personalities:
            safe_floor = -biz.working_capital * 0.75
        else:
            safe_floor = biz.working_capital * 0.02  # small positive cushion

        def inject_od(current_bal: float, breach_amount: float, day_for_inject: int):
            """Inject an OD-utilisation credit that lifts current_bal back
            to (safe_floor + comfort). breach_amount is how far short we are.
            Returns (new_balance, tx_dict)."""
            comfort = biz.working_capital * random.uniform(0.10, 0.25)
            inj = breach_amount + comfort
            new_bal = current_bal + inj
            return new_bal, {
                "credit": inj, "day": day_for_inject,
                "desc": "OD LIMIT UTILISATION/CC ACCT",
                "mode": "NEFT", "category": "Miscellaneous",
            }

        for i, (day, side, amt, mode, cat, desc) in enumerate(combined):
            # Pre-emptive OD check for debits that would breach safe_floor.
            if side == "debit" and (balance - amt) < safe_floor:
                shortfall = safe_floor - (balance - amt)  # positive
                balance, od_row = inject_od(balance, shortfall, day)
                tx_counter += 1
                month_credit_total += od_row["credit"]
                txns.append({
                    "Transaction_ID": f"{biz.business_id}-T{tx_counter:06d}",
                    "Business_ID": biz.business_id,
                    "Date": date(yr, mo, od_row["day"]).isoformat(),
                    "Description": od_row["desc"],
                    "Transaction_Type": "Credit",
                    "Payment_Mode": od_row["mode"],
                    "Category": od_row["category"],
                    "Credit": r2(od_row["credit"]),
                    "Debit": 0.0,
                    "Running_Balance": r2(balance),
                })

            tx_counter += 1
            d = date(yr, mo, day)
            credit = 0.0
            debit = 0.0
            if side == "credit":
                credit = amt
                balance += amt
                month_credit_total += amt
                if cat == "Sales":
                    month_sales_credit_total += amt
            else:
                debit = amt
                balance -= amt
                month_debit_total += amt

            txn_id = f"{biz.business_id}-T{tx_counter:06d}"
            txns.append({
                "Transaction_ID": txn_id,
                "Business_ID": biz.business_id,
                "Date": d.isoformat(),
                "Description": desc,
                "Transaction_Type": "Credit" if side == "credit" else "Debit",
                "Payment_Mode": mode,
                "Category": cat,
                "Credit": r2(credit),
                "Debit": 0.0 if side == "credit" else r2(debit),
                "Running_Balance": r2(balance),
            })

            # Cheque bounce entry: original debit clears, then reverses with charge
            if i == bounce_target_idx:
                # Reversal same day + 2 (typical clearing bounce)
                bounce_day = min(day + 2, n_days)
                bd = date(yr, mo, bounce_day)
                # reversal credit
                balance += amt
                tx_counter += 1
                txns.append({
                    "Transaction_ID": f"{biz.business_id}-T{tx_counter:06d}",
                    "Business_ID": biz.business_id,
                    "Date": bd.isoformat(),
                    "Description": f"CHQ RETURN/{desc.split('/')[-1]}/INSUFF FUNDS",
                    "Transaction_Type": "Credit",
                    "Payment_Mode": "Cheque",
                    "Category": "Miscellaneous",
                    "Credit": r2(amt),
                    "Debit": 0.0,
                    "Running_Balance": r2(balance),
                })
                # Bounce charge debit
                charge = random.uniform(350, 750)
                balance -= charge
                tx_counter += 1
                month_debit_total += charge
                txns.append({
                    "Transaction_ID": f"{biz.business_id}-T{tx_counter:06d}",
                    "Business_ID": biz.business_id,
                    "Date": bd.isoformat(),
                    "Description": "CHQ RETURN CHARGE",
                    "Transaction_Type": "Debit",
                    "Payment_Mode": "Cheque",
                    "Category": "Miscellaneous",
                    "Credit": 0.0,
                    "Debit": r2(charge),
                    "Running_Balance": r2(balance),
                })
                bounce_count_this_month += 1

        # End-of-month cushion: if bounce charge or reversal-charge left balance
        # below safe_floor, top up. Cheque reversals/charges bypass the
        # pre-emptive check because they run inside the bounce block.
        if balance < safe_floor:
            shortfall = safe_floor - balance
            balance, od_row = inject_od(balance, shortfall, n_days)
            tx_counter += 1
            month_credit_total += od_row["credit"]
            txns.append({
                "Transaction_ID": f"{biz.business_id}-T{tx_counter:06d}",
                "Business_ID": biz.business_id,
                "Date": date(yr, mo, od_row["day"]).isoformat(),
                "Description": od_row["desc"],
                "Transaction_Type": "Credit",
                "Payment_Mode": od_row["mode"],
                "Category": od_row["category"],
                "Credit": r2(od_row["credit"]),
                "Debit": 0.0,
                "Running_Balance": r2(balance),
            })

        # Monthly summary row for feature engineering
        # Revenue used for GST must be Sales-only (not all credits — OD injections
        # and bounce reversals inflate the total but aren't taxable sales).
        monthly_rows.append({
            "Business_ID": biz.business_id,
            "Year": yr,
            "Month": mo,
            "Month_Idx": m_idx,
            "Revenue": r2(month_credit_total),          # all credits (cash-flow view)
            "Sales_Revenue": r2(month_sales_credit_total),  # taxable sales only
            "Expense": r2(month_debit_total),
            "End_Balance": r2(balance),
            "Bounces": bounce_count_this_month,
            "GST_Delay_Days": events["gst_delay_days"],
            "N_Txns": 0,  # not used downstream; O(n^2) skipped for perf
        })

    return txns, monthly_rows

# ---------------------------------------------------------------------------
# GST summary
# ---------------------------------------------------------------------------
def generate_gst_rows(biz: Business, monthly: List[dict]) -> List[dict]:
    if biz.gst_registered != "Yes":
        return []
    rows = []
    slab = biz.profile["gst_slab"]
    for row in monthly:
        yr, mo = row["Year"], row["Month"]
        # Use Sales-category credits only for GST — excludes OD utilisation,
        # bounce reversals, and other non-taxable credit entries.
        gross_sales = row["Sales_Revenue"]
        # taxable = gross / (1+slab); GST output = gross - taxable
        taxable = gross_sales / (1 + slab)
        gst_output = gross_sales - taxable
        itc_ratio = random.uniform(0.55, 0.75)
        itc = gst_output * itc_ratio
        liability = max(0, gst_output - itc)
        # Filing dates: due 20th of next month (GSTR-3B)
        if mo == 12:
            due = date(yr + 1, 1, 20)
        else:
            due = date(yr, mo + 1, 20)
        delay = row["GST_Delay_Days"]
        filed = due + timedelta(days=delay)
        filed_on_time = "Yes" if delay == 0 else "No"
        refund = 0.0
        if itc > gst_output:  # net input
            refund = itc - gst_output
        rows.append({
            "Business_ID": biz.business_id,
            "Month": f"{yr:04d}-{mo:02d}",
            "Sales": r2(gross_sales),
            "Taxable_Sales": r2(taxable),
            "GST_Paid": r2(liability),
            "GST_Liability": r2(liability),
            "Return_Filing_Date": filed.isoformat(),
            "Filed_On_Time": filed_on_time,
            "Late_Days": delay,
            "Input_Tax_Credit": r2(itc),
            "Output_Tax": r2(gst_output),
            "Refund": r2(refund),
        })
    return rows

# ---------------------------------------------------------------------------
# Feature engineering
# ---------------------------------------------------------------------------
def stddev(xs: List[float]) -> float:
    if len(xs) < 2:
        return 0.0
    m = sum(xs) / len(xs)
    var = sum((x - m) ** 2 for x in xs) / (len(xs) - 1)
    return math.sqrt(var)

def engineer_features(biz: Business, txns: List[dict], monthly: List[dict], gst_rows: List[dict]) -> dict:
    revenues = [r["Revenue"] for r in monthly]
    expenses = [r["Expense"] for r in monthly]
    end_balances = [r["End_Balance"] for r in monthly]
    all_balances = [t["Running_Balance"] for t in txns]

    avg_rev = sum(revenues) / len(revenues)
    avg_exp = sum(expenses) / len(expenses)
    expense_ratio = avg_exp / avg_rev if avg_rev else 1.0
    avg_bal = sum(all_balances) / len(all_balances) if all_balances else 0.0
    min_bal = min(all_balances) if all_balances else 0.0
    max_bal = max(all_balances) if all_balances else 0.0
    daily_burn = avg_exp / 30.0
    cash_buffer_days = avg_bal / daily_burn if daily_burn > 0 else 0

    rev_mean = avg_rev
    rev_sd = stddev(revenues)
    income_volatility = rev_sd / rev_mean if rev_mean else 1.0

    # Revenue growth: last-3 vs first-3
    first_q = sum(revenues[:3]) / 3
    last_q = sum(revenues[-3:]) / 3
    revenue_growth = (last_q - first_q) / first_q if first_q else 0.0

    # GST regularity: fraction filed on time
    if gst_rows:
        on_time = sum(1 for g in gst_rows if g["Filed_On_Time"] == "Yes")
        gst_score = on_time / len(gst_rows)
    else:
        gst_score = 0.5  # unregistered — neutral-low signal

    bounce_count = sum(m["Bounces"] for m in monthly)

    savings = [r - e for r, e in zip(revenues, expenses)]
    monthly_savings_rate = (sum(savings) / len(savings)) / avg_rev if avg_rev else 0.0

    emi_ratio = biz.existing_emi / avg_rev if avg_rev else 0.0

    credit_freq = sum(1 for t in txns if t["Transaction_Type"] == "Credit") / 12
    debit_freq = sum(1 for t in txns if t["Transaction_Type"] == "Debit") / 12
    cash_credits = sum(t["Credit"] for t in txns if t["Payment_Mode"] == "Cash Deposit")
    total_credits = sum(t["Credit"] for t in txns) or 1.0
    cash_deposit_ratio = cash_credits / total_credits
    digital_modes = ("UPI", "IMPS", "NEFT", "RTGS")
    digital_total = sum(t["Credit"] + t["Debit"] for t in txns if t["Payment_Mode"] in digital_modes)
    all_total = sum(t["Credit"] + t["Debit"] for t in txns) or 1.0
    digital_ratio = digital_total / all_total

    # Business Stability Index (0..1): combines low volatility, positive savings, positive growth
    stability = max(0.0, min(1.0,
        0.5 * (1 - min(income_volatility, 1.0))
        + 0.3 * max(0, monthly_savings_rate)  # positive savings good
        + 0.2 * (1 if revenue_growth >= 0 else 0.4)
    ))
    growth_index = max(-1.0, min(1.0, revenue_growth))
    # Liquidity: cash buffer days scaled + min balance not too negative
    liq = max(0.0, min(1.0,
        0.6 * min(cash_buffer_days / 60.0, 1.0)  # 60d buffer = full
        + 0.4 * (1.0 if min_bal >= 0 else max(0.0, 1 + min_bal / max(1.0, biz.working_capital)))
    ))

    return {
        "Business_ID": biz.business_id,
        "Business_Name": biz.business_name,
        "Industry": biz.industry,
        "Average_Monthly_Revenue": r2(avg_rev),
        "Average_Monthly_Expense": r2(avg_exp),
        "Expense_Ratio": round(expense_ratio, 4),
        "Cash_Buffer_Days": round(cash_buffer_days, 2),
        "Average_Balance": r2(avg_bal),
        "Minimum_Balance": r2(min_bal),
        "Maximum_Balance": r2(max_bal),
        "Income_Volatility": round(income_volatility, 4),
        "Revenue_Growth": round(revenue_growth, 4),
        "GST_Regularity_Score": round(gst_score, 4),
        "Bounce_Count": bounce_count,
        "Monthly_Savings_Rate": round(monthly_savings_rate, 4),
        "EMI_Ratio": round(emi_ratio, 4),
        "Credit_Frequency": round(credit_freq, 2),
        "Debit_Frequency": round(debit_freq, 2),
        "Cash_Deposit_Ratio": round(cash_deposit_ratio, 4),
        "Digital_Payment_Ratio": round(digital_ratio, 4),
        "Business_Stability_Index": round(stability, 4),
        "Growth_Index": round(growth_index, 4),
        "Liquidity_Score": round(liq, 4),
    }

# ---------------------------------------------------------------------------
# Credit scoring — deterministic underwriting logic
# ---------------------------------------------------------------------------
def credit_label(biz: Business, feats: dict) -> dict:
    score = 50.0
    reasons = []

    # Revenue stability (0-15)
    vol = feats["Income_Volatility"]
    stab_pts = max(0.0, 15 * (1 - min(vol, 1.0)))
    score += stab_pts
    reasons.append(f"Volatility {vol:.2f} → +{stab_pts:.1f}")

    # Cash buffer (0-12)
    buf = feats["Cash_Buffer_Days"]
    buf_pts = min(12.0, buf / 5.0)  # 60d = 12
    score += buf_pts
    reasons.append(f"Buffer {buf:.1f}d → +{buf_pts:.1f}")

    # Expense ratio (bad if >0.90) (-10 to +6)
    er = feats["Expense_Ratio"]
    if er < 0.75:
        er_pts = 6.0
    elif er < 0.85:
        er_pts = 3.0
    elif er < 0.92:
        er_pts = -2.0
    else:
        er_pts = -10.0
    score += er_pts
    reasons.append(f"ExpRatio {er:.2f} → {er_pts:+.1f}")

    # EMI burden (0 to -12)
    emi_r = feats["EMI_Ratio"]
    if emi_r == 0:
        emi_pts = 2.0
    elif emi_r < 0.10:
        emi_pts = 0.0
    elif emi_r < 0.18:
        emi_pts = -4.0
    elif emi_r < 0.25:
        emi_pts = -8.0
    else:
        emi_pts = -12.0
    score += emi_pts
    reasons.append(f"EMI ratio {emi_r:.2f} → {emi_pts:+.1f}")

    # Growth (-5 to +8)
    g = feats["Revenue_Growth"]
    if g > 0.20:
        gp = 8.0
    elif g > 0.05:
        gp = 5.0
    elif g > -0.05:
        gp = 1.0
    elif g > -0.15:
        gp = -3.0
    else:
        gp = -6.0
    score += gp
    reasons.append(f"Growth {g:.2f} → {gp:+.1f}")

    # GST regularity (0 to +8)
    gst_pts = 8.0 * feats["GST_Regularity_Score"]
    score += gst_pts
    reasons.append(f"GST reg {feats['GST_Regularity_Score']:.2f} → +{gst_pts:.1f}")

    # Bounces (0 to -12)
    b = feats["Bounce_Count"]
    b_pts = -min(12.0, b * 3.0)
    score += b_pts
    reasons.append(f"Bounces {b} → {b_pts:+.1f}")

    # Min balance (negative -> penalty)
    if feats["Minimum_Balance"] < 0:
        mb_pts = -6.0
    elif feats["Minimum_Balance"] < biz.working_capital * 0.1:
        mb_pts = -2.0
    else:
        mb_pts = 3.0
    score += mb_pts
    reasons.append(f"MinBal → {mb_pts:+.1f}")

    # Business age (0 to +6)
    age_pts = min(6.0, biz.business_age * 0.5)
    score += age_pts

    # Savings rate (-4 to +5)
    s = feats["Monthly_Savings_Rate"]
    if s > 0.12:
        s_pts = 5.0
    elif s > 0.05:
        s_pts = 3.0
    elif s > 0:
        s_pts = 1.0
    elif s > -0.05:
        s_pts = -2.0
    else:
        s_pts = -4.0
    score += s_pts

    # Digital adoption (+0 to +3)
    score += 3.0 * feats["Digital_Payment_Ratio"]

    # Clip
    score = max(5.0, min(100.0, score))

    # Confidence: based on data spread (lower volatility = higher confidence)
    conf = max(0.55, min(0.98, 0.95 - 0.35 * min(vol, 1.0) + 0.05 * feats["GST_Regularity_Score"]))

    # Risk category & decision
    if score >= 75:
        risk = "Low"
        decision = "Approve"
    elif score >= 55:
        risk = "Medium"
        decision = "Conditional Approval"
    else:
        risk = "High"
        decision = "Reject"

    # Recommended loan amount: multiple of avg monthly revenue, adjusted by risk
    avg_rev = feats["Average_Monthly_Revenue"]
    if risk == "Low":
        rec_amt = avg_rev * random.uniform(4.0, 6.0)
        tenure = random.choice([36, 48, 60])
        rate_band = "10.5% - 12.5%"
    elif risk == "Medium":
        rec_amt = avg_rev * random.uniform(2.0, 3.5)
        tenure = random.choice([24, 36, 48])
        rate_band = "13.0% - 15.5%"
    else:
        rec_amt = avg_rev * random.uniform(0.5, 1.5)
        tenure = random.choice([12, 18, 24])
        rate_band = "16.0% - 20.0%"

    # If reject, still provide a small recommended amount for future review, but flag as 0 if very high risk
    if decision == "Reject" and score < 40:
        rec_amt = 0.0
        tenure = 0
        rate_band = "N/A"

    return {
        "Business_ID": biz.business_id,
        "Business_Name": biz.business_name,
        "Financial_Health_Score": round(score, 2),
        "Risk_Category": risk,
        "Confidence": round(conf, 3),
        "Recommended_Loan_Amount": r2(rec_amt),
        "Recommended_Tenure_Months": tenure,
        "Recommended_Interest_Band": rate_band,
        "Approval_Decision": decision,
        "Scoring_Rationale": " | ".join(reasons),
    }

# ---------------------------------------------------------------------------
# Writers
# ---------------------------------------------------------------------------
def write_csv(path: str, rows: List[dict], fieldnames: List[str], append: bool = False):
    mode = "a" if append and os.path.exists(path) else "w"
    with open(path, mode, newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        if mode == "w":
            w.writeheader()
        for r in rows:
            w.writerow(r)

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Generate synthetic MSME dataset.")
    parser.add_argument("--count", type=int, default=25,
                        help="How many businesses to generate (default 25)")
    parser.add_argument("--start-id", type=int, default=1,
                        help="Starting numeric Business_ID suffix (default 1 -> MSME001)")
    parser.add_argument("--seed", type=int, default=SEED,
                        help=f"Random seed (default {SEED})")
    parser.add_argument("--append", action="store_true",
                        help="Append to existing CSVs instead of overwriting")
    parser.add_argument("--suffix", type=str, default="",
                        help="Optional filename suffix, e.g. '_batch2' -> businesses_batch2.csv")
    args = parser.parse_args()

    # Re-seed based on CLI arg
    random.seed(args.seed)

    businesses = generate_businesses(count=args.count, start_id=args.start_id)

    biz_rows = []
    all_txns = []
    all_gst = []
    all_feats = []
    all_labels = []
    per_biz_monthly = {}

    for biz in businesses:
        txns, monthly = generate_business_transactions(biz, [])
        gst_rows = generate_gst_rows(biz, monthly)
        feats = engineer_features(biz, txns, monthly, gst_rows)
        label = credit_label(biz, feats)

        all_txns.extend(txns)
        all_gst.extend(gst_rows)
        all_feats.append(feats)
        all_labels.append(label)
        per_biz_monthly[biz.business_id] = monthly

        biz_rows.append({
            "Business_ID": biz.business_id,
            "Business_Name": biz.business_name,
            "Owner_Name": f"{biz.owner_first} {biz.owner_last}",
            "Industry": biz.industry,
            "City": biz.city,
            "State": biz.state,
            "Business_Age_Years": biz.business_age,
            "Owner_Age": biz.owner_age,
            "Employee_Count": biz.employee_count,
            "Monthly_Operating_Days": biz.monthly_operating_days,
            "Average_Daily_Customers": biz.average_daily_customers,
            "Annual_Turnover_INR": biz.annual_turnover,
            "GST_Registered": biz.gst_registered,
            "Existing_Loan": biz.existing_loan,
            "Existing_EMI_INR": biz.existing_emi,
            "Working_Capital_INR": biz.working_capital,
            "Credit_Limit_INR": biz.credit_limit,
            "Business_Category": biz.business_category,
            "Personality_Tag": biz.personality,
            "Opening_Balance_INR": biz.opening_balance,
        })

    # -----------------------------------------------------------------------
    # DETERMINISTIC RUNNING-BALANCE REBUILD (indexed, O(N))
    # -----------------------------------------------------------------------
    # Index transactions by business_id in one pass, then rebuild balances.
    from collections import defaultdict as _dd
    tx_by_biz = _dd(list)
    for t in all_txns:
        tx_by_biz[t["Business_ID"]].append(t)
    for biz in businesses:
        biz_tx = sorted(
            tx_by_biz[biz.business_id],
            key=lambda t: (t["Date"], int(t["Transaction_ID"].split("T")[-1]))
        )
        bal = biz.opening_balance
        for t in biz_tx:
            bal += t["Credit"] - t["Debit"]
            t["Running_Balance"] = r2(bal)

    # -----------------------------------------------------------------------
    # WRITE CSVs
    # -----------------------------------------------------------------------
    sfx = args.suffix
    def out(name): return os.path.join(OUT_DIR, f"{name}{sfx}.csv")
    ap = args.append

    write_csv(out("businesses"), biz_rows, list(biz_rows[0].keys()), append=ap)

    all_txns.sort(key=lambda t: (t["Business_ID"], t["Date"],
                                 int(t["Transaction_ID"].split("T")[-1])))
    write_csv(out("bank_transactions"), all_txns,
              ["Transaction_ID", "Business_ID", "Date", "Description",
               "Transaction_Type", "Payment_Mode", "Category",
               "Credit", "Debit", "Running_Balance"], append=ap)

    write_csv(out("gst_summary"), all_gst,
              ["Business_ID", "Month", "Sales", "Taxable_Sales", "GST_Paid",
               "GST_Liability", "Return_Filing_Date", "Filed_On_Time",
               "Late_Days", "Input_Tax_Credit", "Output_Tax", "Refund"], append=ap)

    write_csv(out("engineered_features"), all_feats,
              list(all_feats[0].keys()), append=ap)
    write_csv(out("credit_labels"), all_labels,
              list(all_labels[0].keys()), append=ap)

    print("=" * 70)
    print(f"Generated {len(businesses)} businesses (IDs {businesses[0].business_id}..{businesses[-1].business_id})")
    print(f"Total transactions: {len(all_txns):,}")
    print(f"Total GST rows: {len(all_gst):,}")
    print(f"Total feature rows: {len(all_feats):,}")
    print(f"Total labels: {len(all_labels):,}")
    from collections import Counter
    dec_c = Counter(l["Approval_Decision"] for l in all_labels)
    risk_c = Counter(l["Risk_Category"] for l in all_labels)
    print(f"Decisions: {dict(dec_c)}")
    print(f"Risk buckets: {dict(risk_c)}")
    scores = [l["Financial_Health_Score"] for l in all_labels]
    print(f"Score min/mean/max: {min(scores):.1f} / {sum(scores)/len(scores):.1f} / {max(scores):.1f}")
    print(f"\nMode: {'APPEND' if ap else 'OVERWRITE'} | Suffix: {sfx!r} | Seed: {args.seed}")

if __name__ == "__main__":
    main()
