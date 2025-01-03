import {
  createSlice,
  type PayloadAction,
  createAsyncThunk,
} from "@reduxjs/toolkit";
import api from "../../../client/axios.ts";
import { getLanguageByExtension } from "../../../code/language.ts";
import type { EditorFile } from "./type";

interface EditorState {
  openFiles: EditorFile[];
  activeFileId: string | null;
  editorConfig: {
    theme: string;
    fontSize: number;
    tabSize: number;
  };
  loading: boolean;
  error: string | null;
}

const initialState: EditorState = {
  openFiles: [],
  activeFileId: null,
  editorConfig: {
    theme: "vs-dark",
    fontSize: 14,
    tabSize: 4,
  },
  loading: false,
  error: null,
};

export const getFileContent = createAsyncThunk(
  "editor/getFileContent",
  async (params: { filePath: string; repoLink: string }) => {
    const actualFilePath = params.filePath.split("/").slice(1).join("/");
    const response = await api.get(`/github/file-content`, {
      params: {
        repo_link: params.repoLink,
        file_path: actualFilePath,
      },
    });
    return {
      data: response.data as string,
      path: params.filePath,
    };
  }
);

const parseFilePath = (filePath: string) => {
  const parts = filePath.split("/");

  return {
    name: parts[parts.length - 1],
    extension: parts[parts.length - 1].split(".")[1],
  };
};

const editorSlice = createSlice({
  name: "editor",
  initialState,
  reducers: {
    openFile: (state, action: PayloadAction<EditorFile>) => {
      const existingFile = state.openFiles.find(
        (f) => f.path === action.payload.path
      );
      if (!existingFile) {
        state.openFiles.push(action.payload);
      }
      state.activeFileId = action.payload.id;
    },

    updateFileContent: (
      state,
      action: PayloadAction<{
        fileId: string;
        content: string;
      }>
    ) => {
      const file = state.openFiles.find((f) => f.id === action.payload.fileId);
      if (file) {
        file.content = action.payload.content;
        file.isModified = true;
      }
    },

    closeFile: (state, action: PayloadAction<string>) => {
      state.openFiles = state.openFiles.filter((f) => f.id !== action.payload);
      if (state.activeFileId === action.payload) {
        state.activeFileId = state.openFiles[0]?.id || null;
      }
    },

    updateEditorViewState: (
      state,
      action: PayloadAction<{
        fileId: string;
        cursorPosition: number;
        scrollPosition: number;
      }>
    ) => {
      const file = state.openFiles.find((f) => f.id === action.payload.fileId);
      if (file) {
        file.cursorPosition = action.payload.cursorPosition;
        file.scrollPosition = action.payload.scrollPosition;
      }
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(getFileContent.fulfilled, (state, action) => {
        const file = state.openFiles.find((f) => f.id === action.payload.path);
        if (file) {
          file.content = action.payload.data;
        } else {
          const { name, extension } = parseFilePath(action.payload.path);
          state.openFiles.push({
            id: action.payload.path,
            path: action.payload.path,
            name: name,
            content: action.payload.data,
            language: getLanguageByExtension(extension),
            isModified: false,
          });
        }

        state.activeFileId = action.payload.path;
        state.loading = false;
        state.error = null;
      })
      .addCase(getFileContent.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message ?? "Failed to fetch file content";
      })
      .addCase(getFileContent.pending, (state) => {
        state.loading = true;
        state.error = null;
      });
  },
});

export const { openFile, updateFileContent, closeFile, updateEditorViewState } =
  editorSlice.actions;
export default editorSlice.reducer;
