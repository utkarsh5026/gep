import { useCallback } from "react";
import { useAppSelector, useAppDispatch } from "../root/hooks.ts";
import {
  type FileNode,
  fetchRepoStructure as fetchRepoThunk,
} from "../slices/repo";

interface RepoState {
  repoLink: string | null;
  root: FileNode | null;
  loading: boolean;
  error: string | null;
  fileMap: Record<string, FileNode>;
  fetchRepo: (url: string) => void;
}

/**
 * A custom hook for managing repository state and actions
 *
 * @returns {RepoState} An object containing:
 *   - root: The root FileNode of the repository structure
 *   - loading: Boolean indicating if a repository fetch is in progress
 *   - error: Error message if repository fetch failed, null otherwise
 *   - fileMap: Map of file paths to FileNode objects for quick lookups
 *   - repoLink: URL of the currently loaded repository
 *   - fetchRepo: Function to fetch and load a new repository by URL
 */
const useRepo = (): RepoState => {
  const { root, loading, error, fileMap, repoLink } = useAppSelector(
    (state) => state.repo
  );
  const dispatch = useAppDispatch();

  const fetchRepo = useCallback(
    (url: string) => {
      dispatch(fetchRepoThunk(url));
    },
    [dispatch]
  );

  console.dir(fileMap, { depth: null });
  return {
    root,
    loading,
    error,
    fileMap,
    repoLink,
    fetchRepo,
  };
};

export default useRepo;
