import React from "react";
import { useCodeMirror } from "../../../code/useCodeMirror";

interface CodeEditorProps {
  fileId: string;
  onChange?: (value: string) => void;
}

const CodeEditor: React.FC<CodeEditorProps> = ({ fileId, onChange }) => {
  const { containerRef } = useCodeMirror({
    fileId,
    onChange,
  });

  return <div ref={containerRef} className="h-full w-full" />;
};

export default CodeEditor;
