import React, { useEffect } from "react";
import { useSearchParams } from "react-router-dom";
import useRepo from "../../../store/features/repo/hook";
import SearchableDirectoryTree from "../directory/SearchableDirectoryTree.tsx";
import ChatWindow from "../chat/ChatWindow.tsx";
import EditorTabs from "../editor/EditorTabs.tsx";
import {
  ResizableHandle,
  ResizablePanel,
  ResizablePanelGroup,
} from "../../ui/resizable.tsx";
import usePanelWidths from "../../../store/hooks/window";

const GithubRepo: React.FC = () => {
  const { fetchRepo, root } = useRepo();
  const {
    chatWidth,
    editorWidth,
    dirWidth,
    setChatWidth,
    setEditorWidth,
    setDirWidth,
  } = usePanelWidths();
  const [searchParams] = useSearchParams();
  const repoUrl = searchParams.get("url");

  useEffect(() => {
    if (!repoUrl) {
      return;
    }
    fetchRepo(repoUrl);
  }, [repoUrl, fetchRepo]);

  if (!repoUrl) {
    return <div>No repository URL provided</div>;
  }

  if (!root) {
    return <div>Loading...</div>;
  }

  console.log(chatWidth, editorWidth, dirWidth);

  return (
    <div className="h-full w-full border-2 border-gray-500 rounded-lg">
      <ResizablePanelGroup
        direction="horizontal"
        className="h-full"
        onLayout={(sizes) => {
          setChatWidth(sizes[0]);
          setEditorWidth(sizes[1]);
          setDirWidth(sizes[2]);
        }}
      >
        <ResizablePanel defaultSize={chatWidth}>
          <ChatWindow />
        </ResizablePanel>
        <ResizableHandle />
        <ResizablePanel
          defaultSize={editorWidth}
          className="border-l-2 border-gray-500"
        >
          <EditorTabs />
        </ResizablePanel>
        <ResizableHandle />
        <ResizablePanel
          defaultSize={dirWidth}
          className="border-l-2 border-gray-500"
        >
          <div className="h-full overflow-auto">
            <SearchableDirectoryTree />
          </div>
        </ResizablePanel>
      </ResizablePanelGroup>
    </div>
  );
};

export default GithubRepo;
