import { useState } from "react";
import PageHeader from "../components/layout/PageHeader";
import Button from "../components/common/Button";
import VerificationResult from "../components/blockchain/VerificationResult";
import ErrorState from "../components/common/ErrorState";
import { blockchainApi } from "../api/blockchainApi";
import { getErrorMessage } from "../api/client";
import { BlockchainVerifyResponse } from "../types";
import { ShieldCheck } from "lucide-react";

export default function Verify() {
  const [applicationId, setApplicationId] = useState("");
  const [result, setResult] = useState<BlockchainVerifyResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleVerify = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!applicationId.trim()) return;
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const res = await blockchainApi.verify(applicationId.trim());
      setResult(res);
    } catch (e) {
      setError(getErrorMessage(e));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <PageHeader title="Verify Record" description="Check whether an application's database record matches its blockchain-registered hash" />

      <div className="card p-5 mb-6 max-w-xl">
        <form onSubmit={handleVerify} className="flex gap-2">
          <input
            className="input-base"
            placeholder="Enter Application ID (e.g. LN-000001)"
            value={applicationId}
            onChange={(e) => setApplicationId(e.target.value)}
          />
          <Button type="submit" loading={loading}>
            <ShieldCheck size={14} /> Verify Record
          </Button>
        </form>
      </div>

      {error && <ErrorState message={error} />}
      {result && <div className="max-w-xl"><VerificationResult result={result} /></div>}
    </div>
  );
}
