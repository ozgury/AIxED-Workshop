export interface ChartDataset {
  label: string;
  data: (number | null)[];
}

export interface ChartData {
  labels: string[];
  datasets: ChartDataset[];
  chart_type: string;
}

export interface TableData {
  columns: string[];
  rows: unknown[][];
}

export interface QueryResponse {
  answer_text: string;
  display_type: string;
  table_data: TableData | null;
  chart_data: ChartData | null;
  sql_used: string | null;
  sources: string[];
}
