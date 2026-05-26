import { apiRequest } from "./client";
import type { CurrentEntitlements } from "../types/entitlements";

export function getCurrentEntitlements() {
  return apiRequest<CurrentEntitlements>("/api/entitlements/current");
}
