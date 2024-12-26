import React, { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import api from "../../../client/axios";

async function loadRepo(url: string) {
  const response = await api.get(`/github/load-repo?url=${url}`);
  return response.data;
}

const GithubRepo: React.FC = () => {
  const [searchParams] = useSearchParams();
  const [repoData, setRepoData] = useState<string[]>([]);
  const repoUrl = searchParams.get("url");

  const copyToClipboard = () => {
    navigator.clipboard.writeText(repoData.join("\n"));
  };

  useEffect(() => {
    if (!repoUrl) {
      return;
    }

    loadRepo(repoUrl).then((data) => {
      // If data is a string, split by \n, otherwise stringify and split
      const lines =
        typeof data === "string"
          ? data.split("\\n") // Handle escaped newlines
          : JSON.stringify(data, null, 2).split("\n");

      // Remove empty lines and clean up the strings
      const cleanedLines = lines
        .map((line) => line.trim())
        .filter((line) => line.length > 0);

      setRepoData(cleanedLines);
    });
  }, [repoUrl]);

  if (!repoUrl) {
    return <div>No repository URL provided</div>;
  }

  return (
    <div>
      <div style={{ position: "relative" }}>
        <pre
          style={{
            backgroundColor: "#1e1e1e",
            color: "#fff",
            padding: "20px",
            borderRadius: "5px",
            overflow: "auto",
            maxHeight: "500px",
            fontFamily: "monospace",
          }}
        >
          {repoData.map((line, index) => (
            <div key={index} style={{ display: "flex", gap: "1rem" }}>
              <span
                style={{ color: "#666", userSelect: "none", minWidth: "2rem" }}
              >
                {index + 1}
              </span>
              <span style={{ whiteSpace: "pre" }}>
                {line.replace(/^\./, "📁 .")}{" "}
                {/* Add folder icon for paths starting with . */}
              </span>
            </div>
          ))}
        </pre>
        {repoData.length > 0 && (
          <button
            onClick={copyToClipboard}
            style={{
              position: "absolute",
              top: "10px",
              right: "10px",
              padding: "5px 10px",
              background: "#333",
              color: "#fff",
              border: "none",
              borderRadius: "3px",
              cursor: "pointer",
            }}
          >
            Copy
          </button>
        )}
      </div>
    </div>
  );
};

export default GithubRepo;
