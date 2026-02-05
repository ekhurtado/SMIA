FROM ekhurtado/smia:latest-alpine-base

COPY neg_requester_starter.py /
COPY request_acl_neg_behaviour.py /
COPY receive_acl_neg_behaviour.py /

WORKDIR /

CMD ["python3", "-u", "neg_requester_starter.py"]
#CMD [ "tail", "-f", "/dev/null"]