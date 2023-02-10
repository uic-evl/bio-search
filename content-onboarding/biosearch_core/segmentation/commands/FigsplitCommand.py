""" Command for segmenting images in a folder using FigSplit"""

import subprocess
from os import listdir
from pathlib import Path


class FigsplitDockerCommand:
    """Execute figsplit on docker"""

    def __init__(self, instance_name):
        self.command = f"docker exec {instance_name} sh figsplit.sh "

    def execute(self, doc_folder: str):
        """Iterate over folder and segment images"""
        pathlist = [elem for elem in listdir(Path(doc_folder)) if elem.endswith(".jpg")]
        print(pathlist)
        for img_path in pathlist:
            cmd = f"{self.command} {str(img_path)}".split()
            # output = subprocess.run(
            #     [self.command, str(img_path)], capture_output=True, check=True
            # )
            p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
            out, err = p.communicate()
            print("out", out)
            print("err", err)
