import { useMode } from "../../hooks/useMode";
import { Header } from "./Header";
import { EditMode } from "../edit/EditMode";
import { AnalyzeMode } from "../analyze/AnalyzeMode";

export function AppShell() {
  const { mode, setMode } = useMode();

  return (
    <div className="min-h-screen bg-gray-50">
      <Header mode={mode} onModeChange={setMode} />
      <main className="mx-auto max-w-7xl px-6 py-8">
        {mode === "edit" ? <EditMode /> : <AnalyzeMode />}
      </main>
    </div>
  );
}
