import type { QueryHistoryItem } from "../../hooks/useAnalyze";

interface Props {
  history: QueryHistoryItem[];
  onSelect: (index: number) => void;
}

export function QueryHistory({ history, onSelect }: Props) {
  if (history.length === 0) return null;

  return (
    <div className="space-y-2">
      <h3 className="text-sm font-semibold uppercase tracking-wide text-gray-500">
        Recent Questions
      </h3>
      <div className="space-y-1">
        {history.map((item, i) => (
          <button
            key={i}
            onClick={() => onSelect(i)}
            className="w-full rounded-lg px-3 py-2 text-left text-sm text-gray-700 hover:bg-primary-50 hover:text-primary-700 transition-colors truncate"
          >
            {item.question}
          </button>
        ))}
      </div>
    </div>
  );
}
