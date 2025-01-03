import { createSlice, createAsyncThunk } from "@reduxjs/toolkit";
import api from "../../../client/axios.ts";
import axios from "axios";
import type { FileNode } from "./type";

/**
 * Fetch the repository structure from the server
 * @param url - The URL of the repository
 * @returns The repository structure
 */
export const fetchRepoStructure = createAsyncThunk(
  "repo/fetchRepoStructure",
  async (url: string, { rejectWithValue }) => {
    try {
      const response = await api.get(`/github/load-repo?url=${url}`);
      return {
        repo: response.data,
        repoLink: url,
      };
    } catch (error) {
      if (axios.isAxiosError(error)) {
        return rejectWithValue(error.response?.data || error.message);
      }
      return rejectWithValue("An unexpected error occurred");
    }
  }
);

/**
 * Build a file map from the repository structure
 * @param node - The root node of the repository structure
 * @param path - The path of the current node
 * @param fileMap - The file map to build
 */
const buildFileMap = (
  node: FileNode,
  path: string,
  fileMap: Record<string, FileNode>
) => {
  const fullPath = path ? `${path}/${node.name}` : node.name;
  fileMap[fullPath] = node;

  if (node.children) {
    node.children.forEach((child) => buildFileMap(child, fullPath, fileMap));
  }
};

interface RepoState {
  root: FileNode | null;
  loading: boolean;
  error: string | null;
  fileMap: Record<string, FileNode>;
  repoLink: string | null;
}

const initialState: RepoState = {
  root: null,
  loading: false,
  error: null,
  fileMap: {},
  repoLink: null,
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
        state.root = action.payload.repo.files as FileNode;
        const fileMap: Record<string, FileNode> = {};
        buildFileMap(state.root, "", fileMap);
        state.fileMap = fileMap;
        state.repoLink = action.payload.repoLink;
      })
      .addCase(fetchRepoStructure.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      });
  },
});

export default repoSlice.reducer;