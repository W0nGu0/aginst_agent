# CNT-DMZ-Mailrelay: Postfix 3.3 vulnerable build
FROM debian:11-slim

RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y postfix && \
    rm -rf /var/lib/apt/lists/*

ENV COMPANY=ACME_CORP \
    ROLE=dmz_mail \
    HOST_TYPE=CNT-DMZ-MAILRELAY

EXPOSE 25

CMD ["/usr/sbin/postfix", "start-fg"] 