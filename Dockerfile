FROM python:3.9

ENV PYTHONFAULTHANDLER=1
ENV PYTHONUNBUFFERED=1 
ENV PYTHONHASHSEED=random 
ENV PIP_NO_CACHE_DIR=off 
ENV PIP_DISABLE_PIP_VERSION_CHECK=on 
ENV PIP_DEFAULT_TIMEOUT=100 
ENV POETRY_VIRTUALENVS_CREATE=false
ENV PATH=$PATH:/root/.poetry/bin

WORKDIR /app

RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -

COPY poetry.lock pyproject.toml ./
COPY terra_ltv_bot ./terra_ltv_bot

RUN poetry install --no-dev --no-interaction


ENTRYPOINT [ "poetry", "run" ]
CMD [ "terra-ltv-bot" ]
