import { useState, ChangeEvent, FormEvent, RefObject } from "react";
import { TagData } from "../../types";

export interface WriteTagState {
  file: File | null;
  uploadStatus: "idle" | "uploading" | "success" | "error";
  handleFileChange: (e: ChangeEvent<HTMLInputElement>) => void;
  handleSubmit: (e: FormEvent) => void;
  handleCancel: () => void;
  tagData: TagData | null;
}

export function useWriteTag(formRef: RefObject<HTMLFormElement | null>): WriteTagState {
  const [file, setFile] = useState<File | null>(null);
  const [uploadStatus, setUploadStatus] = useState<"idle" | "uploading" | "success" | "error">("idle");
  const [tagData, setTagData] = useState<TagData | null>(null);
  const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    const selected = e.target.files?.[0] ?? null;
    if (selected && !selected.name.endsWith(".bin")) {
      alert("Please select a .bin file");
      setFile(null);
      e.target.value = "";
      return;
    }
    setFile(selected);
    setUploadStatus("idle");
  };

  const handleCancel = async () => {
    try {
      const res = await fetch("/tags/bin", {
        method: "DELETE",
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      setFile(null);
      setUploadStatus("idle");
      setTagData(null);
      formRef.current?.reset();
    } catch (err) {
      setFile(null);
      setUploadStatus("idle");
      setTagData(null);
      formRef.current?.reset();
    }    
  }


  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    console.log("Submitting file:", file);
    if (!file) return;

    const formData = new FormData();
    formData.append("file", file);

    setUploadStatus("uploading");
    try {
      const res = await fetch("/tags/bin", {
        method: "POST",
        body: formData,
      });
      console.log("Upload response:", res);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      setFile(null);
      setUploadStatus("success");
      setTagData((await res.json()).data as TagData);
      formRef.current?.reset();
    } catch (err) {
      console.error("Upload failed:", err);
      setFile(null);      
      setUploadStatus("error");
    } 
  };

  return { file, uploadStatus, handleFileChange, handleSubmit, tagData, handleCancel };
}