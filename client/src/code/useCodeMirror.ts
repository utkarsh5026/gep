import { useEffect, useRef, useCallback } from "react";
import { EditorState, Extension } from "@codemirror/state";
import { EditorView, ViewUpdate, keymap } from "@codemirror/view";
import { languageConfigurations } from "./language";
import useEditor from "../store/hooks/editor";
import { basicSetup } from "codemirror";
import { oneDark } from "@codemirror/theme-one-dark";
import { history, historyKeymap } from "@codemirror/commands";

interface UseCodeMirrorProps {
  fileId: string;
  onChange?: (value: string) => void;
  extensions?: Extension[];
  onSelectedChange?: (selectedText: string) => void;
}

export function useCodeMirror({
  fileId,
  onChange,
  onSelectedChange,
  extensions = [],
}: UseCodeMirrorProps) {
  const { updateFileContent, openFiles } = useEditor();
  const editorRef = useRef<EditorView>();
  const containerRef = useRef<HTMLDivElement>(null);

  const file = openFiles.find((f) => f.id === fileId);
  console.log(file);
  useEffect(() => {
    if (!containerRef.current || !file) return;

    console.log("Editor effect running, editor exists:", !!editorRef.current);

    if (editorRef.current) {
      const currentContent = editorRef.current.state.doc.toString();
      console.log("Content comparison:", {
        current: currentContent,
        file: file.content,
        different: currentContent !== file.content,
      });
      if (currentContent !== file.content) {
        editorRef.current.dispatch({
          changes: {
            from: 0,
            to: currentContent.length,
            insert: file.content,
          },
        });
      }
      return;
    }

    const langConfig = languageConfigurations[file.language];

    const baseExtensions: Extension[] = [
      basicSetup,
      oneDark,
      history(),
      keymap.of(historyKeymap),
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
          if (newContent !== file.content) {
            updateFileContent(fileId, newContent);
            onChange?.(newContent);
          }
        }

        if (update.selectionSet) {
          const selection = update.state.selection.main;
          const selectedText = update.state.doc.sliceString(
            selection.from,
            selection.to
          );
          onSelectedChange?.(selectedText);
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
      if (editorRef.current) {
        editorRef.current.destroy();
        editorRef.current = undefined;
      }
    };
  }, [file, fileId, extensions, onChange, updateFileContent, onSelectedChange]);

  const getContent = useCallback(() => {
    return editorRef.current?.state.doc.toString() ?? "";
  }, [editorRef]);

  const setContent = useCallback(
    (content: string) => {
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
    [editorRef]
  );

  const getSelection = useCallback(() => {
    if (!editorRef.current)
      return {
        text: "",
        startLine: 0,
        endLine: 0,
        file: file,
      };

    const selection = editorRef.current.state.selection.main;
    const doc = editorRef.current.state.doc;
    const text = editorRef.current.state.sliceDoc(selection.from, selection.to);
    return {
      text,
      startLine: doc.lineAt(selection.from).number,
      endLine: doc.lineAt(selection.to).number,
      file: file,
    };
  }, [editorRef, file]);

  return {
    containerRef,
    editor: editorRef.current,
    getContent,
    setContent,
    getSelection,
  };
}
