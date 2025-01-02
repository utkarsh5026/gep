import React, { useCallback } from "react";
import { TabsTrigger } from "../../ui/tabs";
import { X } from "lucide-react";

interface TabTriggerProps {
  fileId: string;
  fileName: string;
  isActive: boolean;
  onClose: (fileId: string) => void;
}

const TabTrigger: React.FC<TabTriggerProps> = ({
  fileId,
  fileName,
  isActive,
  onClose,
}) => {
  const handleClose = useCallback(
    (e: React.MouseEvent) => {
      e.stopPropagation();
      onClose(fileId);
    },
    [fileId, onClose]
  );

  return (
    <TabsTrigger
      value={fileId}
      className={`
        group relative
        data-[state=active]:bg-background
        min-w-[100px]
        pr-8
      `}
    >
      <span className="truncate">{fileName}</span>
      <button
        onClick={handleClose}
        className={`
          absolute right-1
          p-1 rounded-sm
          opacity-0 group-hover:opacity-100
          ${isActive ? "opacity-75" : ""}
          hover:bg-muted
        `}
        aria-label={`Close ${fileName}`}
      >
        <X size={14} />
      </button>
    </TabsTrigger>
  );
};

export default TabTrigger;
