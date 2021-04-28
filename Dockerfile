FROM alpine:latest AS builder

RUN apk add python3 py3-pip py3-virtualenv gcc make musl-dev python3-dev libffi-dev

WORKDIR /GLOB
COPY . .

RUN python3 -m venv env
RUN source env/bin/activate && pip3 install -r requirements.txt


FROM alpine:latest
RUN apk add python3 py3-virtualenv ffmpeg

COPY --from=builder /GLOB /GLOB
WORKDIR /GLOB

CMD ["sh", "-c", "source env/bin/activate && python3 bot.py"]
