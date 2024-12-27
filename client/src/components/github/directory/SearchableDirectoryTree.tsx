import React, { useState, useMemo } from "react";
import DirectoryTree from "./DirectoryTree.tsx";
import useRepo from "../../../store/hooks/repo.ts";

// Generate array of parent paths that need to be opened
const getParentPaths = (path: string): string[] => {
  const parts = path.split("/");
  const paths: string[] = [];
  for (let i = 0; i < parts.length - 1; i++) {
    paths.push(parts.slice(0, i + 1).join("/"));
  }
  return paths;
};

const SearchableDirectoryTree: React.FC = () => {
  const { root, fileMap } = useRepo();
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedPath, setSelectedPath] = useState<string | null>(null);

  // Filter file paths based on search term
  const filteredPaths = useMemo(() => {
    if (!searchTerm) return [];
    return Object.keys(fileMap).filter((path) =>
      path.toLowerCase().includes(searchTerm.toLowerCase())
    );
  }, [searchTerm, fileMap]);

  console.dir(selectedPath, { depth: null });

  return (
    <div className="space-y-4 h-full overflow-auto scrollbar-hide p-4">
      <div className="sticky top-0 z-20 pt-4 pb-2 bg-white dark:bg-gray-900">
        <div className="relative">
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Search files..."
            className="w-full p-2 border rounded dark:bg-gray-800 dark:border-gray-700"
          />

          {/* Autocomplete dropdown */}
          {searchTerm && filteredPaths.length > 0 && (
            <div className="absolute z-10 w-full mt-1 bg-white dark:bg-gray-800 border rounded-md shadow-lg max-h-60 overflow-auto scrollbar-hide">
              {filteredPaths.map((path) => (
                <button
                  key={path}
                  onClick={() => {
                    setSelectedPath(path);
                    setSearchTerm("");
                  }}
                  className="w-full text-left px-4 py-2 hover:bg-gray-100 dark:hover:bg-gray-700"
                >
                  {path}
                </button>
              ))}
            </div>
          )}
        </div>
      </div>

      {root && (
        <div className="overflow-auto max-h-[calc(100vh-8rem)] scrollbar-hide">
          <DirectoryTree
            node={root}
            initialOpenPaths={selectedPath ? getParentPaths(selectedPath) : []}
            selectedPath={selectedPath}
          />
        </div>
      )}
    </div>
  );
};

export default SearchableDirectoryTree;
