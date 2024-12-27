import React, { useEffect} from "react";
import { useSearchParams } from "react-router-dom";
import useRepo from "../../../store/hooks/repo.ts";
import RepoModal from "./RepoModal";


const GithubRepo: React.FC = () => {
  const { fetchRepo, root } = useRepo();
  const [searchParams] = useSearchParams();
  const repoUrl = searchParams.get("url");


  useEffect(() => {
    if (!repoUrl) {
      return;
    }
    fetchRepo(repoUrl);
  }, [repoUrl]);

  if (!repoUrl) {
    return <div>No repository URL provided</div>;
  }

  if (!root) {
    return <div>Loading...</div>;
  }
  console.log(root);
  return (
    <div>
      <RepoModal
        isOpen={true}
        onClose={() => {}}
        repoStructure={root}
      />
    </div>
  );
};

export default GithubRepo;