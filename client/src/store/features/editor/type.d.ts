/**
 * Represents a file in the editor
 */
export type EditorFile = {
  /** Unique identifier for the file */
  id: string;
  /** Full file path */
  path: string;
  /** File name */
  name: string;
  /** File contents as string */
  content: string;
  /** Programming language of the file */
  language: string;
  /** Current cursor position in the file */
  cursorPosition?: number;
  /** Current scroll position in the file */
  scrollPosition?: number;
  /** Whether the file has unsaved changes */
  isModified: boolean;
};
