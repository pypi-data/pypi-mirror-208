# This script should be sourced by the shell with the pythonenvironment where the adabrain wheel package is installed.

ADABRAIN_INSTALL_PATH="$(python -m pip show ant1Interface | grep ^Location: | cut -d ' ' -f 2)"
export PYTHONPATH=${ADABRAIN_INSTALL_PATH}/:${ADABRAIN_INSTALL_PATH}/adabrain/common/interface/ant1:${ADABRAIN_INSTALL_PATH}/python:$PYTHONPATH
