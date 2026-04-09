import client from "./client";
import type { FileListResponse, FileRecord } from "../types/files";
import type { RelationshipListResponse } from "../types/relationships";

export async function listFiles(): Promise<FileListResponse> {
  const res = await client.get<FileListResponse>("/files");
  return res.data;
}

export async function uploadFile(file: File): Promise<FileRecord> {
  const formData = new FormData();
  formData.append("file", file);
  const res = await client.post<FileRecord>("/files/upload", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return res.data;
}

export async function deleteFile(fileId: string): Promise<void> {
  await client.delete(`/files/${fileId}`);
}

export async function listRelationships(): Promise<RelationshipListResponse> {
  const res = await client.get<RelationshipListResponse>("/relationships");
  return res.data;
}
