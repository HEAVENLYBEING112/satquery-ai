// frontend/src/hooks/useJobPoller.ts
import { useEffect, useRef, useState } from 'react';
import { JobResponse } from '../types/engine';
import { pollJob } from '../api/jobs';

const POLL_INTERVAL_MS = 2000;
const MAX_POLL_ATTEMPTS = 150; // 5 minutes maximum as per SRS Section 21.1

export function useJobPoller(jobId: string | null) {
  const [job, setJob] = useState<JobResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isTimedOut, setIsTimedOut] = useState(false);
  const attemptsRef = useRef(0);

  useEffect(() => {
    if (!jobId) {
      setJob(null);
      setError(null);
      setIsTimedOut(false);
      attemptsRef.current = 0;
      return;
    }

    let isMounted = true;
    attemptsRef.current = 0;

    const interval = setInterval(async () => {
      attemptsRef.current += 1;

      if (attemptsRef.current > MAX_POLL_ATTEMPTS) {
        clearInterval(interval);
        if (isMounted) {
          setIsTimedOut(true);
          setError('Analysis timed out after 5 minutes.');
        }
        return;
      }

      try {
        const res = await pollJob(jobId);
        if (!isMounted) return;

        setJob(res);

        if (res.status === 'completed' || res.status === 'failed') {
          clearInterval(interval);
        }
      } catch (err: any) {
        if (!isMounted) return;
        setError(err.message || 'Error polling job');
        clearInterval(interval);
      }
    }, POLL_INTERVAL_MS);

    return () => {
      isMounted = false;
      clearInterval(interval); // Cleanup on unmount or jobId change
    };
  }, [jobId]);

  return { job, error, isTimedOut };
}
