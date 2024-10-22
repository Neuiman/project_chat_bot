FROM python:3.12.4

RUN mkdir /bot

WORKDIR /bot


COPY ../requirements.txt .

RUN pip install -r requirements.txt

COPY . .

RUN chmod a+x bot/start.sh
