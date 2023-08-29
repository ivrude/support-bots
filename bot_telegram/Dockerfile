FROM python:3.11.3
WORKDIR /app
COPY requirements/lint.txt requirements.txt
RUN pip install --upgrade setuptools
RUN pip install -r requirements.txt
COPY bot_telegram .
CMD ["python", "-m", "main"]

