import { apiRequest } from "./client";
import type { ProductizationReadiness } from "../types/productization";

export function getProductizationReadiness(): Promise<ProductizationReadiness> {
  return apiRequest<ProductizationReadiness>("/api/productization/readiness");
}
