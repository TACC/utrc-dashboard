FROM python:3.11-slim

RUN apt-get update && apt-get upgrade -y

COPY requirements.txt .

RUN pip install -r requirements.txt

WORKDIR /app

EXPOSE 8050

COPY . .

CMD ["python", "app.py"]
