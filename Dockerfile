FROM nardeas/tensorflow-syntaxnet

# Clean up stuff we don't need
RUN rm -rf /usr/lib/python2.7/site-packages/dragnn/wrapper

# Get API running
ADD api /opt/api

RUN pip install -U -r /opt/api/requirements.txt --disable-pip-version-check

WORKDIR /opt/api/

ENTRYPOINT ["gunicorn", "-b", "0.0.0.0:80", "server:app"]
