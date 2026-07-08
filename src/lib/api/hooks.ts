import { useQuery, useQueryClient } from "@tanstack/react-query";
import { useCallback } from "react";
import { getBusinessDetail, getPortfolio, getAuditTrail } from "./index";

// Sane defaults:
//  * refetchInterval only fires while the tab is focused (default in v5).
//  * A 15s poll for lists is enough for a demo but doesn't hammer the server
//    every 5s from three different hooks simultaneously.
const LIST_POLL_MS = 15_000;
const DETAIL_POLL_MS = 20_000;

export function usePortfolio() {
  return useQuery({
    queryKey: ["portfolio"],
    queryFn: getPortfolio,
    refetchInterval: LIST_POLL_MS,
    refetchIntervalInBackground: false,
    staleTime: 5_000,
  });
}

export function useBusinessDetail(id: string | undefined) {
  return useQuery({
    queryKey: ["business", id],
    queryFn: () => getBusinessDetail(id!),
    enabled: !!id,
    refetchInterval: DETAIL_POLL_MS,
    refetchIntervalInBackground: false,
    staleTime: 5_000,
  });
}

export function useAuditTrail() {
  return useQuery({
    queryKey: ["audit-trail"],
    queryFn: getAuditTrail,
    refetchInterval: LIST_POLL_MS,
    refetchIntervalInBackground: false,
    staleTime: 5_000,
  });
}

/**
 * Central invalidation hook: any mutation that changes a business's state
 * (e.g., decision, registration) should call `invalidateBusiness(id)` so the
 * portfolio, detail, and audit-trail queries all refetch immediately instead
 * of waiting for their polling tick.
 */
export function useInvalidateBusiness() {
  const qc = useQueryClient();
  return useCallback(
    (id?: string) => {
      qc.invalidateQueries({ queryKey: ["portfolio"] });
      qc.invalidateQueries({ queryKey: ["audit-trail"] });
      if (id) qc.invalidateQueries({ queryKey: ["business", id] });
    },
    [qc]
  );
}
