FROM ekhurtado/smia:latest-alpine-base

COPY health_supervisor_launcher.py /
COPY internal_logic.py /
COPY utilities.py /

WORKDIR /

CMD ["python3", "-u", "health_supervisor_launcher.py"]
#CMD [ "tail", "-f", "/dev/null"]