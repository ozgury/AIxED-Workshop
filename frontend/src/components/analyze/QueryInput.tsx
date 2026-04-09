import { useState, useRef } from "react";

interface Props {
  onSubmit: (question: string) => void;
  isLoading: boolean;
}

export function QueryInput({ onSubmit, isLoading }: Props) {
  const [question, setQuestion] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleSubmit = () => {
    const q = question.trim();
    if (q && !isLoading) {
      onSubmit(q);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className="relative">
      <textarea
        ref={textareaRef}
        value={question}
        onChange={(e) => setQuestion(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="Ask a question about your data..."
        rows={3}
        disabled={isLoading}
        className="w-full resize-none rounded-xl border border-gray-300 bg-white px-5 py-4 pr-24 text-gray-900 placeholder-gray-400 shadow-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-200 disabled:opacity-60"
      />
      <button
        onClick={handleSubmit}
        disabled={isLoading || !question.trim()}
        className="absolute bottom-4 right-4 rounded-lg bg-primary-600 px-4 py-2 text-sm font-medium text-white shadow-sm transition-colors hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {isLoading ? (
          <span className="flex items-center gap-2">
            <span className="h-4 w-4 animate-spin rounded-full border-2 border-white/30 border-t-white" />
            Thinking...
          </span>
        ) : (
          "Ask"
        )}
      </button>
      <p className="mt-1 text-right text-xs text-gray-400">Ctrl+Enter to submit</p>
    </div>
  );
}
