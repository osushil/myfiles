me=$(whoami)

python setup.py --build 000  bdist_rpm --packager="${me}" --group ABCDEFGH --no-autoreq --requires "rh-python36" --release 1
