import React, { useCallback, useEffect } from "react";
import { useCodeMirror } from "../../../code/useCodeMirror";
import useChat from "../../../store/features/chat/hook";
import { getFileName } from "../../../utils/file";

interface CodeEditorProps {
  fileId: string;
}

const CodeEditor: React.FC<CodeEditorProps> = ({ fileId }) => {
  const { containerRef, getSelection } = useCodeMirror({
    fileId,
  });
  const { addFileToHumanMsg, currentHumanMessage } = useChat();

  console.log(currentHumanMessage?.contextFiles);

  const handleKeyDown = useCallback(
    (event: KeyboardEvent) => {
      if (event.ctrlKey && event.key === "l") {
        event.preventDefault();
        const selectedText = getSelection();
        if (!selectedText) return;

        const { startLine, endLine, text } = selectedText;
        addFileToHumanMsg({
          path: fileId,
          fileName: getFileName(fileId),
          startLine,
          endLine,
          content: text,
        });
      }
    },
    [getSelection, addFileToHumanMsg, fileId]
  );

  useEffect(() => {
    const container = containerRef.current;
    if (container) container.addEventListener("keydown", handleKeyDown);

    return () => {
      container?.removeEventListener("keydown", handleKeyDown);
    };
  }, [handleKeyDown, containerRef]);

  return <div ref={containerRef} className="h-full w-full" />;
};

export default CodeEditor;
