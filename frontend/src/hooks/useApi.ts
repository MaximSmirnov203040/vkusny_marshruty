import { useState, useCallback } from 'react';
import { AxiosError } from 'axios';

interface UseApiState<T> {
  data: T | null;
  error: string | null;
  isLoading: boolean;
}

interface UseApiResponse<T> extends UseApiState<T> {
  execute: (...args: any[]) => Promise<void>;
  reset: () => void;
}

export function useApi<T>(
  apiFunction: (...args: any[]) => Promise<any>,
  initialData: T | null = null
): UseApiResponse<T> {
  const [state, setState] = useState<UseApiState<T>>({
    data: initialData,
    error: null,
    isLoading: false,
  });

  const execute = useCallback(
    async (...args: any[]) => {
      try {
        setState((prev) => ({ ...prev, isLoading: true, error: null }));
        const response = await apiFunction(...args);
        setState({
          data: response.data,
          error: null,
          isLoading: false,
        });
        return response.data;
      } catch (error) {
        const axiosError = error as AxiosError<{ detail: string }>;
        const errorMessage =
          axiosError.response?.data?.detail || 'Произошла ошибка';
        setState((prev) => ({
          ...prev,
          error: errorMessage,
          isLoading: false,
        }));
        throw error;
      }
    },
    [apiFunction]
  );

  const reset = useCallback(() => {
    setState({
      data: initialData,
      error: null,
      isLoading: false,
    });
  }, [initialData]);

  return {
    ...state,
    execute,
    reset,
  };
}

export default useApi; 