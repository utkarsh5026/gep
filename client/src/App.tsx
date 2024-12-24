import GithubLinkDownload from "./components/github/GithubLinkDownload";
import ThemeToggle from "./components/theme/ThemeToggle";
function App() {
  return (
    <div className="flex justify-center items-center min-h-screen bg-gray-900 text-white font-roboto-mono">
      <div className="fixed top-4 right-4 z-50">
        <ThemeToggle />
      </div>

      <div className="w-full max-w-4xl p-6 dark:bg-gray-800 dark:text-gray-100">
        <GithubLinkDownload githubLink="https://github.com/username/repository" />
      </div>
    </div>
  );
}

export default App;
