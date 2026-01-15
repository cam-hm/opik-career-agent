import { useState, useEffect, useCallback } from 'react';
import { useAuth } from '@clerk/nextjs';
import { fetchWithAuth } from '@/lib/api';

interface UseFetchOptions extends RequestInit {
    skip?: boolean;
    onSuccess?: (data: any) => void;
    onError?: (error: any) => void;
}

interface UseFetchResult<T> {
    data: T | null;
    loading: boolean;
    error: string | null;
    refetch: () => Promise<void>;
}

export function useFetch<T = any>(endpoint: string, options: UseFetchOptions = {}): UseFetchResult<T> {
    const { getToken } = useAuth();
    const [data, setData] = useState<T | null>(null);
    const [loading, setLoading] = useState(!options.skip);
    const [error, setError] = useState<string | null>(null);

    const fetchData = useCallback(async () => {
        if (options.skip) return;

        setLoading(true);
        setError(null);

        try {
            const res = await fetchWithAuth(endpoint, options, getToken);

            if (!res.ok) {
                throw new Error(`Error ${res.status}: ${res.statusText}`);
            }

            const jsonData = await res.json();
            setData(jsonData);
            options.onSuccess?.(jsonData);
        } catch (err: any) {
            console.error(`Fetch error for ${endpoint}:`, err);
            const errorMessage = err.message || 'Failed to fetch data';
            setError(errorMessage);
            options.onError?.(err);
        } finally {
            setLoading(false);
        }
    }, [endpoint, getToken, options.skip]); // Dependencies need care to avoid loops if options change

    useEffect(() => {
        fetchData();
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [endpoint, options.skip]);

    return { data, loading, error, refetch: fetchData };
}
