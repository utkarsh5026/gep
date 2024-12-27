import { createSlice, createAsyncThunk } from "@reduxjs/toolkit";
import api from "../../client/axios";
import axios from "axios";

export const fetchRepoStructure = createAsyncThunk(
  "repo/fetchRepoStructure",
  async (url: string, { rejectWithValue }) => {
    try {
      const response = await api.get(`/github/load-repo?url=${url}`);
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        return rejectWithValue(error.response?.data || error.message);
      }
      return rejectWithValue("An unexpected error occurred");
    }
  }
);

export type FileNode = {
  name: string;
  type: "file" | "directory";
  children?: FileNode[];
};

interface RepoState {
  root: FileNode | null;
  loading: boolean;
  error: string | null;
}

const initialState: RepoState = {
  root: null,
  loading: false,
  error: null,
};

const repoSlice = createSlice({
  name: "repo",
  initialState: initialState,
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(fetchRepoStructure.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchRepoStructure.fulfilled, (state, action) => {
        state.loading = false;
        state.root = action.payload.files;
      })
      .addCase(fetchRepoStructure.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      });
  },
});

export default repoSlice.reducer;