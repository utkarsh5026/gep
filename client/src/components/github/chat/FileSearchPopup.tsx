import React, { useRef, useEffect, useState } from "react";
import FileList from "./FileList";

interface FileSearchPopupProps {
  onFileSelect: (file: string) => void;
  onClose: () => void; // Added to handle closing the popup
}

/**
 * A popup component for searching and selecting files
 * @param {(file: string) => void} onFileSelect - Callback function when a file is selected
 * @param {() => void} onClose - Callback function to close the popup
 */
const FileSearchPopup: React.FC<FileSearchPopupProps> = ({
  onFileSelect,
  onClose,
}) => {
  const [searchQuery, setSearchQuery] = useState("");
  const searchContainerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        searchContainerRef.current &&
        !searchContainerRef.current.contains(event.target as Node)
      ) {
        onClose();
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, [onClose]);

  return (
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
          onFileSelect(file);
          setSearchQuery("");
        }}
      />
    </div>
  );
};

export default FileSearchPopup;
