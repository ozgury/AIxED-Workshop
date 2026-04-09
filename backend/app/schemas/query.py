from pydantic import BaseModel


class QueryRequest(BaseModel):
    question: str


class ChartDataset(BaseModel):
    label: str
    data: list[float | int | None]


class ChartData(BaseModel):
    labels: list[str]
    datasets: list[ChartDataset]
    chart_type: str


class TableData(BaseModel):
    columns: list[str]
    rows: list[list]


class QueryResponse(BaseModel):
    answer_text: str
    display_type: str  # "table" | "bar_chart" | "line_chart" | "pie_chart" | "summary"
    table_data: TableData | None = None
    chart_data: ChartData | None = None
    sql_used: str | None = None
    sources: list[str] = []
