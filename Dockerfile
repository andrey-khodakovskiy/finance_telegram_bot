FROM python:3.8.6
WORKDIR /finance-bot
RUN apt update && apt install -y sqlite3
COPY ./requirements.txt .
RUN pip install -r requirements.txt
ENV BOT_TOKEN="<>"
ENV ADMINS="<>"
ENV SEASON_TOTAL="<>"
ENV SPENDINGS_TOTAL="<>"
COPY . .
CMD python finance_bot.py
