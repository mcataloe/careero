import { ApiError, apiRequest } from "./client";
import type {
  StrideEvaluation,
  StrideEvaluationCreatePayload,
} from "../types/strideEvaluations";

export async function getLatestEvaluation(
  roleId: string,
): Promise<StrideEvaluation | null> {
  try {
    return await apiRequest<StrideEvaluation>(
      `/api/roles/${roleId}/evaluations/latest`,
    );
  } catch (error) {
    if (error instanceof ApiError && error.status === 404) {
      return null;
    }
    throw error;
  }
}

export function createEvaluation(
  roleId: string,
  payload: StrideEvaluationCreatePayload = {},
): Promise<StrideEvaluation> {
  return apiRequest<StrideEvaluation>(`/api/roles/${roleId}/evaluations`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export interface CreateEvaluationResult {
  evaluation: StrideEvaluation;
  status: number;
}

export async function createEvaluationWithStatus(
  roleId: string,
  payload: StrideEvaluationCreatePayload = {},
): Promise<CreateEvaluationResult> {
  const response = await fetch(`/api/roles/${roleId}/evaluations`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });
  const contentType = response.headers.get("content-type") ?? "";
  const data = contentType.includes("application/json")
    ? await response.json()
    : await response.text();

  if (!response.ok) {
    const detail =
      typeof data === "object" && data !== null && "detail" in data
        ? String(data.detail)
        : `Request failed with status ${response.status}`;
    throw new ApiError(detail, response.status);
  }

  return {
    evaluation: data as StrideEvaluation,
    status: response.status,
  };
}
