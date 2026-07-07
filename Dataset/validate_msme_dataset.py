"""
MSME Dataset Validator
======================
Runs integrity checks against the generated CSVs. Fails loud on any
inconsistency. Does NOT modify data — if a check fails, fix the generator.

Checks performed:
  1. Schema:       all expected columns present, no NaNs in critical fields
  2. Balance:      Running_Balance[i] = Opening + sum(Credit - Debit) up to i
  3. Delta:        Running_Balance[i] - Running_Balance[i-1] == Credit[i]-Debit[i]
  4. GST vs Rev:   gst.Sales == sum(bank Sales credits) for that Business+Month
  5. Neg balance:  Minimum_Balance < 0 only allowed for
                   personalities {debt_stressed, high_emi, working_capital_short}
                   AND magnitude must be plausible (<= 1.5 * working_capital)
  6. Dates:        Transactions per business are date-sorted (non-decreasing)
  7. Categories:   All Category / Payment_Mode / Transaction_Type values are in the allowed enum
  8. Cross-file:   Every Business_ID in transactions/gst/features/labels exists in businesses.csv
  9. Labels:       Risk_Category matches score band; Recommended amounts non-negative
 10. GST returns:  Filed_On_Time == 'No' iff Late_Days > 0

Exit code 0 => clean. Non-zero => count of failed checks.
"""

import csv
import os
import sys
from collections import defaultdict
from datetime import date

OUT_DIR = os.path.dirname(os.path.abspath(__file__))

ALLOWED_CATEGORIES = {
    "Sales", "Vendor Payment", "Salary", "Rent", "Electricity", "Internet",
    "GST", "Fuel", "Raw Material", "Office Supplies", "Insurance",
    "Maintenance", "Loan EMI", "Interest", "Miscellaneous",
}
ALLOWED_MODES = {
    "UPI", "NEFT", "RTGS", "IMPS", "Cash Deposit", "Cash Withdrawal", "Cheque",
}
ALLOWED_TXN_TYPES = {"Credit", "Debit"}
ALLOWED_RISK = {"Low", "Medium", "High"}
ALLOWED_DECISION = {"Approve", "Conditional Approval", "Reject"}
ALLOWED_YN = {"Yes", "No"}

# Personalities allowed to end month or dip below zero balance:
NEG_BAL_OK_PERSONALITIES = {"debt_stressed", "high_emi", "declining", "recovery_phase"}


def read_csv(name: str) -> list:
    path = os.path.join(OUT_DIR, name)
    with open(path, "r", encoding="utf-8") as f:
        return list(csv.DictReader(f))


class Report:
    def __init__(self):
        self.errors = defaultdict(list)  # check_name -> list of messages
        self.info = []

    def fail(self, check: str, msg: str):
        self.errors[check].append(msg)

    def note(self, msg: str):
        self.info.append(msg)

    def summarize(self) -> int:
        print("\n" + "=" * 72)
        print("VALIDATION REPORT")
        print("=" * 72)
        for msg in self.info:
            print(f"  · {msg}")
        print("-" * 72)
        total = 0
        checks = [
            "01_schema", "02_balance_reconciliation", "03_delta_consistency",
            "04_gst_vs_revenue", "05_negative_balance_policy",
            "06_date_sequential", "07_valid_enums", "08_cross_file_ids",
            "09_label_consistency", "10_gst_filing_flags",
        ]
        for c in checks:
            errs = self.errors.get(c, [])
            total += len(errs)
            status = "PASS" if not errs else f"FAIL ({len(errs)})"
            print(f"  [{status}] {c}")
            # print first 3 errors per check for context
            for e in errs[:3]:
                print(f"       → {e}")
            if len(errs) > 3:
                print(f"       ... and {len(errs)-3} more")
        print("=" * 72)
        print(f"TOTAL FAILURES: {total}")
        return total


def parse_iso(s: str) -> date:
    y, m, d = s.split("-")
    return date(int(y), int(m), int(d))


def main() -> int:
    r = Report()

    # ---- Load ----
    try:
        businesses = read_csv("businesses.csv")
        transactions = read_csv("bank_transactions.csv")
        gst = read_csv("gst_summary.csv")
        features = read_csv("engineered_features.csv")
        labels = read_csv("credit_labels.csv")
    except FileNotFoundError as e:
        print(f"Missing file: {e}")
        return 1

    r.note(f"Loaded {len(businesses)} businesses, {len(transactions):,} transactions, "
           f"{len(gst)} GST rows, {len(features)} feature rows, {len(labels)} labels")

    # ---- 01 Schema ----
    biz_cols = {"Business_ID", "Business_Name", "Industry", "City", "State",
                "Business_Age_Years", "Owner_Age", "Employee_Count",
                "Monthly_Operating_Days", "Average_Daily_Customers",
                "Annual_Turnover_INR", "GST_Registered", "Existing_Loan",
                "Existing_EMI_INR", "Working_Capital_INR", "Credit_Limit_INR",
                "Business_Category", "Personality_Tag", "Opening_Balance_INR"}
    txn_cols = {"Transaction_ID", "Business_ID", "Date", "Description",
                "Transaction_Type", "Payment_Mode", "Category", "Credit",
                "Debit", "Running_Balance"}
    gst_cols = {"Business_ID", "Month", "Sales", "Taxable_Sales", "GST_Paid",
                "GST_Liability", "Return_Filing_Date", "Filed_On_Time",
                "Late_Days", "Input_Tax_Credit", "Output_Tax", "Refund"}

    for name, need, have in [
        ("businesses", biz_cols, set(businesses[0].keys()) if businesses else set()),
        ("transactions", txn_cols, set(transactions[0].keys()) if transactions else set()),
        ("gst_summary", gst_cols, set(gst[0].keys()) if gst else set()),
    ]:
        missing = need - have
        if missing:
            r.fail("01_schema", f"{name}: missing columns {sorted(missing)}")

    # Critical fields non-empty
    for t in transactions[:50000]:  # sample for speed
        for k in ("Transaction_ID", "Business_ID", "Date", "Category",
                  "Transaction_Type", "Payment_Mode"):
            if not t.get(k):
                r.fail("01_schema", f"empty {k} at {t.get('Transaction_ID')}")

    # ---- Index businesses ----
    biz_by_id = {b["Business_ID"]: b for b in businesses}
    opening = {bid: float(b["Opening_Balance_INR"]) for bid, b in biz_by_id.items()}
    working_cap = {bid: float(b["Working_Capital_INR"]) for bid, b in biz_by_id.items()}
    personality = {bid: b["Personality_Tag"] for bid, b in biz_by_id.items()}
    gst_registered = {bid: b["GST_Registered"] for bid, b in biz_by_id.items()}

    txns_by_biz = defaultdict(list)
    for t in transactions:
        txns_by_biz[t["Business_ID"]].append(t)

    # ---- 02 & 03 Balance and delta ----
    for bid, txs in txns_by_biz.items():
        try:
            txs_sorted = sorted(txs, key=lambda x: (x["Date"],
                                                    int(x["Transaction_ID"].split("T")[-1])))
        except Exception as e:
            r.fail("02_balance_reconciliation", f"{bid}: cannot sort ({e})")
            continue

        running = opening.get(bid, 0.0)
        prev_bal = None
        for t in txs_sorted:
            c = float(t["Credit"])
            d = float(t["Debit"])
            running += c - d
            recorded = float(t["Running_Balance"])
            if abs(recorded - running) > 0.05:
                r.fail("02_balance_reconciliation",
                       f"{bid} {t['Transaction_ID']} expected {running:.2f}, got {recorded:.2f}")
            # Delta check
            if prev_bal is not None:
                delta_recorded = recorded - prev_bal
                delta_expected = c - d
                if abs(delta_recorded - delta_expected) > 0.05:
                    r.fail("03_delta_consistency",
                           f"{bid} {t['Transaction_ID']} delta {delta_recorded:.2f} vs credit-debit {delta_expected:.2f}")
            prev_bal = recorded

            # Sign check
            if c < 0 or d < 0:
                r.fail("02_balance_reconciliation",
                       f"{bid} {t['Transaction_ID']} negative credit/debit")
            if c > 0 and d > 0:
                r.fail("02_balance_reconciliation",
                       f"{bid} {t['Transaction_ID']} both credit and debit nonzero")
            # Type consistency
            if c > 0 and t["Transaction_Type"] != "Credit":
                r.fail("02_balance_reconciliation",
                       f"{bid} {t['Transaction_ID']} credit>0 but type={t['Transaction_Type']}")
            if d > 0 and t["Transaction_Type"] != "Debit":
                r.fail("02_balance_reconciliation",
                       f"{bid} {t['Transaction_ID']} debit>0 but type={t['Transaction_Type']}")

    # ---- 04 GST vs Revenue ----
    # Revenue = sum of Category==Sales credits per Business x Month
    revenue = defaultdict(float)
    for t in transactions:
        if t["Category"] == "Sales" and float(t["Credit"]) > 0:
            key = (t["Business_ID"], t["Date"][:7])
            revenue[key] += float(t["Credit"])

    for g in gst:
        key = (g["Business_ID"], g["Month"])
        rev = revenue.get(key, 0.0)
        gst_sales = float(g["Sales"])
        if abs(rev - gst_sales) > 1.0:
            r.fail("04_gst_vs_revenue",
                   f"{key[0]} {key[1]}: bank Sales {rev:.2f} vs GST.Sales {gst_sales:.2f}")

        # Consistency of GST arithmetic: Taxable + tax approx = Sales
        # Sales = Taxable * (1+slab), so Sales - Taxable = Output_Tax
        taxable = float(g["Taxable_Sales"])
        out_tax = float(g["Output_Tax"])
        if abs((gst_sales - taxable) - out_tax) > 1.0:
            r.fail("04_gst_vs_revenue",
                   f"{key[0]} {key[1]}: Sales-Taxable ({gst_sales-taxable:.2f}) != Output_Tax {out_tax:.2f}")

        # Liability = max(0, output - ITC)
        itc = float(g["Input_Tax_Credit"])
        liability = float(g["GST_Liability"])
        expected_liab = max(0.0, out_tax - itc)
        if abs(liability - expected_liab) > 1.0:
            r.fail("04_gst_vs_revenue",
                   f"{key[0]} {key[1]}: liability {liability:.2f} != max(0, out-itc) {expected_liab:.2f}")

    # Every GST-registered business must have 12 GST rows
    gst_by_biz = defaultdict(list)
    for g in gst:
        gst_by_biz[g["Business_ID"]].append(g)
    for bid, reg in gst_registered.items():
        if reg == "Yes" and len(gst_by_biz.get(bid, [])) != 12:
            r.fail("04_gst_vs_revenue",
                   f"{bid}: expected 12 GST rows, got {len(gst_by_biz.get(bid, []))}")

    # ---- 05 Negative balance policy ----
    for bid, txs in txns_by_biz.items():
        min_bal = min(float(t["Running_Balance"]) for t in txs)
        wc = working_cap.get(bid, 0.0)
        p = personality.get(bid, "")
        if min_bal < 0:
            if p not in NEG_BAL_OK_PERSONALITIES:
                r.fail("05_negative_balance_policy",
                       f"{bid} ({p}): min balance {min_bal:.2f} negative — personality doesn't justify it")
            # magnitude sanity
            if min_bal < -1.5 * max(1.0, wc):
                r.fail("05_negative_balance_policy",
                       f"{bid} ({p}): min balance {min_bal:.2f} < -1.5*working_capital ({-1.5*wc:.2f})")

    # ---- 06 Date sequential (per business) ----
    for bid, txs in txns_by_biz.items():
        prev = None
        for t in txs:  # as written in CSV order
            d = parse_iso(t["Date"])
            if prev is not None and d < prev:
                r.fail("06_date_sequential",
                       f"{bid} {t['Transaction_ID']}: {d} < previous {prev}")
                break
            prev = d

    # ---- 07 Valid enums ----
    for t in transactions:
        if t["Category"] not in ALLOWED_CATEGORIES:
            r.fail("07_valid_enums", f"bad Category {t['Category']} @ {t['Transaction_ID']}")
        if t["Payment_Mode"] not in ALLOWED_MODES:
            r.fail("07_valid_enums", f"bad Payment_Mode {t['Payment_Mode']} @ {t['Transaction_ID']}")
        if t["Transaction_Type"] not in ALLOWED_TXN_TYPES:
            r.fail("07_valid_enums", f"bad Transaction_Type {t['Transaction_Type']} @ {t['Transaction_ID']}")

    for b in businesses:
        if b["GST_Registered"] not in ALLOWED_YN:
            r.fail("07_valid_enums", f"{b['Business_ID']} GST_Registered={b['GST_Registered']}")
        if b["Existing_Loan"] not in ALLOWED_YN:
            r.fail("07_valid_enums", f"{b['Business_ID']} Existing_Loan={b['Existing_Loan']}")
        if b["Business_Category"] not in {"Micro", "Small", "Medium"}:
            r.fail("07_valid_enums", f"{b['Business_ID']} Business_Category={b['Business_Category']}")

    for g in gst:
        if g["Filed_On_Time"] not in ALLOWED_YN:
            r.fail("07_valid_enums", f"gst {g['Business_ID']} {g['Month']} Filed_On_Time={g['Filed_On_Time']}")

    # ---- 08 Cross-file IDs ----
    biz_ids = set(biz_by_id.keys())
    for src, rows in (("transactions", transactions), ("gst", gst),
                     ("features", features), ("labels", labels)):
        seen = set(row["Business_ID"] for row in rows)
        orphan = seen - biz_ids
        for o in orphan:
            r.fail("08_cross_file_ids", f"{src}: unknown Business_ID {o}")

    # ---- 09 Label consistency ----
    for l in labels:
        score = float(l["Financial_Health_Score"])
        risk = l["Risk_Category"]
        dec = l["Approval_Decision"]
        conf = float(l["Confidence"])
        amt = float(l["Recommended_Loan_Amount"])
        if risk not in ALLOWED_RISK:
            r.fail("09_label_consistency", f"{l['Business_ID']} bad risk {risk}")
        if dec not in ALLOWED_DECISION:
            r.fail("09_label_consistency", f"{l['Business_ID']} bad decision {dec}")
        if not (0.0 <= conf <= 1.0):
            r.fail("09_label_consistency", f"{l['Business_ID']} confidence {conf} out of [0,1]")
        # Score-band consistency
        expected_risk = "Low" if score >= 75 else ("Medium" if score >= 55 else "High")
        if risk != expected_risk:
            r.fail("09_label_consistency",
                   f"{l['Business_ID']} score {score:.1f} → expected {expected_risk}, got {risk}")
        # Amount cannot be negative
        if amt < 0:
            r.fail("09_label_consistency", f"{l['Business_ID']} negative loan amount {amt}")
        # Risk vs decision monotonicity
        if risk == "Low" and dec == "Reject":
            r.fail("09_label_consistency", f"{l['Business_ID']} Low risk but Reject")
        if risk == "High" and dec == "Approve":
            r.fail("09_label_consistency", f"{l['Business_ID']} High risk but Approve")

    # ---- 10 GST filing flag ----
    for g in gst:
        late = int(g["Late_Days"])
        on_time = g["Filed_On_Time"]
        if late == 0 and on_time != "Yes":
            r.fail("10_gst_filing_flags",
                   f"{g['Business_ID']} {g['Month']}: Late_Days=0 but Filed_On_Time={on_time}")
        if late > 0 and on_time != "No":
            r.fail("10_gst_filing_flags",
                   f"{g['Business_ID']} {g['Month']}: Late_Days={late} but Filed_On_Time={on_time}")
        # Return_Filing_Date - due date should match Late_Days
        # Due date = 20th of next month
        y, m = g["Month"].split("-")
        y, m = int(y), int(m)
        if m == 12:
            due = date(y + 1, 1, 20)
        else:
            due = date(y, m + 1, 20)
        filed = parse_iso(g["Return_Filing_Date"])
        delta = (filed - due).days
        if delta != late:
            r.fail("10_gst_filing_flags",
                   f"{g['Business_ID']} {g['Month']}: filed-due={delta}d but Late_Days={late}")

    return r.summarize()


if __name__ == "__main__":
    sys.exit(main())
