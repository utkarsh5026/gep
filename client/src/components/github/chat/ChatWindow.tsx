import React, { useState } from "react";
import HumanMessage from "./HumanMessage";
import ChatInput from "./ChatInput";

interface Message {
  role: "user" | "assistant";
  content: string;
}

export default function ChatWindow() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [selectedFiles, setSelectedFiles] = useState<string[]>([]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;

    setMessages([...messages, { role: "user", content: input }]);
    setInput("");
  };

  return (
    <div className="flex flex-col h-full max-w-3xl mx-auto p-4">
      <div className="flex-1 overflow-y-auto mb-4 p-4 border border-gray-200 dark:border-gray-700 rounded-lg dark:bg-gray-800">
        {messages.map((message, index) => (
          <HumanMessage
            key={`${message.role}-${index}`}
            content={message.content}
          />
        ))}
      </div>
      <form
        onSubmit={handleSubmit}
        className="flex w-full h-60 border border-gray-200 dark:border-gray-700 rounded-lg p-2"
      >
        <ChatInput onFileSelect={(files) => setSelectedFiles(files)} />
      </form>
    </div>
  );
}
