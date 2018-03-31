#
# DEPENDENCY IMAGE
#

FROM python:3.6-alpine AS build
LABEL maintainer="Sean Johnson <pirogoeth@maio.me>"

WORKDIR /wheel
ADD ./requirements.txt /wheel
RUN apk add --no-cache build-base git libffi-dev openssl-dev python-dev && \
        pip wheel -r /wheel/requirements.txt && \
        rm -rf /wheel/requirements.txt

#
# APP IMAGE
#

FROM python:3.6-alpine AS app

COPY --from=build /wheel /wheel

WORKDIR /app
ADD . /app
RUN pip install /wheel/*.whl && \
        pip install -e /app/

ENV DB_DIR="sqlite:///data/tubedlapi.db"

VOLUME /data
EXPOSE 5000
CMD ["tubedlapi"]
