FROM python:alpine AS builder

RUN apk add gcc make musl-dev libffi-dev

WORKDIR /GLOB
COPY . .

RUN python3 -m venv env
RUN source env/bin/activate && pip3 install -r requirements.txt


FROM python:alpine AS runner
RUN apk add ffmpeg

COPY --from=builder /GLOB /GLOB
WORKDIR /GLOB

CMD ["sh", "-c", "source env/bin/activate && python3 bot.py"]
