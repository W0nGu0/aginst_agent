# CNT-SYSLOG: RSyslog vulnerable build (8.1901)
FROM ubuntu:18.04

RUN apt-get update \
    && apt-get install -y rsyslog \
    && rm -rf /var/lib/apt/lists/*

ENV COMPANY=ACME_CORP \
    ROLE=siem \
    HOST_TYPE=CNT-SYSLOG

COPY rsyslog.conf /etc/rsyslog.conf

EXPOSE 514/udp

CMD ["rsyslogd", "-n"] 