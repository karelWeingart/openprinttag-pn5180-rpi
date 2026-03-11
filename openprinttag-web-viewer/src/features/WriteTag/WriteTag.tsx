import { useRef } from "react";
import { useWriteTag } from "./useWriteTag";
import { TagCard } from "../TagCard";

export function WriteTag() {
  const formRef = useRef<HTMLFormElement>(null);
  const { file, uploadStatus, handleFileChange, handleSubmit, tagData, handleCancel } = useWriteTag(formRef);

  return (
    <div className="container">
      <div className="row">
        <div className="col">
        <div className="card w-100 pb-0">    
          <div className="card-body pb-0">
            <form ref={formRef} onSubmit={handleSubmit}>
              <div className="d-flex">
                <input
                  type="file"
                  className="form-control w-50 me-2"
                  id="binFile"
                  accept=".bin"
                  onChange={handleFileChange}
                />
                <button type="submit" className="btn btn-primary me-2" disabled={!file || uploadStatus === "uploading"}>
                  {uploadStatus === "uploading" ? "Uploading…" : "Upload"}
                </button>
                <button type="button" className="btn btn-secondary" disabled={uploadStatus !== "success"} onClick={handleCancel}>
                  Cancel
                </button>
              </div>
            </form>
            <p className="text-secondary mt-2 fst-italic">.bin file can be generated <a className="link-dark" href="https://openprinttag.org/generator/" target="_blank">here</a>. 
              The file can be uploaded here and then written to a spool.</p>
            <div className="text-end">
              <small className="text-muted">
                {file && `Selected File: ${file.name} (${(file.size / 1024).toFixed(1)} KB)`}
                {uploadStatus === "error" && "Upload failed. Please try again."}
                {uploadStatus === "success" && "Upload successful!"}
              </small>
            </div> 
          </div>
          </div>
        </div>
        <div className="col">
          {tagData && <TagCard tag={tagData} />}
        </div>
      </div>
    </div>
  );
}