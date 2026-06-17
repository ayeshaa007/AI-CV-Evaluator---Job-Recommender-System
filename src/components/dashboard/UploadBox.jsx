import { useRef, useState } from "react";
import { UploadCloud, FileText, CheckCircle2, X } from "lucide-react";
import "./UploadBox.css";

export default function UploadBox({ file, onChange }) {
  const [dragging, setDragging] = useState(false);
  const inputRef = useRef();

  const accept = (f) => {
    if (f?.type === "application/pdf") onChange(f);
  };

  return (
    <div
      className={`upload-box${dragging ? " upload-box--drag" : ""}${file ? " upload-box--filled" : ""}`}
      onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
      onDragLeave={() => setDragging(false)}
      onDrop={(e) => { e.preventDefault(); setDragging(false); accept(e.dataTransfer.files[0]); }}
      onClick={() => !file && inputRef.current.click()}
    >
      <input
        ref={inputRef}
        type="file"
        accept=".pdf"
        style={{ display: "none" }}
        onChange={(e) => accept(e.target.files[0])}
      />

      {file ? (
        /* File ready state */
        <div className="upload-ready">
          <div className="upload-ready-icon">
            <FileText size={22} />
          </div>
          <div className="upload-ready-info">
            <span className="upload-ready-name">{file.name}</span>
            <span className="upload-ready-size">{(file.size / 1024).toFixed(1)} KB · PDF</span>
          </div>
          <button
            className="upload-ready-remove"
            onClick={(e) => { e.stopPropagation(); onChange(null); }}
            title="Remove file"
          >
            <X size={14} />
          </button>
        </div>
      ) : (
        /* Empty state */
        <div className="upload-empty">
          <div className={`upload-icon-ring${dragging ? " upload-icon-ring--drag" : ""}`}>
            <UploadCloud size={26} />
          </div>
          <p className="upload-empty-title">
            {dragging ? "Drop to upload" : "Drag & drop your CV"}
          </p>
          <p className="upload-empty-sub">or</p>
          <button
            className="btn btn-secondary btn-sm"
            onClick={(e) => { e.stopPropagation(); inputRef.current.click(); }}
          >
            Browse files
          </button>
          <p className="upload-empty-note">PDF only · Max 5 MB</p>
        </div>
      )}
    </div>
  );
}
