import { useEffect, useRef, useCallback, useMemo } from "react";
import { EditorState, Extension } from "@codemirror/state";
import { EditorView, ViewUpdate, keymap } from "@codemirror/view";
import { languageConfigurations } from "./language";
import useEditor from "../store/features/editor/hook";
import { basicSetup } from "codemirror";
import { oneDark } from "@codemirror/theme-one-dark";
import { history, historyKeymap } from "@codemirror/commands";

interface UseCodeMirrorProps {
  fileId: string;
  onChange?: (value: string) => void;
}

export function useCodeMirror({ fileId }: UseCodeMirrorProps) {
  const { updateFileContent, openFileIds, openFiles } = useEditor();
  const editorRef = useRef<EditorView>();
  const containerRef = useRef<HTMLDivElement>(null);
  const initialContentRef = useRef<string>("");

  console.log("openFileIds", openFileIds);

  const file = useMemo(
    () => openFiles.find((f) => f.id === fileId),
    [fileId, openFileIds]
  );

  useEffect(() => {
    if (!containerRef.current || !file) return;

    console.log("file.content", file.content === initialContentRef.current);

    // Only create new editor if it doesn't exist
    if (!editorRef.current) {
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
            // Only update if the content change came from user input
            if (newContent !== file.content) {
              updateFileContent(fileId, newContent);
            }
          }

          if (update.selectionSet) {
            const selection = update.state.selection.main;
            const selectedText = update.state.doc.sliceString(
              selection.from,
              selection.to
            );
            console.log(selectedText);
          }
        }),
      ];

      const state = EditorState.create({
        doc: file.content,
        extensions: baseExtensions,
      });

      initialContentRef.current = file.content;
      editorRef.current = new EditorView({
        state,
        parent: containerRef.current,
      });
    }
    // Only update content if it's different from our initial content
    // This prevents cursor jumping during normal typing
    else if (file.content !== initialContentRef.current) {
      console.log("updating content");
      initialContentRef.current = file.content;
      editorRef.current.dispatch({
        changes: {
          from: 0,
          to: editorRef.current.state.doc.length,
          insert: file.content,
        },
      });
    }

    return () => {
      if (editorRef.current) {
        editorRef.current.destroy();
        editorRef.current = undefined;
      }
    };
  }, [fileId, updateFileContent]); // Only depend on fileId changes

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
