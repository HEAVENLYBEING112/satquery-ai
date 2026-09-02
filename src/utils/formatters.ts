// frontend/src/utils/formatters.ts

/**
 * Format confidence score strictly adhering to SRS Section 28:
 * If confidence is null/undefined -> "Confidence: N/A"
 * If float -> formatted to 1 decimal place (e.g., 92.4%)
 */
export function formatConfidence(confidence: number | null | undefined): {
  text: string;
  percentage: string;
  variant: 'neutral' | 'success' | 'warning' | 'error';
  isAvailable: boolean;
} {
  if (confidence === null || confidence === undefined || isNaN(confidence)) {
    return {
      text: 'Confidence: N/A (No probabilistic estimate)',
      percentage: 'N/A',
      variant: 'neutral',
      isAvailable: false,
    };
  }

  const clamped = Math.max(0, Math.min(1, confidence));
  const pct = (clamped * 100).toFixed(1);

  let variant: 'success' | 'warning' | 'error' = 'error';
  if (clamped >= 0.8) {
    variant = 'success';
  } else if (clamped >= 0.5) {
    variant = 'warning';
  }

  return {
    text: `Confidence: ${pct}%`,
    percentage: `${pct}%`,
    variant,
    isAvailable: true,
  };
}

/**
 * Format file size in bytes to human readable string
 */
export function formatBytes(bytes: number, decimals = 1): string {
  if (!bytes || bytes === 0) return '0 B';
  const k = 1024;
  const dm = decimals < 0 ? 0 : decimals;
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(dm))} ${sizes[i]}`;
}

/**
 * Format ISO date string into readable timestamp
 */
export function formatISODate(isoString: string): string {
  if (!isoString) return '—';
  try {
    const d = new Date(isoString);
    return d.toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    });
  } catch {
    return isoString;
  }
}

/**
 * Format milliseconds into readable duration
 */
export function formatDuration(ms: number): string {
  if (ms < 1000) return `${ms}ms`;
  return `${(ms / 1000).toFixed(2)}s`;
}
