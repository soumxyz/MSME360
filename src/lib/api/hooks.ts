import { useQuery } from "@tanstack/react-query";
import { getBusinessDetail, getPortfolio, getAuditTrail } from "./index";

export function usePortfolio() {
  return useQuery({ 
    queryKey: ["portfolio"], 
    queryFn: getPortfolio,
    refetchInterval: 5000, // Poll portfolio list every 5 seconds for live queue updates!
  });
}

export function useBusinessDetail(id: string | undefined) {
  const activeId = id === "MSME014" 
    ? (localStorage.getItem("active_business_id") || "MSME014") 
    : id;

  return useQuery({
    queryKey: ["business", activeId],
    queryFn: () => getBusinessDetail(activeId!),
    enabled: !!activeId,
    refetchInterval: 5000, // Poll every 5s so officer decisions (Approved/Rejected) appear on customer side in real-time
  });
}

export function useAuditTrail() {
  return useQuery({
    queryKey: ["audit-trail"],
    queryFn: getAuditTrail,
    refetchInterval: 5000, // Poll audit trail every 5 seconds for live compliance logs
  });
}
