# CNT-DMZ-DNS: BIND 9.11.5 vulnerable
FROM ubuntu:18.04

RUN apt-get update && \
    apt-get install -y bind9 && \
    rm -rf /var/lib/apt/lists/* && \
    mkdir -p /run/named /usr/share/dns && \
    touch /usr/share/dns/root.hints && \
    chown -R bind:bind /run/named /usr/share/dns

COPY named.conf /etc/bind/named.conf
RUN chmod 644 /etc/bind/named.conf && chown bind:bind /etc/bind/named.conf

ENV COMPANY=ACME_CORP \
    ROLE=dmz_dns \
    HOST_TYPE=CNT-DMZ-DNS

EXPOSE 53/udp 53/tcp

CMD ["/usr/sbin/named", "-g", "-u", "bind"]