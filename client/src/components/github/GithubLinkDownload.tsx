import React, { useState, useCallback } from "react";
import { Input } from "../ui/input";
import { Button } from "../ui/button";
import api from "../../client/axios";
import debounce from "../../utils/debounce";

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
  const gitUrl = `https://github.com/${owner}/${repo}`;
  const response = await api.get("/github/check-git-url", {
    params: {
      url: gitUrl,
    },
  });
  console.log(response.data);
  return response.data;
};

const downloadGitRepo = async (url: string) => {
  const response = await api.get("/github/download-github-repo", {
    params: {
      url: url,
    },
  });
  return response.data;
};

const GithubLinkDownload: React.FC<{
  githubLink: string;
}> = ({ githubLink }) => {
  const [repoLink, setRepoLink] = useState(githubLink);
  const [error, setError] = useState<string>("");
  const [isLoading, setIsLoading] = useState(false);
  const [isValid, setIsValid] = useState(false);

  const debouncedValidation = useCallback((url: string) => {
    return debounce(async (url: string) => {
      if (!url) {
        setError("");
        setIsValid(false);
        return;
      }

      setIsLoading(true);
      setError("");

      try {
        await validateGithubRepo(url);
        setIsValid(true);
        setError("");
      } catch (err) {
        setIsValid(false);
        setError(err instanceof Error ? err.message : "Invalid repository URL");
      } finally {
        setIsLoading(false);
      }
    }, 500)(url);
  }, []);

  // Update the onChange handler
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = e.target.value;
    setRepoLink(newValue);
    setIsValid(false);
    debouncedValidation(newValue);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!isValid) setError("Please enter a valid repository URL");
    if (isValid) {
      const data = await downloadGitRepo(repoLink);
      console.log(data);
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
            onChange={handleInputChange}
            placeholder="https://github.com/username/repository"
            required
          />
          {error ? (
            <p className="text-red-500 text-sm">{error}</p>
          ) : isValid ? (
            <p className="text-green-500 text-sm">Repository is valid!</p>
          ) : null}
        </div>

        <Button type="submit" disabled={isLoading}>
          {isLoading ? "Validating..." : "Download Repository"}
        </Button>
      </form>
    </div>
  );
};

export default GithubLinkDownload;
