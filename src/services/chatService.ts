// frontend/src/services/chatService.ts
// ============================================================================
// SATQUERY AI - CONVERSATIONAL AGENT SERVICE
// ============================================================================
// FUTURE: Replace mock response with backend API call.
// When backend endpoints are deployed, connect to streaming WebSocket or
// POST /api/v1/chat/stream for token-by-token vision-language answers.
// ============================================================================

import { ChatMessage } from '../types/app';
import { EngineResult } from '../types/engine';

export function createWelcomeMessage(): ChatMessage {
  return {
    id: 'msg-welcome',
    sender: 'agent',
    content:
      'SATQUERY AI ONLINE.\nUpload satellite imagery and submit a natural language query to begin analysis.',
    timestamp: new Date().toISOString(),
  };
}

export function createUserMessage(query: string): ChatMessage {
  return {
    id: `msg-${Date.now()}-user`,
    sender: 'user',
    content: query,
    timestamp: new Date().toISOString(),
  };
}

export function createAgentResultMessage(result: EngineResult): ChatMessage {
  return {
    id: `msg-${Date.now()}-agent`,
    sender: 'agent',
    content: result.answer || 'Analysis complete. Structured evidence generated in viewport.',
    timestamp: new Date().toISOString(),
    result,
  };
}
