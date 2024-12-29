import { configureStore } from "@reduxjs/toolkit";
import repoReducer from "../slices/repo";
import editorReducer from "../slices/editor";

export const store = configureStore({
  reducer: {
    repo: repoReducer,
    editor: editorReducer,
  },
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
