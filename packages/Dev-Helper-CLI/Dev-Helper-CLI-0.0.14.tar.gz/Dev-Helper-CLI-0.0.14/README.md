# Dev-Helper-2.0

En el mundo del desarrollo de software, es común tener que lidiar con una gran cantidad de comandos y scripts para ejecutar tareas específicas. Con el tiempo, puede volverse difícil administrar y recordar todos estos comandos. Aquí es donde entra en juego el programa que vamos a analizar, escrito en Python.

[Link de GitHub.](https://github.com/luigicfh/Dev-Helper-2.0)

## Descripción del programa

El programa es un administrador de comandos que permite agregar, eliminar, actualizar y ejecutar comandos de forma sencilla. Está diseñado para ayudar a los desarrolladores a organizar y ejecutar sus comandos de manera eficiente. Veamos cómo funciona.

## Estructura del programa

El programa consta de varios componentes, incluidos módulos y funciones auxiliares, para lograr su funcionalidad completa. A continuación, se muestra una descripción general de los componentes clave del programa:

### Backend

El programa utiliza un backend para gestionar una base de datos de documentos. La base de datos se implementa utilizando el archivo `db.json`, que contiene la información sobre los comandos y proyectos existentes. El módulo `document_db` se encarga de interactuar con la base de datos y proporciona métodos para agregar, eliminar y actualizar documentos.

### Validaciones

El programa cuenta con un conjunto de funciones de validación en el módulo `validations`. Estas funciones se utilizan para validar la entrada del usuario y asegurarse de que cumple con los requisitos necesarios para ejecutar ciertos comandos.

### Generación de comandos

La función `generate_new_command` se encarga de generar un nuevo comando con su nombre, descripción y el comando real que se ejecutará. Esta función se utiliza al agregar un nuevo comando al sistema.

### Análisis de argumentos

El programa utiliza el módulo `argparse` para analizar los argumentos de línea de comandos proporcionados por el usuario. Se definen varios argumentos, como el comando a ejecutar, el nombre de espacio, el proyecto, la descripción, el comando real y la pregunta. Estos argumentos se utilizan para determinar la acción que se debe realizar y los datos asociados a esa acción.

### Acciones principales

El programa define varias acciones principales que se pueden ejecutar. Estas acciones incluyen: listar comandos, agregar comando, eliminar comando, actualizar comando, ejecutar comando, configuración y cambio de proyecto activo. Cada acción se implementa como una rama condicional basada en el comando proporcionado por el usuario.

## Uso del programa

El programa se utiliza ejecutando el script principal a través de la línea de comandos. Los argumentos proporcionados determinarán la acción que se debe realizar. Aquí hay un resumen de las acciones principales y cómo se utilizan:

Instala el programa ejecutando:

```bash
pip install Dev-Helper-CLI
```

- **Listar comandos**: El comando `list` se utiliza para mostrar una lista de comandos almacenados en la base de datos. También se puede especificar un nombre de espacio y proyecto para mostrar comandos específicos.
    
    Listar todos los proyectos:
    
    ```bash
    dh list
    ```
    
    Listar comandos en un proyecto:
    
    ```bash
    dh list -n project_name
    ```
    
- **Agregar comando**: El comando `add` se utiliza para agregar un nuevo comando a la base de datos. Se deben proporcionar el nombre del proyecto, el nombre corto del comando, una descripción y el comando real que se ejecutará.
    
    Agregar un comando simple:
    
    ```bash
    dh add -p project_name -s shortcut_name -d description -c "command"
    ```
    
    Agregar secuencias de comandos:
    
    ```bash
    dh add -p project_name -s shortcut_name -d description -c "command1; command2; command3"
    ```
    
- **Eliminar comando**: El comando `delete` se utiliza para eliminar un comando existente de la base de datos. Se debe proporcionar el nombre del proyecto y el nombre corto del comando a eliminar.
    
    Borrar proyecto:
    
    ```bash
    dh delete -p project_name
    ```
    
    Borrar comando:
    
    ```bash
    dh delete -p project_name -s shortcut_name
    ```
    

- **Actualización de un comando**: el comando de `update` se utiliza para actualizar un comando existente en la base de datos. Se debe proporcionar el nombre del proyecto, el acceso directo del comando y el comando actualizado, la descripcion es opcional.
    
    Actualizar comando:
    
    ```bash
    dh update -p project_name -s shortcut_name -c command_name -d description
    ```
    
- **Ejecutar un comando**: El comando `run` se utiliza para ejecutar un comando específico. Se debe proporcionar el acceso directo del comando.
    
    Ejecutar un comando:
    
    ```bash
    dh run -s shortcut_name
    ```
    
    Si ningun proyecto esta activo se te pedira activar el proyecto correspondiente al comando que deseas ejecutar.
    
- **Configuración**: el comando `config` se usa para mostrar la configuración activa, que incluye el proyecto actualmente activo.
    
    ```bash
    dh config
    ```
    
- **Cambio de proyecto activo**: el comando de `switch` se utiliza para establecer la configuración activa en un proyecto específico. Se debe proporcionar el nombre del proyecto.
    
    ```bash
    dh switch -p project_name
    ```
    

Al usar estos comandos, los desarrolladores pueden administrar sus comandos de manera efectiva y optimizar su flujo de trabajo.