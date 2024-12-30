import React from "react";
import useRepo from "../../../store/hooks/repo";
import { getFileIcon } from "../directory/fileIcons";

interface FileListProps {
  searchQuery: string;
  onFileSelect: (file: string) => void;
}


const FileList: React.FC<FileListProps> = ({ searchQuery, onFileSelect }) => {
  const { files } = useRepo();

  const filteredPaths = files.filter((path) =>
    path.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="max-h-72 overflow-y-auto scrollbar-thin scrollbar-thumb-gray-300 dark:scrollbar-thumb-gray-600 scrollbar-track-transparent">
      {filteredPaths.map((path) => {
        const fileName = path.split("/").pop() ?? "";
        const dirPath = path.slice(0, -fileName.length);

        return (
          <button
            key={path}
            onClick={() => onFileSelect(path)}
            className="w-full text-left p-2 hover:bg-gray-100 dark:hover:bg-gray-600 cursor-pointer flex items-center gap-2 text-sm"
          >
            <div className="flex items-center gap-2 mr-4">
              {getFileIcon(fileName)}
              <span className="font-medium">{fileName}</span>
            </div>
            <span className="text-gray-500 dark:text-gray-400 text-xs truncate">
              {dirPath}
            </span>
          </button>
        );
      })}
    </div>
  );
};

export default FileList;