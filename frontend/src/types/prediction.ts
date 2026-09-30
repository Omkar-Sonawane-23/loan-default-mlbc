import { LoanFeatures, RiskCategory } from "./application";

export interface PredictionResult {
  prediction: number;
  default_probability: number;
  non_default_probability: number;
  risk_category: RiskCategory;
  model_name: string;
  model_version: string;
  model_hash?: string;
  credit_score?: number;
  expected_loss?: number;
  local_explanation?: { status: string; method?: string; target?: string; contributors: { feature: string; impact: number }[] };
  explanation_scope?: string;
  storage_status?: string;
  risk_factors: { feature: string; importance: number }[];
  disclaimer: string;
}

export interface PredictionRequest {
  input_features: LoanFeatures;
  applicant_reference?: string;
}
