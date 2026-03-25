
import json
from pathlib import Path
from typing import Dict


class Repository:
    def __init__(self, path="."):
        self.path = Path(path).resolve()
        self.git_dir = self.path / ".cit"

         # .git/objects
        self.objects_dir = self.git_dir / "objects"

        # .git/refs
        self.ref_dir = self.git_dir / "refs"
        self.heads_dir = self.ref_dir / "heads"

        # HEAD file
        self.head_file = self.git_dir / "HEAD"

        # .git/index
        self.index_file = self.git_dir / "index"

    def init(self) -> bool:
        if self.git_dir.exists():
            return False

        # create directories
        self.git_dir.mkdir()
        self.objects_dir.mkdir()
        self.ref_dir.mkdir()
        self.heads_dir.mkdir()

        # create initial HEAD pointing to a branch
        self.head_file.write_text("ref: refs/heads/master\n")

        self.save_index({})

        print(f"Initialized empty Git repository in {self.git_dir}")

        return True
    
    def save_index(self, index: Dict[str, str]):
        self.index_file.write_text(json.dumps(index, indent=2))