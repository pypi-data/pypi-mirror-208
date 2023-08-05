FROM python:3.10.1

RUN apt-get update \
    && apt-get install -y \
    dialog \
    apt-utils \
    locales \
    jq

RUN python -m pip install --upgrade setuptools

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

RUN python setup.py install

RUN sed -i -e 's/# es_AR.UTF-8 UTF-8/es_AR.UTF-8 UTF-8/' /etc/locale.gen && \
    locale-gen

ENV LANG es_AR.UTF-8
ENV LANGUAGE es_AR:es
ENV LC_ALL es_AR.UTF-8

ENV PATH="~/.local/bin/:${PATH}"

RUN rm -rf /var/www/html/* \
  && rm -rf /var/lib/apt/lists/*

COPY docker/scripts/* /opt/bin/

RUN chmod +x /opt/bin/*

WORKDIR /app

ENTRYPOINT ["stf"]