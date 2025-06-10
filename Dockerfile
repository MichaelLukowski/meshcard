ARG AZLINUX_BASE_VERSION=master

# Base stage with python-build-base
FROM quay.io/cdis/python-build-base:${AZLINUX_BASE_VERSION} AS base

ENV appname=cedar-wrapper-service
ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1

WORKDIR /src

# create gen3 user
# Create a group 'gen3' with GID 1000 and a user 'gen3' with UID 1000
RUN groupadd -g 1000 gen3 && \
    useradd -m -s /bin/bash -u 1000 -g gen3 gen3  && \
    chown -R gen3:gen3 /src && \
    chown -R gen3:gen3 /venv

# Builder stage
FROM base AS builder

RUN yum update && \
    yum install -y postgresql-libs gcc

USER gen3

RUN python -m venv /venv

COPY poetry.lock pyproject.toml README.md /src/

RUN pip install poetry && \
    poetry install -vv --only main --no-interaction --no-root

COPY --chown=gen3:gen3 main.py /src
COPY --chown=gen3:gen3 start.sh /src
COPY --chown=gen3:gen3 alembic.ini /src
COPY --chown=gen3:gen3 ./src /src/src
COPY --chown=gen3:gen3 ./deployment/wsgi/wsgi.py /src/deployment/wsgi/wsgi.py
COPY --chown=gen3:gen3 ./deployment/wsgi/gunicorn.conf.py /src/deployment/wsgi/gunicorn.conf.py


# Run poetry again so this app itself gets installed too
RUN poetry install --without dev --no-interaction

# Final stage
FROM base

COPY --from=builder /venv /venv
COPY --from=builder /src /src

# Switch to non-root user 'gen3' for the serving process
USER gen3

RUN source /venv/bin/activate

ENV PYTHONUNBUFFERED=1 \
    PYTHONIOENCODING=UTF-8

CMD [ "/bin/bash", "./start.sh" ]