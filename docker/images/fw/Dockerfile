# Generic firewall container with iptables
FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install -y iproute2 iptables iptables-persistent && \
    rm -rf /var/lib/apt/lists/*

ENV COMPANY=ACME_CORP \
    ROLE=firewall \
    HOST_TYPE=FW

COPY start.sh /start.sh
RUN chmod +x /start.sh

CMD ["/start.sh"] 