import { useEffect, useState } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import { ArrowLeft, Link2, ShieldCheck, Download, FileDown } from "lucide-react";
import PageHeader from "../components/layout/PageHeader";
import LoadingSpinner from "../components/common/LoadingSpinner";
import ErrorState from "../components/common/ErrorState";
import Button from "../components/common/Button";
import RiskBadge from "../components/risk/RiskBadge";
import StatusBadge from "../components/risk/StatusBadge";
import RiskMeter from "../components/risk/RiskMeter";
import FeatureImportance from "../components/risk/FeatureImportance";
import BlockchainDetails from "../components/blockchain/BlockchainDetails";
import AuditTimeline from "../components/audit/AuditTimeline";
import { applicationApi } from "../api/applicationApi";
import { blockchainApi } from "../api/blockchainApi";
import { exportApi } from "../api/exportApi";
import { modelApi } from "../api/modelApi";
import { getErrorMessage } from "../api/client";
import { Application, AuditEvent } from "../types";
import { formatCurrency, formatDateTime } from "../utils/formatters";
import { APPLICATION_STATUSES } from "../utils/constants";

export default function ApplicationDetails() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [app, setApp] = useState<Application | null>(null);
  const [events, setEvents] = useState<AuditEvent[]>([]);
  const [featureImportance, setFeatureImportance] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [actionBusy, setActionBusy] = useState(false);
  const [toast, setToast] = useState<string | null>(null);

  const load = () => {
    if (!id) return;
    setLoading(true);
    Promise.all([
      applicationApi.get(id),
      applicationApi.auditLog(id),
      modelApi.metrics().catch(() => null),
    ])
      .then(([appData, auditData, modelData]) => {
        setApp(appData);
        setEvents(auditData.events);
        if (modelData) setFeatureImportance(modelData.feature_importance || []);
      })
      .catch((e) => setError(getErrorMessage(e)))
      .finally(() => setLoading(false));
  };

  useEffect(load, [id]);

  const handleRegister = async () => {
    if (!id) return;
    setActionBusy(true);
    try {
      await blockchainApi.register(id);
      setToast("Registered on blockchain successfully.");
      load();
    } catch (e) {
      setToast(getErrorMessage(e));
    } finally {
      setActionBusy(false);
    }
  };

  const handleVerify = async () => {
    if (!id) return;
    setActionBusy(true);
    try {
      const res = await blockchainApi.verify(id);
      setToast(res.verified ? "VERIFIED: record matches blockchain." : "VERIFICATION FAILED: record does not match blockchain.");
    } catch (e) {
      setToast(getErrorMessage(e));
    } finally {
      setActionBusy(false);
    }
  };

  const handleStatusChange = async (status: string) => {
    if (!id) return;
    try {
      await applicationApi.updateStatus(id, status as any);
      load();
    } catch (e) {
      setToast(getErrorMessage(e));
    }
  };

  if (loading) return <LoadingSpinner label="Loading application..." />;
  if (error) return <ErrorState message={error} />;
  if (!app) return null;

  const f = app.input_features;

  return (
    <div>
      <button onClick={() => navigate("/applications")} className="flex items-center gap-1 text-xs text-slate-500 hover:text-slate-700 mb-3">
        <ArrowLeft size={13} /> Back to Applications
      </button>

      <PageHeader
        title={app.application_id}
        description={`Applicant reference: ${app.applicant_reference}`}
        actions={
          <>
            <select className="input-base w-auto" value={app.status} onChange={(e) => handleStatusChange(e.target.value)}>
              {APPLICATION_STATUSES.map((s) => <option key={s} value={s}>{s.replace("_", " ")}</option>)}
            </select>
            {!app.blockchain.registered ? (
              <Button onClick={handleRegister} loading={actionBusy}><Link2 size={14} /> Register on Blockchain</Button>
            ) : (
              <Button variant="secondary" onClick={handleVerify} loading={actionBusy}><ShieldCheck size={14} /> Verify</Button>
            )}
            <Button variant="secondary" onClick={() => exportApi.downloadApplicationPdf(app.application_id)}>
              <FileDown size={14} /> PDF
            </Button>
          </>
        }
      />

      {toast && (
        <div className="mb-4 text-xs bg-blue-50 border border-blue-200 text-blue-700 rounded-md px-3 py-2 flex justify-between">
          {toast}
          <button onClick={() => setToast(null)} className="text-blue-400">×</button>
        </div>
      )}

      <div className="grid lg:grid-cols-3 gap-5">
        <div className="lg:col-span-2 space-y-5">
          <div className="card p-5">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-sm font-semibold text-slate-900">ML Assessment</h3>
              <div className="flex gap-2">
                <RiskBadge risk={app.risk_category} />
                <StatusBadge status={app.status} />
              </div>
            </div>
            {app.default_probability !== null && (
              <>
                <RiskMeter probability={app.default_probability} risk={app.risk_category || "LOW"} />
                <div className="grid grid-cols-2 gap-3 text-sm mt-4">
                  <div><div className="text-xs text-slate-400">Model</div><div className="font-medium">{app.model_name}</div></div>
                  <div><div className="text-xs text-slate-400">Model Version</div><div className="font-medium">{app.model_version}</div></div>
                </div>
                <div className="mt-4">
                  <div className="text-xs font-medium text-slate-600 mb-2">Feature Importance (model-wide)</div>
                  <FeatureImportance factors={featureImportance.slice(0, 5)} />
                </div>
              </>
            )}
          </div>

          <div className="card p-5">
            <h3 className="text-sm font-semibold text-slate-900 mb-4">Loan &amp; Financial Details</h3>
            <div className="grid sm:grid-cols-2 gap-x-6 gap-y-3 text-sm">
              <Detail label="Loan Amount" value={formatCurrency(f.loan_amount)} />
              <Detail label="Loan Term" value={`${f.loan_term_months} months`} />
              <Detail label="Loan Purpose" value={f.requested_loan_purpose} />
              <Detail label="Annual Income" value={formatCurrency(f.annual_income)} />
              <Detail label="Credit Score" value={String(f.credit_score)} />
              <Detail label="Existing Debt" value={formatCurrency(f.existing_debt)} />
              <Detail label="Debt-to-Income Ratio" value={f.debt_to_income_ratio.toFixed(2)} />
              <Detail label="Savings Amount" value={formatCurrency(f.savings_amount)} />
              <Detail label="Employment Type" value={f.employment_type} />
              <Detail label="Employment Years" value={String(f.employment_years)} />
              <Detail label="Previous Loans" value={String(f.number_of_previous_loans)} />
              <Detail label="Previous Default" value={f.previous_default ? "Yes" : "No"} />
              <Detail label="Dependents" value={String(f.dependents)} />
              <Detail label="Age" value={String(f.age)} />
            </div>
          </div>

          <BlockchainDetails blockchain={app.blockchain} />
        </div>

        <div className="lg:col-span-1">
          <div className="card p-5">
            <h3 className="text-sm font-semibold text-slate-900 mb-4">Audit Timeline</h3>
            <AuditTimeline events={events} />
          </div>
          <div className="text-[11px] text-slate-400 mt-3">
            Created {formatDateTime(app.created_at)} · Updated {formatDateTime(app.updated_at)}
          </div>
        </div>
      </div>
    </div>
  );
}

function Detail({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <div className="text-xs text-slate-400">{label}</div>
      <div className="font-medium text-slate-800">{value}</div>
    </div>
  );
}
