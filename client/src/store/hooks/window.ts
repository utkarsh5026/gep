import { useCallback } from "react";
import { useAppDispatch, useAppSelector } from "../root/hooks";
import {
  setEditorWidth as setEditorWidthAction,
  setDirWidth as setDirWidthAction,
  setChatWidth as setChatWidthAction,
  toggleChat as toggleChatAction,
  toggleDir as toggleDirAction,
} from "../slices/window";

interface PanelWidths {
  editorWidth: number;
  dirWidth: number;
  chatWidth: number;
  setEditorWidth: (width: number) => void;
  setDirWidth: (width: number) => void;
  setChatWidth: (width: number) => void;
  toggleChat: () => void;
  toggleDir: () => void;
}

/**
 * Custom hook to manage panel widths in the application layout
 *
 * @returns {PanelWidths} Object containing:
 *   - editorWidth: Current width of the editor panel
 *   - dirWidth: Current width of the directory panel
 *   - chatWidth: Current width of the chat panel
 *   - setEditorWidth: Function to update editor panel width
 *   - setDirWidth: Function to update directory panel width
 *   - setChatWidth: Function to update chat panel width
 *   - toggleChat: Function to toggle chat panel visibility
 *   - toggleDir: Function to toggle directory panel visibility
 */
const usePanelWidths = (): PanelWidths => {
  const dispatch = useAppDispatch();
  const { editorWidth, dirWidth, chatWidth } = useAppSelector(({ window }) => {
    return {
      editorWidth: window.editorWidth,
      dirWidth: window.dirWidth,
      chatWidth: window.chatWidth,
    };
  });

  const setEditorWidth = useCallback(
    (width: number) => dispatch(setEditorWidthAction(width)),
    [dispatch]
  );

  const setDirWidth = useCallback(
    (width: number) => dispatch(setDirWidthAction(width)),
    [dispatch]
  );

  const setChatWidth = useCallback(
    (width: number) => dispatch(setChatWidthAction(width)),
    [dispatch]
  );

  const toggleChat = useCallback(
    () => dispatch(toggleChatAction()),
    [dispatch]
  );

  const toggleDir = useCallback(() => dispatch(toggleDirAction()), [dispatch]);

  return {
    editorWidth,
    dirWidth,
    chatWidth,
    setEditorWidth,
    setDirWidth,
    setChatWidth,
    toggleChat,
    toggleDir,
  };
};

export default usePanelWidths;
