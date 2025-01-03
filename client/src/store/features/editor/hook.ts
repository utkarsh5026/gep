import { useCallback, useEffect } from "react";
import { useAppDispatch, useAppSelector } from "../../root/hooks.ts";
import {
  openFile as openFileAction,
  updateFileContent as updateFileContentAction,
  closeFile as closeFileAction,
  updateEditorViewState as updateEditorViewStateAction,
  getFileContent,
} from "./slice";
import useRepo from "../../hooks/repo.ts";
import { shallowEqual } from "react-redux";
import type { EditorFile } from "./type";

type EditorHook = {
  openFileIds: string[];
  openFiles: EditorFile[];
  activeFileId: string | null;
  editorConfig: {
    theme: string;
    fontSize: number;
    tabSize: number;
  };
  openFile: (file: EditorFile) => void;
  updateFileContent: (fileId: string, content: string) => void;
  closeFile: (fileId: string) => void;
  updateEditorViewState: (
    fileId: string,
    cursorPosition: number,
    scrollPosition: number
  ) => void;
  setCurrentFile: (fileId: string) => void;
  fetchFileContent: (filePath: string) => void;
};

/**
 * A custom hook for managing the editor state and actions
 *
 * @returns {EditorHook} An object containing:
 *   - openFiles: Array of currently open files in the editor
 *   - activeFileId: ID of the currently active/focused file
 *   - editorConfig: Configuration object for editor settings
 *   - openFile: Function to open a new file in the editor
 *   - updateFileContent: Function to update a file's content
 *   - closeFile: Function to close a file
 *   - updateEditorViewState: Function to update cursor and scroll positions
 *   - setCurrentFile: Function to set the currently active file
 *   - fetchFileContent: Function to fetch a file's content
 */
const useEditor = (): EditorHook => {
  const dispatch = useAppDispatch();

  // Track file IDs separately for stable comparison
  const openFileIds = useAppSelector(
    (state) => state.editor.openFiles.map((f) => f.id),
    shallowEqual
  );

  // Get full file data
  const openFiles = useAppSelector((state) => state.editor.openFiles);

  // Debug hook to track reference changes
  useEffect(() => {
    console.log("openFileIds changed:", openFileIds);
  }, [openFileIds]);

  // Use separate selectors for each piece of state
  const activeFileId = useAppSelector((state) => state.editor.activeFileId);
  const editorConfig = useAppSelector(
    (state) => state.editor.editorConfig,
    shallowEqual
  );
  const repoLink = useRepo().repoLink;

  const openFile = useCallback(
    (file: EditorFile) => {
      dispatch(openFileAction(file));
    },
    [dispatch]
  );

  const updateFileContent = useCallback(
    (fileId: string, content: string) =>
      dispatch(updateFileContentAction({ fileId, content })),
    [dispatch]
  );

  const closeFile = useCallback(
    (fileId: string) => dispatch(closeFileAction(fileId)),
    [dispatch]
  );

  const updateEditorViewState = useCallback(
    (fileId: string, cursorPosition: number, scrollPosition: number) => {
      dispatch(
        updateEditorViewStateAction({ fileId, cursorPosition, scrollPosition })
      );
    },
    [dispatch]
  );

  const setCurrentFile = useCallback(
    (fileId: string) => {
      const file = openFileIds.find((f) => f === fileId);
      if (file) {
        dispatch(openFileAction(openFiles.find((f) => f.id === fileId)!));
      }
    },
    [dispatch, openFileIds, openFiles]
  );

  const fetchFileContent = useCallback(
    (filePath: string) => {
      dispatch(getFileContent({ filePath, repoLink: repoLink! }));
    },
    [dispatch, repoLink]
  );

  return {
    openFileIds,
    openFiles,
    activeFileId,
    editorConfig,
    openFile,
    updateFileContent,
    closeFile,
    updateEditorViewState,
    setCurrentFile,
    fetchFileContent,
  };
};

export default useEditor;
