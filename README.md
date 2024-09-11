# sftp-python-shell #

## Problema ##

Se requiere crear procesos automatizados en GCP Cloud Run que sincronicen dos servidores SFTP ubicados fuera del entorno de la nube, de los cuales no se tiene conocimiento detallado sobre su configuración interna. Adicionalmente, se debe respaldar el trafico en Bucket GCP.

Se realizaron pruebas en Python utilizando las bibliotecas `paramiko` y `pysftp` para conectar con los servidores SFTP, mientras que para la conexión con el bucket se implementó el montaje nativo que ofrece Cloud Run. La configuración del entorno se estableció con 512 MB de memoria RAM, 1 CORE, y un tiempo de espera de 10 minutos.

Para archivos menores a 100 MB, aunque los tiempos de transferencia SFTP son elevados, se consideran aceptables, con una media de 1 minuto por archivo. Sin embargo, el problema surge al manejar archivos de mayor tamaño, particularmente aquellos de 2.8 GB.

Los inconvenientes observados son los siguientes:

- Uso de memoria: La memoria asignada en Cloud Run se emplea para:

  - La RAM del contenedor.
  - El almacenamiento temporal del contenedor. Si un archivo de 2.8 GB se guarda temporalmente, se necesita suficiente memoria en la configuración de Cloud Run.
  - El montaje del bucket. La documentación oficial señala que el uso de archivos en el bucket requiere memoria del entorno de Cloud Run, pero no se especifica claramente cuánto se consume. Además, como no es posible montar solo una carpeta, sino todo el bucket, creemos que el uso de memoria adicional varía según la cantidad de archivos y carpetas presentes en el bucket.

- Desempeño de las bibliotecas SFTP: Debido a la falta de control sobre la configuración de los servidores SFTP, se ha observado que paramiko y pysftp no funcionan de manera óptima en todos los casos. Algunas operaciones de GET/PUT de archivos de 2.8 GB tardan entre 45 minutos y 4 horas, lo que hace inviable la solución. Esto resulta en errores de tiempo de espera y problemas de espacio en el montaje de GCSFuse.

## Enfoque de Solución ##

Para abordar los problemas de conexión a los servidores SFTP:

- Se realizaron pruebas de transferencia SFTP desde la terminal, obteniendo tiempos de entre 5 y 15 minutos para el mismo archivo de 2.8 GB, lo que descarta problemas relacionados con la red.
- Se intentó ajustar los parámetros WINSIZE y MAXPACKETSIZE de paramiko, pero los resultados no fueron satisfactorios.
- Finalmente, se decidió utilizar el cliente SFTP del sistema operativo. Se probó con el método "subprocess" (ver old/main.subprocess.py), pero se optó por la biblioteca "sh", que ofrece una configuración más natural.

Para solucionar los problemas de memoria:

- Se empleó la biblioteca google-cloud-storage para realizar operaciones específicas sin necesidad de montar todo el bucket.
- Se incrementó la memoria asignada de 512 MB a 4 GB.
- Para evitar problemas de tiempo de espera, se extendió el parámetro de timeout a 50 minutos en Cloud Run.

## Instalación ##

Ejecutar comando para levantar ambiente python

```shell
pipenv shell
```

## Configurar variables ambiente ##

Crear variables ambiente

```shell
export SFTPHOSTNAME=192.168.1.1
export SFTPPORT=22
export SFTPUSERNAME=test
export SFTPPASSWORD=test
export SFTPLOCALFILE=/home/test/archivo.txt
export SFTPREMOTEPATH=/home/test/archivo.txt
export SFTPACTION=put #get/put
export GCPBUCKET=bucket-xxx #nombre del bucket en GCP
export GCPFILEPATH=ubicacion/archivo.txt #el path no debe contener el backslash inicial
export SERVICE_ACCOUNT=/tmp/service-acount.json #service account
```

## Ejecución ##

Ejecutar directamente

```shell
python src/main.py
```

Ejecutar docker

```shell
#construir imagen
docker build --pull --rm -f "Dockerfile" -t sftp_python_shell:latest "sftp_python_shell"

#ejecutar imagen
docker run --rm --name sftp_python_shell_test -e SFTPHOSTNAME=192.168.1.1 -e SFTPPORT=22 -e SFTPUSERNAME=test -e SFTPPASSWORD=test -e SFTPLOCALFILE=/home/test/archivo.txt -e SFTPREMOTEPATH=/home/test/archivo.txt -e SFTPACTION=put -e GCPBUCKET=bucket-xxx -e GCPFILEPATH=ubicacion/archivo.txt -e SERVICE_ACCOUNT=/tmp/service-acount.json sftp_python_shell:latest

#ver log
docker logs -f sftp_python_shell_test
```
