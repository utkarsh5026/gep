/**
 * Get the file name from a file path
 * @param filePath - The file path
 * @returns The file name
 */
export const getFileName = (filePath: string) => {
  return filePath.split("/").pop() ?? "";
};
