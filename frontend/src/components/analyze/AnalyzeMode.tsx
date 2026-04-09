import { useAnalyze } from "../../hooks/useAnalyze";
import { ErrorBanner } from "../shared/ErrorBanner";
import { QueryInput } from "./QueryInput";
import { ResultDisplay } from "./ResultDisplay";
import { QueryHistory } from "./QueryHistory";

export function AnalyzeMode() {
  const { submitQuestion, isLoading, currentResult, error, history, selectHistory } =
    useAnalyze();

  return (
    <div className="grid grid-cols-1 gap-8 lg:grid-cols-[1fr_280px]">
      <div className="space-y-6">
        <QueryInput onSubmit={submitQuestion} isLoading={isLoading} />

        {error && (
          <ErrorBanner
            message={
              (error as Error).message || "Something went wrong. Please try again."
            }
          />
        )}

        {currentResult && <ResultDisplay result={currentResult} />}

        {!currentResult && !isLoading && (
          <div className="rounded-xl border border-dashed border-gray-300 p-12 text-center">
            <p className="text-gray-500">
              Ask a question about your uploaded data to get started
            </p>
            <div className="mt-4 space-y-1 text-sm text-gray-400">
              <p>Try questions like:</p>
              <p>"Which programs have the most enrollment?"</p>
              <p>"How has retention trended over time?"</p>
              <p>"What does the strategic plan say about program quality?"</p>
            </div>
          </div>
        )}
      </div>

      <aside className="hidden lg:block">
        <QueryHistory history={history} onSelect={selectHistory} />
      </aside>
    </div>
  );
}
