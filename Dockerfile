FROM python

COPY . /api

WORKDIR /api

RUN pip install -r requirements.txt


ENTRYPOINT ["python", "./run.py"]
