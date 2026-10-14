# Consulta de novedades

Web local en español para preguntar sobre documentos Word de una carpeta y consultar los fragmentos que sustentan las respuestas. Usa Python y Ollama; no requiere paquetes Python ni clave de API. Los documentos se leen en cada consulta, sin modificarlos ni copiarlos al repositorio.

## Ejecutar en Windows

1. Instala Python 3.10 o superior desde https://www.python.org/downloads/ y Ollama desde https://ollama.com/download/windows.
2. Abre Ollama y ejecuta en PowerShell: `ollama pull llama3.2`. La descarga requiere Internet y varios GB libres. La velocidad de respuesta depende de la RAM y del hardware de tu PC.
3. Descarga este proyecto y ejecuta `start.bat`, o abre PowerShell en su carpeta y ejecuta `py -3 app.py`.
4. Abre `http://127.0.0.1:8000` en tu navegador. Comprueba los documentos disponibles y escribe una pregunta.

Carpeta predeterminada: `C:\Users\corebi\Desktop\CoreBI\FORECAST NOVEDADES`. Incluye subcarpetas. El proceso debe ejecutarse en la PC donde existe esa carpeta; una máquina en la nube no puede leerla directamente.

Para cambiar la carpeta o el modelo, antes de iniciar:

```powershell
$env:DOCUMENTS_PATH = 'D:\Otra carpeta'
$env:OLLAMA_MODEL = 'llama3.2'
py -3 app.py
```

La web y Ollama deben permanecer ejecutándose. Cierra la web con Ctrl+C en la terminal. Para comprobar Ollama: `ollama list`. Si cambias el modelo, descárgalo primero con `ollama pull NOMBRE`.

## Alcance

- Lee texto y tablas del cuerpo principal de `.docx`. Omite imágenes, encabezados, pies y documentos cifrados. Para `.doc` antiguo, abre el documento en Word y guarda una copia `.docx`.
- Recupera hasta ocho fragmentos mediante búsqueda por palabras y genera una respuesta con citas. No garantiza encontrar conceptos expresados con sinónimos ni resumir todos los documentos. Pregunta por nombres y términos concretos; verifica las fuentes y los posibles errores del modelo.
- Por defecto procesa contenido con Ollama local. No envía documentos a una API externa. `OLLAMA_URL` permite configurar otro servidor: si lo cambias, los fragmentos se enviarán allí.
- Escucha únicamente en la interfaz local. No está diseñada para publicarse en Internet.

## Validación

```powershell
py -3 -m unittest discover -s tests -v
```

Las pruebas usan documentos sintéticos y un servidor Ollama simulado, sin leer tus archivos. La respuesta real requiere un modelo instalado y debe verificarse en tu PC.
