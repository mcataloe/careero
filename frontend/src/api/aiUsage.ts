import { apiRequest } from "./client";
import type { AIUsageList } from "../types/aiUsage";

export function listAIUsage(limit = 25) {
  return apiRequest<AIUsageList>(`/api/usage/ai?limit=${limit}`);
}
