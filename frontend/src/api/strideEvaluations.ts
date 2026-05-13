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
