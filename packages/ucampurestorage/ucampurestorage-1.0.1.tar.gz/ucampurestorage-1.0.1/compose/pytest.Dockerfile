FROM python
RUN mkdir /myapp
COPY ./ /myapp
RUN pip install --upgrade pip && pip install --no-cache-dir -r /myapp/requirements-dev.txt
CMD /usr/local/bin/pytest /myapp -s -v
