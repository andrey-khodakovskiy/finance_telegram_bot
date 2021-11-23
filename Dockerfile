FROM python:3.8.6
WORKDIR /finance-bot
COPY . .
RUN pip install -r requirements.txt
RUN apt update && apt install sqlite3
CMD python finance_bot.py