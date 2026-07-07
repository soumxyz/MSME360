import { PlusCircle, MinusCircle } from "lucide-react";
import type { Factor } from "../lib/api/types";

interface FactorBarsProps {
  factors: Factor[];
}

export function FactorBars({ factors }: FactorBarsProps) {
  // Sort factors by absolute weight descending just in case
  const sortedFactors = [...factors].sort((a, b) => b.weight - a.weight);

  return (
    <div className="space-y-4">
      {sortedFactors.map((factor) => {
        const isPositive = factor.direction === "+";
        const percent = Math.round(factor.weight * 100);

        return (
          <div
            key={factor.name}
            className="group rounded-card border border-border bg-white p-3.5 transition-all duration-150 hover:border-primary/30 hover:shadow-sm"
          >
            {/* Header info */}
            <div className="flex items-start justify-between gap-2.5">
              <div className="space-y-0.5">
                <span className="text-sm font-semibold text-text-primary">
                  {factor.label}
                </span>
                <p className="text-xs leading-relaxed text-text-secondary">
                  {factor.detail}
                </p>
              </div>

              {/* Status Indicator Icon */}
              <div className="shrink-0 pt-0.5">
                {isPositive ? (
                  <PlusCircle
                    className="w-4 h-4 text-success"
                    aria-label="Positive impact"
                  />
                ) : (
                  <MinusCircle
                    className="w-4 h-4 text-error"
                    aria-label="Negative impact"
                  />
                )}
              </div>
            </div>

            {/* Diverging Bar Chart Row */}
            <div className="relative mt-3 h-6 w-full rounded bg-background-muted/50">
              {/* Center Line Axis */}
              <div className="absolute top-0 bottom-0 left-1/2 w-[1.5px] bg-border z-10" />

              {/* Negative side track (left) */}
              <div className="absolute top-0 bottom-0 left-0 right-1/2 flex items-center justify-end">
                {!isPositive && (
                  <div
                    className="h-4 rounded-l bg-error/80 transition-all duration-500 flex items-center justify-end pr-2 group-hover:bg-error"
                    style={{ width: `${percent}%` }}
                  >
                    <span className="font-mono text-[10px] font-bold text-white">
                      -{percent}%
                    </span>
                  </div>
                )}
              </div>

              {/* Positive side track (right) */}
              <div className="absolute top-0 bottom-0 left-1/2 right-0 flex items-center justify-start">
                {isPositive && (
                  <div
                    className="h-4 rounded-r bg-success/80 transition-all duration-500 flex items-center justify-start pl-2 group-hover:bg-success"
                    style={{ width: `${percent}%` }}
                  >
                    <span className="font-mono text-[10px] font-bold text-white">
                      +{percent}%
                    </span>
                  </div>
                )}
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}
