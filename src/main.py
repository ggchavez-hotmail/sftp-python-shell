import sh
from sh import sshpass
from storage_cloud import upload, download

import re

import os
import time


def sftp_transfer(username, password, host, port, local_file, remote_path, operation, bucket_name, bucket_file_path):
    try:
        # Medir el tiempo de inicio
        start_time = time.time()
        
        # Ejecutar el comando SFTP con sshpass usando la librería sh
        sftp_command = sshpass.bake(
            '-p', password, 
            'sftp', 
            '-v',
            '-oStrictHostKeyChecking=no',
            f'-oPort={port}',
            f'{username}@{host}')
        
        if operation == "put":
            # Descarga de Gcloud
            result_gcloud = download(file_path_local=local_file,file_path_cloud=bucket_file_path, bucket_name=bucket_name)
            
            if result_gcloud:
                # Ejecutar el comando 'put' para transferir el archivo
                result_sftp = sftp_command(_in=f'{operation} {local_file} {remote_path}\nbye\n', _err_to_out=True)
            else:
                # Captura de errores si el comando falla
                print("Error durante la ejecución del proceso GCLOUD")
                return False, 0, 0, 0
                
        elif operation == "get":
            # Ejecutar el comando 'get' para transferir el archivo
            result_sftp = sftp_command(_in=f'{operation} {remote_path} {local_file}\nbye\n', _err_to_out=True)
            
            # Subir a Gcloud
            result_gcloud = upload(file_path_local=local_file,file_path_cloud=bucket_file_path, bucket_name=bucket_name)
            if result_gcloud == False:
                # Captura de errores si el comando falla
                print("Error durante la ejecución del proceso GCLOUD")
                return False, 0, 0, 0
        else:
            # Captura de errores si el comando falla
            print("Operacion incorrecta")
            return False, 0, 0, 0
            
        # Verificar el resultado
        print(f"Operacion {operation} SFTP completada con exito")
    
        # Medir el tiempo de finalización
        end_time = time.time()
        
        # Calcular el tiempo total de transferencia
        total_time = end_time - start_time

        # Obtener el tamaño del archivo en bytes
        file_size = os.path.getsize(local_file)
            
        # Calcular el ancho de banda en Mbps
        bandwidth_mbps = (file_size * 8) / (total_time * 1024 * 1024)
        
        # Validar si la cantidad de datos transferidos es correcto
        chek_transfer = validar_log(result_sftp, file_size, operation)
        
        return chek_transfer, bandwidth_mbps, total_time, file_size
    except sh.ErrorReturnCode as e:
        # Captura de errores si el comando falla
        print("Error durante la ejecucion Shell proceso SFTP")
        print("Error:", e)
        print("Salida del error:", e.stdout.decode())
        return False, 0, 0, 0
    except Exception as e:
        # Captura de errores si el comando falla
        print("Excepcion durante la ejecucion del proceso SFTP")
        print("Error:", e)
        print("Salida del error:", e)
        return False, 0, 0, 0

def validar_log(log_data, file_size, operation):
    # Utiliza una expresión regular para encontrar los valores de "Transferred: sent" y "received"
    match = re.search(r'Transferred: sent (\d+), received (\d+)', log_data)
    validado = False
    if match:
        sent_bytes = match.group(1)
        received_bytes = match.group(2)
        print(f"Operation: {operation}")
        sbytes = int(sent_bytes)
        rbytes = int(received_bytes)
        print(f"Sent: {sbytes} bytes")
        print(f"Received: {rbytes} bytes")
        print(f"File_size: {file_size} bytes")
        
        if operation == "put":
            if sbytes >= file_size:            
                validado = True
        elif operation == "get":
            if rbytes >= file_size:
                validado = True
    else:
        print("No se encontraron los valores de transferencia.")
        
    return validado
        
# Parámetros de conexión
hostname    = os.environ["SFTPHOSTNAME"]
port        = int(os.environ["SFTPPORT"])
username    = os.environ["SFTPUSERNAME"]
password    = os.environ["SFTPPASSWORD"]
local_file  = os.environ["SFTPLOCALFILE"]
remote_path = os.environ["SFTPREMOTEPATH"]
operation   = os.environ["SFTPACTION"]
bucket_name   = os.environ["GCPBUCKET"]
bucket_file_path   = os.environ["GCPFILEPATH"]

# Llamar a la función de transferencia SFTP
termino_ok, bandwidth, total_time, file_size = sftp_transfer(username, password, hostname, port, local_file, remote_path, operation, bucket_name, bucket_file_path)
if termino_ok:
    print(f"Ancho de banda: {bandwidth:.2f} Mbps, se demoro {total_time} en tramitir {file_size}")
else:
    print(f"No se pudo trasmitir archivo")
