/**
 * Represents a file selected by the user to provide context in the chat
 */
export type SelectedFile = {
  /** Full path to the file */
  path: string;
  /** Name of the file without path */
  fileName: string;
  /** Starting line number for partial file selection */
  startLine: number;
  /** Ending line number for partial file selection */
  endLine: number;
  /** Content of the file, null if not yet loaded */
  content: string | null;
};

/**
 * Represents a message from the human user
 */
export type HumanMessage = {
  /** The text content of the message */
  messageText: string;
  /** Array of files provided as context for this message */
  contextFiles: SelectedFile[];
};

/**
 * Represents a message from the AI assistant
 */
export type AiMessage = {
  /** The text content of the message */
  messageText: string;
  /** Array of code snippets included in the response */
  codeTexts: string[];
};

/**
 * Represents a chat session between the user and AI
 */
export type Chat = {
  /** Unique identifier for the chat */
  chatId: string;
  /** Array of messages in the chat, alternating between human and AI */
  messages: (HumanMessage | AiMessage)[];
  /** The current message being composed by the human user */
  currentHumanMessage: HumanMessage | null;
};

/**
 * Represents the global state for chat functionality
 */
export type ChatState = {
  /** ID of the currently active chat */
  currentChatId: string;
  /** Array of all chat sessions */
  chats: Chat[];
  /** Whether a chat operation is in progress */
  loading: boolean;
  /** Error message if something went wrong, null otherwise */
  error: string | null;
  /** Map of chat IDs to chat objects for quick lookup */
  chatMap: Record<string, Chat>;
};
