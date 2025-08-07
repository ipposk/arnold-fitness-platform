import os
import json
from typing import List, Dict


class FileSystemStorage:
    def __init__(self, base_path: str):
        self.base_path = base_path
        os.makedirs(self.base_path, exist_ok=True)

    def _get_test_folder(self, test_id: str, subfolder: str = None) -> str:
        path = os.path.join(self.base_path, test_id)
        if subfolder:
            path = os.path.join(path, subfolder)
        os.makedirs(path, exist_ok=True)
        return path

    def _get_context_path(self, test_id: str) -> str:
        return self._get_test_folder(test_id, "contexts")

    def load_all_versions(self, test_id: str) -> List[Dict]:
        folder = self._get_test_folder(test_id, "contexts")
        versions = []
        for filename in sorted(os.listdir(folder)):
            if filename.endswith(".json"):
                with open(os.path.join(folder, filename), "r") as f:
                    versions.append(json.load(f))
        return versions

    def save_context_version(self, test_id: str, context: Dict) -> None:
        folder = self._get_test_folder(test_id, "contexts")
        version_number = len([
            f for f in os.listdir(folder)
            if f.startswith("v") and f.endswith(".json")
        ]) + 1
        version_filename = f"v{version_number:03d}.json"
        version_path = os.path.join(folder, version_filename)

        with open(version_path, "w", encoding="utf-8") as f:
            json.dump(context, f, indent=2)

    def save_output_markdown(self, test_id: str, filename: str, content_md: str) -> None:
        output_dir = os.path.join(self.base_path, test_id, "outputs")
        os.makedirs(output_dir, exist_ok=True)
        file_path = os.path.join(output_dir, filename)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content_md)

    def delete_last_version(self, test_id: str):
        context_path = self._get_context_path(test_id)
        versions = sorted(f for f in os.listdir(context_path) if f.endswith(".json"))
        if versions:
            last_version = versions[-1]
            os.remove(os.path.join(context_path, last_version))