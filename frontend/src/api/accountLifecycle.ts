import { apiRequest } from "./client";
import type {
  AccountLifecycleRequest,
  AccountLifecycleRequestCreate,
  AccountLifecycleRequestList,
} from "../types/accountLifecycle";

export function listAccountLifecycleRequests() {
  return apiRequest<AccountLifecycleRequestList>("/api/account/lifecycle-requests");
}

export function createAccountLifecycleRequest(payload: AccountLifecycleRequestCreate) {
  return apiRequest<AccountLifecycleRequest>("/api/account/lifecycle-requests", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function cancelAccountLifecycleRequest(requestId: string) {
  return apiRequest<AccountLifecycleRequest>(
    `/api/account/lifecycle-requests/${requestId}/cancel`,
    {
      method: "POST",
    },
  );
}
