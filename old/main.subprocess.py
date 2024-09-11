import subprocess
import os
import time

def sftp_transfer(username, password, host, port, local_file, remote_path):
    # Comando SFTP usando sshpass
    sftp_command = [
        'sshpass', 
        '-p', password, 
        'sftp',
        '-o', 'StrictHostKeyChecking=no',
        f'-oPort={port}',
        f'{username}@{host}'
    ]
    
    # Medir el tiempo de inicio
    start_time = time.time()
    
    termino_correctamente = False
    
    try:
        

        # Ejecutar el comando SFTP usando subprocess
        with subprocess.Popen(sftp_command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE) as process:
            # Enviar el archivo local al servidor SFTP
            sftp_input = f'put {local_file} {remote_path} \nbye\n'.encode('utf-8')
            stdout, stderr = process.communicate(input=sftp_input)
            
            # Verificar el resultado del proceso
            if process.returncode == 0:
                print("Transferencia SFTP completada con éxito")
                print("Salida del comando:", stdout.decode())
                termino_correctamente = True
            else:
                print("Error durante la transferencia SFTP")
                print("Error:", stderr.decode())
                
    except Exception as e:
        print(f"Error al ejecutar el proceso SFTP: {e}")
    
    # Medir el tiempo de finalización
    end_time = time.time()
    
    # Calcular el tiempo total de transferencia
    total_time = end_time - start_time

    # Obtener el tamaño del archivo en bytes
    file_size = os.path.getsize(local_file)

    # Calcular el ancho de banda en Mbps
    bandwidth_mbps = (file_size * 8) / (total_time * 1024 * 1024)
    
    return termino_correctamente, bandwidth_mbps, total_time, file_size


# Parámetros de conexión
hostname    = os.environ["SFTPHOSTNAME"]
port        = int(os.environ["SFTPPORT"])
username    = os.environ["SFTPUSERNAME"]
password    = os.environ["SFTPPASSWORD"]
local_file  = os.environ["SFTPLOCALFILE"]
remote_path = os.environ["SFTPREMOTEPATH"]

# Llamar a la función de transferencia SFTP
termino_correctamente, bandwidth, total_time, file_size = sftp_transfer(username, password, hostname, port, local_file, remote_path)
if termino_correctamente:
    print(f"Ancho de banda de subida: {bandwidth:.2f} Mbps, se demoro {total_time} en transmitir {file_size}")
else:
    print(f"No se pudo trasmitir archivo")
