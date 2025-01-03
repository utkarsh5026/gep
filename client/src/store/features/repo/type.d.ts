/**
 * Represents a node in a file tree structure
 */
export type FileNode = {
  /** The name of the file or directory */
  name: string;
  /** The type of node - either a file or directory */
  type: "file" | "directory";
  /** Optional array of child nodes, only present for directories */
  children?: FileNode[];
};
