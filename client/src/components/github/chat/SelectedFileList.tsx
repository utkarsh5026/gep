import React from "react";
import { X } from "lucide-react";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "../../ui/tooltip";
import { getFileIcon } from "../directory/fileIcons";
import { type SelectedFile } from "../../../store/slices/chat";
import useChat from "../../../store/hooks/chat";

interface SelectedFileListProps {
  selectedFiles: SelectedFile[];
  onFileSelect: (file: SelectedFile) => void;
}

const SelectedFileList: React.FC<SelectedFileListProps> = ({
  selectedFiles,
  onFileSelect,
}) => {
  const { removeFileFromHumanMsg } = useChat();

  return (
    <div className="flex flex-wrap gap-2 mb-4">
      {selectedFiles.map((file) => (
        <TooltipProvider key={file.path}>
          <Tooltip>
            <TooltipTrigger>
              <div className="flex items-center gap-1 px-2 py-1 bg-gray-100 dark:bg-gray-700 rounded-full text-sm">
                {getFileIcon(file.fileName)}
                <span>{file.fileName}</span>
                <button
                  onClick={() => removeFileFromHumanMsg(file)}
                  aria-label={`Remove ${file.fileName}`}
                  className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
                >
                  <X size={14} />
                </button>
              </div>
            </TooltipTrigger>
            <TooltipContent className="bg-gray-100 dark:bg-gray-700">
              <p className="text-xs truncate dark:text-gray-400">{file.path}</p>
            </TooltipContent>
          </Tooltip>
        </TooltipProvider>
      ))}
    </div>
  );
};

export default SelectedFileList;
