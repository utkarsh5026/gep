import { createSlice, PayloadAction } from "@reduxjs/toolkit";

const DEFAULT_CHAT_WIDTH = 25;
const DEFAULT_DIR_WIDTH = 25;
const DEFAULT_EDITOR_WIDTH = 50;

type PanelWidths = {
  editorWidth: number;
  dirWidth: number;
  chatWidth: number;
};

const initialState: PanelWidths = {
  editorWidth: DEFAULT_EDITOR_WIDTH,
  dirWidth: DEFAULT_DIR_WIDTH,
  chatWidth: DEFAULT_CHAT_WIDTH,
};

const panelSlice = createSlice({
  name: "window",
  initialState,
  reducers: {
    setEditorWidth: (state, action: PayloadAction<number>) => {
      state.editorWidth = action.payload;
    },
    setDirWidth: (state, action: PayloadAction<number>) => {
      state.dirWidth = action.payload;
    },
    setChatWidth: (state, action: PayloadAction<number>) => {
      state.chatWidth = action.payload;
    },
    toggleChat: (state) => {
      state.editorWidth =
        state.editorWidth + state.chatWidth === DEFAULT_EDITOR_WIDTH
          ? DEFAULT_EDITOR_WIDTH - state.chatWidth
          : DEFAULT_EDITOR_WIDTH;
      state.chatWidth = state.chatWidth === 0 ? DEFAULT_CHAT_WIDTH : 0;
    },
    toggleDir: (state) => {
      state.editorWidth =
        state.editorWidth + state.dirWidth === DEFAULT_EDITOR_WIDTH
          ? DEFAULT_EDITOR_WIDTH - state.dirWidth
          : DEFAULT_EDITOR_WIDTH;
      state.dirWidth = state.dirWidth === 0 ? DEFAULT_DIR_WIDTH : 0;
    },
  },
});

export const {
  setEditorWidth,
  setDirWidth,
  setChatWidth,
  toggleChat,
  toggleDir,
} = panelSlice.actions;
export default panelSlice.reducer;
