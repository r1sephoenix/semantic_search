FROM python:3.9

WORKDIR /app

COPY requirements.txt .
COPY application.py .
COPY download_models.py .
COPY model_func.py .

RUN python3 -m venv .venv
ENV PATH="/app/.venv/bin:$PATH"

RUN pip install --no-cache-dir -r requirements.txt && \
    python3 download_models.py

COPY . .

EXPOSE 5000
CMD [ "python", "application.py"]