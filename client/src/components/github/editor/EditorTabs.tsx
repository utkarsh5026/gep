import React, { useCallback } from "react";
import useEditor from "../../../store/hooks/editor";
import CodeEditor from "./CodeEditor";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "../../ui/tabs";
import { X } from "lucide-react";
import EditorBreadCrumb from "./EditorBreadCrumb";

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

const EmptyEditor: React.FC = () => (
  <div className="h-full flex items-center justify-center flex-col gap-2 text-muted-foreground">
    <p>No files open</p>
    <p className="text-sm">
      Open a file from the file explorer to start editing
    </p>
  </div>
);

const EditorTabs: React.FC = () => {
  const { openFiles, activeFileId, closeFile, setCurrentFile } = useEditor();

  const handleTabChange = useCallback(
    (fileId: string) => {
      if (fileId && fileId !== activeFileId) {
        setCurrentFile(fileId);
      }
    },
    [activeFileId, setCurrentFile]
  );

  const handleCloseTab = useCallback(
    (fileId: string) => {
      if (openFiles.length > 0) {
        closeFile(fileId);
      }
    },
    [closeFile, openFiles.length]
  );

  if (openFiles.length === 0) {
    return <EmptyEditor />;
  }

  return (
    <Tabs
      value={activeFileId ?? undefined}
      onValueChange={handleTabChange}
      className="h-full flex flex-col"
      defaultValue={openFiles[0]?.id}
    >
      <TabsList className="border-b rounded-none h-auto flex-nowrap overflow-x-auto flex items-start justify-start">
        {openFiles.map((file) => (
          <TabTrigger
            key={file.id}
            fileId={file.id}
            fileName={file.name || file.path.split("/").pop() || "Untitled"}
            isActive={file.id === activeFileId}
            onClose={handleCloseTab}
          />
        ))}
      </TabsList>

      <div className="flex-1 relative">
        {openFiles.map((file) => (
          <TabsContent
            key={file.id}
            value={file.id}
            className="absolute inset-0 m-0 border-0 data-[state=inactive]:hidden"
          >
            <EditorBreadCrumb filePath={file.path} />
            <CodeEditor
              key={file.id}
              fileId={file.id}
              onChange={(content) => {
                // Optional: Add debounced content change handling here
                console.log(`File ${file.id} content changed`);
              }}
            />
          </TabsContent>
        ))}
      </div>
    </Tabs>
  );
};

export default EditorTabs;
