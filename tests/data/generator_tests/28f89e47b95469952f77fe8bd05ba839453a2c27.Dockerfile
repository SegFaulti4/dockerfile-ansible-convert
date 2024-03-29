# docker build -t yandex/clickhouse-test-old-ubuntu .
FROM ubuntu-test-stand

CMD /bin/sh -c "/clickhouse server --config /config/config.xml > /var/log/clickhouse-server/stderr.log 2>&1 & \
    sleep 5 && /clickhouse client --query \"select 'OK'\" 2> /var/log/clickhouse-server/clientstderr.log || echo 'FAIL'"
