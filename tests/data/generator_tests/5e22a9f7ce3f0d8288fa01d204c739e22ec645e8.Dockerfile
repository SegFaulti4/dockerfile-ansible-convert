FROM ubuntu-test-stand

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    ca-certificates \
    libc6-dev \
    gcc-powerpc64-linux-gnu \
    libc6-dev-ppc64-cross \
    qemu-user  \
    qemu-system-ppc

ENV CARGO_TARGET_POWERPC64_UNKNOWN_LINUX_GNU_LINKER=powerpc64-linux-gnu-gcc \
    # TODO: should actually run these tests
    #CARGO_TARGET_POWERPC64_UNKNOWN_LINUX_GNU_RUNNER="qemu-ppc64 -L /usr/powerpc64-linux-gnu" \
    CARGO_TARGET_POWERPC64_UNKNOWN_LINUX_GNU_RUNNER=true \
    CC=powerpc64-linux-gnu-gcc
