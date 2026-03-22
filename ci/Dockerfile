FROM ubuntu:22.04
ARG DEBIAN_FRONTEND=noninteractive

ENV DEBIAN_FRONTEND=noninteractive

# Install a minimal, reliable base of packages. Avoid installing apache/nginx/php versions
# here because version availability differs between Ubuntu releases and can cause build failures.
# RUN apt-get update && apt-get install -y --no-install-recommends \
#     ca-certificates curl build-essential sudo \
#     python3 python3-pip python3-venv git tar jq moreutils \
#     libseccomp-dev libboost-all-dev poppler-utils valgrind postgresql-client && \
#   apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

# Copy repository into image (keep context small where possible)
COPY . /workspace

# Run the heavy setup steps inside the image so the resulting image is prebuilt.
# Emit listings so CI logs show whether the scripts are present, make them
# executable if needed, and run them with bash so they execute even without
# the exec bit. Use `set -ex` so commands are verbose and fail the build on
# error.
RUN bash -lc "cd /workspace && echo '--- /workspace top-level ---' && ls -la . || true && echo '--- listing .setup ---' && ls -la ./.setup || true && echo '--- listing .setup/testing ---' && ls -la ./.setup/testing || true && echo '--- find files under .setup ---' && find ./.setup -maxdepth 3 -type f -printf '%p %M %s\n' || true && if [ -f ./.setup/testing/autograder.sh ]; then echo 'FOUND autograder.sh - running'; chmod +x ./.setup/testing/autograder.sh || true; set -ex; bash ./.setup/testing/autograder.sh config=/usr/local/submitty/config; else echo 'autograder.sh NOT FOUND'; fi && if [ -f ./.setup/testing/setup.sh ]; then echo 'FOUND setup.sh - running'; chmod +x ./.setup/testing/setup.sh || true; set -ex; bash ./.setup/testing/setup.sh; else echo 'setup.sh NOT FOUND'; fi"

# Keep the prepared Submitty install available
VOLUME ["/usr/local/submitty"]

CMD ["/bin/bash"]
