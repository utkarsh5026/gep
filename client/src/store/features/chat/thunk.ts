import { createAsyncThunk } from "@reduxjs/toolkit";
import type { HumanMessage } from "./type";
import type { RootState } from "../../root/store";
import api from "../../../client/axios";

/**
 * Send a message to the AI assistant
 * @param message - The message to send to the AI assistant
 * @returns The response from the AI assistant
 */
export const sendMessageThunk = createAsyncThunk(
  "chat/sendMessage",
  async (msg: HumanMessage, { rejectWithValue, getState }) => {
    try {
      const { chat, repo } = getState() as RootState;
      const { messageText, contextFiles } = msg;
      const payload = {
        chatId: chat.currentChatId,
        message: messageText,
        contextFiles,
        githubRepo: repo.repoLink ?? "",
      };

      const response = await api.post("/llm/chat", payload);
      return response.data;
    } catch (error) {
      return rejectWithValue(error);
    }
  }
);
