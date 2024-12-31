import React, { useState, useRef, useEffect } from "react";
import { Plus, X } from "lucide-react";
import FileList from "./FileList";
import { getFileIcon } from "../directory/fileIcons";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "../../ui/tooltip";

interface SelectedFile {
  path: string;
  fileName: string;
}

interface ChatInputProps {
  onFileSelect?: (files: string[]) => void;
}

const ChatInput: React.FC<ChatInputProps> = ({ onFileSelect }) => {
  const [showFileSearch, setShowFileSearch] = useState(false);
  const [selectedFiles, setSelectedFiles] = useState<SelectedFile[]>([]);
  const searchContainerRef = useRef<HTMLDivElement>(null);
  const [searchQuery, setSearchQuery] = useState("");

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        searchContainerRef.current &&
        !searchContainerRef.current.contains(event.target as Node)
      ) {
        setShowFileSearch(false);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const handleFileSelect = (path: string) => {
    const fileName = path.split("/").pop() ?? "";
    // Check for duplicate paths
    if (!selectedFiles.some((file) => file.path === path)) {
      const newFile = { path, fileName };
      const newFiles = [...selectedFiles, newFile];
      setSelectedFiles(newFiles);
      onFileSelect?.(newFiles.map((f) => f.path));
    }
  };

  return (
    <div className="relative w-full h-full flex flex-col">
      {/* File chips */}
      {selectedFiles.length > 0 && (
        <div className="flex flex-wrap gap-2 mb-4">
          {selectedFiles.map((file) => (
            <TooltipProvider key={file.path}>
              <Tooltip>
                <TooltipTrigger>
                  <div className="flex items-center gap-1 px-2 py-1 bg-gray-100 dark:bg-gray-700 rounded-full text-sm">
                    {getFileIcon(file.fileName)}
                    <span>{file.fileName}</span>
                    <button
                      onClick={() => {
                        const newFiles = selectedFiles.filter(
                          (f) => f.path !== file.path
                        );
                        setSelectedFiles(newFiles);
                        onFileSelect?.(newFiles.map((f) => f.path));
                      }}
                      aria-label={`Remove ${file.fileName}`}
                      className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
                    >
                      <X size={14} />
                    </button>
                  </div>
                </TooltipTrigger>
                <TooltipContent className="bg-gray-100 dark:bg-gray-700">
                  <p className="text-xs truncate dark:text-gray-400">
                    {file.path}
                  </p>
                </TooltipContent>
              </Tooltip>
            </TooltipProvider>
          ))}
        </div>
      )}

      {showFileSearch && (
        <div
          className="absolute bottom-full mb-2 w-full bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg shadow-lg"
          ref={searchContainerRef}
        >
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search files..."
            className="w-full p-2 border-b border-gray-200 dark:border-gray-700 rounded-t-lg focus:outline-none dark:bg-gray-700 dark:text-gray-100"
          />
          <FileList
            searchQuery={searchQuery}
            onFileSelect={(file) => {
              handleFileSelect(file);
              setSearchQuery("");
              setShowFileSearch(false);
            }}
          />
        </div>
      )}

      <div className="relative flex flex-1">
        <button
          type="button"
          aria-label="Add file to chat"
          onClick={() => setShowFileSearch(!showFileSearch)}
          className="absolute left-2 top-2 p-1 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
        >
          <Plus className="w-5 h-5" />
        </button>
        <textarea
          placeholder="Type your message..."
          className="w-full pl-10 p-2 border border-gray-200 dark:border-gray-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-gray-100 resize-none h-full"
        />
      </div>
    </div>
  );
};

export default ChatInput;
