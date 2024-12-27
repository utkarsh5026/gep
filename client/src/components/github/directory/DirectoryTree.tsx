import React, { useEffect, useState } from "react";
import { ChevronDown, ChevronRight, File, Folder } from "lucide-react";
import type { FileNode } from "../../../store/slices/repo.ts";

interface DirectoryTreeProps {
  node: FileNode;
  level?: number;
  initialOpenPaths?: string[];
  selectedPath?: string | null;
  currentPath?: string;
}

const DirectoryTree: React.FC<DirectoryTreeProps> = ({
  node,
  level = 0,
  initialOpenPaths = [],
  selectedPath = null,
  currentPath = "",
}) => {
  const fullPath = currentPath ? `${currentPath}/${node.name}` : node.name;
  const [isOpen, setIsOpen] = useState(
    initialOpenPaths.includes(fullPath) ||
      (selectedPath?.startsWith(fullPath + "/") ?? false)
  );
  const isSelected = selectedPath === fullPath;

  const itemRef = React.useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Open parent directories when selectedPath changes
    if (selectedPath?.startsWith(fullPath + "/") || selectedPath === fullPath) {
      setIsOpen(true);
    }
  }, [selectedPath, fullPath]);

  useEffect(() => {
    if (isSelected && itemRef.current) {
      setTimeout(() => {
        itemRef.current?.scrollIntoView({
          behavior: "smooth",
          block: "center",
        });
      }, 100);
    }
  }, [isSelected, selectedPath]);

  const handleClick = () => {
    if (node.type === "directory") {
      setIsOpen(!isOpen);
    }
  };

  return (
    <div className="select-none mx-4" ref={itemRef}>
      <button
        type="button"
        className={`flex items-center gap-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded px-2 py-1 w-full text-left
          ${isSelected ? "bg-blue-100 dark:bg-blue-900" : ""}`}
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
            initialOpenPaths={initialOpenPaths}
            selectedPath={selectedPath}
            currentPath={fullPath}
          />
        ))}
    </div>
  );
};

export default DirectoryTree;