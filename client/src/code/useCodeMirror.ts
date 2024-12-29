import { useEffect, useRef } from "react";
import { EditorState, Extension } from "@codemirror/state";
import { EditorView, ViewUpdate } from "@codemirror/view";
import { languageConfigurations } from "./language";
import useEditor from "../store/hooks/editor";
import { basicSetup } from "codemirror";
import { oneDark } from "@codemirror/theme-one-dark";

interface UseCodeMirrorProps {
  fileId: string;
  onChange?: (value: string) => void;
  extensions?: Extension[];
}

export function useCodeMirror({
  fileId,
  onChange,
  extensions = [],
}: UseCodeMirrorProps) {
  const { updateFileContent, openFiles } = useEditor();
  const editorRef = useRef<EditorView>();
  const containerRef = useRef<HTMLDivElement>(null);

  const file = openFiles.find((f) => f.id === fileId);
  console.log(file);
  useEffect(() => {
    if (!containerRef.current || !file || editorRef.current) return;

    const langConfig = languageConfigurations[file.language];

    const baseExtensions: Extension[] = [
      basicSetup,
      oneDark,
      langConfig.extension(),
      EditorState.tabSize.of(langConfig.editorConfig?.tabSize ?? 2),
      EditorView.theme({
        "&": {
          height: "100%",
          maxHeight: "100%",
          fontSize: "20px",
          fontFamily: "var(--font-mono)",
        },
        ".cm-scroller": {
          overflow: "auto",
          "&::-webkit-scrollbar": {
            width: "8px",
            height: "8px",
          },
          "&::-webkit-scrollbar-track": {
            background: "transparent",
          },
          "&::-webkit-scrollbar-thumb": {
            background: "#4b5563",
            borderRadius: "4px",
          },
          "&::-webkit-scrollbar-thumb:hover": {
            background: "#6b7280",
          },
        },
      }),
      ...(langConfig.additionalExtensions || []),
      EditorView.updateListener.of((update: ViewUpdate) => {
        if (update.docChanged) {
          const newContent = update.state.doc.toString();
          updateFileContent(fileId, newContent);
          onChange?.(newContent);
        }
      }),
    ];

    const state = EditorState.create({
      doc: file.content,
      extensions: [...baseExtensions, ...extensions],
    });

    editorRef.current = new EditorView({
      state,
      parent: containerRef.current,
    });

    return () => {
      editorRef.current?.destroy();
      editorRef.current = undefined;
    };
  }, [file, fileId, extensions, onChange, updateFileContent]);

  return {
    containerRef,
    editor: editorRef.current,
    getContent: () => editorRef.current?.state.doc.toString() ?? "",
    setContent: (content: string) => {
      if (editorRef.current) {
        editorRef.current.dispatch({
          changes: {
            from: 0,
            to: editorRef.current.state.doc.length,
            insert: content,
          },
        });
      }
    },
  };
}
