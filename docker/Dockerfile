FROM ubuntu:24.04 AS setup
  SHELL ["/bin/bash", "-c"]
  
  # Package Management
  ARG DEBIAN_FRONTEND=noninteractive
  RUN echo 'APT::Sandbox::Seccomp "true";' > '/etc/apt/apt.conf.d/40sandbox' &&\
    apt-get update &&\
    apt-get install --yes apt-transport-https &&\
    apt-get install --yes socat python3 &&\
    rm -rf /var/lib/apt/lists/*


FROM setup AS tester
  # Package Management
  RUN apt-get update &&\
  apt-get install --yes --no-install-recommends git pylint python3-bandit python3-pytest python3-psutil python3-pytest-mock &&\
  rm -rf /var/lib/apt/lists/*

  WORKDIR "/tmp/"
    # Project Clone
    RUN git clone "https://github.com/HenryRabelo/tcp-stack-demo.git"
    COPY tests/ /tmp/tcp-stack-demo/Stack/tests/

  WORKDIR "/tmp/tcp-stack-demo/Stack/"
    RUN pylint --disable=trailing-whitespace,invalid-name,consider-using-f-string,missing-function-docstring --fail-under=8.0 client.py server.py
    RUN bandit --skip B322 -lll client.py server.py
    RUN python3 -m pytest --capture=no tests/
    

FROM setup AS base
  WORKDIR "/tmp/"
    # File Management
    COPY health.sh /usr/local/bin/
    RUN chmod +x /usr/local/bin/health.sh
    # User Lockdown
    RUN usermod --shell "/sbin/nologin" --lock root


FROM base AS client
  LABEL name="pod-python-client" created-by="Henry Rabelo"
  WORKDIR "/home/ubuntu/"

    COPY --from=tester "/tmp/tcp-stack-demo/Stack/client.py" "/home/ubuntu/"

  ENTRYPOINT ["python3 /home/ubuntu/client.py"]


FROM base AS server
  LABEL name="pod-python-server" created-by="Henry Rabelo"
  WORKDIR "/home/ubuntu/"

    COPY --from=tester "/tmp/tcp-stack-demo/Stack/server.py" "/home/ubuntu/"

  ENTRYPOINT ["python3 /home/ubuntu/server.py"]
