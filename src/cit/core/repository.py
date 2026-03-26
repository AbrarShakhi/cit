
import json
from pathlib import Path
import time
from typing import Dict

from cit.core.objects.commit import Commit
from cit.core.objects.object import Object
from cit.core.objects.blob import Blob
from cit.core.objects.tree import Tree


class Repository:
    def __init__(self, path="."):
        self.path = Path(path).resolve()
        self.cit_dir = self.path / ".cit"

         # .cit/objects
        self.objects_dir = self.cit_dir / "objects"

        # .cit/refs
        self.ref_dir = self.cit_dir / "refs"
        self.heads_dir = self.ref_dir / "heads"

        # HEAD file
        self.head_file = self.cit_dir / "HEAD"

        # .cit/index
        self.index_file = self.cit_dir / "index"

    def init(self) -> bool:
        if self.cit_dir.exists():
            return False

        self.cit_dir.mkdir()
        self.objects_dir.mkdir()
        self.ref_dir.mkdir()
        self.heads_dir.mkdir()

        self.head_file.write_text("ref: refs/heads/master\n")

        self.save_index({})

        print(f"Initialized empty cit repository in {self.cit_dir}")

        return True


    def save_index(self, index: Dict[str, str]):
        self.index_file.write_text(json.dumps(index, indent=2))


    def add_path(self, path: str) -> None:
        full_path = self.path / path

        if not full_path.exists():
            raise FileNotFoundError(f"fatal: pathspec '{path}' did not match any files")

        if full_path.is_file():
            self.add_file(path)
        elif full_path.is_dir():
            self.add_directory(path)
        else:
            raise ValueError(f"{path} is neither a file nor a directory")
        
    def add_file(self, path: str):
        full_path = self.path / path
        if not full_path.exists():
            raise FileNotFoundError(f"Path {path} not found")
        
        content = full_path.read_bytes()

        blob = Blob(content)

        blob_hash = self.store_object(blob)

        index = self.load_index()
        index[path] = blob_hash
        self.save_index(index)

        print(f"Added {path}")

    def add_directory(self, path: str):
        full_path = self.path / path
        if not full_path.exists():
            raise FileNotFoundError(f"Directory {path} not found")
        if not full_path.is_dir():
            raise ValueError(f"{path} is not a directory")
        index = self.load_index()
        added_count = 0

        for file_path in full_path.rglob("*"):
            if file_path.is_file():
                if ".cit" in file_path.parts:
                    continue


                content = file_path.read_bytes()
                blob = Blob(content)
                blob_hash = self.store_object(blob)

                rel_path = str(file_path.relative_to(self.path))
                index[rel_path] = blob_hash
                added_count += 1

        self.save_index(index)

        if added_count > 0:
            print(f"Added {added_count} files from directory {path}")
        else:
            print(f"Directory {path} already up to date")


    def store_object(self, obj: Object) -> str:
        obj_hash = obj.hash()
        obj_dir = self.objects_dir / obj_hash[:2]
        obj_file = obj_dir / obj_hash[2:]

        if not obj_file.exists():
            obj_dir.mkdir(exist_ok=True)
            obj_file.write_bytes(obj.serialize())

        return obj_hash

    def load_index(self) -> Dict[str, str]:
        if not self.index_file.exists():
            return {}

        try:
            return json.loads(self.index_file.read_text())
        except:
            return {}

    
    def get_current_branch(self) -> str:
        if not self.head_file.exists():
            return "master"

        head_content = self.head_file.read_text().strip()
        if head_content.startswith("ref: refs/heads/"):
            return head_content[16:]

        return "HEAD"
    
    
    def get_branch_commit(self, current_branch: str):
        branch_file = self.heads_dir / current_branch

        if branch_file.exists():
            return branch_file.read_text().strip()

        return None
    

    def set_branch_commit(self, current_branch: str, commit_hash: str):
        branch_file = self.heads_dir / current_branch
        branch_file.write_text(commit_hash + "\n")


    def branch(self, branch_name: str, delete: bool = False):
        # delete
        if delete and branch_name:
            branch_file = self.heads_dir / branch_name
            if branch_file.exists():
                branch_file.unlink()
                print(f"Deleted branch {branch_name}")
            else:
                print(f"Branch {branch_name} not found")

            return

        current_branch = self.get_current_branch()
        if branch_name:
            current_commit = self.get_branch_commit(current_branch)
            if current_commit:
                self.set_branch_commit(branch_name, current_commit)
                print(f"Created branch {branch_name}")
            else:
                print(f"No commits yet, cannot create a new branch")
        else:
            branches = []
            for branch_file in self.heads_dir.iterdir():
                if branch_file.is_file() and not branch_file.name.startswith("."):
                    branches.append(branch_file.name)

            for branch in sorted(branches):
                current_marker = "* " if branch == current_branch else "  "
                print(f"{current_marker}{branch}")


    def load_object(self, obj_hash: str) -> Object:
        obj_dir = self.objects_dir / obj_hash[:2]
        obj_file = obj_dir / obj_hash[2:]

        if not obj_file.exists():
            raise FileNotFoundError(f"Object {obj_hash} not found")

        return Object.deserialize(obj_file.read_bytes())
    

    def commit(self, message: str, author: str):
        tree_hash = self.create_tree_from_index()

        current_branch = self.get_current_branch()
        parent_commit = self.get_branch_commit(current_branch)
        parent_hashes = [parent_commit] if parent_commit else []

        index = self.load_index()
        if not index:
            print("nothing to commit, working tree clean")
            return None

        if parent_commit:
            parent_cit_commit_obj = self.load_object(parent_commit)
            parent_commit_data = Commit.from_content(parent_cit_commit_obj.content)
            if tree_hash == parent_commit_data.tree_hash:
                print("nothing to commit, working tree clean")
                return None

        commit = Commit(
            tree_hash=tree_hash,
            parent_hashes=parent_hashes,
            author=author,
            committer=author,
            message=message,
        )
        commit_hash = self.store_object(commit)

        self.set_branch_commit(current_branch, commit_hash)
        self.save_index({})
        print(f"Created commit {commit_hash} on branch {current_branch}")
        return commit_hash
    
    def create_tree_from_index(self):
        index = self.load_index()
        if not index:
            tree = Tree()
            return self.store_object(tree)

        dirs = {}
        files = {}

        for file_path, blob_hash in index.items():
            parts = file_path.split("/")

            if len(parts) == 1:
                # file in root
                files[parts[0]] = blob_hash
            else:
                dir_name = parts[0]
                if dir_name not in dirs:
                    dirs[dir_name] = {}

                current = dirs[dir_name]
                for part in parts[1:-1]:
                    if part not in current:
                        current[part] = {}

                    current = current[part]

                current[parts[-1]] = blob_hash

        def create_tree_recursive(entries_dict: Dict):
            tree = Tree()

            for name, blob_hash in entries_dict.items():
                if isinstance(blob_hash, str):
                    tree.add_entry("100644", name, blob_hash)

                if isinstance(blob_hash, dict):
                    subtree_hash = create_tree_recursive(blob_hash)
                    tree.add_entry("40000", name, subtree_hash)

            return self.store_object(tree)

        root_entries = {**files}
        for dir_name, dir_contents in dirs.items():
            root_entries[dir_name] = dir_contents

        return create_tree_recursive(root_entries)


    def checkout(self, branch: str, create_branch: bool):
        # computed the files to clear from the previous branch
        previous_branch = self.get_current_branch()
        files_to_clear = set()
        try:
            previous_commit_hash = self.get_branch_commit(previous_branch)
            if previous_commit_hash:
                prev_commit_object = self.load_object(previous_commit_hash)
                prev_commit = Commit.from_content(prev_commit_object.content)
                if prev_commit.tree_hash:
                    files_to_clear = self.get_files_from_tree_recursive(
                        prev_commit.tree_hash
                    )
        except Exception:
            files_to_clear = set()

        # created/moved to a new branch
        branch_file = self.heads_dir / branch
        if not branch_file.exists():
            if create_branch:
                if previous_commit_hash:
                    self.set_branch_commit(branch, previous_commit_hash)
                    print(f"Created new branch {branch}")
                else:
                    print("No commits yet, cannot create a branch")
                    return
            else:
                print(f"Branch '{branch}' not found.")
                print(
                    "Use 'python3 main.py checkout -b {branch}' to create and switch to a new branch."
                )
                return
        self.head_file.write_text(f"ref: refs/heads/{branch}\n")

        self.restore_working_directory(branch, files_to_clear)
        print(f"Switched to branch {branch}")


    def restore_working_directory(
        self,
        branch: str,
        files_to_clear: set[str],
    ):
        target_commit_hash = self.get_branch_commit(branch)
        if not target_commit_hash:
            return

        for rel_path in sorted(files_to_clear):
            file_path = self.path / rel_path
            try:
                if file_path.is_file():
                    file_path.unlink()
                elif file_path.is_dir():
                    if not any(file_path.iterdir()):
                        file_path.rmdir()
            except Exception:
                pass

        target_commit_obj = self.load_object(target_commit_hash)
        target_commit = Commit.from_content(target_commit_obj.content)

        if target_commit.tree_hash:
            self.restore_tree(target_commit.tree_hash, self.path)

        self.save_index({})


    def restore_tree(self, tree_hash: str, path: Path):
        tree_obj = self.load_object(tree_hash)
        tree = Tree.from_content(tree_obj.content)
        for mode, name, obj_hash in tree.entries:
            file_path = path / name
            if mode.startswith("100"):
                blob_obj = self.load_object(obj_hash)
                blob = Blob(blob_obj.content)
                file_path.write_bytes(blob.content)
            elif mode.startswith("400"):
                file_path.mkdir(exist_ok=True)
                self.restore_tree(obj_hash, file_path)



    def log(self, max_count: int = 10):
        current_branch = self.get_current_branch()
        commit_hash = self.get_branch_commit(current_branch)

        if not commit_hash:
            print("No commits yet!")
            return

        count = 0
        while commit_hash and count < max_count:
            commit_obj = self.load_object(commit_hash)
            commit = Commit.from_content(commit_obj.content)

            print(f"commit {commit_hash}")
            print(f"Author: {commit.author}")
            print(f"Date: {time.ctime(commit.timestamp)}")
            print(f"\n    {commit.message}\n")

            commit_hash = commit.parent_hashes[0] if commit.parent_hashes else None
            count += 1


    def status(self):
        current_branch = self.get_current_branch()
        print(f"On branch {current_branch}")
        index = self.load_index()
        current_commit_hash = self.get_branch_commit(current_branch)

        
        last_index_files = {}
        if current_commit_hash:
            try:
                commit_obj = self.load_object(current_commit_hash)
                commit = Commit.from_content(commit_obj.content)
                if commit.tree_hash:
                    last_index_files = self.build_index_from_tree(commit.tree_hash)
            except:
                last_index_files = {}

        
        working_files = {}  
        for item in self.get_all_files():
            rel_path = str(item.relative_to(self.path))

            try:
                content = item.read_bytes()
                blob = Blob(content)
                working_files[rel_path] = blob.hash()
            except:
                continue

        staged_files = []
        unstaged_files = []
        untracked_files = []
        deleted_files = []

        
        for file_path in set(index.keys()) | set(last_index_files.keys()):
            index_hash = index.get(file_path)
            last_index_hash = last_index_files.get(file_path)

            if index_hash and not last_index_hash:
                staged_files.append(("new file", file_path))
            elif index_hash and last_index_hash and index_hash != last_index_hash:
                staged_files.append(("modified", file_path))

        if staged_files:
            print("\nChanges to be committed:")
            for stage_status, file_path in sorted(staged_files):
                print(f"   {stage_status}: {file_path}")

        
        for file_path in working_files:
            if file_path in index:
                if working_files[file_path] != index[file_path]:
                    unstaged_files.append(file_path)

        if unstaged_files:
            print("\nChanges not staged for commit:")
            for file_path in sorted(unstaged_files):
                print(f"   modified: {file_path}")

        
        for file_path in working_files:
            if file_path not in index and file_path not in last_index_files:
                untracked_files.append(file_path)

        if untracked_files:
            print("\nUntracked files:")
            for file_path in sorted(untracked_files):
                print(f"   {file_path}")

        
        for file_path in index:
            if file_path not in working_files:
                deleted_files.append(file_path)

        if deleted_files:
            print("\nDeleted files:")
            for file_path in sorted(deleted_files):
                print(f"   deleted: {file_path}")

        if (
            not staged_files
            and not unstaged_files
            and not deleted_files
            and not untracked_files
        ):
            print("\nnothing to commit, working tree clean")


    def build_index_from_tree(self, tree_hash: str, prefix: str = ""):
        index = {}
        try:
            tree_obj = self.load_object(tree_hash)
            tree = Tree.from_content(tree_obj.content)
            # list<tuple<str, str, str>>
            for mode, name, obj_hash in tree.entries:
                full_name = f"{prefix}{name}"
                if mode.startswith("100"):
                    index[full_name] = obj_hash
                elif mode.startswith("400"):
                    subindex = self.build_index_from_tree(obj_hash, f"{full_name}/")

                    index.update(subindex)
        except Exception as e:
            print(f"Warning: Could not read tree {tree_hash}: {e}")

        return index

    def get_all_files(self) -> List[Path]:
        files = []

        for item in self.path.rglob("*"):
            if ".cit" in item.parts:
                continue

            if item.is_file():
                files.append(item)

        return files

