FROM ubuntu-test-stand
RUN date > date.txt  
CMD sh -c 'cat date.txt; date'  

