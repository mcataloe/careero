import { ApiError, apiRequest } from "./client";
import type {
  CompassEvaluation,
  CompassEvaluationCreatePayload,
} from "../types/compassEvaluations";

export async function getLatestEvaluation(
  roleId: string,
): Promise<CompassEvaluation | null> {
  try {
    return await apiRequest<CompassEvaluation>(
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
  payload: CompassEvaluationCreatePayload = {},
): Promise<CompassEvaluation> {
  return apiRequest<CompassEvaluation>(`/api/roles/${roleId}/evaluations`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export interface CreateEvaluationResult {
  evaluation: CompassEvaluation;
  status: number;
}

export async function createEvaluationWithStatus(
  roleId: string,
  payload: CompassEvaluationCreatePayload = {},
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
    evaluation: data as CompassEvaluation,
    status: response.status,
  };
}
