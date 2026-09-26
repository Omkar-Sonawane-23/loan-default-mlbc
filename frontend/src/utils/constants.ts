export const RISK_COLORS: Record<string, string> = {
  LOW: "#16a34a",
  MEDIUM: "#d97706",
  HIGH: "#dc2626",
};

export const RISK_BG: Record<string, string> = {
  LOW: "bg-green-50 text-green-700 border border-green-200",
  MEDIUM: "bg-amber-50 text-amber-700 border border-amber-200",
  HIGH: "bg-red-50 text-red-700 border border-red-200",
};

export const STATUS_BG: Record<string, string> = {
  DRAFT: "bg-slate-100 text-slate-600 border border-slate-200",
  ASSESSED: "bg-blue-50 text-blue-700 border border-blue-200",
  UNDER_REVIEW: "bg-amber-50 text-amber-700 border border-amber-200",
  VERIFIED: "bg-green-50 text-green-700 border border-green-200",
  CLOSED: "bg-slate-100 text-slate-500 border border-slate-200",
};

export const EMPLOYMENT_TYPES = ["Salaried", "Self-Employed", "Business Owner", "Contract", "Unemployed"];
export const LOAN_PURPOSES = ["Home", "Education", "Vehicle", "Personal", "Medical", "Business", "Debt Consolidation"];
export const APPLICATION_STATUSES = ["DRAFT", "ASSESSED", "UNDER_REVIEW", "VERIFIED", "CLOSED"];

export const ACADEMIC_DISCLAIMER =
  "This system is an academic Machine Learning and Blockchain demonstration. The predicted default probability is an estimated model output and is not financial advice, a guaranteed prediction, or an automated loan approval/rejection decision.";
