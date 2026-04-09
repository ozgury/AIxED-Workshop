export interface Relationship {
  id: string;
  column_name: string;
  table_names: string[];
  file_ids: string[];
  detected_at: string;
}

export interface RelationshipListResponse {
  relationships: Relationship[];
}
