import { useState, useCallback } from "react";

export type Mode = "edit" | "analyze";

export function useMode() {
  const [mode, setModeState] = useState<Mode>(() => {
    const saved = localStorage.getItem("wildcard-mode");
    return saved === "analyze" ? "analyze" : "edit";
  });

  const setMode = useCallback((m: Mode) => {
    setModeState(m);
    localStorage.setItem("wildcard-mode", m);
  }, []);

  return { mode, setMode };
}
