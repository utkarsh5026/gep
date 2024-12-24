import React, { useState } from "react";
import { Input } from "../ui/input";
import { Button } from "../ui/button";

/**
 * Extracts owner and repository name from a GitHub URL.
 * @param url - The GitHub repository URL to parse
 * @returns An object containing the owner and repository name
 * @throws {Error} If the URL format is invalid or missing owner/repo parts
 * @example
 * extractRepoInfo("https://github.com/facebook/react")
 * // Returns { owner: "facebook", repo: "react" }
 */
const extractRepoInfo = (url: string) => {
  try {
    const parsedUrl = new URL(url);
    const pathParts = parsedUrl.pathname.split("/").filter(Boolean);
    if (pathParts.length < 2) throw new Error("Invalid repository URL");
    return {
      owner: pathParts[0],
      repo: pathParts[1],
    };
  } catch {
    throw new Error("Invalid URL format");
  }
};

/**
 * Validates if a GitHub repository exists and is accessible.
 * Makes a request to GitHub's API to check repository status.
 * @param url - The GitHub repository URL to validate
 * @returns Promise resolving to the repository data from GitHub API
 * @throws {Error} If repository is not found, private, or URL is invalid
 * @example
 * await validateGithubRepo("https://github.com/facebook/react")
 * // Returns repository data if successful
 */
const validateGithubRepo = async (url: string) => {
  const { owner, repo } = extractRepoInfo(url);
  const response = await fetch(`https://api.github.com/repos/${owner}/${repo}`);

  if (!response.ok) {
    throw new Error("Repository not found or private");
  }

  return await response.json();
};

const GithubLinkDownload: React.FC<{
  githubLink: string;
}> = ({ githubLink }) => {
  const [repoLink, setRepoLink] = useState(githubLink);
  const [error, setError] = useState<string>("");
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setIsLoading(true);

    try {
      await validateGithubRepo(repoLink);
      // TODO: Handle the submission
      console.log("Repository validated successfully:", repoLink);
    } catch (error) {
      setError(
        error instanceof Error ? error.message : "Failed to validate repository"
      );
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex items-center justify-center min-h-[60vh] w-full p-4 dark:bg-gray-900">
      <form
        onSubmit={handleSubmit}
        className="w-full max-w-3xl space-y-6 p-8 bg-white rounded-lg shadow-lg dark:bg-gray-800"
      >
        <h2 className="text-2xl font-bold text-center mb-8 text-gray-900 dark:text-white">
          Enter GitHub Repository Link
        </h2>

        <div className="space-y-2">
          <Input
            type="url"
            className="w-full dark:bg-gray-800 text-black dark:text-white"
            value={repoLink}
            onChange={(e) => setRepoLink(e.target.value)}
            placeholder="https://github.com/username/repository"
            required
          />
          {error && <p className="text-red-500 text-sm">{error}</p>}
        </div>

        <Button type="submit" disabled={isLoading}>
          {isLoading ? "Validating..." : "Download Repository"}
        </Button>
      </form>
    </div>
  );
};

export default GithubLinkDownload;
