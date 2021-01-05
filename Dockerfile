FROM alpine:latest

RUN apk add python3 py3-dotenv py3-pip py3-multidict py3-yarl youtube-dl
RUN pip3 install discord.py

WORKDIR /GLOB
COPY . .

CMD ["python3", "bot.py"]
