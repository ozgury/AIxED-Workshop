import { cn } from "../../lib/utils";
import type { Mode } from "../../hooks/useMode";

interface Props {
  mode: Mode;
  onModeChange: (mode: Mode) => void;
}

export function ModeToggle({ mode, onModeChange }: Props) {
  return (
    <div className="inline-flex rounded-lg bg-gray-100 p-1">
      <button
        onClick={() => onModeChange("edit")}
        className={cn(
          "rounded-md px-4 py-2 text-sm font-medium transition-colors",
          mode === "edit"
            ? "bg-white text-primary-700 shadow-sm"
            : "text-gray-600 hover:text-gray-900"
        )}
      >
        Manage Data
      </button>
      <button
        onClick={() => onModeChange("analyze")}
        className={cn(
          "rounded-md px-4 py-2 text-sm font-medium transition-colors",
          mode === "analyze"
            ? "bg-white text-primary-700 shadow-sm"
            : "text-gray-600 hover:text-gray-900"
        )}
      >
        Ask Questions
      </button>
    </div>
  );
}
