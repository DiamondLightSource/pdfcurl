# The devcontainer should use the developer target and run as root with podman
# or docker with user namespaces.
FROM ghcr.io/diamondlightsource/ubuntu-devcontainer:resolute AS developer

# Add any system dependencies for the developer/build environment here
RUN apt-get update -y && apt-get install -y --no-install-recommends \
    graphviz \
    && apt-get dist-clean

# The build stage installs the context into the venv
FROM developer AS build

# Change the working directory to the `app` directory
# and copy in the project
WORKDIR /app
COPY . /app
RUN chmod o+wrX .

# Tell uv sync to install python in a known location so we can copy it out later
ENV UV_PYTHON_INSTALL_DIR=/python

# Sync the project without its dev dependencies
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-editable --no-dev --managed-python

# The runtime stage copies the built venv into a runtime container
FROM ubuntu:resolute AS runtime

ENV HOME=/tmp
ENV XDG_CACHE_HOME=/tmp/uv-cache
ENV UV_CACHE_DIR=/tmp/uv-cache

RUN mkdir -p /tmp/uv-cache && chmod -R 777 /tmp/uv-cache

# Add apt-get system dependecies for runtime here if needed
RUN DEBIAN_FRONTEND=noninteractive apt-get update && apt-get install -y --no-install-recommends \
    # Git required for installing packages at runtime
    git \
    # gdb required for attaching debugger
    gdb \
    nano \
    # May be required if attaching devcontainer
    libnss-ldapd \
    && apt-get dist-clean 

# Install uv to allow setup-scratch to run
COPY --from=ghcr.io/astral-sh/uv:0.11 /uv /uvx /bin/

# For this pod to understand finding user information from LDAP
RUN sed -i 's/files/ldap files/g' /etc/nsswitch.conf

# Set the MPLCONFIGDIR environment variable to a temporary directory to avoid
# writing to the home directory. This is necessary because the home directory
# is read-only in the runtime container.
# https://matplotlib.org/stable/install/environment_variables_faq.html#envvar-MPLCONFIGDIR

ENV MPLCONFIGDIR=/tmp/matplotlib
RUN export DISPLAY=:0

# Copy the python installation from the build stage
COPY --from=build /python /python

# Copy the environment, but not the source code
COPY --chown=1000:1000 --from=build /app/.venv /app/.venv
RUN chmod -R 777 /app
ENV PATH=/app/.venv/bin:$PATH

# Add copy of source to container for debugging
WORKDIR /workspaces
COPY --chown=1000:1000 . pdfcurl
# Make allowance for non-1000 uid
RUN chmod o+wrX pdfcurl

# Make invariant symlink to site-packages for debugging
# /app/.venv/lib/python/site-packages/pdfcurl:/workspaces/pdfcurl
WORKDIR /app/.venv/lib
RUN ln -s python* python

# Switch user 1000
USER ubuntu

# change this entrypoint if it is not the same as the repo
ENTRYPOINT ["pdfcurl"]
CMD ["--version"]
