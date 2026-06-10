import type {
  Opportunity as RoleBackedOpportunity,
  OpportunityCreatePayload as RoleBackedOpportunityCreatePayload,
  OpportunityParseRequest as RoleBackedOpportunityParseRequest,
  OpportunityParseResponse as RoleBackedOpportunityParseResponse,
  OpportunityUpdatePayload as RoleBackedOpportunityUpdatePayload,
} from "./roles";

// Layer 7B compatibility: Opportunities are the outward product/API concept,
// while the frontend receives Role-backed payloads until Layer 7C is approved.
export type Opportunity = RoleBackedOpportunity;
export type OpportunityCreatePayload = RoleBackedOpportunityCreatePayload;
export type OpportunityUpdatePayload = RoleBackedOpportunityUpdatePayload;
export type OpportunityParseRequest = RoleBackedOpportunityParseRequest;
export type OpportunityParseResponse = RoleBackedOpportunityParseResponse;
