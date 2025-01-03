import { createSlice, type PayloadAction } from "@reduxjs/toolkit";
import { v4 as uuidv4 } from "uuid";
import type { Chat, HumanMessage, ChatState } from "./type";
import { sendMessageThunk } from "./thunk";

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
  extraReducers: (builder) => {
    builder.addCase(sendMessageThunk.pending, (state) => {
      state.loading = true;
    });
  },
});

export const { setCurrentChatId, setCurrentHumanMessage, createNewChat } =
  chatSlice.actions;

export default chatSlice.reducer;
