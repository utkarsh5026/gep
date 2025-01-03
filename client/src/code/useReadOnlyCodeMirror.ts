import { useEffect, useRef, useMemo } from "react";
import { EditorState, Extension } from "@codemirror/state";
import { EditorView } from "@codemirror/view";
import { languageConfigurations } from "./language";
import { basicSetup } from "codemirror";
import { oneDark } from "@codemirror/theme-one-dark";

interface UseReadOnlyCodeMirrorProps {
  content: string;
  language: string;
}

export function useReadOnlyCodeMirror({
  content,
  language,
}: UseReadOnlyCodeMirrorProps) {
  const editorRef = useRef<EditorView>();
  const containerRef = useRef<HTMLDivElement>(null);

  const extensions = useMemo(() => {
    const langConfig =
      languageConfigurations[language] || languageConfigurations["text"];

    const baseExtensions: Extension[] = [
      basicSetup,
      oneDark,
      langConfig.extension(),
      EditorState.readOnly.of(true), // Make it read-only
      EditorView.theme({
        "&": {
          height: "100%",
          maxHeight: "100%",
          fontSize: "14px",
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
    ];

    return baseExtensions;
  }, [language]);

  useEffect(() => {
    if (!containerRef.current) return;

    // Create new editor if it doesn't exist
    if (!editorRef.current) {
      const state = EditorState.create({
        doc: content,
        extensions,
      });

      editorRef.current = new EditorView({
        state,
        parent: containerRef.current,
      });
    }
    // Update content if editor exists
    else {
      editorRef.current.dispatch({
        changes: {
          from: 0,
          to: editorRef.current.state.doc.length,
          insert: content,
        },
      });
    }

    return () => {
      if (editorRef.current) {
        editorRef.current.destroy();
        editorRef.current = undefined;
      }
    };
  }, [content, extensions]);

  return {
    containerRef,
    editor: editorRef.current,
  };
}
