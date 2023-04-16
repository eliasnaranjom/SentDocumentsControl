# Script de Python para agregar código identificador de documentos y código de barras

Este script de Python es útil para llevar el control de los documentos enviados en una oficina o entidad. El script recibe un documento en formato PDF y agrega un código identificador del documento y un código de barras en su primera página.

Actualmente funciona al pasarle en el codigo el nombre del documento y el 

## Requisitos

Para ejecutar este script, necesita tener instalado Python en su sistema. Además, deberá instalar las siguientes bibliotecas:

- PyPDF2
- reportlab
- cvs

Puede instalar estas bibliotecas mediante el siguiente comando:

`pip install -r requirements.txt`

## Uso

Para utilizar este script, simplemente ejecute el archivo main.py y proporcione el nombre del archivo PDF al que desea agregar el código identificador y el código de barras.

El código identificador se genera automáticamente y se agrega a la primera página del documento junto con el código de barras.

El código de barras se genera utilizando el módulo reportlab y se agrega en la primera página del documento.

El documento de salida se guarda con el nombre del identificador en la carpeta **SentDocuments**.

**Nota:** El listado todos los archivos procesados se guardaran en el archivo *logs.csv*.

Actualmente está lista la generación del codigo identificador de cada documento asi como el codigo de barras, se debe pasar el nombre del documento a procesar y establecer el formato codigo identificador, en posteriores commits se trabajara en una interface grafica para usar el script.

## Ejemplo

Supongamos que tiene un archivo PDF llamado archivo.pdf que desea procesar. Para agregar el código identificador y el código de barras, ejecute el siguiente comando:

`python main.py`

El script procesará el archivo archivo.pdf y generará un archivo de salida en la carpeta **SentDocuments** llamado *001.pdf* (suponiendo que sea el codigo identificador establecido) que contendrá el código identificador y el código de barras en la esquina superior derecha de la primera página.