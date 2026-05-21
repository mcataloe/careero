import { apiRequest } from "./client";
import type {
  Opportunity,
  OpportunityCreatePayload,
  OpportunityParseRequest,
  OpportunityParseResponse,
  OpportunityUpdatePayload,
} from "../types/roles";

export function listOpportunities(): Promise<Opportunity[]> {
  return apiRequest<Opportunity[]>("/api/opportunities");
}

export function getOpportunity(opportunityId: string): Promise<Opportunity> {
  return apiRequest<Opportunity>(`/api/opportunities/${opportunityId}`);
}

export function createOpportunity(
  payload: OpportunityCreatePayload,
): Promise<Opportunity> {
  return apiRequest<Opportunity>("/api/opportunities", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function parseOpportunity(
  payload: OpportunityParseRequest,
): Promise<OpportunityParseResponse> {
  return apiRequest<OpportunityParseResponse>("/api/opportunities/parse", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function updateOpportunity(
  opportunityId: string,
  payload: OpportunityUpdatePayload,
): Promise<Opportunity> {
  return apiRequest<Opportunity>(`/api/opportunities/${opportunityId}`, {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
}

export function refreshOpportunityIntelligence(
  opportunityId: string,
): Promise<Opportunity> {
  return apiRequest<Opportunity>(
    `/api/opportunities/${opportunityId}/opportunity-intelligence`,
    {
      method: "POST",
    },
  );
}

export function archiveOpportunity(opportunityId: string): Promise<void> {
  return apiRequest<void>(`/api/opportunities/${opportunityId}`, {
    method: "DELETE",
  });
}
