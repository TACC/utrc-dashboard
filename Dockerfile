FROM python:3.13-bookworm
RUN apt-get update && apt-get upgrade -y
COPY requirements.txt .
RUN pip install -r requirements.txt
WORKDIR /app
COPY . .
RUN chmod +rx ./app.py
ENV PATH="/app:$PATH"
ENV PORT=8050
EXPOSE 8050
ENTRYPOINT ["gunicorn", "-c", "gunicorn_conf.py", "app:server"]
