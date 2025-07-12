# CNT-FILES: Vulnerable Apache + PHP file server
FROM php:5.6-apache

ENV COMPANY=ACME_CORP \
    ROLE=fileserver \
    HOST_TYPE=CNT-FILES

# ===== 将易受攻击的上传脚本复制到站点根目录 =====
COPY vulnerable_upload /var/www/html/

EXPOSE 80 