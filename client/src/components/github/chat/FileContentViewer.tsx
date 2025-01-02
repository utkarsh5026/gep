import React from "react";
import { getLanguageByExtension } from "../../../code/language";
import { useReadOnlyCodeMirror } from "../../../code/useReadOnlyCodeMirror";

const FileContentViewer: React.FC<{
  content: string;
  fileName: string;
  isOpen: boolean;
  onClose: () => void;
}> = ({ content, fileName, isOpen, onClose }) => {
  const language = getLanguageByExtension(fileName);
  const { containerRef } = useReadOnlyCodeMirror({
    content,
    language,
  });

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center">
      <div className="bg-white dark:bg-gray-800 rounded-lg w-[80vw] h-[80vh] flex flex-col">
        <div className="flex justify-between items-center p-4 border-b dark:border-gray-700">
          <h3 className="text-lg font-semibold">{fileName}</h3>
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
          >
            ✕
          </button>
        </div>
        <div className="flex-1 overflow-hidden" ref={containerRef} />
      </div>
    </div>
  );
};

export default FileContentViewer;
