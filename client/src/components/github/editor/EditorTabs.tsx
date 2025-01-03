import React, { useCallback } from "react";
import useEditor from "../../../store/features/editor/hook";
import CodeEditor from "./CodeEditor";
import { Tabs, TabsContent, TabsList } from "../../ui/tabs";
import TabTrigger from "./EditorTabsTrigger";
import EditorBreadCrumb from "./EditorBreadCrumb";

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
            <CodeEditor key={file.id} fileId={file.id} />
          </TabsContent>
        ))}
      </div>
    </Tabs>
  );
};

export default EditorTabs;
