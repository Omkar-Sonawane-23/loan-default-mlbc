import { useState, useCallback } from "react";
import { blockchainApi } from "../api/blockchainApi";
import { getErrorMessage } from "../api/client";
import { BlockchainVerifyResponse, BlockchainRegisterResponse } from "../types";

export function useBlockchain() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const register = useCallback(async (applicationId: string): Promise<BlockchainRegisterResponse | null> => {
    setLoading(true);
    setError(null);
    try {
      return await blockchainApi.register(applicationId);
    } catch (e) {
      setError(getErrorMessage(e));
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  const verify = useCallback(async (applicationId: string): Promise<BlockchainVerifyResponse | null> => {
    setLoading(true);
    setError(null);
    try {
      return await blockchainApi.verify(applicationId);
    } catch (e) {
      setError(getErrorMessage(e));
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  return { register, verify, loading, error };
}
