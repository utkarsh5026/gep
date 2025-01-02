import React from "react";
import {
  ContextMenu,
  ContextMenuContent,
  ContextMenuItem,
  ContextMenuTrigger,
} from "../../ui/context-menu";

interface FileTabProps {
  isActive: boolean;
}

const FileTab: React.FC<FileTabProps> = ({ isActive }) => {
  return (
    <div className="flex items-center justify-center">
      <ContextMenu>
        <ContextMenuContent>
          <ContextMenuItem onClick={() => console.log("close")}>
            Close
          </ContextMenuItem>
          <ContextMenuItem onClick={() => console.log("close other")}>
            Close Others
          </ContextMenuItem>
          <ContextMenuItem onClick={() => console.log("close to right")}>
            Close to Right
          </ContextMenuItem>
          <ContextMenuItem onClick={() => console.log("save")}>
            Save
          </ContextMenuItem>
          <ContextMenuItem onClick={() => console.log("copy path")}>
            Copy Path
          </ContextMenuItem>
        </ContextMenuContent>
      </ContextMenu>
    </div>
  );
};

export default FileTab;
