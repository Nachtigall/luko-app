FROM python:3.7-alpine
RUN pip install pipenv

WORKDIR /app

COPY ./Pipfile ./
COPY ./Pipfile.lock ./

RUN pipenv install --deploy --system

COPY . .
EXPOSE 5000

CMD ["flask", "run", "--host=0.0.0.0"]
