FROM ubuntu-test-stand
CMD ["bash", "-c", "read -t 1 stdin; echo $stdin"]  

