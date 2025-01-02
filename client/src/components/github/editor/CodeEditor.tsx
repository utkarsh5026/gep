import React, { useCallback, useEffect } from "react";
import { useCodeMirror } from "../../../code/useCodeMirror";

interface CodeEditorProps {
  fileId: string;
  onChange?: (value: string) => void;
}

const CodeEditor: React.FC<CodeEditorProps> = ({ fileId, onChange }) => {
  const { containerRef, getSelection } = useCodeMirror({
    fileId,
    onChange,
  });

  const handleKeyDown = useCallback(
    (event: KeyboardEvent) => {
      if (event.ctrlKey && event.key === "l") {
        event.preventDefault();
        const selectedText = getSelection();
        if (selectedText) {
          console.log(selectedText);
        }
      }
    },
    [getSelection]
  );

  useEffect(() => {
    const container = containerRef.current;
    if (container) {
      container.addEventListener("keydown", handleKeyDown);
    }
    return () => {
      container?.removeEventListener("keydown", handleKeyDown);
    };
  }, [handleKeyDown, containerRef]);

  return <div ref={containerRef} className="h-full w-full" />;
};

export default CodeEditor;
