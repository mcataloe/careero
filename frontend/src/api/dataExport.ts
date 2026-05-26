import { apiRequest } from "./client";
import type { LocalDataExport } from "../types/dataExport";

export function getLocalDataExport() {
  return apiRequest<LocalDataExport>("/api/data-export/local");
}
