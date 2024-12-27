import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "../../ui/dialog";
import SearchableDirectoryTree from "./SearchableDirectoryTree";

interface RepoModalProps {
  isOpen: boolean;
  onClose: () => void;
}

const RepoModal: React.FC<RepoModalProps> = ({ isOpen, onClose }) => {
  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-[600px] max-h-[80vh] overflow-hidden">
        <DialogHeader>
          <DialogTitle>Repository Structure</DialogTitle>
        </DialogHeader>
        <div className="overflow-y-auto max-h-[calc(80vh-80px)] scrollbar-hide">
          <SearchableDirectoryTree />
        </div>
      </DialogContent>
    </Dialog>
  );
};

export default RepoModal;
