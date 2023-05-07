FROM ubuntu-test-stand

EXPOSE 6543 8010

CMD /data/tty_server --sender_address :6543 --web_address localhost:8010 -url https://tty-share.elisescu.com
