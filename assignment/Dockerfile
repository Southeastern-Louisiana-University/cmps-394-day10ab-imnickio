FROM python:3.12-alpine
RUN apk update && apk upgrade
RUN apk add --no-cache gcc musl-dev mariadb-connector-c-dev
WORKDIR /app
RUN pip install --no-cache-dir --upgrade pip wheel setuptools
RUN pip install --no-cache-dir \
    fastapi \
    uvicorn \
    sqlalchemy \
    pymysql \
    cryptography \
    python-keycloak

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]