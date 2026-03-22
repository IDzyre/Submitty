FROM ubuntu:22.04
ARG DEBIAN_FRONTEND=noninteractive

ENV DEBIAN_FRONTEND=noninteractive

# Install a minimal, reliable base of packages. Avoid installing apache/nginx/php versions
# here because version availability differs between Ubuntu releases and can cause build failures.
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates curl build-essential sudo \
    python3 python3-pip python3-venv git tar jq moreutils \
    libseccomp-dev libboost-all-dev poppler-utils valgrind postgresql-client && \
  apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

# Copy repository into image (keep context small where possible)
COPY . /workspace

# If the CI composite action produced a prepared archive `submitty.tgz` and
# placed it in the repo root, it will be copied into /workspace by the
# previous COPY. When present, extract it into / and skip running the
# heavy setup scripts. Otherwise fall back to running the setup steps.
ARG USE_PREPARED=false
RUN bash -lc "cd /workspace && if [ -f submitty.tgz ]; then echo 'Found submitty.tgz - extracting to /'; tar -xzf submitty.tgz -C / && rm -f submitty.tgz; else echo 'No submitty.tgz found in build context; running setup scripts if present'; if [ -f ./.setup/testing/autograder.sh ]; then set -ex; bash ./.setup/testing/autograder.sh config=/usr/local/submitty/config; fi; if [ -f ./.setup/testing/setup.sh ]; then set -ex; bash ./.setup/testing/setup.sh; fi; fi"

# Keep the prepared Submitty install available
VOLUME ["/usr/local/submitty"]

CMD ["/bin/bash"]
