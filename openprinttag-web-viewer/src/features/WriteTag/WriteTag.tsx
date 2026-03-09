import { useRef } from "react";
import { useWriteTag } from "./useWriteTag";
import { TagCard } from "../TagCard";

export function WriteTag() {
  const formRef = useRef<HTMLFormElement>(null);
  const { file, uploadStatus, handleFileChange, handleSubmit, tagData, handleCancel } = useWriteTag(formRef);

  return (
    <>
    <form ref={formRef} onSubmit={handleSubmit}>
      <div className="mb-3">
        <label htmlFor="binFile" className="form-label">
          Upload .bin file
        </label>
        <input
          type="file"
          className="form-control"
          id="binFile"
          accept=".bin"
          onChange={handleFileChange}
        />
      </div>
      
        <div className="mb-3">
          <small className="text-muted">
            {file && `Selected File: ${file.name} (${(file.size / 1024).toFixed(1)} KB)`}
            {uploadStatus === "error" && "Upload failed. Please try again."}
            {uploadStatus === "success" && "Upload successful!"}
          </small>
        </div>
      
      <button type="submit" className="btn btn-primary" disabled={!file || uploadStatus === "uploading"}>
        {uploadStatus === "uploading" ? "Uploading…" : "Upload"}
      </button>
      <button type="button" className="btn btn-secondary" disabled={uploadStatus !== "success"} onClick={handleCancel}>
        Cancel
      </button>
    </form>
    {tagData && <TagCard tag={tagData} />}
    </>
  );
}