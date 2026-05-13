import { apiRequest } from "./client";
import type {
  Role,
  RoleCreatePayload,
  RoleParseRequest,
  RoleParseResponse,
  RoleUpdatePayload,
} from "../types/roles";

export function listRoles(): Promise<Role[]> {
  return apiRequest<Role[]>("/api/roles");
}

export function getRole(roleId: string): Promise<Role> {
  return apiRequest<Role>(`/api/roles/${roleId}`);
}

export function createRole(payload: RoleCreatePayload): Promise<Role> {
  return apiRequest<Role>("/api/roles", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function parseRole(payload: RoleParseRequest): Promise<RoleParseResponse> {
  return apiRequest<RoleParseResponse>("/api/roles/parse", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function updateRole(
  roleId: string,
  payload: RoleUpdatePayload,
): Promise<Role> {
  return apiRequest<Role>(`/api/roles/${roleId}`, {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
}

export function archiveRole(roleId: string): Promise<void> {
  return apiRequest<void>(`/api/roles/${roleId}`, {
    method: "DELETE",
  });
}
