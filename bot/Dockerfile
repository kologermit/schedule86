FROM python:latest

COPY ./requirements.txt ./requirements.txt
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

WORKDIR /code/

CMD ["python", "main.py"]