import { useEffect, useState } from "react";
import type { RiskBand } from "../lib/api/types";
import { ShieldCheck, AlertTriangle, ShieldAlert } from "lucide-react";
import { BRAND } from "../lib/palette";

interface ScoreGaugeProps {
  score: number;
  band: RiskBand;
  confidence: number;
}

export function ScoreGauge({ score, band, confidence }: ScoreGaugeProps) {
  const [animatedScore, setAnimatedScore] = useState(0);

  useEffect(() => {
    const timer = setTimeout(() => {
      setAnimatedScore(score);
    }, 100);
    return () => clearTimeout(timer);
  }, [score]);

  // Calculate needle rotation: 0 score is -90deg, 50 is 0deg, 100 is 90deg
  const rotation = (animatedScore / 100) * 180 - 90;

  // Render inline chip details
  const getChip = (b: RiskBand) => {
    switch (b) {
      case "Low":
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded bg-success/10 text-success text-xs font-semibold border border-success/20 uppercase">
            <ShieldCheck className="w-3.5 h-3.5" /> Low Risk
          </span>
        );
      case "Medium":
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded bg-warning/10 text-warning text-xs font-semibold border border-warning/20 uppercase">
            <AlertTriangle className="w-3.5 h-3.5" /> Med Risk
          </span>
        );
      case "High":
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded bg-error/10 text-error text-xs font-semibold border border-error/20 uppercase">
            <ShieldAlert className="w-3.5 h-3.5" /> High Risk
          </span>
        );
    }
  };

  return (
    <div className="flex flex-col items-center justify-center p-2">
      <div className="relative flex h-[110px] w-[200px] justify-center overflow-hidden">
        <svg viewBox="0 0 200 110" className="w-full h-auto">
          <defs>
            <linearGradient id="gauge-grad" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor={BRAND.error} />
              <stop offset="45%" stopColor={BRAND.error} />
              <stop offset="55%" stopColor={BRAND.warning} />
              <stop offset="70%" stopColor={BRAND.warning} />
              <stop offset="80%" stopColor={BRAND.success} />
              <stop offset="100%" stopColor={BRAND.success} />
            </linearGradient>
          </defs>

          {/* Background Track (Grey) */}
          <path
            d="M 20,95 A 80,80 0 0,1 180,95"
            fill="none"
            stroke={BRAND.surfaceMuted}
            strokeWidth="12"
            strokeLinecap="round"
          />

          {/* Colored Risk Band Track */}
          <path
            d="M 20,95 A 80,80 0 0,1 180,95"
            fill="none"
            stroke="url(#gauge-grad)"
            strokeWidth="12"
            strokeLinecap="round"
            className="opacity-90"
          />

          {/* Pivot Base */}
          <circle cx="100" cy="95" r="8" fill={BRAND.ink} />

          {/* Needle Pointer */}
          <g
            className="transition-transform duration-1000 ease-out"
            style={{
              transform: `rotate(${rotation}deg)`,
              transformOrigin: "100px 95px",
            }}
          >
            <polygon
              points="97,95 100,20 103,95"
              fill={BRAND.ink}
              stroke="#ffffff"
              strokeWidth="1"
            />
            <circle cx="100" cy="95" r="3" fill={BRAND.primary} />
          </g>

          {/* Grid labels */}
          <text x="16" y="108" className="font-mono text-[9px] font-semibold" fill={BRAND.slate}>0</text>
          <text x="96" y="12" className="font-mono text-[9px] font-semibold" fill={BRAND.slate}>50</text>
          <text x="176" y="108" className="font-mono text-[9px] font-semibold" fill={BRAND.slate}>100</text>
        </svg>
      </div>

      <div className="mt-4 text-center">
        <div className="flex items-baseline justify-center gap-2">
          <span className="font-mono text-5xl font-bold tracking-tight text-text-primary">
            {score}
          </span>
          <span className="text-sm font-semibold text-text-secondary">/100</span>
        </div>

        <div className="mt-3 flex items-center justify-center gap-3">
          {getChip(band)}
          <span className="font-mono text-xs text-text-secondary" title="Model confidence score">
            Conf: {(confidence * 100).toFixed(0)}%
          </span>
        </div>
      </div>
    </div>
  );
}
