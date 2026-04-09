import { useCallback, useState } from "react";
import { useDropzone } from "react-dropzone";
import { useUploadFile } from "../../hooks/useFiles";
import { ErrorBanner } from "../shared/ErrorBanner";

const ACCEPTED = {
  "text/csv": [".csv"],
  "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": [".xlsx"],
  "application/vnd.ms-excel": [".xls"],
  "application/pdf": [".pdf"],
  "application/vnd.openxmlformats-officedocument.wordprocessingml.document": [".docx"],
  "application/msword": [".doc"],
  "text/plain": [".txt"],
};

export function FileUploader() {
  const upload = useUploadFile();
  const [error, setError] = useState<string | null>(null);

  const onDrop = useCallback(
    (acceptedFiles: File[]) => {
      setError(null);
      for (const file of acceptedFiles) {
        upload.mutate(file, {
          onError: (err: Error) => {
            setError(err.message || "Upload failed");
          },
        });
      }
    },
    [upload]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: ACCEPTED,
    maxSize: 50 * 1024 * 1024,
    onDropRejected: (rejections) => {
      const msg = rejections[0]?.errors[0]?.message || "File not accepted";
      setError(msg);
    },
  });

  return (
    <div className="space-y-4">
      <div
        {...getRootProps()}
        className={`flex cursor-pointer flex-col items-center justify-center rounded-xl border-2 border-dashed p-10 transition-colors ${
          isDragActive
            ? "border-primary-400 bg-primary-50"
            : "border-gray-300 bg-white hover:border-primary-300 hover:bg-gray-50"
        }`}
      >
        <input {...getInputProps()} />
        <div className="text-center">
          <div className="mx-auto mb-3 flex h-12 w-12 items-center justify-center rounded-full bg-primary-100">
            <svg className="h-6 w-6 text-primary-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
            </svg>
          </div>
          {upload.isPending ? (
            <p className="text-sm text-primary-600 font-medium">Uploading and processing...</p>
          ) : (
            <>
              <p className="text-sm font-medium text-gray-700">
                {isDragActive ? "Drop files here" : "Drag & drop files here, or click to browse"}
              </p>
              <p className="mt-1 text-xs text-gray-500">
                Spreadsheets (CSV, Excel) or Documents (PDF, Word, TXT)
              </p>
            </>
          )}
        </div>
      </div>
      {error && <ErrorBanner message={error} onDismiss={() => setError(null)} />}
    </div>
  );
}
