import React from "react";
import useChat from "../../../store/hooks/chat";

/**
 * A text area for the chat input
 */
const ChatInputTextArea: React.FC = () => {
  const { currentHumanMessage, setHumanMsgText } = useChat();
  return (
    <div className="flex flex-1">
      <textarea
        value={currentHumanMessage?.messageText ?? ""}
        onChange={(e) => setHumanMsgText(e.target.value)}
        placeholder="Type your message..."
        className="w-full pl-10 p-2 border border-gray-200 dark:border-gray-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-gray-100 resize-none h-full"
      />
    </div>
  );
};

export default ChatInputTextArea;
