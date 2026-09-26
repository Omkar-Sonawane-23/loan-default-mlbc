import apiClient from "./client";
import { Application, PaginatedApplications, LoanFeatures, ApplicationStatus, AuditEvent } from "../types";

export interface ApplicationFilters {
  page?: number;
  page_size?: number;
  search?: string;
  risk_category?: string;
  status?: string;
  date_from?: string;
  date_to?: string;
  loan_amount_min?: number;
  loan_amount_max?: number;
  credit_score_min?: number;
  credit_score_max?: number;
  sort_by?: string;
  sort_order?: string;
}

export const applicationApi = {
  create: async (input_features: LoanFeatures, applicant_reference?: string): Promise<Application> => {
    const res = await apiClient.post<Application>("/applications", { input_features, applicant_reference });
    return res.data;
  },
  list: async (filters: ApplicationFilters): Promise<PaginatedApplications> => {
    const res = await apiClient.get<PaginatedApplications>("/applications", { params: filters });
    return res.data;
  },
  get: async (applicationId: string): Promise<Application> => {
    const res = await apiClient.get<Application>(`/applications/${applicationId}`);
    return res.data;
  },
  update: async (applicationId: string, updates: Partial<{ input_features: LoanFeatures; applicant_reference: string; status: ApplicationStatus }>): Promise<Application> => {
    const res = await apiClient.put<Application>(`/applications/${applicationId}`, updates);
    return res.data;
  },
  updateStatus: async (applicationId: string, status: ApplicationStatus): Promise<Application> => {
    const res = await apiClient.patch<Application>(`/applications/${applicationId}/status`, { status });
    return res.data;
  },
  remove: async (applicationId: string): Promise<{ deleted: boolean; blockchain_note: string | null }> => {
    const res = await apiClient.delete(`/applications/${applicationId}`);
    return res.data;
  },
  auditLog: async (applicationId: string): Promise<{ application_id: string; events: AuditEvent[] }> => {
    const res = await apiClient.get(`/applications/${applicationId}/audit`);
    return res.data;
  },
};
