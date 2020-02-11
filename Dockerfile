FROM python:3.6

COPY ./requirements.txt /app/requirements.txt

WORKDIR /app

RUN pip install -r requirements.txt

COPY . /app

RUN python -m spacy download en_core_web_sm
RUN python train.py

ENTRYPOINT [ "python" ]

CMD [ "app.py" ]
