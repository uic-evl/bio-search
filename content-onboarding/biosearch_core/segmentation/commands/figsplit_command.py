""" Command for segmenting images in a folder using FigSplit"""

import subprocess
import logging
from os import listdir
from pathlib import Path


class FigsplitCommand:
    """Execute figsplit on docker"""

    def __init__(self, instance_name: str, container_type: str = "docker"):
        if container_type == "docker":
            self.command = f"docker exec {instance_name} sh figsplit.sh "
        elif container_type == "pod":
            self.command = f"kubectl exec {instance_name} -- sh figsplit.sh "

    def execute(self, base_dir: str, rel_folder_dir: str) -> bool:
        """Iterate over folder and segment images
        Parameters:
        doc_folder: str
            Location of the document with figures to extract on local machine
        rel_folder_dir: str
            Relative folder location mounted on container without initial /
        Returns:
            True, if every element is processed without errors
            False, otherwise
        """
        local_dir = Path(base_dir) / rel_folder_dir
        pathlist = [elem for elem in listdir(Path(local_dir)) if elem.endswith(".jpg")]
        folder_name = Path(rel_folder_dir).name
        for img_name in pathlist:
            img_docker_path = Path("/mnt") / rel_folder_dir / img_name
            cmd = f"{self.command} {str(img_docker_path)}".split()
            try:
                subprocess.check_call(cmd)
            except subprocess.CalledProcessError:
                message = f"{folder_name},{img_name},{cmd}"
                logging.error(message, exc_info=True)
                return False
        return True
