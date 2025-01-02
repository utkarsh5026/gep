import { createSlice, type PayloadAction } from "@reduxjs/toolkit";
import { v4 as uuidv4 } from "uuid";

export type SelectedFile = {
  path: string;
  fileName: string;
  startLine: number;
  endLine: number;
};

export type HumanMessage = {
  messageText: string;
  contextFiles: SelectedFile[];
};

export type AiMessage = {
  messageText: string;
  codeTexts: string[];
};

export type Chat = {
  chatId: string;
  messages: (HumanMessage | AiMessage)[];
  currentHumanMessage: HumanMessage | null;
};

interface ChatState {
  currentChatId: string;
  chats: Chat[];
  loading: boolean;
  error: string | null;
  chatMap: Record<string, Chat>;
}

/**
 * Create a new chat with a unique ID
 * @returns Chat
 */
const createChat = (): Chat => {
  return {
    chatId: uuidv4(),
    messages: [],
    currentHumanMessage: {
      messageText: "",
      contextFiles: [],
    },
  };
};

/**
 * Initialize the chat state with a new chat
 * @returns ChatState
 */
const initState = (): ChatState => {
  const chat = createChat();
  return {
    currentChatId: chat.chatId,
    chats: [chat],
    loading: false,
    error: null,
    chatMap: { [chat.chatId]: chat },
  };
};

const chatSlice = createSlice({
  name: "chat",
  initialState: initState(),
  reducers: {
    setCurrentChatId: (state, action: PayloadAction<string>) => {
      state.currentChatId = action.payload;
    },
    setCurrentHumanMessage: (state, action: PayloadAction<HumanMessage>) => {
      state.chatMap[state.currentChatId].currentHumanMessage = action.payload;
    },

    createNewChat: (state) => {
      const newChat = createChat();
      state.chats = [...state.chats, newChat];
      state.currentChatId = newChat.chatId;
      state.chatMap[newChat.chatId] = newChat;
    },
  },
});

export const { setCurrentChatId, setCurrentHumanMessage, createNewChat } =
  chatSlice.actions;

export default chatSlice.reducer;
