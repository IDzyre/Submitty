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
RUN bash -lc "cd /workspace && if [ -x ./.setup/testing/autograder.sh ]; then ./.setup/testing/autograder.sh config=/usr/local/submitty/config || true; fi"
RUN bash -lc "cd /workspace && if [ -x ./.setup/testing/setup.sh ]; then ./.setup/testing/setup.sh || true; fi"

# Keep the prepared Submitty install available
VOLUME ["/usr/local/submitty"]

CMD ["/bin/bash"]
