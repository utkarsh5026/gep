import React from "react";

interface HumanMessageProps {
  content: string;
}

const HumanMessage: React.FC<HumanMessageProps> = ({ content }) => {
  return (
    <div className="w-full flex justify-center py-4 px-4 border border-gray-200 rounded-lg">
      <div className="w-full max-w-2xl">
        <div className="flex items-start gap-3">
          <div className="flex-grow">
            <div className="text-gray-700 dark:text-red-500">{content}</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default HumanMessage;
