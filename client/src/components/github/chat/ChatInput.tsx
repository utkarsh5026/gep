import React, { useState, useRef, useEffect, useMemo } from "react";
import { Plus } from "lucide-react";
import FileList from "./FileList";
import useChat, {
  FULL_FILE_END_LINE,
  FULL_FILE_START_LINE,
} from "../../../store/hooks/chat";
import SelectedFileList from "./SelectedFileList";

const ChatInput: React.FC = () => {
  const [showFileSearch, setShowFileSearch] = useState(false);
  const searchContainerRef = useRef<HTMLDivElement>(null);
  const [searchQuery, setSearchQuery] = useState("");
  const { setHumanMsgText, currentHumanMessage, addFileToHumanMsg } = useChat();

  const selectedFiles = useMemo(
    () => currentHumanMessage?.contextFiles ?? [],
    [currentHumanMessage]
  );

  console.log(currentHumanMessage);

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
      const newFile = {
        path,
        fileName,
        startLine: FULL_FILE_START_LINE,
        endLine: FULL_FILE_END_LINE,
      };
      addFileToHumanMsg(newFile);
    }
  };

  return (
    <div className="relative w-full h-full flex flex-col">
      {/* File chips */}
      {selectedFiles.length > 0 && (
        <SelectedFileList selectedFiles={selectedFiles} />
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
          value={currentHumanMessage?.messageText ?? ""}
          onChange={(e) => setHumanMsgText(e.target.value)}
          placeholder="Type your message..."
          className="w-full pl-10 p-2 border border-gray-200 dark:border-gray-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-gray-100 resize-none h-full"
        />
      </div>
    </div>
  );
};

export default ChatInput;
