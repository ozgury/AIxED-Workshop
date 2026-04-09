import { ModeToggle } from "./ModeToggle";
import type { Mode } from "../../hooks/useMode";

interface Props {
  mode: Mode;
  onModeChange: (mode: Mode) => void;
}

export function Header({ mode, onModeChange }: Props) {
  return (
    <header className="border-b border-gray-200 bg-white">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4">
        <div className="flex items-center gap-3">
          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-primary-600 text-white font-bold text-lg">
            W
          </div>
          <h1 className="text-xl font-bold text-gray-900">WildCard</h1>
        </div>
        <ModeToggle mode={mode} onModeChange={onModeChange} />
      </div>
    </header>
  );
}
