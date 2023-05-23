# computerfr33k/ruby-bionic:latest  
  
FROM ubuntu-test-stand
LABEL maintainer="Eric Pfeiffer <computerfreak@computerfr33k.com>"  
  
RUN apt-get update && apt-get install -y \  
curl \  
wget \  
ruby-full \  
&& rm -rf /var/lib/apt/lists/*  
  
CMD ["irb"]

