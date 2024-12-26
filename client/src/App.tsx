import { Routes, Route } from "react-router-dom";
import GithubLinkDownload from "./components/github/GithubLinkDownload";
import GithubRepo from "./components/github/repo/GithubRepo";
import ThemeToggle from "./components/theme/ThemeToggle";

function App() {
  return (
    <div className="flex justify-center items-center min-h-screen bg-gray-900 text-white font-roboto-mono">
      <div className="fixed top-4 right-4 z-50">
        <ThemeToggle />
      </div>

      <div className="w-full max-w-4xl p-6 dark:bg-gray-800 dark:text-gray-100">
        <Routes>
          <Route
            path="/"
            element={
              <GithubLinkDownload githubLink="https://github.com/username/repository" />
            }
          />
          <Route path="/repos" element={<GithubRepo />} />
        </Routes>
      </div>
    </div>
  );
}

export default App;
