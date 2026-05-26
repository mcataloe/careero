import { apiRequest } from "./client";
import type { AuthUser, LoginPayload, RegisterPayload } from "../types/auth";

export function getCurrentUser() {
  return apiRequest<AuthUser>("/api/auth/me");
}

export function login(payload: LoginPayload) {
  return apiRequest<AuthUser>("/api/auth/login", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function register(payload: RegisterPayload) {
  return apiRequest<AuthUser>("/api/auth/register", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function logout() {
  return apiRequest<void>("/api/auth/logout", {
    method: "POST",
  });
}
