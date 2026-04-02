FROM ubuntu:22.04

LABEL org.opencontainers.image.title="submitty-e2e-setup"
LABEL org.opencontainers.image.description="Dockerfile converted from .github/actions/e2e-Setup-Composite/action.yml"

ENV PGPASSWORD=submitty_dbuser \
    PHP_USER=submitty_php \
    PHP_GROUP=submitty_php \
    CGI_USER=submitty_cgi \
    SUBMITTY_DATA_DIR=/var/local/submitty \
    SUBMITTY_INSTALL_DIR=/usr/local/submitty \
    SUBMITTY_REPOSITORY=/usr/local/submitty/GIT_CHECKOUT/Submitty \
    POSTGRES_HOST=localhost \
    PHP_VER=8.2 \
    NODE_VERSION=16 \
    PYTHON_VERSION=3.10

ARG DEBIAN_FRONTEND=noninteractive

# Basic tools, Python, Composer and common build deps. PHP 8.2 via sury, Node 16 via NodeSource.
RUN apt-get update \
     && apt-get install -y --no-install-recommends \
         apt-utils ca-certificates curl gnupg lsb-release build-essential sudo git \
         python3 python3-pip python3-venv python3-dev unzip jq moreutils \
         libseccomp-dev libboost-all-dev postgresql-client \
         nginx apache2 apache2-suexec-custom libapache2-mod-authnz-external libapache2-mod-authz-unixgroup libapache2-mod-wsgi-py3 \
     && curl -fsSL https://packages.sury.org/php/apt.gpg | gpg --dearmor -o /usr/share/keyrings/sury-php.gpg \
     && echo "deb [signed-by=/usr/share/keyrings/sury-php.gpg] https://packages.sury.org/php/ $(lsb_release -sc) main" > /etc/apt/sources.list.d/sury-php.list \
     && apt-get update \
     && apt-get install -y --no-install-recommends \
         php${PHP_VER}-fpm php${PHP_VER}-cli php${PHP_VER}-imagick php${PHP_VER}-ldap \
     && curl -fsSL https://deb.nodesource.com/setup_16.x | bash - \
     && apt-get install -y --no-install-recommends nodejs \
     && curl -sS https://getcomposer.org/installer | php -- --install-dir=/usr/local/bin --filename=composer \
     && apt-get clean \
     && rm -rf /var/lib/apt/lists/*

# Prepare submitty install directory and copy repository into image. When building the image
# provide repository files in the build context (e.g. `docker build .` from repo root).
RUN mkdir -p ${SUBMITTY_INSTALL_DIR}/GIT_CHECKOUT
COPY . ${SUBMITTY_INSTALL_DIR}/GIT_CHECKOUT/Submitty
RUN chmod -R a+rwx ${SUBMITTY_INSTALL_DIR} && chmod -R a+rwx /tmp/

# Python dependencies used by tests
RUN python3 -m pip install --upgrade pip setuptools wheel packaging \
    && pip3 install selenium websocket_client \
    && if [ -f "${SUBMITTY_REPOSITORY}/.setup/pip/system_requirements.txt" ]; then pip3 install -r ${SUBMITTY_REPOSITORY}/.setup/pip/system_requirements.txt; fi

# Install PHP dependencies via composer
WORKDIR ${SUBMITTY_REPOSITORY}/site
RUN if [ -f composer.json ]; then composer install --no-interaction --prefer-dist; fi

# Install Submitty python utilities
WORKDIR ${SUBMITTY_REPOSITORY}/python_submitty_utils
RUN if [ -f setup.py ] || [ -f pyproject.toml ]; then pip3 install .; fi

# Run the project's testing/setup scripts to prepare the install (best-effort)
RUN bash -lc "cd ${SUBMITTY_REPOSITORY} && if [ -x ./.setup/testing/autograder.sh ]; then ./.setup/testing/autograder.sh config=/usr/local/submitty/config || true; fi"
RUN bash -lc "cd ${SUBMITTY_REPOSITORY} && if [ -x ./.setup/testing/setup.sh ]; then ./.setup/testing/setup.sh || true; fi"

# Copy a lightweight entrypoint that documents next manual steps that require services
COPY entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

WORKDIR /
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
CMD ["/bin/bash"]
