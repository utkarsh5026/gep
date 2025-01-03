import { createSlice, type PayloadAction } from "@reduxjs/toolkit";
import { v4 as uuidv4 } from "uuid";
import type {
  Chat,
  HumanMessage,
  ChatState,
  SelectedFile,
  UpdateContextFilesPayload,
} from "./type";
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

function fileExists(f: SelectedFile, files: SelectedFile[]): [boolean, number] {
  const idx = files.findIndex(
    (file) =>
      file.path === f.path &&
      file.startLine === f.startLine &&
      file.endLine === f.endLine
  );
  return [idx !== -1, idx];
}

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
      const chat = state.chatMap[state.currentChatId];
      state.chatMap[state.currentChatId] = {
        ...chat,
        currentHumanMessage: action.payload,
      };
    },

    createNewChat: (state) => {
      const newChat = createChat();
      state.chats = [...state.chats, newChat];
      state.currentChatId = newChat.chatId;
      state.chatMap[newChat.chatId] = newChat;
    },

    updateContextFile: (
      state,
      action: PayloadAction<UpdateContextFilesPayload>
    ) => {
      const chat = state.chatMap[state.currentChatId];
      const currMessage = chat.currentHumanMessage;
      if (!currMessage) {
        return;
      }

      const { operation, contextFile } = action.payload;
      if (operation !== "add" && operation !== "remove") {
        return;
      }

      const currFiles = [...currMessage.contextFiles];
      const [exists, idx] = fileExists(contextFile, currFiles);
      if (operation === "add") {
        if (exists) {
          return;
        }
        currFiles.push(contextFile);
      } else if (operation === "remove") {
        if (!exists) {
          return;
        }
        currFiles.splice(idx, 1);
      }

      state.chatMap[state.currentChatId] = {
        ...chat,
        currentHumanMessage: {
          ...currMessage,
          contextFiles: currFiles,
        },
      };
    },
  },
  extraReducers: (builder) => {
    builder.addCase(sendMessageThunk.pending, (state) => {
      state.loading = true;
    });
  },
});

export const {
  setCurrentChatId,
  setCurrentHumanMessage,
  createNewChat,
  updateContextFile,
} = chatSlice.actions;

export default chatSlice.reducer;
