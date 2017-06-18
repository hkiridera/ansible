FROM jenkins:latest

USER root

RUN apt-get update && \
    apt-get upgrade && \
    apt-get install -y \
      build-essential \
      libssl-dev \
      libffi-dev \
      python-dev \
      sshpass \
      ruby \
      ruby-dev
# install ansible+winrm
RUN curl -sSL \
      https://bootstrap.pypa.io/get-pip.py \
    | python && \
    pip install \
      ansible \
      pywinrm
# install serverspec+winrm
RUN gem update && \
	gem install \
	  serverspec \
	  rake

USER jenkins
