import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { submitQuery } from "../api/query";
import type { QueryResponse } from "../types/query";

export interface QueryHistoryItem {
  question: string;
  response: QueryResponse;
  timestamp: Date;
}

export function useAnalyze() {
  const [history, setHistory] = useState<QueryHistoryItem[]>([]);

  const mutation = useMutation({
    mutationFn: submitQuery,
    onSuccess: (data, question) => {
      setHistory((prev) => [
        { question, response: data, timestamp: new Date() },
        ...prev,
      ]);
    },
  });

  return {
    submitQuestion: mutation.mutate,
    isLoading: mutation.isPending,
    currentResult: history[0]?.response ?? null,
    error: mutation.error,
    history,
    selectHistory: (index: number) => {
      const item = history[index];
      if (item) {
        setHistory((prev) => {
          const copy = [...prev];
          const [selected] = copy.splice(index, 1);
          return [selected, ...copy];
        });
      }
    },
  };
}
