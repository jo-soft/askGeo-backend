FROM frolvlad/alpine-python3
ADD . /askGeo
WORKDIR /askGeo/
RUN pip install -r requirements.txt

