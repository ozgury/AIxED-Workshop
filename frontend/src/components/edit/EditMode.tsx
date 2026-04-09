import { useFiles } from "../../hooks/useFiles";
import { LoadingSpinner } from "../shared/LoadingSpinner";
import { FileUploader } from "./FileUploader";
import { SpreadsheetList } from "./SpreadsheetList";
import { DocumentList } from "./DocumentList";
import { RelationshipMap } from "./RelationshipMap";

export function EditMode() {
  const { data, isLoading } = useFiles();
  const files = data?.files ?? [];

  return (
    <div className="space-y-8">
      <FileUploader />

      {isLoading ? (
        <LoadingSpinner className="py-12" />
      ) : (
        <>
          <SpreadsheetList files={files} />
          <DocumentList files={files} />
          <RelationshipMap />
        </>
      )}
    </div>
  );
}
