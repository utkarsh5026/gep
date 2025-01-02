import { Routes, Route } from "react-router-dom";
import GithubLinkDownload from "./components/github/GithubLinkDownload";
import GithubRepo from "./components/github/repo/GithubRepo";
import ThemeToggle from "./components/theme/ThemeToggle";

function App() {
  return (
    <div className="min-h-screen bg-gray-900 text-white font-roboto-mono">
      {/* App Bar */}
      <div className="fixed top-0 left-0 right-0 h-12 bg-gray-800 border-b border-gray-700 flex items-center justify-between px-6 z-50">
        <h1 className="text-xl font-bold">Your App Name</h1>
        <ThemeToggle />
      </div>

      <main className="pt-12 h-screen">
        <div className="h-full w-full dark:bg-gray-800 dark:text-gray-100 border-2 border-gray-500 rounded-lg">
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
      </main>
    </div>
  );
}

export default App;
