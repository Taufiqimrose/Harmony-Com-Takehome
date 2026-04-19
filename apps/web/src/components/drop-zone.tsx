import { UploadSimple } from "@phosphor-icons/react";
import { useId, useState } from "react";
import { cn } from "@/lib/utils";

export interface DropZoneFile {
  file: File;
  sizeLabel: string;
  pages?: number;
}

export function DropZone({
  disabled,
  file,
  onFile,
  onClear,
}: {
  disabled?: boolean;
  file: DropZoneFile | null;
  onFile: (f: File) => void;
  onClear: () => void;
}) {
  const id = useId();
  const [drag, setDrag] = useState(false);

  return (
    <div className="mx-auto mb-6 w-full max-w-4xl">
      <label
        htmlFor={id}
        onDragEnter={() => setDrag(true)}
        onDragLeave={() => setDrag(false)}
        onDrop={(e) => {
          e.preventDefault();
          setDrag(false);
          const f = e.dataTransfer.files?.[0];
          if (f) onFile(f);
        }}
        onDragOver={(e) => e.preventDefault()}
        className={cn(
          "flex cursor-pointer flex-col items-center justify-center rounded-[12px] border-2 border-dashed transition-all duration-300 ease-out",
          file ? "h-16 px-4" : "h-36 px-6",
          drag
            ? "border-[var(--color-primary-600)] bg-[var(--color-primary-50)]"
            : "border-[var(--color-border)] bg-[var(--color-surface)]",
          disabled && "pointer-events-none opacity-60",
        )}
      >
        <input
          id={id}
          type="file"
          accept="application/pdf"
          className="hidden"
          disabled={disabled}
          onChange={(e) => {
            const f = e.target.files?.[0];
            if (f) onFile(f);
          }}
        />

        {!file ? (
          <>
            <UploadSimple
              className={cn(
                "mb-2 h-8 w-8",
                drag ? "text-[var(--color-primary-600)]" : "text-[var(--color-muted)]",
              )}
            />
            <div className="text-[15px] font-medium">Drop your title here</div>
            <div className="mt-1 text-[13px] text-[var(--color-muted)]">or click to browse</div>
            <div className="mt-2 text-[11px] font-medium uppercase tracking-wide text-[var(--color-muted)]">
              PDF · up to 10MB
            </div>
          </>
        ) : (
          <div className="flex w-full items-center justify-between gap-3">
            <div className="truncate text-[14px]">
              <span className="mr-2">📄</span>
              <span className="font-medium">{file.file.name}</span>
              <span className="text-[var(--color-muted)]"> · {file.sizeLabel}</span>
              {file.pages != null ? (
                <span className="text-[var(--color-muted)]"> · {file.pages} page(s)</span>
              ) : null}
            </div>
            <button
              type="button"
              className="rounded-md px-2 py-1 text-sm text-[var(--color-muted)] hover:bg-black/5"
              onClick={(e) => {
                e.preventDefault();
                e.stopPropagation();
                onClear();
              }}
            >
              ✕
            </button>
          </div>
        )}
      </label>
    </div>
  );
}
