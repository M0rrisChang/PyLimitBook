FROM python:3

WORKDIR /PyLimitBook

ADD . /PyLimitBook

RUN pip install --no-cache-dir -r requirements.txt




# Run app.py when the container launches
CMD ["python3", "./ba_server/bid_ask_server/manage.py", "runserver"]
