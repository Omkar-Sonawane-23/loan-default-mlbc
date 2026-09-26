import apiClient from "./client";
import { BlockchainRegisterResponse, BlockchainVerifyResponse, BlockchainStatus, BlockchainTransaction } from "../types";

export const blockchainApi = {
  register: async (applicationId: string): Promise<BlockchainRegisterResponse> => {
    const res = await apiClient.post<BlockchainRegisterResponse>(`/blockchain/register/${applicationId}`);
    return res.data;
  },
  verify: async (applicationId: string): Promise<BlockchainVerifyResponse> => {
    const res = await apiClient.get<BlockchainVerifyResponse>(`/blockchain/verify/${applicationId}`);
    return res.data;
  },
  getRecord: async (applicationId: string) => {
    const res = await apiClient.get(`/blockchain/record/${applicationId}`);
    return res.data;
  },
  status: async (): Promise<BlockchainStatus> => {
    const res = await apiClient.get<BlockchainStatus>("/blockchain/status");
    return res.data;
  },
  transactions: async (): Promise<{ transactions: BlockchainTransaction[]; total_registered: number }> => {
    const res = await apiClient.get("/blockchain/transactions");
    return res.data;
  },
};
