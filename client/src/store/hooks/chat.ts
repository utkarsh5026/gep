import { useCallback } from "react";
import { useAppSelector, useAppDispatch } from "../root/hooks";
import {
  type SelectedFile,
  createNewChat as createNewChatAction,
  setCurrentChatId as setCurrentChatIdAction,
  setCurrentHumanMessage as setCurrentHumanMessageAction,
} from "../slices/chat";

const useChat = () => {
  const dispatch = useAppDispatch();
  const currentChatId = useAppSelector((state) => state.chat.currentChatId);
  const currentHumanMessage = useAppSelector(
    (state) => state.chat.chatMap[currentChatId].currentHumanMessage
  );

  const newChat = useCallback(
    () => dispatch(createNewChatAction()),
    [dispatch]
  );

  const setHumanMsgText = useCallback(
    (text: string) =>
      dispatch(
        setCurrentHumanMessageAction({
          messageText: text,
          contextFiles: currentHumanMessage?.contextFiles ?? [],
          selectionTexts: currentHumanMessage?.selectionTexts ?? [],
        })
      ),
    [dispatch, currentHumanMessage]
  );

  const addFileToHumanMsg = useCallback(
    (file: SelectedFile) =>
      dispatch(
        setCurrentHumanMessageAction({
          messageText: currentHumanMessage?.messageText ?? "",
          contextFiles: [...(currentHumanMessage?.contextFiles ?? []), file],
          selectionTexts: currentHumanMessage?.selectionTexts ?? [],
        })
      ),
    [dispatch, currentHumanMessage]
  );

  const removeFileFromHumanMsg = useCallback(
    (file: SelectedFile) =>
      dispatch(
        setCurrentHumanMessageAction({
          messageText: currentHumanMessage?.messageText ?? "",
          contextFiles:
            currentHumanMessage?.contextFiles.filter(
              (f) => f.path !== file.path
            ) ?? [],
          selectionTexts: currentHumanMessage?.selectionTexts ?? [],
        })
      ),
    [dispatch, currentHumanMessage]
  );

  const setCurrentChatId = useCallback(
    (chatId: string) => dispatch(setCurrentChatIdAction(chatId)),
    [dispatch]
  );

  return {
    currentChatId,
    currentHumanMessage,
    newChat,
    setHumanMsgText,
    addFileToHumanMsg,
    removeFileFromHumanMsg,
    setCurrentChatId,
  };
};

export default useChat;
