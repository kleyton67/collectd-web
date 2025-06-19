FROM python:3.10-slim

COPY . .

ENV TZ=America/Recife

RUN apt update && \
    apt-get install -y librrds-perl libjson-perl libhtml-parser-perl libcgi-pm-perl && \
    pip install --no-cache-dir -r requirements.txt && \
    apt-get install -y tzdata && \
    ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && \
    echo $TZ > /etc/timezone

EXPOSE 8888

CMD ["python", "run_w_fastapi.py"]