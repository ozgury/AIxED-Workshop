import { useState } from "react";
import type { FileRecord } from "../../types/files";
import { useDeleteFile } from "../../hooks/useFiles";
import { formatFileSize } from "../../lib/utils";
import { ConfirmDialog } from "../shared/ConfirmDialog";

interface Props {
  file: FileRecord;
}

export function FileCard({ file }: Props) {
  const [showConfirm, setShowConfirm] = useState(false);
  const deleteMutation = useDeleteFile();

  const icon = file.file_type === "spreadsheet" ? (
    <svg className="h-5 w-5 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 10h18M3 14h18m-9-4v8m-7 0h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
    </svg>
  ) : (
    <svg className="h-5 w-5 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
    </svg>
  );

  return (
    <>
      <div className="flex items-center justify-between rounded-lg border border-gray-200 bg-white p-4">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-gray-50">
            {icon}
          </div>
          <div>
            <p className="font-medium text-gray-900">{file.original_name}</p>
            <div className="flex items-center gap-3 text-xs text-gray-500">
              <span>{formatFileSize(file.file_size)}</span>
              {file.file_type === "spreadsheet" && file.row_count != null && (
                <span>{file.row_count.toLocaleString()} rows</span>
              )}
              {file.file_type === "spreadsheet" && file.column_names && (
                <span>{file.column_names.length} columns</span>
              )}
              {file.status === "processing" && (
                <span className="text-amber-600">Processing...</span>
              )}
              {file.status === "error" && (
                <span className="text-red-600">Error</span>
              )}
            </div>
            {file.file_type === "spreadsheet" && file.column_names && (
              <p className="mt-1 text-xs text-gray-400 truncate max-w-md">
                {file.column_names.join(", ")}
              </p>
            )}
          </div>
        </div>
        <button
          onClick={() => setShowConfirm(true)}
          disabled={deleteMutation.isPending}
          className="rounded-lg p-2 text-gray-400 hover:bg-red-50 hover:text-red-600 transition-colors"
        >
          <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
          </svg>
        </button>
      </div>
      <ConfirmDialog
        open={showConfirm}
        title="Delete File"
        message={`Are you sure you want to delete "${file.original_name}"? This will remove all associated data.`}
        onConfirm={() => {
          deleteMutation.mutate(file.id);
          setShowConfirm(false);
        }}
        onCancel={() => setShowConfirm(false)}
      />
    </>
  );
}
