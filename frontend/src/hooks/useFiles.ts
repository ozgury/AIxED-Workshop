import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { listFiles, uploadFile, deleteFile, listRelationships } from "../api/files";

export function useFiles() {
  return useQuery({
    queryKey: ["files"],
    queryFn: listFiles,
  });
}

export function useRelationships() {
  return useQuery({
    queryKey: ["relationships"],
    queryFn: listRelationships,
  });
}

export function useUploadFile() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: uploadFile,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["files"] });
      qc.invalidateQueries({ queryKey: ["relationships"] });
    },
  });
}

export function useDeleteFile() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: deleteFile,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["files"] });
      qc.invalidateQueries({ queryKey: ["relationships"] });
    },
  });
}
