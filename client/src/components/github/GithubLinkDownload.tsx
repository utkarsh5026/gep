import React, { useState } from "react";

const GithubLinkDownload: React.FC<{
  githubLink: string;
}> = ({ githubLink }) => {
  const [repoLink, setRepoLink] = useState(githubLink);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // TODO: Handle the submission
    console.log("Submitted repo link:", repoLink);
  };

  return (
    <div className="flex items-center justify-center min-h-[60vh] w-full p-4 dark:bg-gray-900">
      <form
        onSubmit={handleSubmit}
        className="w-full max-w-3xl space-y-6 p-8 bg-white rounded-lg shadow-lg"
      >
        <h2 className="text-2xl font-bold text-center mb-8 text-gray-900">
          Enter GitHub Repository Link
        </h2>

        <input
          type="url"
          value={repoLink}
          onChange={(e) => setRepoLink(e.target.value)}
          placeholder="https://github.com/username/repository"
          className="w-full p-4 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          required
        />

        <button
          type="submit"
          className="w-full py-4 px-6 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          Download Repository
        </button>
      </form>
    </div>
  );
};

export default GithubLinkDownload;
