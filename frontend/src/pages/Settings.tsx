import { useEffect, useState } from "react";
import PageHeader from "../components/layout/PageHeader";
import LoadingSpinner from "../components/common/LoadingSpinner";
import { apiClient } from "../api/client";
import { blockchainApi } from "../api/blockchainApi";
import { modelApi } from "../api/modelApi";
import { CheckCircle2, XCircle } from "lucide-react";

export default function Settings() {
  const [health, setHealth] = useState<any>(null);
  const [chain, setChain] = useState<any>(null);
  const [model, setModel] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      apiClient.get("/health").then((r) => r.data).catch(() => null),
      blockchainApi.status().catch(() => null),
      modelApi.info().catch(() => null),
    ]).then(([h, c, m]) => {
      setHealth(h); setChain(c); setModel(m);
    }).finally(() => setLoading(false));
  }, []);

  if (loading) return <LoadingSpinner label="Checking system status..." />;

  const StatusRow = ({ label, ok, value }: { label: string; ok: boolean; value?: string }) => (
    <div className="flex items-center justify-between py-2.5 border-b border-slate-100 last:border-0">
      <span className="text-sm text-slate-600">{label}</span>
      <div className="flex items-center gap-2">
        {value && <span className="text-xs text-slate-400 font-mono">{value}</span>}
        {ok ? <CheckCircle2 size={15} className="text-green-600" /> : <XCircle size={15} className="text-red-500" />}
      </div>
    </div>
  );

  return (
    <div>
      <PageHeader title="Settings" description="System configuration and service status" />

      <div className="grid lg:grid-cols-2 gap-5 max-w-3xl">
        <div className="card p-5">
          <h3 className="text-sm font-semibold text-slate-900 mb-2">System Status</h3>
          <StatusRow label="Backend API" ok={!!health} />
          <StatusRow label="MongoDB" ok={!!health?.mongodb_connected} />
          <StatusRow label="ML Model Loaded" ok={!!health?.ml_model_loaded} />
          <StatusRow label="Blockchain Available" ok={!!chain?.available} />
        </div>

        <div className="card p-5">
          <h3 className="text-sm font-semibold text-slate-900 mb-2">Blockchain Configuration</h3>
          <div className="text-sm space-y-2.5">
            <div className="flex justify-between"><span className="text-slate-500">Network</span><span className="font-mono text-xs">{chain?.rpc_url || "-"}</span></div>
            <div className="flex justify-between"><span className="text-slate-500">Chain ID</span><span className="font-mono text-xs">{chain?.chain_id ?? "-"}</span></div>
            <div className="flex justify-between"><span className="text-slate-500">Contract Address</span><span className="font-mono text-xs truncate max-w-[160px]">{chain?.contract_address || "Not deployed"}</span></div>
          </div>
        </div>

        <div className="card p-5">
          <h3 className="text-sm font-semibold text-slate-900 mb-2">ML Model</h3>
          <div className="text-sm space-y-2.5">
            <div className="flex justify-between"><span className="text-slate-500">Model Version</span><span className="font-mono text-xs">{model?.model_version || "-"}</span></div>
            <div className="flex justify-between"><span className="text-slate-500">Model Name</span><span>{model?.model_name || "-"}</span></div>
          </div>
        </div>

        <div className="card p-5">
          <h3 className="text-sm font-semibold text-slate-900 mb-2">API Configuration</h3>
          <div className="text-sm space-y-2.5">
            <div className="flex justify-between"><span className="text-slate-500">API URL</span><span className="font-mono text-xs">{import.meta.env.VITE_API_URL}</span></div>
            <div className="flex justify-between"><span className="text-slate-500">App Version</span><span>{health?.app_version || "-"}</span></div>
          </div>
        </div>
      </div>

      <p className="text-[11px] text-slate-400 mt-6 max-w-3xl leading-relaxed">
        This system is an academic Machine Learning and Blockchain demonstration. The predicted default probability
        is an estimated model output and is not financial advice, a guaranteed prediction, or an automated loan
        approval/rejection decision. No private keys or secrets are displayed in this interface.
      </p>
    </div>
  );
}
