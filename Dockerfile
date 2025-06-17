FROM python:3.13.2

WORKDIR /usr/src/app

COPY requirments.txt ./

RUN pip install --no-cache-dir -r requirments.txt

COPY app ./app
COPY roamly_alembic ./roamly_alembic
COPY alembic.ini .

CMD [ "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000" ]