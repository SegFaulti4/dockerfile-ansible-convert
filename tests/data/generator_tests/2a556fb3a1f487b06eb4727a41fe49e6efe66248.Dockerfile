FROM ubuntu-test-stand

CMD while true; do sleep 2 ; echo "{\"app\": \"dummy\", \"foo\": \"bar\"}"; done