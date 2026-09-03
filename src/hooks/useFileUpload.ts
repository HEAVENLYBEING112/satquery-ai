// frontend/src/hooks/useFileUpload.ts
import { useState, useCallback } from 'react';
import { useAppStore } from '../store/useAppStore';

const MAX_FILE_SIZE = 52428800; // 50MB (Backend limit)
const WARN_FILE_SIZE = 41943040; // 40MB (SRS warning threshold)
const ALLOWED_EXTENSIONS = ['.tif', '.tiff', '.png', '.jpg', '.jpeg'];

export function useFileUpload() {
  const [isDragging, setIsDragging] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [warningMessage, setWarningMessage] = useState<string | null>(null);
  const { files, addFiles } = useAppStore();

  const validateAndAddFiles = useCallback(
    (droppedFiles: FileList | File[]) => {
      setErrorMessage(null);
      setWarningMessage(null);

      const fileArray = Array.from(droppedFiles);

      if (fileArray.length === 0) return;

      if (files.length + fileArray.length > 2) {
        setErrorMessage('Maximum 2 satellite images allowed per analysis session.');
        return;
      }

      const validFiles: File[] = [];

      for (const file of fileArray) {
        const lowerName = file.name.toLowerCase();
        const isValidExt = ALLOWED_EXTENSIONS.some((ext) => lowerName.endsWith(ext));

        if (!isValidExt) {
          setErrorMessage(`Invalid format: ${file.name}. Only GeoTIFF (.tif, .tiff) and image benchmarks (.png, .jpg) are supported.`);
          return;
        }

        if (file.size > MAX_FILE_SIZE) {
          setErrorMessage(`File ${file.name} exceeds maximum allowed size of 50MB.`);
          return;
        }

        if (file.size > WARN_FILE_SIZE) {
          setWarningMessage(`Large file (${(file.size / 1024 / 1024).toFixed(1)}MB) — upload and rendering may take a moment.`);
        }

        validFiles.push(file);
      }

      if (validFiles.length > 0) {
        addFiles(validFiles);
      }
    },
    [files, addFiles]
  );

  const onDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  }, []);

  const onDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  }, []);

  const onDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      e.stopPropagation();
      setIsDragging(false);
      if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
        validateAndAddFiles(e.dataTransfer.files);
      }
    },
    [validateAndAddFiles]
  );

  return {
    isDragging,
    errorMessage,
    warningMessage,
    onDragOver,
    onDragLeave,
    onDrop,
    validateAndAddFiles,
    clearErrors: () => {
      setErrorMessage(null);
      setWarningMessage(null);
    },
  };
}
