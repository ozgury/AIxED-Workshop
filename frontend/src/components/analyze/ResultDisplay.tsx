import { useState } from "react";
import type { QueryResponse } from "../../types/query";
import { DataTable } from "./DataTable";
import { ChartDisplay } from "./ChartDisplay";
import { SummaryDisplay } from "./SummaryDisplay";

interface Props {
  result: QueryResponse;
}

export function ResultDisplay({ result }: Props) {
  const [showSql, setShowSql] = useState(false);

  return (
    <div className="space-y-6">
      {/* Answer text */}
      <SummaryDisplay text={result.answer_text} />

      {/* Chart */}
      {result.chart_data && (
        <div className="rounded-lg border border-gray-200 bg-white p-6">
          <ChartDisplay data={result.chart_data} />
        </div>
      )}

      {/* Table */}
      {result.table_data && result.display_type === "table" && (
        <DataTable data={result.table_data} />
      )}

      {/* Supporting table for chart results */}
      {result.table_data && result.display_type !== "table" && result.chart_data && (
        <details className="rounded-lg border border-gray-200 bg-white">
          <summary className="cursor-pointer px-4 py-3 text-sm font-medium text-gray-600 hover:text-gray-900">
            View data table
          </summary>
          <div className="p-4 pt-0">
            <DataTable data={result.table_data} />
          </div>
        </details>
      )}

      {/* Sources */}
      {result.sources.length > 0 && (
        <div className="flex flex-wrap items-center gap-2 text-xs text-gray-500">
          <span>Sources:</span>
          {result.sources.map((s) => (
            <span key={s} className="rounded bg-gray-100 px-2 py-1">
              {s}
            </span>
          ))}
        </div>
      )}

      {/* SQL */}
      {result.sql_used && (
        <div>
          <button
            onClick={() => setShowSql(!showSql)}
            className="text-xs text-gray-400 hover:text-gray-600"
          >
            {showSql ? "Hide SQL" : "Show SQL"}
          </button>
          {showSql && (
            <pre className="mt-2 overflow-x-auto rounded-lg bg-gray-900 p-4 text-xs text-gray-100">
              <code>{result.sql_used}</code>
            </pre>
          )}
        </div>
      )}
    </div>
  );
}
