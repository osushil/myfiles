set -e

me=$(whoami)

dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null && pwd )"
cd ${dir}

source /opt/app/abc/virtualenv/bin/activate

python setup.py --build $1  bdist_rpm --packager="${me}" --group ABCDEFGH --no-autoreq --requires "rh-python36" --release 1
pip install -e .

deactivate