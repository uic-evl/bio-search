# Segmentation module

Executes Figsplit on input images based on the Python wrapper for Matlab:
https://github.com/KasraNezamabadi/figsplit_wrapper

## Building a docker image for Figsplit

```bash
docker build --build-arg MATLAB_PRODUCT_LIST="MATLAB Image_Processing_Toolbox Computer_Vision_Toolbox" --build-arg LICENSE_SERVER=PORT@LICENSE_SERVER -t figsplit:1.0 .

docker run -ti --rm  -p 8888:8888 --user root -e NB_GID=100 -e GEN_CERT=yes -e GRANT_SUDO=yes -v IMAGE_FOLDER:/mnt figsplit:1.0 start.sh bash

ctrl p + ctrl q # to leave the container running
```

The Dockerfile is a modified version from the Dockerfile provided by Mathworks in
the Matlab for Jupyter [repository](https://github.com/mathworks-ref-arch/matlab-integration-for-jupyter/tree/main/matlab).
