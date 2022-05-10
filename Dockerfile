FROM python:3.8.6
WORKDIR /finance-bot
RUN apt update && apt install sqlite3
COPY ./requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD python finance_bot.py