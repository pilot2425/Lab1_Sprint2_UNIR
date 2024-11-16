import base64
import logging
import os.path
import sys

from typing import List
from argparse import ArgumentParser, Namespace

import requests


def parse_args(args: List) -> Namespace:
   parser = ArgumentParser(description="Mi primer script")
   parser.add_argument('-n', '--count', type=int, required=True,default=10)
   parser.add_argument('-v', '--verbosity', action='count', default=0)
   return parser.parse_args(args)

def get_credenciales():
   user=input("Por favor ingrese su nombre de usuario").strip()
   psswd=input("Por favor ingrese su contraseña").strip()
   return user, psswd


def get_auth_response(username:str, password:str)->dict: #Envia la solicitud de autentificacion
   endpoint= f"https://httpbin.org/basic-auth/{username}/{password}"
   response=requests.get(endpoint, auth=(username,password))
   return response.json()


def configure_logger(verbosity_level: int):
   log_level= logging.WARNING - (10* verbosity_level)
   logging.basicConfig(level=log_level)
   logging.getLogger("urllib3.connectionpool").propagate=False

#def get_httpbin_data(username: str, password: str) -> dict:
  #endpoint = f"https://httpbin.org/basic-auth/{username}/{password}"
   #headers = {'Accept': 'application/json', 'Authorization': get_auth_header(username, password)}
   #response = requests.get(endpoint, headers=headers)
 #  if response.ok:
  #     return response.json()

   #raise RuntimeError("Unable to get response from server")
def menu_options(): #Esta funcion obtiene la eleccion del usuario y valida que es correcta antes de devolverla
   opcion_correcta=False
   print("-- Menú de Gestión de Tareas --")
   print("1. Agregar tarea")
   print("2. Listar tareas")
   print("3. Eliminar tarea")
   print("4. Salir")
   print("-- Menú de Gestión de Tareas --")
   while not opcion_correcta:
      eleccion=input("Seleccione una opcion (1-4)").strip()
      try:
         eleccion=int(eleccion)
         if eleccion>=1 and eleccion<=4:
            opcion_correcta=True
         else:
            print("Ha introducido una opción inválida")
      except ValueError:
         print("Ha introducido un valor no válido.")
   return eleccion

def agregar_tarea():
   ok=False #El usuario debe introducir una tarea
   while not ok:
      new_task=input("Ingrese el título de la tarea:").strip()
      if new_task=="":
         print("No se ha guardado la tarea ya que no ha introducido ninguna tarea")
      else:
         ok=True
   return new_task
def mostrar_tareas(tareas):
   if not tareas: #Si no hay tareas se comunica al usuario y se vuelve al menu
      print("No hay tareas")
   else:
      for tarea in tareas:
         print(f"Titulo: {tarea['titulo']} Estado: {tarea["estado"]}")
def buscar_tarea(tareas,titulo):
   pos=-1 #Se asigna -1 para indicar que no se ha encontrado de la tarea buscada, cambiara cuando se encuentre
   i=0 #contador
   for tarea in tareas:
      if tarea['titulo']==titulo:
         pos=i
         break
      else:
         pos=pos+1
   return pos

def borrar_tarea(tareas):
   if not tareas:
      print("No hay tareas")
   else:
      mostrar_tareas(tareas)
      task_del=input("Introduzca el titulo de la tarea que desea borrar").strip()
      pos=buscar_tarea(tareas,task_del)
      if pos==-1:
         print("No se ha encontrado ninguna tarea con dicho titulo")
      else:
         del tareas[pos]
         print("Tarea eliminada correctamente!")
   return tareas


def main(args: List):
   opcion=0 #Se inicializa la elección del usuario a 0 (opcion invalida) para que entre en el bucle correctamente y coja ya un valor válida
   tareas=[]
   logger = logging.getLogger(__name__)

   # Configuración del logger (por defecto no será muy detallado)
   configure_logger(verbosity_level=2)

   attempts = 0
   max_attempts = 3
   authenticated = False

   while attempts < max_attempts and not authenticated:
      # Pedir credenciales al usuario
      username, password = get_credenciales()

      # Verificar las credenciales con httpbin
      auth_response = get_auth_response(username, password)

      # Verificar si la autenticación fue exitosa
      if auth_response.get('authenticated', False):
         logger.info("Autenticación exitosa!")
         authenticated = True
      else:
         attempts += 1
         logger.error(f"Credenciales incorrectas. Intento {attempts}/{max_attempts}")

         if attempts >= max_attempts:
            logger.error("Número máximo de intentos alcanzado. Acceso denegado.")

   if authenticated:
      # Si la autenticación fue exitosa, continuar con la lógica posterior
      print("Acceso concedido. Bienvenido.")
      while(opcion !=4):
         opcion=menu_options()
         if opcion==1:
            new_task=agregar_tarea()
            tareas.append({"titulo":new_task, "estado": "pendiente"})
            print("Tarea añadida correctamente a la lista de tareas pendientes!!")
         elif opcion==2:
            mostrar_tareas(tareas)
         elif opcion==3:
            tareas=borrar_tarea(tareas)

   else:
      # Si no se logró autenticar en los intentos permitidos
      print("No se pudo autenticar después de 3 intentos. Adiós.")


if __name__ == '__main__':
   main(sys.argv[1:])