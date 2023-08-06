# **Automatización del Flujo de Trabajo sobre el Proyecto Final del curso de Introducción a los Mercados Bursátiles con la librería pyportfolioanalytics en Python**
#### **Realizado por Sebastian Marat Urdanegui Bisalaya**

<br>

<div style = "text-align:center">
    <img src = "https://img.shields.io/badge/Python-14354C?style=for-the-badge&logo=python&logoColor=white">
    <img src = "https://img.shields.io/badge/deployment-passing-brightgreen">
<div>

<div style = "text-align:left">
<div>
<br>
<img src = "./images/Black Elegant Photography Logo.png" width = "100%" height = "350px">
<br>
<br>

## **¿Qué te permite hacer la librería pyportfolioanalytics?**



<br>

## **¿Cuáles son los pasos que debo seguir para utilizar correctamente la librería?**

<br>

### **1. El camino más directo**
El camino más directo es usar la platforma Google Colab [Clic aquí para usar Google Colab](https://colab.research.google.com/). Google Colaboratory es un cuaderno de trabajo de Jupyter almacenado en la nube que te permite escribir código en Python y procesarlo de forma ágil. **Solo necesitas tener una cuenta de Google Gmail para acceder.**

Al hacer clic en el enlace, obtendrás como output el entorno de Google Colab:

<img src = "./images/introduce_google_colab.png" width = "100%" height = "70px">

Deberás hacer clic en el botón <span style = "color:orange">**Conectar**<span> <span style = "color:white">para encender la máquina virtual de Google Colaboratory y poder correr código Python.

Luego, en la primera línea de código es importante copiar y pegar el siguiente código para evitar inconvenientes entre dependencias. **(Control + Enter para correr el código de la celda)**
<br>

```python
!apt-get install -y python3-dev libffi-dev libcairo2-dev
```
Ahora, es hora de instalar la librería <span style = "color:orange">pyportfolioanalytics:<span> <span style = "color:white"><span>

```python
pip install pyportfolioanalytics==0.3.0
```

Por último, para iniciar a tirar código, debemos importar las librerías que serán necesarias para el trabajo a realizar:

```python
from pyportfolioanalytics.utils import stock_price_close
from pyportfolioanalytics.utils import return_daily
from pyportfolioanalytics.utils import covariance_matrix
from pyportfolioanalytics.utils import plot_price_close
from pyportfolioanalytics.utils import histogram_yield
from pyportfolioanalytics.utils import plot_yield_deviation_mean
from pyportfolioanalytics.utils import plot_cov_matrix
from pyportfolioanalytics.utils import plot_corr_matrix
from pyportfolioanalytics.utils import plot_logarithmic_yield
from pyportfolioanalytics.utils import BuySellStocks
from pyportfolioanalytics.utils import ReportFinancial
```
```python
import matplotlib.pyplot as plt
%matplotlib inline
```
**<span style="color:orange">¡Listo!<span> <span style="color:white">Tienes todo lo necesario para realizar un análisis financiero en Python<span>**

### **Caso 1: Obtener los precios de cierre de las acciones de Apple (AAPL), Amazon (AMZN), Netflix (NFLX), TESLA (TSLA), Google (GOOGL) y AIRBNB (ABNB) entre el periodo de 2022-01-01 y 2023-03-31**

```python
# Almacenar en una variable los datos que se obtendrán
dataframe_stock = stock_price_close(stock_list = ["AAPL", "AMZN", "NFLX", "TSLA", "GOOGL", "ABNB"], start = "2022-01-01", end = "2023-03-31")
```

### **Output Caso 1**

<div>
<img src = "./images/df.png" width = "100%" height = "350px">
<div>

### **Caso 2: Obtener un gráfico de la evolución de los precios de cierre de las acciones**

```python
# Retornará un gráfico de la evolución del precio de cierre en el periodo en cuestión
plot_price_close(["AAPL", "AMZN", "NFLX", "TSLA", "GOOGL", "ABNB"], "2022-01-01", "2023-03-31")
```

### **Output Caso 2**

<div>
<img src="./images/output2.png" width = "100%">
<div>

### **Caso 3: Obtener un gráfico del rendimiento de las acciones**

```python
plot_logarithmic_yield(["AAPL", "AMZN", "NFLX", "TSLA", "GOOGL", "ABNB"], "2022-01-01", "2023-03-31")
```

### **Output Caso 3**

<div>
<img src="./images/output3.png" width = "100%">
<div>

### **Caso 4: Obtener un histograma del rendimiento de las acciones**

```python
histogram_yield(["AAPL", "AMZN", "NFLX", "TSLA", "GOOGL", "ABNB"], "2022-01-01", "2023-03-31")
```

### **Output Caso 4**

<div>
<img src="./images/output4.png" width = "100%">
<div>

### **Caso 5: Obtener una matriz de correlación entre el rendimiento de las acciones**

```python
plot_corr_matrix(["AAPL", "AMZN", "NFLX", "TSLA", "GOOGL", "ABNB"], "2022-01-01", "2023-03-31")
```

### **Output Caso 5**

<div>
<img src = "./images/output5.png" width = "100%">
<div>

### **Caso 6: Obtener una matriz de varianza y covarianza entre el rendimiento de las acciones**

```python
plot_cov_matrix(["AAPL", "AMZN", "NFLX", "TSLA", "GOOGL", "ABNB"], "2022-01-01", "2023-03-31")
```

### **Output Caso 6**

<div>
<img src="./images/output6.png" width = "100%">
<div>

### **Caso 7: Presentar un reporte financiero con los insights más relevantes**

```python
# Este código se encarga de traer la instancia de la clase ReportFinancial con el objetivo de construir automáticamente un reporte financiero con los insights más relevantes
reporte = ReportFinancial(["AAPL", "AMZN", "NFLX", "TSLA", "GOOGL", "ABNB"], "2022-01-01", "2023-03-31", [0.2, 0.1, 0.1, 0.25, 0.25, 0.1], 100000, "Sebastian Marat Urdanegui Bisalaya")
reporte.report()
```

Luego de escribir el código en Google Colab para generar el reporte financiero, en la parte izquierda se almacenará el reporte en formato .pdf dentro de una carpeta llamada **pdfs** y dentro en la carpeta llamada **plots** podrás tener en formato .png todos los gráficos que se utilizaron en el reporte.

<div>
<img src="./images/df2.png" width = "100%">
<div>

### **!Listo! Ahora solo tienes que descargar tu reporte y presentarlo**

### **Ouput Caso 7**

<div>
<img src="./images/pdf1.png" width = "100%">
<div>

<div>
<img src="./images/pdf2.png" width = "100%">
<div>

<div>
<img src="./images/pdf3.png" width = "100%">
<div>
<br>

### **2. El camino complejo**

• Descargar un entorno de trabajo en local como **Visual Studio Code (VSC)** y/o **Jupyter Notebook**. Al descargar VSC, tendrás que instalar la extensión de Python y Jupyter. Para ello, debes decargar Python desde la página oficial de los desarrolladores [Descargar Python](https://www.python.org/) e instalarlo.

• También, recomiendo instalar CMDER para codificar en consola.
[Clic aquí para descargar CMDER como consola](https://cmder.app/)

• Luego, debes crear una carpeta en el cual almacenarás tu proyecto. Posteriormente, abrir CMDER y ubicarse en la carpeta del proyecto con el objetivo de crear un file **.ipynb**.

```cmder
touch analisis_financiero.ipynb
```
Desde la consola de CMDER, se puede escribir **code .** para abrir directamente el entorno de trabajo de Visual Studio Code.
```cmder
code .
```

**!Listo! Puedes instalar las librerías necesarias y escribir el código tal cual se explica desde el paso 1 del camino más directo.**











