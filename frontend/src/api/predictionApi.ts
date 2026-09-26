import apiClient from "./client";
import { PredictionRequest, PredictionResult } from "../types";

export const predictionApi = {
  predict: async (payload: PredictionRequest): Promise<PredictionResult> => {
    const res = await apiClient.post<PredictionResult>("/predictions", payload);
    return res.data;
  },
};
