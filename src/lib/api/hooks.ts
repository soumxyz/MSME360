import { useQuery } from "@tanstack/react-query";
import { getBusinessDetail, getPortfolio, getAuditTrail } from "./index";

export function usePortfolio() {
  return useQuery({ queryKey: ["portfolio"], queryFn: getPortfolio });
}

export function useBusinessDetail(id: string | undefined) {
  return useQuery({
    queryKey: ["business", id],
    queryFn: () => getBusinessDetail(id!),
    enabled: !!id,
  });
}

export function useAuditTrail() {
  return useQuery({
    queryKey: ["audit-trail"],
    queryFn: getAuditTrail,
    refetchInterval: 5000, // Poll audit trail every 5 seconds for live compliance logs
  });
}
