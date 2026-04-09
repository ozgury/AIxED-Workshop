import client from "./client";
import type { QueryResponse } from "../types/query";

export async function submitQuery(question: string): Promise<QueryResponse> {
  const res = await client.post<QueryResponse>("/query", { question });
  return res.data;
}
