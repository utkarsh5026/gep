import React, { useState } from "react";
import { ChevronDown, ChevronRight, File, Folder } from "lucide-react";
import type { FileNode } from "../../../store/slices/repo";

interface DirectoryTreeProps {
  node: FileNode;
  level?: number;
}

const DirectoryTree: React.FC<DirectoryTreeProps> = ({ node, level = 0 }) => {
  const [isOpen, setIsOpen] = useState(false);

  const handleClick = () => {
    if (node.type === "directory") {
      setIsOpen(!isOpen);
    }
  };

  return (
    <div className="select-none mx-4">
      <button
        type="button"
        className="flex items-center gap-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded px-2 py-1 w-full text-left"
        onClick={handleClick}
      >
        {node.type === "directory" ? (
          <>
            {isOpen ? <ChevronDown size={16} /> : <ChevronRight size={16} />}
            <Folder size={16} className="text-blue-500" />
          </>
        ) : (
          <>
            <span className="w-4" /> {/* Spacing for alignment */}
            <File size={16} className="text-gray-500" />
          </>
        )}
        <span>{node.name}</span>
      </button>

      {isOpen &&
        node.children?.map((child, index) => (
          <DirectoryTree
            key={`${node.name}-${index}`}
            node={child}
            level={level + 1}
          />
        ))}
    </div>
  );
};

export default DirectoryTree;