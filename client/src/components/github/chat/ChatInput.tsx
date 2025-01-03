import React, { useState, useRef, useEffect, useMemo } from "react";
import { Plus } from "lucide-react";
import useChat, {
  FULL_FILE_END_LINE,
  FULL_FILE_START_LINE,
} from "../../../store/features/chat/hook";
import SelectedFileList from "./SelectedFileList";
import ChatInputTextArea from "./ChatInputTextArea";
import FileSearchPopup from "./FileSearchPopup";
import FileContentViewer from "./FileContentViewer";

const ChatInput: React.FC = () => {
  const [showFileSearch, setShowFileSearch] = useState(false);
  const [previewCode, setPreviewCode] = useState("");
  const searchContainerRef = useRef<HTMLDivElement>(null);
  const { currentHumanMessage, addFileToHumanMsg } = useChat();

  const selectedFiles = useMemo(
    () => currentHumanMessage?.contextFiles ?? [],
    [currentHumanMessage?.contextFiles]
  );

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
        content: null,
      };
      addFileToHumanMsg(newFile);
    }
  };

  return (
    <div className="relative w-full h-full flex flex-col">
      <SelectedFileList />
      {showFileSearch && (
        <FileSearchPopup
          onFileSelect={handleFileSelect}
          onClose={() => setShowFileSearch(false)}
        />
      )}

      {previewCode && (
        <FileContentViewer
          content={previewCode}
          fileName={previewCode}
          isOpen={true}
          onClose={() => setPreviewCode("")}
        />
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
        <ChatInputTextArea />
      </div>
    </div>
  );
};

export default ChatInput;
