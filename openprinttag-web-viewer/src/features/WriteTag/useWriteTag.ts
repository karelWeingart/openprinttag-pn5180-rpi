import { useState, ChangeEvent, FormEvent, RefObject } from "react";

export interface WriteTagState {
  file: File | null;
  uploadStatus: "idle" | "uploading" | "success" | "error";
  handleFileChange: (e: ChangeEvent<HTMLInputElement>) => void;
  handleSubmit: (e: FormEvent) => void;
}

export function useWriteTag(formRef: RefObject<HTMLFormElement | null>): WriteTagState {
  const [file, setFile] = useState<File | null>(null);
  const [uploadStatus, setUploadStatus] = useState<"idle" | "uploading" | "success" | "error">("idle");

  const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    const selected = e.target.files?.[0] ?? null;
    if (selected && !selected.name.endsWith(".bin")) {
      alert("Please select a .bin file");
      setFile(null);
      e.target.value = "";
      return;
    }
    setFile(selected);
  };

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
      formRef.current?.reset();
    } catch (err) {
      console.error("Upload failed:", err);
      alert(`Upload failed: ${err}`);
      setUploadStatus("error");
    } 
  };

  return { file, uploadStatus, handleFileChange, handleSubmit };
}