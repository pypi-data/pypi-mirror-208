# Creates a ray docker image with Java on it.
# And also contains the fat .jar of the application.

FROM anyscale/ray:1.12.1-cu102

# Copy the txp wheel from local dir
COPY txp-0.1.72-py3-none-any.whl /home/ray

#
RUN pip install /home/ray/txp-0.1.72-py3-none-any.whl

ENTRYPOINT /bin/bash
