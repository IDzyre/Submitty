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

# Run the heavy setup steps inside the image so the resulting image is prebuilt
# Use -f to check for file presence (executable bit may be lost in some contexts)
# and invoke scripts with bash so they run even without the exec bit. Enable
# verbose/exit-on-error to surface failures in CI.
RUN bash -lc "cd /workspace && if [ -f ./.setup/testing/autograder.sh ]; then set -ex; bash ./.setup/testing/autograder.sh config=/usr/local/submitty/config; fi"
RUN bash -lc "cd /workspace && if [ -f ./.setup/testing/setup.sh ]; then set -ex; bash ./.setup/testing/setup.sh; fi"

# Keep the prepared Submitty install available
VOLUME ["/usr/local/submitty"]

CMD ["/bin/bash"]
