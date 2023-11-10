FROM openjdk:17-slim

RUN apt-get update && \
    apt-get install -y ant && \
    apt-get install -y maven && \
    apt-get clean;

    
RUN mvn -version

CMD ["bash"]