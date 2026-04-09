import { useRelationships, useFiles } from "../../hooks/useFiles";

export function RelationshipMap() {
  const { data: relData } = useRelationships();
  const { data: fileData } = useFiles();

  const relationships = relData?.relationships ?? [];

  if (relationships.length === 0) {
    return null;
  }

  const fileNameMap = new Map<string, string>();
  for (const f of fileData?.files ?? []) {
    if (f.table_name) {
      fileNameMap.set(f.table_name, f.original_name);
    }
  }

  return (
    <div className="space-y-3">
      <h2 className="text-sm font-semibold uppercase tracking-wide text-gray-500">
        Detected Relationships
      </h2>
      <div className="space-y-2">
        {relationships.map((rel) => (
          <div
            key={rel.id}
            className="rounded-lg border border-primary-200 bg-primary-50 p-4"
          >
            <div className="flex items-center gap-2">
              <span className="rounded-md bg-primary-600 px-2 py-1 text-xs font-medium text-white">
                {rel.column_name}
              </span>
              <span className="text-xs text-gray-500">links</span>
            </div>
            <div className="mt-2 flex flex-wrap gap-2">
              {rel.table_names.map((tn) => (
                <span
                  key={tn}
                  className="rounded-md bg-white px-3 py-1 text-sm text-gray-700 border border-primary-200"
                >
                  {fileNameMap.get(tn) ?? tn}
                </span>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
