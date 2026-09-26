export type RiskCategory = "LOW" | "MEDIUM" | "HIGH";
export type ApplicationStatus = "DRAFT" | "ASSESSED" | "UNDER_REVIEW" | "VERIFIED" | "CLOSED";

export interface LoanFeatures {
  age: number;
  annual_income: number;
  employment_years: number;
  employment_type: "Salaried" | "Self-Employed" | "Business Owner" | "Contract" | "Unemployed";
  credit_score: number;
  loan_amount: number;
  loan_term_months: number;
  existing_debt: number;
  debt_to_income_ratio: number;
  number_of_previous_loans: number;
  previous_default: 0 | 1;
  dependents: number;
  savings_amount: number;
  requested_loan_purpose: "Home" | "Education" | "Vehicle" | "Personal" | "Medical" | "Business" | "Debt Consolidation";
}

export interface BlockchainInfo {
  registered: boolean;
  record_hash: string | null;
  transaction_hash: string | null;
  block_number: number | null;
  contract_address: string | null;
  chain_id: number | null;
  registered_at: string | null;
}

export interface Application {
  application_id: string;
  applicant_reference: string;
  input_features: LoanFeatures;
  prediction: number | null;
  default_probability: number | null;
  non_default_probability: number | null;
  risk_category: RiskCategory | null;
  model_name: string | null;
  model_version: string | null;
  status: ApplicationStatus;
  created_at: string;
  updated_at: string;
  blockchain: BlockchainInfo;
}

export interface PaginatedApplications {
  items: Application[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface AuditEvent {
  application_id: string;
  event: string;
  details: Record<string, unknown>;
  timestamp: string;
}
