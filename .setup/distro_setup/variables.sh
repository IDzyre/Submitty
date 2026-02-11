#!/usr/bin/env bash

# this script must be run by root or sudo
if [[ "$UID" -ne "0" ]] ; then
    echo "ERROR: This script must be run by root or sudo"
    exit
fi

# Note: This script is source by install_system.sh and so caution should be used on naming variables
# to ensure there is no collision.
SETUP_DISTRO_DIR="$( cd -P "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
DISTRO=$(lsb_release -si | tr '[:upper:]' '[:lower:]')
VERSION=$(lsb_release -sr | tr '[:upper:]' '[:lower:]')

if [ ! -d ${SETUP_DISTRO_DIR}/${DISTRO}/${VERSION} ]; then
    (>&2 echo "Unknown distro: ${DISTRO} ${VERSION}")
    exit 1
fi

source ${SETUP_DISTRO_DIR}/${DISTRO}/${VERSION}/variables.sh
