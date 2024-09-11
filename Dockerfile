FROM python:3.11-slim

# Instalar openssh-client y sshpass
RUN apt-get update && \
    apt-get install -y openssh-client sshpass

WORKDIR /app

ADD requirements.txt .
RUN pip install -r requirements.txt

ADD src/. .

ENV SFTPHOSTNAME=VALUE
ENV SFTPPORT=VALUE
ENV SFTPUSERNAME=VALUE
ENV SFTPPASSWORD=VALUE
ENV SFTPLOCALFILE=VALUE
ENV SFTPREMOTEPATH=VALUE
ENV SFTPACTION=VALUE
ENV GCPBUCKET=VALUE
ENV GCPFILEPATH=VALUE
ENV SERVICE_ACCOUNT=VALUE

#Comando para ejecutar proceso principal
CMD ["python", "main.py"]