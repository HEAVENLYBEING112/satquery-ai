// frontend/src/utils/sanitize.ts
// Adheres to SRS Section 33: Security & XSS Mitigation

/**
 * Escapes HTML entities to prevent XSS injection from engine/user inputs.
 */
export function sanitizeText(str: string | null | undefined): string {
  if (str === null || str === undefined) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

/**
 * Validates whether an evidence visualization URL matches the safe prefix pattern
 */
export function isSafeEvidenceUrl(url: string): boolean {
  if (!url) return false;
  // Allow relative API routes, blob URLs, data URLs, and safe samples
  return (
    url.startsWith('/api/v1/jobs/') ||
    url.startsWith('blob:') ||
    url.startsWith('data:image/') ||
    url.startsWith('/samples/') ||
    url.startsWith('http://localhost:') ||
    url.startsWith('https://')
  );
}
