import { configureStore } from "@reduxjs/toolkit";
import repoReducer from "../slices/repo";
import editorReducer from "../features/editor/slice";
import chatReducer from "../features/chat/slice";
import panelReducer from "../slices/window";

export const store = configureStore({
  reducer: {
    repo: repoReducer,
    editor: editorReducer,
    chat: chatReducer,
    window: panelReducer,
  },
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
