import apiClient from "./client";

export const exportApi = {
  downloadApplications: async (format: "csv" | "json") => {
    const res = await apiClient.get(`/export/applications`, { params: { format }, responseType: "blob" });
    const url = window.URL.createObjectURL(new Blob([res.data]));
    const link = document.createElement("a");
    link.href = url;
    link.setAttribute("download", `applications.${format}`);
    document.body.appendChild(link);
    link.click();
    link.remove();
  },
  downloadApplicationPdf: async (applicationId: string) => {
    const res = await apiClient.get(`/export/applications/${applicationId}/pdf`, { responseType: "blob" });
    const url = window.URL.createObjectURL(new Blob([res.data]));
    const link = document.createElement("a");
    link.href = url;
    link.setAttribute("download", `${applicationId}.pdf`);
    document.body.appendChild(link);
    link.click();
    link.remove();
  },
};
