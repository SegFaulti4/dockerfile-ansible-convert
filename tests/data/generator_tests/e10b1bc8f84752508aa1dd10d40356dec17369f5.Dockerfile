FROM ubuntu-test-stand
  
RUN apt-get update \  
&& apt-get install -y jq \  
&& apt-get autoremove  
  
ENTRYPOINT ["jq"]  
  
CMD [""]

