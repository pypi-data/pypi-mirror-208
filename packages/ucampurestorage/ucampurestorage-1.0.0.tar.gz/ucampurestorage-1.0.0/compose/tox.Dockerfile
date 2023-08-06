FROM python
WORKDIR /app/
ADD requirements-dev.txt ./requirements-dev.txt
RUN pip install --upgrade pip && pip install --no-cache-dir -r ./requirements-dev.txt
VOLUME /app
