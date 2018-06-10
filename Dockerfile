#
# DEPENDENCY IMAGE
#

FROM containers.dev.maio.me/sjohnson/containers/python:latest AS build
LABEL maintainer="Sean Johnson <pirogoeth@maio.me>"

WORKDIR /wheel
ADD ./requirements.txt /wheel
RUN apk add --no-cache build-base git libffi-dev libressl-dev python-dev && \
        pip wheel -r /wheel/requirements.txt && \
        rm -rf /wheel/requirements.txt

#
# APP IMAGE
#

FROM containers.dev.maio.me/sjohnson/containers/python:latest AS app

COPY --from=build /wheel /wheel

WORKDIR /app
ADD . /app
RUN pip install /wheel/*.whl && \
        pip install -e /app/

ENV DB_DIR="sqlite:///data/tubedlapi.db"

VOLUME /data
EXPOSE 5000
CMD ["tubedlapi"]
