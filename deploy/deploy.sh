#!/bin/bash

REPO="${REPO}"
BRANCH="${BRANCH:-master}"
REPO_FILE="${REPO##*/}"
REPO_NAME="${REPO%.git}"

BASE_DIR="/var/www"
PROJECT_DIR="${BASE_DIR}/${REPO_NAME}"

VENV_DIR="/opt/venv"
PROJECT_VENV_DIR="${VENV_DIR}/battlesnake"

WEB_USER="www-data"
WEB_GROUP="www-data"

set -o errexit \
    -o nounset

# Package Dependencies
apt-get update
apt-get -qy install \
    nginx \
    nginx-extras \
    python3 \
    python3-pip \
    python-virtualenv \
    uwsgi \
    uwsgi-plugin-python3

# Code
cd "$BASE_DIR"
git clone "${REPO}"
pushd "${PROJECT_DIR}"
git checkout "${BRANCH}"
popd
chown -R "${WEB_USER}:${WEB_GROUP}" "$PROJECT_DIR"
chmod 755 "${BASE_DIR}"

# Virtualenv and Python Package Dependencies
mkdir "${VENV_DIR}"
virtualenv "${PROJECT_VENV_DIR}" -p python3
. "${PROJECT_VENV_DIR}/bin/activate"
pip install -r requirements.txt

# Server configs
cd "$PROJECT_DIR"
cp deploy/uwsgi/battlesnake.ini /etc/uwsgi/apps-available/
ln -s /etc/uwsgi/apps-available/battlesnake.ini /etc/uwsgi/apps-enabled/

cp deploy/nginx/battlesnake /etc/nginx/sites-available/
ln -s /etc/nginx/sites-available/battlesnake /etc/nginx/sites-enabled/

# Restart
systemctl restart nginx
systemctl restart uwsgi
