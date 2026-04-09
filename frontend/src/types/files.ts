export interface FileRecord {
  id: string;
  original_name: string;
  file_type: "spreadsheet" | "document";
  mime_type: string;
  file_size: number;
  table_name: string | null;
  row_count: number | null;
  column_names: string[] | null;
  status: string;
  error_message: string | null;
  created_at: string;
  updated_at: string;
}

export interface FileListResponse {
  files: FileRecord[];
  total: number;
}
