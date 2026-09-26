import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Download, Plus } from "lucide-react";
import PageHeader from "../components/layout/PageHeader";
import ApplicationTable from "../components/tables/ApplicationTable";
import ApplicationFilters, { FilterState } from "../components/tables/ApplicationFilters";
import Pagination from "../components/tables/Pagination";
import LoadingSpinner from "../components/common/LoadingSpinner";
import ErrorState from "../components/common/ErrorState";
import EmptyState from "../components/common/EmptyState";
import ConfirmDialog from "../components/common/ConfirmDialog";
import Button from "../components/common/Button";
import { useApplications } from "../hooks/useApplications";
import { applicationApi } from "../api/applicationApi";
import { blockchainApi } from "../api/blockchainApi";
import { exportApi } from "../api/exportApi";
import { getErrorMessage } from "../api/client";

export default function Applications() {
  const navigate = useNavigate();
  const [filters, setFilters] = useState<FilterState>({ search: "", risk_category: "", status: "" });
  const [page, setPage] = useState(1);
  const [deleteTarget, setDeleteTarget] = useState<string | null>(null);
  const [deleting, setDeleting] = useState(false);
  const [toast, setToast] = useState<string | null>(null);

  const { data, loading, error, refetch } = useApplications({
    page, page_size: 10,
    search: filters.search || undefined,
    risk_category: filters.risk_category || undefined,
    status: filters.status || undefined,
  });

  const handleDelete = async () => {
    if (!deleteTarget) return;
    setDeleting(true);
    try {
      const res = await applicationApi.remove(deleteTarget);
      setToast(res.blockchain_note || "Application deleted.");
      setDeleteTarget(null);
      refetch();
    } catch (e) {
      setToast(getErrorMessage(e));
    } finally {
      setDeleting(false);
    }
  };

  const handleRegister = async (applicationId: string) => {
    try {
      const res = await blockchainApi.register(applicationId);
      setToast(`Registered ${applicationId} on blockchain (tx: ${res.transaction_hash.slice(0, 12)}...)`);
      refetch();
    } catch (e) {
      setToast(getErrorMessage(e));
    }
  };

  const handleVerify = async (applicationId: string) => {
    try {
      const res = await blockchainApi.verify(applicationId);
      setToast(res.verified ? `VERIFIED: ${applicationId}` : `VERIFICATION FAILED: ${applicationId}`);
    } catch (e) {
      setToast(getErrorMessage(e));
    }
  };

  return (
    <div>
      <PageHeader
        title="Applications"
        description="Manage and review all loan risk assessment applications"
        actions={
          <>
            <Button variant="secondary" onClick={() => exportApi.downloadApplications("csv")}>
              <Download size={14} /> CSV
            </Button>
            <Button variant="secondary" onClick={() => exportApi.downloadApplications("json")}>
              <Download size={14} /> JSON
            </Button>
            <Button onClick={() => navigate("/predict")}>
              <Plus size={14} /> New Application
            </Button>
          </>
        }
      />

      {toast && (
        <div className="mb-4 text-xs bg-blue-50 border border-blue-200 text-blue-700 rounded-md px-3 py-2 flex justify-between items-center">
          {toast}
          <button onClick={() => setToast(null)} className="text-blue-400 hover:text-blue-600">×</button>
        </div>
      )}

      <div className="card p-4">
        <ApplicationFilters filters={filters} onChange={(f) => { setFilters(f); setPage(1); }} />

        {loading && <LoadingSpinner />}
        {error && <ErrorState message={error} />}
        {!loading && !error && data && data.items.length === 0 && (
          <EmptyState title="No applications found" description="Try adjusting your filters or create a new application." />
        )}
        {!loading && !error && data && data.items.length > 0 && (
          <>
            <ApplicationTable
              applications={data.items}
              onDelete={setDeleteTarget}
              onRegister={handleRegister}
              onVerify={handleVerify}
            />
            <Pagination page={data.page} totalPages={data.total_pages} onPageChange={setPage} />
          </>
        )}
      </div>

      <ConfirmDialog
        open={!!deleteTarget}
        title="Delete Application"
        message={`Are you sure you want to delete ${deleteTarget}? If it has been registered on the blockchain, that on-chain record cannot be removed.`}
        confirmLabel="Delete"
        danger
        loading={deleting}
        onConfirm={handleDelete}
        onCancel={() => setDeleteTarget(null)}
      />
    </div>
  );
}
