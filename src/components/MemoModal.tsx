import { useEffect, useRef, useState } from "react";
import { Clipboard, Check, Download, X } from "lucide-react";
import type { BusinessDetail } from "../lib/api/types";
import { formatINR, formatDate } from "../lib/format";

interface MemoModalProps {
  isOpen: boolean;
  onClose: () => void;
  business: BusinessDetail;
}

export function MemoModal({ isOpen, onClose, business }: MemoModalProps) {
  const [copied, setCopied] = useState(false);
  const closeBtnRef = useRef<HTMLButtonElement>(null);
  const previouslyFocused = useRef<HTMLElement | null>(null);

  // Focus management: capture the element that opened the modal, focus the
  // close button on mount, and restore focus on close. Escape closes the modal.
  useEffect(() => {
    if (!isOpen) return;
    previouslyFocused.current = document.activeElement as HTMLElement | null;
    closeBtnRef.current?.focus();
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    document.addEventListener("keydown", onKey);
    return () => {
      document.removeEventListener("keydown", onKey);
      previouslyFocused.current?.focus?.();
    };
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const formattedDate = formatDate(new Date().toISOString());

  const memoText = `======================================================================
IDBI BANK MSME CREDIT INTELLIGENCE WORKSPACE
CREDIT EVALUATION MEMORANDUM
======================================================================
Generated Date : ${formattedDate}
Business Name  : ${business.profile.name}
Business ID    : ${business.business_id}
Industry       : ${business.profile.industry}
Location       : ${business.profile.city}, ${business.profile.state}
Category       : ${business.profile.category} MSME
GST Status     : ${business.profile.gst_registered ? "Registered & Verified" : "Not Registered"}

----------------------------------------------------------------------
1. CREDIT SCORE & RISK PROFILE
----------------------------------------------------------------------
Financial Health Score : ${business.score.score} / 100
Risk Category          : ${business.score.band} Risk
Model Confidence       : ${(business.score.confidence * 100).toFixed(0)}%
Application Date       : ${formatDate(business.applied_at)}

----------------------------------------------------------------------
2. MODEL RECOMMENDATION
----------------------------------------------------------------------
Suggested Decision     : ${business.recommendation.decision}
Suggested Loan Size    : ${formatINR(business.recommendation.loan_amount)}
Suggested Tenure       : ${business.recommendation.tenure_months} Months
Suggested Interest Band: ${business.recommendation.interest_band}

----------------------------------------------------------------------
3. KEY SHAP EXPLANATION FACTORS
----------------------------------------------------------------------
${business.factors
  .map(
    (f, i) =>
      `${i + 1}. [${f.direction}] ${f.label} (Weight: ${(f.weight * 100).toFixed(0)}%)\n   Detail: ${f.detail}`
  )
  .join("\n")}

----------------------------------------------------------------------
4. METRICS SUMMARY
----------------------------------------------------------------------
Annual Turnover             : ${formatINR(business.profile.annual_turnover)}
Average Monthly Revenue     : ${formatINR(business.profile.annual_turnover / 12)}
Expense-to-Income Ratio     : ${(business.metrics.expense_ratio * 100).toFixed(1)}%
Cash Buffer Days            : ${business.metrics.cash_buffer_days.toFixed(0)} Days
Cheque Bounce Count (12m)   : ${business.metrics.bounce_count}
Existing Debt (EMI)         : ${business.profile.existing_loan ? formatINR(business.profile.existing_emi) + " / month" : "None"}
GST Filing Regularity       : ${(business.metrics.gst_regularity * 100).toFixed(0)}%

======================================================================
DECISION CONTEXT (For Credit Officer Approval)
----------------------------------------------------------------------
This memo acts as a formal record of the AI scoring engine's output. 
Final decisioning resides with the IDBI credit officer.
======================================================================`;

  const handleCopy = () => {
    navigator.clipboard.writeText(memoText);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownload = () => {
    const blob = new Blob([memoText], { type: "text/plain;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `credit_memo_${business.business_id}.txt`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4 backdrop-blur-xs"
      role="dialog"
      aria-modal="true"
      aria-labelledby="memo-modal-title"
      onClick={onClose}
    >
      <div
        className="relative w-full max-w-3xl rounded-card border border-border bg-white shadow-2xl p-6 flex flex-col max-h-[90vh]"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between pb-4 border-b border-border mb-4">
          <div>
            <h3 id="memo-modal-title" className="text-lg font-bold text-text-primary">Credit Evaluation Memo</h3>
            <p className="text-xs text-text-secondary">Draft evaluation record for {business.profile.name}</p>
          </div>
          <button
            ref={closeBtnRef}
            onClick={onClose}
            aria-label="Close credit memo dialog"
            className="rounded-lg p-1 text-text-secondary hover:bg-background-muted hover:text-text-primary transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Modal Body */}
        <div className="flex-1 overflow-y-auto mb-4">
          <textarea
            readOnly
            value={memoText}
            className="w-full h-[350px] font-mono text-[11px] leading-relaxed text-text-primary bg-background-muted/40 border border-border rounded p-4 focus:outline-none resize-none"
          />
        </div>

        {/* Modal Footer */}
        <div className="flex justify-end gap-3 pt-4 border-t border-border mt-auto">
          <button
            onClick={handleCopy}
            className="px-4 py-2 border border-border hover:bg-background-muted text-text-primary text-sm font-semibold rounded flex items-center gap-2 transition-colors cursor-pointer"
          >
            {copied ? (
              <>
                <Check className="w-4 h-4 text-success" /> Copied!
              </>
            ) : (
              <>
                <Clipboard className="w-4 h-4" /> Copy to clipboard
              </>
            )}
          </button>
          <button
            onClick={handleDownload}
            className="px-4 py-2 bg-primary hover:bg-primary-hover text-white text-sm font-semibold rounded flex items-center gap-2 transition-colors cursor-pointer"
          >
            <Download className="w-4 h-4" /> Download memo (.txt)
          </button>
        </div>
      </div>
    </div>
  );
}
