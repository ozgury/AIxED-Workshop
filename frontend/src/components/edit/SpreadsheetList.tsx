import type { FileRecord } from "../../types/files";
import { FileCard } from "./FileCard";

interface Props {
  files: FileRecord[];
}

export function SpreadsheetList({ files }: Props) {
  const spreadsheets = files.filter((f) => f.file_type === "spreadsheet");

  if (spreadsheets.length === 0) {
    return (
      <div className="rounded-lg border border-dashed border-gray-300 p-8 text-center">
        <p className="text-sm text-gray-500">No spreadsheets uploaded yet</p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      <h2 className="text-sm font-semibold uppercase tracking-wide text-gray-500">
        Spreadsheets ({spreadsheets.length})
      </h2>
      <div className="space-y-2">
        {spreadsheets.map((f) => (
          <FileCard key={f.id} file={f} />
        ))}
      </div>
    </div>
  );
}
