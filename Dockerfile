FROM python:3.10-slim

WORKDIR /app

COPY ./ /app/src

RUN pip install -r requirements.txt

EXPOSE 8000

CMD ["fastapi", "run", "src"]