FROM python:3-bullseye

RUN apt-get update
RUN apt-get install -yq --no-install-recommends \ 
    python3-dev \ 
    default-libmysqlclient-dev \
    build-essential

WORKDIR /usr/src/zion

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
RUN useradd -r -s /usr/sbin/nologin zion

COPY . .
CMD ["python3","-m","zion.zionctl"]
# RUN chown -R zion:zion zion/logs
# RUN chown -R zion:zion zion/static/images

# CMD runuser - zion -s /bin/sh -c "python3 -m /usr/src/zion/zionctl"
