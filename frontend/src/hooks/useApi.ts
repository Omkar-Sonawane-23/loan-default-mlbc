import { useState, useCallback } from "react";
import { getErrorMessage } from "../api/client";

export function useApi<T, Args extends unknown[]>(fn: (...args: Args) => Promise<T>) {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const execute = useCallback(
    async (...args: Args) => {
      setLoading(true);
      setError(null);
      try {
        const result = await fn(...args);
        setData(result);
        return result;
      } catch (e) {
        setError(getErrorMessage(e));
        throw e;
      } finally {
        setLoading(false);
      }
    },
    [fn]
  );

  return { data, loading, error, execute, setData };
}
