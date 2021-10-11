FROM python:3.9.7-bullseye
RUN pip install pandas openpyxl xlsxwriter meraki
RUN mkdir /script
COPY . /script/
WORKDIR /script/
RUN bash