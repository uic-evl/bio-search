""" Command for segmenting images in a folder using FigSplit"""

import subprocess
from pathlib import Path


class FigsplitDockerCommand:
    """Execute figsplit on docker"""

    def __init__(self, instance_name):
        self.command = f"docker exec ${instance_name} sh figsplit.sh "

    def execute(self, doc_folder: str):
        """Iterate over folder and segment images"""
        pathlist = Path(doc_folder).rglob("*.jpg")
        for img_path in pathlist:
            output = subprocess.run(
                [self.command, str(img_path)], capture_output=True, check=True
            )
            print(output)
