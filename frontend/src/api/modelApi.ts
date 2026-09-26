import apiClient from "./client";

export const modelApi = {
  info: async () => {
    const res = await apiClient.get("/model/info");
    return res.data;
  },
  metrics: async () => {
    const res = await apiClient.get("/model/metrics");
    return res.data;
  },
};
