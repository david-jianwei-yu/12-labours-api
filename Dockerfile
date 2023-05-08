FROM python:3.9.0

WORKDIR /12-labours-api

COPY . .

RUN pip install --no-cache-dir --upgrade -r /12-labours-api/requirements.txt

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]