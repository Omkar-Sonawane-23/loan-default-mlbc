import apiClient from "./client";

export const analyticsApi = {
  dashboardStats: async () => {
    const res = await apiClient.get("/dashboard/stats");
    return res.data;
  },
  fullAnalytics: async () => {
    const res = await apiClient.get("/analytics");
    return res.data;
  },
};
