# SPDX-License-Identifier: LicenseRef-DSA-EOL-1.0
# Copyright (c) 2025 José Fandos. All Rights Reserved.

"""
Doitective — source-available (evaluation-only).
See LICENSE.txt for terms and contact for any permission beyond viewing.
"""
#e_mail_validation.py





## CURRENTLY NOT CONECTED ##





import re
import smtplib
from email.mime.text import MIMEText

def validate_email_format(email):
  """
  Valida el formato de una dirección de correo electrónico utilizando una expresión regular.

  Args:
    email: La dirección de correo electrónico a validar.

  Returns:
    True si el formato es válido, False en caso contrario.
  """
  regex = r"^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$"
  return bool(re.match(regex, email))

def validate_email_existence(email):
    """
    Valida la existencia de un correo electrónico verificando el servidor SMTP.
    **ADVERTENCIA: Esta función puede ser lenta y generar tráfico en servidores SMTP,
    se recomienda usarla con precaución para validación masiva.**

    Args:
      email: La dirección de correo electrónico a validar.

    Returns:
      True si el correo electrónico parece válido, False en caso contrario.
    """
    try:
        # Divide el email en nombre de usuario y dominio
        nombre_usuario, dominio = email.split('@', 1)

        # Intenta conectar con el servidor SMTP del dominio
        smtp_server = smtplib.SMTP(f'smtp.{dominio}', 25)  # Puerto estándar
        smtp_server.ehlo()  # Inicia la conversación con el servidor

        # Intenta establecer la conexión con el servidor
        smtp_server.close()
        return True  # Si no hubo error, el dominio parece existir
    except (smtplib.SMTPConnectError, smtplib.SMTPHeloError, smtplib.SMTPServerDisconnected, Exception) as e:
        print(f"Error al validar {email}: {e}")
        return False  # Si hay error, el dominio podría no existir o haber problemas de conexión

def verify_email(email):
    """
    Verifica si un email tiene un formato válido y si parece existir.

    Args:
      email: La dirección de correo electrónico a validar.

    Returns:
      Una tupla con dos valores booleanos: (formato_valido, existencia_valida)
    """
    formato_valido = validate_email_format(email)
    # Existencia solo se valida si el formato es válido
    if formato_valido:
      #existencia_valida = validar_existencia_email(email)
      existencia_valida = True # Se comenta la validación de existencia por ser delicada
    else:
        existencia_valida = False
    return formato_valido, existencia_valida


def read_or_create_file(nombre_archivo, modo="r"):
  """
  Lee un archivo o lo crea si no existe.
  Args:
    nombre_archivo: El nombre del archivo a leer o crear.
    modo: El modo de apertura del archivo (por defecto "r" para lectura).
  Returns:
    El archivo abierto en el modo especificado, o None si ocurre un error.
  """
  try:
    archivo = open(nombre_archivo, modo)
    return archivo
  except FileNotFoundError:
    print(f"El archivo '{nombre_archivo}' no existe. Creándolo...")
    try:
        archivo = open(nombre_archivo, "w") # Crea el archivo en modo escritura
        return archivo
    except Exception as e:
        print(f"Error al crear el archivo: {e}")
        return None
  except Exception as e:
    print(f"Error al abrir el archivo: {e}")
    return None


def fetch_variable_in_txt(archivo_path, variable):
    txt_path = 'user_settings.txt'
    try:
        with open(archivo_path, 'r') as archivo:
            for linea in archivo:
                if variable in linea:
                    # Supongamos que la variable y su valor están separados por '='
                    partes = linea.strip().split('=')
                    if len(partes) == 2:
                        return partes[1].strip()  # Devuelve el valor
                    else:
                        return None # Si no hay valor
        return None  # Variable no encontrada
    except FileNotFoundError:
        print(f"Error: Archivo no encontrado en {archivo_path}")
        return None
    except Exception as e:
        print(f"Ocurrió un error: {e}")
        return None


# Ejemplo de uso:

#txt_key = 'mailto'
#txt_value = fetch_variable_in_txt(txt_path, txt_key)

#if txt_value:
  #  print(f"El valor de '{txt_key}' es: {txt_value}")
#else:
  #  print(f"La variable '{txt_key}' no fue encontrada en el archivo.")

    
#mailto_txt = read_or_create_file('user_settings.txt')
#archivo_abierto = read_or_create_file(mailto_txt)

#if archivo_abierto:
 #   try:
  #    if 'r' in archivo_abierto.mode:  # Verifica si el archivo se abrió para lectura
   #     contenido = archivo_abierto.read()
   #     print("Contenido del archivo:")
    #    print(contenido)
    #  else:
 #       print(f"El archivo se creó y está abierto en modo: {archivo_abierto.mode}")

#   except Exception as e:
  #      print(f"Error al leer el archivo: {e}")
#    finally:
 #       archivo_abierto.close()

        
def buscar_variable_en_txt(archivo_path, variable):

    try:
        with open(archivo_path, 'r') as archivo:
            for linea in archivo:
                if variable in linea:
                    # Supongamos que la variable y su valor están separados por '='
                    partes = linea.strip().split('=')
                    if len(partes) == 2:
                        return partes[1].strip()  # Devuelve el valor
                    else:
                        return None # Si no hay valor
        return None  # Variable no encontrada
    except FileNotFoundError:
        print(f"Error: Archivo no encontrado en {archivo_path}")
        return None
    except Exception as e:
        print(f"Ocurrió un error: {e}")
        return None
    

def valid_print_e_mail (email):

  is_e_valid, is_e_real = verify_email(email)

  if is_e_valid:
      print(f"El formato de {email} es válido.")
      if is_e_real:
          print(f"La dirección {email} existe.")
          return True
      else:
          print(f"La dirección {email} parece no existir o hay problemas de conexión con el servidor.")
          return False
  else:
      print(f"El formato de {email} no es válido.")
      return False