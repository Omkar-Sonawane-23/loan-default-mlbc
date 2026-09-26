import { useState } from "react";
import { useNavigate } from "react-router-dom";
import PageHeader from "../components/layout/PageHeader";
import LoanPredictionForm from "../components/forms/LoanPredictionForm";
import RiskResultCard from "../components/risk/RiskResultCard";
import Button from "../components/common/Button";
import ErrorState from "../components/common/ErrorState";
import { usePrediction } from "../hooks/usePrediction";
import { applicationApi } from "../api/applicationApi";
import { blockchainApi } from "../api/blockchainApi";
import { getErrorMessage } from "../api/client";
import { LoanFeatures } from "../types";
import { Save, Link2 } from "lucide-react";

export default function Predict() {
  const navigate = useNavigate();
  const { result, loading, error, predict } = usePrediction();
  const [lastFeatures, setLastFeatures] = useState<LoanFeatures | null>(null);
  const [saving, setSaving] = useState(false);
  const [registering, setRegistering] = useState(false);
  const [savedAppId, setSavedAppId] = useState<string | null>(null);
  const [actionMessage, setActionMessage] = useState<string | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);

  const handlePredict = async (features: LoanFeatures) => {
    setLastFeatures(features);
    setSavedAppId(null);
    setActionMessage(null);
    setActionError(null);
    try {
      await predict(features);
    } catch {
      // error already captured in hook
    }
  };

  const handleSave = async () => {
    if (!lastFeatures) return;
    setSaving(true);
    setActionError(null);
    try {
      const app = await applicationApi.create(lastFeatures);
      setSavedAppId(app.application_id);
      setActionMessage(`Saved as ${app.application_id}`);
    } catch (e) {
      setActionError(getErrorMessage(e));
    } finally {
      setSaving(false);
    }
  };

  const handleRegister = async () => {
    if (!savedAppId) return;
    setRegistering(true);
    setActionError(null);
    try {
      const reg = await blockchainApi.register(savedAppId);
      setActionMessage(`Registered on blockchain. Tx: ${reg.transaction_hash.slice(0, 14)}...`);
    } catch (e) {
      setActionError(getErrorMessage(e));
    } finally {
      setRegistering(false);
    }
  };

  return (
    <div>
      <PageHeader title="Loan Risk Prediction" description="Enter application details to generate a real-time ML risk assessment" />
      <div className="grid lg:grid-cols-2 gap-6">
        <LoanPredictionForm onSubmit={handlePredict} loading={loading} />

        <div>
          {error && <ErrorState message={error} />}
          {!error && result && (
            <div className="space-y-4">
              <RiskResultCard result={result} />
              <div className="flex gap-2">
                <Button onClick={handleSave} loading={saving} disabled={!!savedAppId} className="flex-1 justify-center">
                  <Save size={14} /> {savedAppId ? "Saved" : "Save Application"}
                </Button>
                <Button variant="secondary" onClick={handleRegister} loading={registering} disabled={!savedAppId} className="flex-1 justify-center">
                  <Link2 size={14} /> Register on Blockchain
                </Button>
              </div>
              {actionMessage && <p className="text-xs text-green-600">{actionMessage}</p>}
              {actionError && <p className="text-xs text-red-600">{actionError}</p>}
              {savedAppId && (
                <button onClick={() => navigate(`/applications/${savedAppId}`)} className="text-xs text-accent-600 hover:underline">
                  View application details →
                </button>
              )}
            </div>
          )}
          {!error && !result && (
            <div className="card p-10 text-center text-sm text-slate-400">
              Fill in the form and click "Predict Risk" to see the assessment here.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
