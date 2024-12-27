import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "../../ui/dialog";
import DirectoryTree from "./DirectoryTree";
import type { FileNode } from "../../../store/slices/repo";

interface RepoModalProps {
  isOpen: boolean;
  onClose: () => void;
  repoStructure: FileNode;
}

const RepoModal: React.FC<RepoModalProps> = ({
  isOpen,
  onClose,
  repoStructure,
}) => {
  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-[600px] max-h-[80vh] overflow-hidden">
        <DialogHeader>
          <DialogTitle>Repository Structure</DialogTitle>
        </DialogHeader>
        <div className="overflow-y-auto max-h-[calc(80vh-80px)] scrollbar-hide">
          <DirectoryTree node={repoStructure} />
        </div>
      </DialogContent>
    </Dialog>
  );
};

export default RepoModal;
