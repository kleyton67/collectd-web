FROM python:3.10-slim

COPY . .

RUN apt update && \
apt-get install -y librrds-perl libjson-perl libhtml-parser-perl libcgi-pm-perl && \
pip install --no-cache-dir -r requirements.txt

EXPOSE 8888

CMD ["python", "run_w_fastapi.py"]