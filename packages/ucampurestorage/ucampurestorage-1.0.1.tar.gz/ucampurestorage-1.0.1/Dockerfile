FROM python
RUN pip3 install pytest
RUN mkdir /myapp
COPY ./ /myapp
CMD /usr/local/bin/pytest /myapp -s -v
