import { useCallback } from "react";
import { useAppSelector, useAppDispatch } from "../root/hooks.ts";
import {
  type FileNode,
  fetchRepoStructure as fetchRepoThunk,
} from "../slices/repo";

interface RepoState {
  root: FileNode | null;
  loading: boolean;
  error: string | null;
  fileMap: Record<string, FileNode>;
  fetchRepo: (url: string) => void;
}

const useRepo = (): RepoState => {
  const { root, loading, error, fileMap } = useAppSelector(
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
  return { root, loading, error, fileMap, fetchRepo };
};

export default useRepo;
