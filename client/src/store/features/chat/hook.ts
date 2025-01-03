import { useCallback } from "react";
import { useAppSelector, useAppDispatch } from "../../root/hooks.ts";
import {
  createNewChat as createNewChatAction,
  setCurrentChatId as setCurrentChatIdAction,
  setCurrentHumanMessage as setCurrentHumanMessageAction,
  updateContextFile as updateContextFileAction,
} from "./slice.ts";
import type { SelectedFile, HumanMessage } from "./type";
import { sendMessageThunk } from "./thunk";
import { getFileName } from "../../../utils/file.ts";

export const FULL_FILE_START_LINE = -1;
export const FULL_FILE_END_LINE = -1;

/**
 * Interface defining the chat hook functionality
 */
type ChatHook = {
  /** ID of the currently active chat */
  currentChatId: string;
  /** The current message being composed by the human user */
  currentHumanMessage: HumanMessage | null;
  /** Creates a new chat session */
  newChat: () => void;
  /** Updates the text content of the current human message */
  setHumanMsgText: (text: string) => void;
  /** Adds a file to provide context for the current human message */
  addFileToHumanMsg: (file: SelectedFile) => void;
  /** Removes a file from the current human message context */
  removeFileFromHumanMsg: (file: SelectedFile) => void;
  /** Sets the currently active chat ID */
  setCurrentChatId: (chatId: string) => void;
  /** Sends the current human message to the AI assistant */
  sendMessage: () => Promise<void>;
  /** Adds a full context file to the current human message */
  addFullContextFile: (filePath: string) => void;
};

/**
 * Custom hook providing chat functionality
 * @returns ChatHook object containing chat state and actions
 */
const useChat = (): ChatHook => {
  const dispatch = useAppDispatch();
  const currentChatId = useAppSelector((state) => state.chat.currentChatId);
  const currentHumanMessage = useAppSelector(
    (state) => state.chat.chatMap[currentChatId].currentHumanMessage
  );

  // Helper function to update the current human message
  const updateHumanMessage = useCallback(
    (updates: Partial<HumanMessage>) => {
      const updatedMessage = {
        messageText: currentHumanMessage?.messageText ?? "",
        contextFiles: currentHumanMessage?.contextFiles ?? [],
        ...updates,
      };
      dispatch(setCurrentHumanMessageAction(updatedMessage));
    },
    [dispatch, currentHumanMessage]
  );

  const setHumanMsgText = useCallback(
    (text: string) => updateHumanMessage({ messageText: text }),
    [updateHumanMessage]
  );

  const addFileToHumanMsg = useCallback(
    (newFile: SelectedFile) => {
      dispatch(
        updateContextFileAction({
          operation: "add",
          contextFile: newFile,
        })
      );
    },
    [dispatch]
  );

  const removeFileFromHumanMsg = useCallback(
    (fileToRemove: SelectedFile) => {
      dispatch(
        updateContextFileAction({
          operation: "remove",
          contextFile: fileToRemove,
        })
      );
    },
    [dispatch]
  );

  const addFullContextFile = useCallback(
    (filePath: string) => {
      const file = {
        path: filePath,
        fileName: getFileName(filePath),
        startLine: FULL_FILE_START_LINE,
        endLine: FULL_FILE_END_LINE,
        content: null,
      };
      dispatch(
        updateContextFileAction({ operation: "add", contextFile: file })
      );
    },
    [dispatch]
  );

  const setCurrentChatId = useCallback(
    (chatId: string) => dispatch(setCurrentChatIdAction(chatId)),
    [dispatch]
  );

  const newChat = useCallback(
    () => dispatch(createNewChatAction()),
    [dispatch]
  );

  const sendMessage = useCallback(async () => {
    if (!currentHumanMessage) return;
    await dispatch(sendMessageThunk(currentHumanMessage));
  }, [dispatch, currentHumanMessage]);

  return {
    currentChatId,
    currentHumanMessage,
    newChat,
    setHumanMsgText,
    addFileToHumanMsg,
    removeFileFromHumanMsg,
    setCurrentChatId,
    sendMessage,
    addFullContextFile,
  };
};

export default useChat;
