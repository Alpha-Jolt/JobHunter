"use client";

import { useState, useRef } from "react";
import { Upload, File, CheckCircle2, Eye } from "lucide-react";
import { resumeApi } from "@/shared/api/gateway";
import { useAuthStore } from "@/shared/state/authStore";
import { useUserProfileStore } from "@/shared/state/userProfileStore";
import { useUiStore } from "@/shared/state/uiStore";
import { Button } from "@/shared/components/Button";
import { ApiError } from "@/shared/api/errors";

// Allowed MIME types and their magic byte signatures
const ALLOWED_TYPES = ["application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"];
const ALLOWED_EXTENSIONS = [".pdf", ".docx"];
const MAX_SIZE_BYTES = 10 * 1024 * 1024; // 10 MB

// PDF magic: %PDF (25 50 44 46)
// DOCX magic: PK (50 4B 03 04) — ZIP-based
const MAGIC_BYTES: Record<string, number[]> = {
  ".pdf": [0x25, 0x50, 0x44, 0x46],
  ".docx": [0x50, 0x4b, 0x03, 0x04],
};

async function validateFileSecurity(file: File): Promise<string | null> {
  const ext = file.name.slice(file.name.lastIndexOf(".")).toLowerCase();

  if (!ALLOWED_EXTENSIONS.includes(ext)) return "Only PDF and DOCX files are allowed.";
  if (!ALLOWED_TYPES.includes(file.type)) return "Invalid file type.";
  if (file.size > MAX_SIZE_BYTES) return "File size must be under 10 MB.";

  // Verify magic bytes (prevents MIME-type spoofing)
  const header = await file.slice(0, 8).arrayBuffer();
  const bytes = new Uint8Array(header);
  const expected = MAGIC_BYTES[ext];
  if (!expected) return "Unsupported file format.";

  for (let i = 0; i < expected.length; i++) {
    if (bytes[i] !== expected[i]) return "File content does not match its extension.";
  }

  // Scan for known malicious patterns in PDF (embedded JS, /OpenAction, /Launch)
  if (ext === ".pdf") {
    const textChunk = await file.slice(0, 8192).text().catch(() => "");
    const maliciousPatterns = ["/JavaScript", "/JS ", "/OpenAction", "/Launch", "/EmbeddedFile"];
    for (const pattern of maliciousPatterns) {
      if (textChunk.includes(pattern)) {
        return "File contains potentially unsafe content and cannot be uploaded.";
      }
    }
  }

  // Sanitize filename: reject path traversal or null bytes
  if (/[/\\<>:"|?*\x00]/.test(file.name)) return "File name contains invalid characters.";

  return null; // valid
}

export function ResumeUpload() {
  const { user } = useAuthStore();
  const { resumeKey, resumeFileName, setResume } = useUserProfileStore();
  const { addToast } = useUiStore();
  const [isLoading, setIsLoading] = useState(false);
  const [dragOver, setDragOver] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const [isPreviewLoading, setIsPreviewLoading] = useState(false);

  const handleFile = async (file: File) => {
    const error = await validateFileSecurity(file);
    if (error) {
      addToast("error", error);
      return;
    }
    if (!user) return;
    setIsLoading(true);
    try {
      const data = await resumeApi.upload(file, user.user_id);
      setResume(data.s3_key, data.file_name);
      addToast("success", "Resume uploaded successfully.");
    } catch (err) {
      const msg = err instanceof ApiError ? err.message : "Upload failed. Please try again.";
      addToast("error", msg);
    } finally {
      setIsLoading(false);
    }
  };

  const handlePreview = async () => {
    setIsPreviewLoading(true);
    try {
      const data = await resumeApi.preview();
      window.open(data.url, "_blank");
    } catch (err) {
      addToast("error", "Failed to load preview.");
    } finally {
      setIsPreviewLoading(false);
    }
  };

  const onDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    const file = e.dataTransfer.files[0];
    if (file) handleFile(file);
  };

  if (resumeKey) {
    return (
      <div className="flex items-center gap-3 p-4 rounded-lg border border-green-200 bg-green-50 dark:bg-green-900/10 dark:border-green-800">
        <CheckCircle2 className="h-5 w-5 text-green-600 shrink-0" />
        <div className="flex-1 min-w-0">
          <p className="text-sm font-medium text-foreground truncate">{resumeFileName}</p>
          <p className="text-xs text-muted-foreground">Resume uploaded</p>
        </div>
        <Button variant="outline" size="sm" onClick={handlePreview} isLoading={isPreviewLoading}>
          <Eye className="h-3.5 w-3.5 mr-1" />
          Preview
        </Button>
        <Button variant="outline" size="sm" onClick={() => inputRef.current?.click()}>
          Replace
        </Button>
        <input
          ref={inputRef}
          type="file"
          accept=".pdf,.docx"
          className="hidden"
          onChange={(e) => e.target.files?.[0] && handleFile(e.target.files[0])}
        />
      </div>
    );
  }

  return (
    <div
      onDrop={onDrop}
      onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
      onDragLeave={() => setDragOver(false)}
      onClick={() => inputRef.current?.click()}
      className={`flex flex-col items-center gap-3 p-8 rounded-lg border-2 border-dashed cursor-pointer transition-colors ${
        dragOver ? "border-primary bg-accent" : "border-border hover:border-primary hover:bg-accent/50"
      }`}
    >
      <Upload className="h-8 w-8 text-muted-foreground" />
      <div className="text-center">
        <p className="text-sm font-medium text-foreground">Drop your resume here or click to browse</p>
        <p className="text-xs text-muted-foreground mt-1">PDF or DOCX · Max 10 MB</p>
      </div>
      {isLoading && <p className="text-xs text-primary animate-pulse">Uploading…</p>}
      <input
        ref={inputRef}
        type="file"
        accept=".pdf,.docx"
        className="hidden"
        onChange={(e) => e.target.files?.[0] && handleFile(e.target.files[0])}
      />
    </div>
  );
}
