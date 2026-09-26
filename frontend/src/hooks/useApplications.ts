import { useEffect, useState, useCallback } from "react";
import { applicationApi, ApplicationFilters } from "../api/applicationApi";
import { PaginatedApplications } from "../types";
import { getErrorMessage } from "../api/client";

export function useApplications(filters: ApplicationFilters) {
  const [data, setData] = useState<PaginatedApplications | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const refetch = useCallback(() => {
    setLoading(true);
    setError(null);
    applicationApi
      .list(filters)
      .then(setData)
      .catch((e) => setError(getErrorMessage(e)))
      .finally(() => setLoading(false));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [JSON.stringify(filters)]);

  useEffect(() => {
    refetch();
  }, [refetch]);

  return { data, loading, error, refetch };
}
