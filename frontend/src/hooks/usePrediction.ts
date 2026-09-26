import { useState, useCallback } from "react";
import { predictionApi } from "../api/predictionApi";
import { LoanFeatures, PredictionResult } from "../types";
import { getErrorMessage } from "../api/client";

export function usePrediction() {
  const [result, setResult] = useState<PredictionResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const predict = useCallback(async (features: LoanFeatures) => {
    setLoading(true);
    setError(null);
    try {
      const res = await predictionApi.predict({ input_features: features });
      setResult(res);
      return res;
    } catch (e) {
      setError(getErrorMessage(e));
      throw e;
    } finally {
      setLoading(false);
    }
  }, []);

  return { result, loading, error, predict, reset: () => setResult(null) };
}
