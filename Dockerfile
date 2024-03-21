FROM python:3.12.2-slim

WORKDIR /app

COPY pyproject.toml /app/

RUN pip install poetry

RUN poetry config virtualenvs.create false

RUN poetry install --without tests,docs,dev --no-root

COPY . /app/

EXPOSE 8555

CMD ["task","run"]
