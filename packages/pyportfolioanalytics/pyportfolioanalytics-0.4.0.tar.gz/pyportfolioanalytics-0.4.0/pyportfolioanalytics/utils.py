import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
import seaborn as sns
import math
import os
# import plotly
# import plotly.graph_objects as go

from reportlab.lib.pagesizes import A4, inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageTemplate, Frame
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.lib.utils import ImageReader

# Funciones para realizar solo el análisis finaniero
def stock_price_close(stock_list, start = '2022-01-01', end = '2023-01-01'):
    stock_dataframe = pd.DataFrame()
    for stock in stock_list:
        data = yf.download(stock, start = start, end = end, progress = False)
        stock_dataframe[stock] = data["Close"]
    return stock_dataframe

def get_name_columns(stock_list, start = '2022-01-01', end = '2023-01-01'):
    stock_dataframe = pd.DataFrame()
    for stock in stock_list:
        data = yf.download(stock, start = start, end = end, progress = False)
        stock_dataframe[stock] = data["Close"]
    columnas = ", ".join(stock_dataframe.columns)
    return columnas

def get_date_start(stock_list, start = '2022-01-01', end = '2023-01-01'):
    stock_dataframe = pd.DataFrame()
    for stock in stock_list:
        data = yf.download(stock, start = start, end = end, progress = False)
        stock_dataframe[stock] = data["Close"]
    start = stock_dataframe.index[0].strftime(format = "%Y-%m-%d")
    return start

def get_date_end(stock_list, start = '2022-01-01', end = '2023-01-01'):
    stock_dataframe = pd.DataFrame()
    for stock in stock_list:
        data = yf.download(stock, start = start, end = end, progress = False)
        stock_dataframe[stock] = data["Close"]
    end = start = stock_dataframe.index[-1].strftime(format = "%Y-%m-%d")
    return end

def return_daily(list_stock, start = '2022-01-01', end = '2023-01-01'):
    stocks = stock_price_close(list_stock, start = start, end = end)
    log_returns = np.log(stocks / stocks.shift(1))
    log_returns = log_returns.dropna()
    return log_returns

def covariance_matrix(list_stock, start = '2022-01-01', end = '2023-01-01'):
    returns_data = return_daily(list_stock, start = start, end = end)
    covmatrix = returns_data.cov()
    return covmatrix

def return_positive_negative(value):
    value = float(value)
    if value < 0:
        return 'pérdida'
    elif value >= 0:
        return 'ganancia'
    
# Funciones para graficar el análisis financiero y mostrar en el IDE 
# no almacenarlo en directorio
def plot_price_close(stock_list, start = '2022-01-01', end = '2023-01-01'):
    stock_dataframe = stock_price_close(stock_list=stock_list, start=start, end=end)
    orange_color = sns.color_palette("YlOrBr", as_cmap = False, n_colors=5)
    sns.set_palette(orange_color)
    fig, ax = plt.subplots(figsize = (8,6), dpi = 80)
    stock_dataframe.plot(ax = ax)
    plt.legend()
    plt.title("Evolución del precio de cierre de las acciones", size = 15)
    plt.xlabel("Fecha")
    plt.ylabel("Precio de las acciones")
    for i in ['bottom', 'left']:
        ax.spines[i].set_color('black')
        ax.spines[i].set_linewidth(1.5) 
    right_side = ax.spines["right"]
    right_side.set_visible(False)
    top_side = ax.spines["top"]
    top_side.set_visible(False)
    ax.set_axisbelow(True)
    ax.grid(color='gray', linewidth=1, axis='y', alpha=0.4)
    plt.show()
    


def histogram_yield(list_stocks, start = '2022-01-01', end = '2023-01-01'):
    return_stock = return_daily(list_stock = list_stocks, start = start, end = end)
    red_color = sns.cubehelix_palette(start=2,rot=0, dark=0, light=.95)
    sns.set_palette(red_color)
    fig, ax = plt.subplots(figsize = (8,6), dpi = 80)
    for i in return_stock.columns.values:
        plt.hist(return_stock[i], label = i, bins = 100)
    plt.legend()
    for i in ['bottom', 'left']:
            ax.spines[i].set_color('black')
            ax.spines[i].set_linewidth(1.5) 
    right_side = ax.spines["right"]
    right_side.set_visible(False)
    top_side = ax.spines["top"]
    top_side.set_visible(False)
    ax.set_axisbelow(True)
    ax.grid(color='gray', linewidth=1, axis='y', alpha=0.4)
    plt.title(f"Histograma del rendimiento\nlogarítmico de las acciones", size = 15)
    plt.xlabel("Rendimiento")
    plt.ylabel("Frecuencia")
    plt.show()
    
def plot_yield_deviation_mean(list_stocks, start = '2022-01-01', end = '2023-01-01'):
    return_stock = pd.DataFrame(return_daily(list_stock = list_stocks, start = start, end = end).mean()).rename(columns = {
        0:'Rendimiento promedio anualizado %'
    }).reset_index()
    return_stock = return_stock.rename(columns = {'index':"Acción"})
    return_stock["Rendimiento promedio anualizado %"] = return_stock["Rendimiento promedio anualizado %"]
    std_stock = pd.DataFrame(return_daily(list_stock = list_stocks, start = start, end = end).var()).rename(columns = {
        0:'Desviación estándar %'
    }).reset_index()
    std_stock = std_stock.rename(columns = {'index':'Acción'})
    df = pd.merge(return_stock, std_stock, on = "Acción", how = 'left')
    df = df.set_index("Acción")
    df["Rendimiento promedio anualizado %"] = df["Rendimiento promedio anualizado %"] * 252 * 100
    df["Desviación estándar %"] = df["Desviación estándar %"] * 252
    df["Desviación estándar anualizada %"] = df["Desviación estándar %"].apply(lambda x : math.sqrt(x)*100)
    
    fig, ax1 = plt.subplots(figsize = (8,6), dpi = 80)
    ax1.bar(df.index, df["Rendimiento promedio anualizado %"], color = 'tab:blue', alpha = 0.8)
    ax1.set_ylabel('Rendimiento promedio %')
    ax2 = ax1.twinx()
    ax2.plot(df.index, df["Desviación estándar anualizada %"],linewidth = 4, color = 'tab:orange', alpha = 0.8)
    ax2.set_ylabel('Desviación estándar %')
    
    for i in ['bottom', 'left']:
        ax2.spines[i].set_color('black')
        ax2.spines[i].set_linewidth(1.5) 
    right_side = ax2.spines["right"]
    right_side.set_visible(False)
    top_side = ax2.spines["top"]
    top_side.set_visible(False)
    ax2.set_axisbelow(True)
    ax2.grid(color='gray', linewidth=1, axis='y', alpha=0.4)
    plt.title(f'Rendimiento promedio y volatilidad anualizada\nde las acciones', size = 15)
    plt.show()
    return fig

def plot_cov_matrix(list_stock, start = '2022-01-01', end = '2023-01-01'):
    covmatrix = covariance_matrix(list_stock, start = start, end = end)
    fig, ax = plt.subplots(figsize = (15,8), dpi = 80)
    plt.title("Matriz de varianza y covarianza", size = 15)
    ax = sns.heatmap(covmatrix, cmap = 'Blues', annot = True)
    plt.show()
    
    

def plot_corr_matrix(list_stock, start = '2022-01-01', end = '2023-01-01'):
    return_stock = return_daily(list_stock, start = start, end = end)
    fig, ax = plt.subplots(figsize = (15,8), dpi = 80)
    ax = sns.heatmap(data = return_stock.corr(), annot = True, cmap = 'YlGnBu')
    plt.title("Matriz de Correlación", size = 15)
    plt.show()
    return fig
    

def plot_logarithmic_yield(list_stock, start = '2022-01-01', end = '2023-01-01'):
    return_stocks = return_daily(list_stock = list_stock, start = start, end = end)
    dark_color = sns.dark_palette("#69d", reverse = True, as_cmap = False, n_colors=5)
    sns.set_palette(dark_color)
    fig, ax = plt.subplots(figsize = (8,6), dpi = 80)
    return_stocks.plot(ax = ax)
    plt.xlabel("Fecha")
    plt.ylabel("Rendimiento logarítmico")
    plt.title("Evolución del rendimiemto logarítmico de las acciones", size = 15)
    for i in ['bottom', 'left']:
        ax.spines[i].set_color('black')
        ax.spines[i].set_linewidth(1.5) 
    right_side = ax.spines["right"]
    right_side.set_visible(False)
    top_side = ax.spines["top"]
    top_side.set_visible(False)
    ax.set_axisbelow(True)
    ax.grid(color='gray', linewidth=1, axis='y', alpha=0.4)
    plt.legend()
    plt.show()
    return fig

# def stock_chart_candlestick(ticker_name, start_time, end_time):
#     stock_dataframe = yf.Ticker(ticker_name).history(start = start_time, end = end_time)[["Open", "High", "Low", "Close"]].reset_index()
    
#     fig = go.Figure(data = [go.Candlestick(x = stock_dataframe["Date"],
#                                            open = stock_dataframe["Open"],
#                                            high = stock_dataframe["High"],
#                                            low = stock_dataframe["Low"],
#                                            close = stock_dataframe["Close"])])
#     fig.update_layout(title = f'Candlestick Price History of {ticker_name}',
#                       yaxis_title = f'{ticker_name} stock')
    
#     fig.show()
#     return fig


# Funciones para graficar el análisis financiero
def plot_stock_price_close(func):
    def wrapper(*args, **kwargs):
        stock_dataframe = func(*args, **kwargs)
        proyect_directory = os.getcwd()
        plots_directory = os.path.join(proyect_directory, "plots")
        os.makedirs(plots_directory, exist_ok=True)
        image_file_name = 'precios_cierre.png'
        image_file_path = os.path.join(plots_directory, image_file_name)
        orange_color = sns.color_palette("YlOrBr", as_cmap = False, n_colors=5)
        sns.set_palette(orange_color)
        fig, ax = plt.subplots(figsize = (8,6), dpi = 80)
        stock_dataframe.plot(ax = ax)
        plt.legend()
        plt.title("Evolución del precio de cierre de las acciones", size = 15)
        plt.xlabel("Fecha")
        plt.ylabel("Precio de las acciones")
        for i in ['bottom', 'left']:
            ax.spines[i].set_color('black')
            ax.spines[i].set_linewidth(1.5) 
        right_side = ax.spines["right"]
        right_side.set_visible(False)
        top_side = ax.spines["top"]
        top_side.set_visible(False)
        ax.set_axisbelow(True)
        ax.grid(color='gray', linewidth=1, axis='y', alpha=0.4)
        plt.savefig(image_file_path)
        plt.close()
    return wrapper

@plot_stock_price_close
def get_stock_price_close(stock_list, start = '2022-01-01', end = '2023-01-01'):
    stock_dataframe = pd.DataFrame()
    for stock in stock_list:
        data = yf.download(stock, start = start, end = end, progress = False)
        stock_dataframe[stock] = data["Close"]
    return stock_dataframe


def histogram_stock_returns(list_stocks, start = '2022-01-01', end = '2023-01-01'):
    proyect_directory = os.getcwd()
    plots_directory = os.path.join(proyect_directory, "plots")
    os.makedirs(plots_directory, exist_ok=True)
    image_file_name = 'precios_histograma.png'
    image_file_path = os.path.join(plots_directory, image_file_name)
    return_stock = return_daily(list_stock = list_stocks, start = start, end = end)
    red_color = sns.cubehelix_palette(start=2,rot=0, dark=0, light=.95)
    sns.set_palette(red_color)
    fig, ax = plt.subplots(figsize = (8,6), dpi = 80)
    for i in return_stock.columns.values:
        plt.hist(return_stock[i], label = i, bins = 100)
    plt.legend()
    for i in ['bottom', 'left']:
            ax.spines[i].set_color('black')
            ax.spines[i].set_linewidth(1.5) 
    right_side = ax.spines["right"]
    right_side.set_visible(False)
    top_side = ax.spines["top"]
    top_side.set_visible(False)
    ax.set_axisbelow(True)
    ax.grid(color='gray', linewidth=1, axis='y', alpha=0.4)
    plt.title(f"Histograma del rendimiento\nlogarítmico de las acciones", size = 15)
    plt.xlabel("Rendimiento")
    plt.ylabel("Frecuencia")
    plt.savefig(image_file_path)
    plt.close()


def return_log_mean_and_standard_deviation(list_stocks, start = '2022-01-01', end = '2023-01-01'):
    proyect_directory = os.getcwd()
    plots_directory = os.path.join(proyect_directory, "plots")
    os.makedirs(plots_directory, exist_ok=True)
    image_file_name = 'rendimiento_volatilidad_anualizada.png'
    image_file_path = os.path.join(plots_directory, image_file_name)
    return_stock = pd.DataFrame(return_daily(list_stock = list_stocks, start = start, end = end).mean()).rename(columns = {
        0:'Rendimiento promedio anualizado %'
    }).reset_index()
    return_stock = return_stock.rename(columns = {'index':"Acción"})
    return_stock["Rendimiento promedio anualizado %"] = return_stock["Rendimiento promedio anualizado %"]
    std_stock = pd.DataFrame(return_daily(list_stock = list_stocks, start = start, end = end).var()).rename(columns = {
        0:'Desviación estándar %'
    }).reset_index()
    std_stock = std_stock.rename(columns = {'index':'Acción'})
    df = pd.merge(return_stock, std_stock, on = "Acción", how = 'left')
    df = df.set_index("Acción")
    df["Rendimiento promedio anualizado %"] = df["Rendimiento promedio anualizado %"] * 252 * 100
    df["Desviación estándar %"] = df["Desviación estándar %"] * 252
    df["Desviación estándar anualizada %"] = df["Desviación estándar %"].apply(lambda x : math.sqrt(x)*100)
    
    fig, ax1 = plt.subplots(figsize = (8,6), dpi = 80)
    ax1.bar(df.index, df["Rendimiento promedio anualizado %"], color = 'tab:blue', alpha = 0.8)
    ax1.set_ylabel('Rendimiento promedio %')
    ax2 = ax1.twinx()
    ax2.plot(df.index, df["Desviación estándar anualizada %"],linewidth = 4, color = 'tab:orange', alpha = 0.8)
    ax2.set_ylabel('Desviación estándar %')
    
    for i in ['bottom', 'left']:
        ax2.spines[i].set_color('black')
        ax2.spines[i].set_linewidth(1.5) 
    right_side = ax2.spines["right"]
    right_side.set_visible(False)
    top_side = ax2.spines["top"]
    top_side.set_visible(False)
    ax2.set_axisbelow(True)
    ax2.grid(color='gray', linewidth=1, axis='y', alpha=0.4)
    plt.title(f'Rendimiento promedio y volatilidad anualizada\nde las acciones', size = 15)
    plt.savefig(image_file_path)
    plt.close()
    
    
def plot_covariance_matrix(list_stock, start = '2022-01-01', end = '2023-01-01'):
    proyect_directory = os.getcwd()
    plots_directory = os.path.join(proyect_directory, "plots")
    os.makedirs(plots_directory, exist_ok=True)
    image_file_name = 'variaza_covarianza.png'
    image_file_path = os.path.join(plots_directory, image_file_name)
    covmatrix = covariance_matrix(list_stock, start = start, end = end)
    fig, ax = plt.subplots(figsize = (15,8), dpi = 80)
    plt.title("Matriz de varianza y covarianza", size = 15)
    ax = sns.heatmap(covmatrix, cmap = 'Blues', annot = True)
    plt.savefig(image_file_path)
    plt.close()
    

def plot_correlation_matrix(list_stock, start = '2022-01-01', end = '2023-01-01'):
    proyect_directory = os.getcwd()
    plots_directory = os.path.join(proyect_directory, "plots")
    os.makedirs(plots_directory, exist_ok=True)
    image_file_name = 'matriz_correlacion.png'
    image_file_path = os.path.join(plots_directory, image_file_name)
    return_stock = return_daily(list_stock, start = start, end = end)
    fig, ax = plt.subplots(figsize = (15,8), dpi = 80)
    ax = sns.heatmap(data = return_stock.corr(), annot = True, cmap = 'YlGnBu')
    plt.title("Matriz de Correlación", size = 15)
    plt.savefig(image_file_path)
    plt.close()
    

def plot_return_log(list_stock, start = '2022-01-01', end = '2023-01-01'):
    proyect_directory = os.getcwd()
    plots_directory = os.path.join(proyect_directory, "plots")
    os.makedirs(plots_directory, exist_ok=True)
    image_file_name = 'rendimiento_log.png'
    image_file_path = os.path.join(plots_directory, image_file_name)
    return_stocks = return_daily(list_stock = list_stock, start = start, end = end)
    dark_color = sns.dark_palette("#69d", reverse = True, as_cmap = False, n_colors=5)
    sns.set_palette(dark_color)
    fig, ax = plt.subplots(figsize = (8,6), dpi = 80)
    return_stocks.plot(ax = ax)
    plt.xlabel("Fecha")
    plt.ylabel("Rendimiento logarítmico")
    plt.title("Evolución del rendimiemto logarítmico de las acciones", size = 15)
    for i in ['bottom', 'left']:
        ax.spines[i].set_color('black')
        ax.spines[i].set_linewidth(1.5) 
    right_side = ax.spines["right"]
    right_side.set_visible(False)
    top_side = ax.spines["top"]
    top_side.set_visible(False)
    ax.set_axisbelow(True)
    ax.grid(color='gray', linewidth=1, axis='y', alpha=0.4)
    plt.legend()
    plt.savefig(image_file_path)
    plt.close()
    
# Definición de la clase que será capaz de realizar el análisis de adquisición y venta de acciones

class BuySellStocks:
    
    def __init__(self, ticker, start, end, weights, investment):
        self.ticker = ticker
        self.start = start
        self.end = end
        self.weights = weights
        self.investment = investment
    
    def first_price_stock(self):
        stock_first_df = pd.DataFrame()
        for i in self.ticker:
            tickers = yf.Ticker(i).history(start = self.start, end = self.end)["Close"].head(1)
            stock_first_df[i] = tickers
        stock_first_df = pd.melt(stock_first_df.reset_index(), id_vars = ['Date'], var_name = 'Ticket',
           value_name = 'Precio')
        stock_first_df = stock_first_df.set_index("Date")
        stock_first_df["Precio"] = round(stock_first_df["Precio"],2)
        stock_first_df["Pesos %"] = [100 * x for x in self.weights] 
        stock_first_df["Inversión Parcial"] = [self.investment * x for x in self.weights]
        stock_first_df["Número de Acciones"] = round(stock_first_df["Inversión Parcial"] / stock_first_df["Precio"],0)
        stock_first_df["Inversión Inicial"] = self.investment
        stock_first_df = stock_first_df[["Inversión Inicial", "Ticket", "Precio", "Pesos %", "Inversión Parcial", 
                                         "Número de Acciones"]]
        stock_first_df = stock_first_df.reset_index()
        return stock_first_df
    
    def last_price_stock(self):
        stock_last_df = pd.DataFrame()
        for i in self.ticker:
            tickers = yf.Ticker(i).history(start = self.start, end = self.end)["Close"].tail(1)
            stock_last_df[i] = tickers
        stock_last_df = pd.melt(stock_last_df.reset_index(), id_vars = ['Date'], var_name = 'Ticket',
           value_name = 'Precio')
        stock_last_df = stock_last_df.set_index("Date")
        stock_last_df["Precio"] = round(stock_last_df["Precio"],2)
        stock_last_df["Pesos %"] = [100 * x for x in self.weights]
        stock_last_df["Inversión Inicial"] = self.investment
        stock_last_df["Inversión Parcial"] = [self.investment * x for x in self.weights]
        quantity_stock = round(stock_last_df["Inversión Parcial"] / stock_last_df["Precio"],0)
        stock_last_df["Número de Acciones"] = quantity_stock
        stock_last_df["Ingreso Parcial"] = round(stock_last_df["Número de Acciones"] * stock_last_df["Precio"],2)
        stock_last_df = stock_last_df[["Inversión Inicial", "Ticket", "Inversión Parcial", "Pesos %", "Precio", 
                                       "Número de Acciones", "Ingreso Parcial"]]
        stock_last_df = stock_last_df.reset_index()
        return stock_last_df
    
    def benefits_buy_sell_stock(self):
        result = self.last_price_stock()
        income = result["Ingreso Parcial"].sum()
        benefits = round(income - self.investment,2)
        return benefits    
    
    def plot_income_outcome_benefits(self):
        proyect_directory = os.getcwd()
        plots_directory = os.path.join(proyect_directory, "plots")
        os.makedirs(plots_directory, exist_ok=True)
        image_file_name = 'beneficio_ingreso_inversion.png'
        image_file_path = os.path.join(plots_directory, image_file_name)
        df = []
        df_columns = ["Inversión", "Ingreso", "Beneficio"]
        result = self.last_price_stock()
        income = result["Ingreso Parcial"].sum()
        benefits = round(income - self.investment, 2)
        df.append(round(self.investment,2))
        df.append(round(income, 2))
        df.append(round(benefits, 2))
        df = pd.DataFrame({
            'Column':df_columns,
            'Values':df
        })
        fig, ax = plt.subplots(figsize = (8,6), dpi = 80)
        bars = ax.bar(df["Column"], df["Values"], width = 0.5)
        for i, bar in enumerate(bars):
            if df['Values'][i] < 0:
                bar.set_color('#E9512E')
            else:
                bar.set_color('#3675D6')
        ax.set_ylabel('Valores')
        ax.bar_label(ax.containers[0], fontsize = 8.5)
        plt.title(f'Inversión, Ingreso y Beneficio', size = 15)
        for i in ['bottom', 'left']:
            ax.spines[i].set_color('black')
            ax.spines[i].set_linewidth(1.5) 
        right_side = ax.spines["right"]
        right_side.set_visible(False)
        top_side = ax.spines["top"]
        top_side.set_visible(False)
        ax.set_axisbelow(True)
        plt.savefig(image_file_path)
        plt.close()
        

class ReportFinancial:
    
    def __init__(self, stock, start, end, weights, investment, authorname):
        self.stock = stock
        self.start = start
        self.end = end
        self.investment = investment
        self.weights = weights
        self.authorname = authorname
        
    def report(self):
        plot_precio_cierre = get_stock_price_close(self.stock, self.start, self.end)
        get_start_date = get_date_start(self.stock, self.start, self.end)
        get_date_ends = get_date_end(self.stock, self.start, self.end)
        plot_rendimiento = plot_return_log(self.stock, self.start, self.end)
        histogram_stock_return = histogram_stock_returns(self.stock, self.start, self.end)
        return_log_mean_and_standard_deviatio = return_log_mean_and_standard_deviation(self.stock, self.start, self.end)
        plot_covariance_matri = plot_covariance_matrix(self.stock, self.start, self.end)
        plot_correlation_matri = plot_correlation_matrix(self.stock, self.start, self.end)
        
        bs = BuySellStocks(self.stock, self.start, self.end, self.weights, self.investment)
        first = bs.first_price_stock()
        final = bs.last_price_stock()
        plot = bs.plot_income_outcome_benefits()
        investment = self.investment
        benefits = bs.benefits_buy_sell_stock()
        benefits_str = return_positive_negative(benefits)
        
        #author = 'Sebastian Marat Urdanegui Bisalaya
        

        proyect_directory = os.getcwd()
        path_dir = os.path.join(proyect_directory, 'pdfs')
        os.makedirs(path_dir, exist_ok=True)
        report_path = 'report.pdf'
        report_paths = os.path.join(path_dir, report_path)
        pdf = SimpleDocTemplate(report_paths, pagesize = A4)
        estilos = getSampleStyleSheet()
        estilo_titulo = ParagraphStyle(name = 'centrado', parent = estilos['Title'],
                                    alignment = TA_CENTER)
        estilo_titulo.fontSize = 10

        estilo_subtitulo = estilos['Heading2']
        estilo_subtitulo.alignment = TA_CENTER

        estilo_texto = estilos["Normal"]
        estilo_texto.alignment = TA_JUSTIFY

        estilo_linea = ParagraphStyle(name = 'linea', parent = estilo_titulo, borderWidth = 2,
                                    borderColor = colors.black, spaceBefore = 5,
                                    spaceAfter = 5)

        titulo = Paragraph(f'{self.authorname}', estilo_titulo)
        pdf_title = [titulo, Spacer(1,0.05)]

        subtitulo = Paragraph("Reporte Financiero - Introducción a los Mercados Bursátiles", estilo_subtitulo)
        pdf_title.append(subtitulo)
        pdf_title.append(Spacer(1, 0.05))

        pdf_title.append(Spacer(1, 0.05))
        pdf_title.append(Paragraph('<hr width="50%" align="center" color="black">', estilo_texto))
        pdf_title.append(Spacer(1, 0.05))
        linea = Paragraph('<hr width="50%" align="center" size="5">', estilo_linea)
        pdf_title.append(linea)

        data = [['', ''],
                ['', '']]

        imagen1 = ImageReader("./plots/precios_cierre.png")
        data[0][0] = Image(open(imagen1.fileName, 'rb'), width=3.5*inch,
                        height=3.5*inch)


        imagen2 = ImageReader("./plots/rendimiento_log.png")
        data[0][1] = Image(open(imagen2.fileName, 'rb'), width=3.5*inch,
                        height=3.5*inch)

        imagen3 = ImageReader("./plots/precios_histograma.png")
        data[1][0] = Image(open(imagen3.fileName, 'rb'), width=3.5*inch,
                        height=3.5*inch)

        imagen4 = ImageReader("./plots/rendimiento_volatilidad_anualizada.png")
        data[1][1] = Image(open(imagen4.fileName, 'rb'), width=3.5*inch,
                        height=3.5*inch)


        tabla = Table(data, colWidths=250, rowHeights=300)
        estilo_tabla = TableStyle([('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                                ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.white),
                                ('BOX', (0, 0), (-1, -1), 1, colors.white)])
        tabla.setStyle(estilo_tabla)

        pdf_content = [tabla]


        data_2 = [[''],
                ['']]

        imagen5 = ImageReader("./plots/variaza_covarianza.png")
        data_2[0][0] = Image(open(imagen5.fileName, 'rb'), width=5.6*inch,
                        height=5*inch)

        imagen6 = ImageReader("./plots/matriz_correlacion.png")
        data_2[1][0] = Image(open(imagen6.fileName, 'rb'), width=5.6*inch,
                        height=5*inch)

        tabla_2 = Table(data_2, colWidths=500, rowHeights=340)
        tabla_2.setStyle(estilo_tabla)
        pdf_content.append(tabla_2)

        estilo_subtitulo2 = estilos['Heading2']
        estilo_subtitulo2.alignment = TA_CENTER
        subtitulo2 = Paragraph("Análisis de Compra y Venta de las Acciones", estilo_subtitulo2)
        pdf_content.append(subtitulo2)
        pdf_content.append(Spacer(1, 0.05))
        estilo_linea2 = ParagraphStyle(name = 'linea2', parent = estilo_titulo, borderWidth = 2,
                                    borderColor = colors.black, spaceBefore = 5,
                                    spaceAfter = 5)
        linea2 = Paragraph('<hr width="50%" align="center" size="5">', estilo_linea2)
        pdf_content.append(linea2)
        pdf_content.append(Spacer(1, 0.25*inch))
        estilo_texto2 = estilos["Normal"]
        estilo_texto2.alignment = TA_JUSTIFY
        texto2 = Paragraph(f'''A continuación, se muestra el resumen de la adquisición de 
                        acciones tomando como referencia la inversión inicial de S/. {investment} con el 
                        obtejivo de obtener el número de acciones necesarias para optimizar el rendimiento 
                        del portafolio de inversión en función del peso que representa cada compañía.''', estilo_texto2)
        pdf_content.append(texto2)
        pdf_content.append(Spacer(1, 0.25*inch))

        datos_tablas_estilos = TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                                ('FONTSIZE', (0, 0), (-1, 0), 6),
                                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                                ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                                ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
                                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                                ('FONTSIZE', (0, 1), (-1, -1), 5),
                                ('BOX', (0, 0), (-1, -1), 1, colors.black)])

        data_tabla_1 = [list(first.columns)]
        for row in first.itertuples(index = False):
                data_tabla_1.append(list(row))
        tabla_3 = Table(data_tabla_1)
        tabla_3.setStyle(datos_tablas_estilos)
        pdf_content.append(tabla_3)
        pdf_content.append(Spacer(1, 0.25*inch))

        estilo_texto3 = estilos["Normal"]
        estilo_texto3.alignment = TA_JUSTIFY
        texto3 = Paragraph(f'''La siguiente tabla ofrece información con respecto a la venta de las acciones
                        que estaban en nuestro portafolio. Reflejando el precio de la fecha de venta para calcular
                        los ingresos parciales con respecto al número de acciones que el inversor había adquirido.''', estilo_texto2)
        pdf_content.append(texto3)
        pdf_content.append(Spacer(1, 0.25*inch))

        data_tabla_2 = [list(final.columns)]
        for row in final.itertuples(index = False):
                data_tabla_2.append(list(row))
        tabla_4 = Table(data_tabla_2)
        tabla_4.setStyle(datos_tablas_estilos)
        pdf_content.append(tabla_4)
        pdf_content.append(Spacer(1, 0.25*inch))

        estilo_texto4 = estilos["Normal"]
        estilo_texto4.alignment = TA_JUSTIFY
        texto4 = Paragraph(f'''Luego de la venta de acciones del portafolio, se obtiene un beneficio neto (reduciendo el costo
                        de adquisición) de S/. {benefits}. En este caso, el ejercicio muestra una {benefits_str} en el
                        flujo de efectivo.''', estilo_texto4)
        pdf_content.append(texto4)
        pdf_content.append(Spacer(1, 0.1*inch))

        data_3 = [['']]
        imagen7 = ImageReader("./plots/beneficio_ingreso_inversion.png")
        data_3[0][0] = Image(open(imagen7.fileName, 'rb'), width=3.5*inch,
                        height=2*inch)
        tabla_5 = Table(data_3, colWidths=500, rowHeights=150)
        tabla_5.setStyle(estilo_tabla)
        pdf_content.append(tabla_5)


        pdf.build(pdf_title + pdf_content)
        
# if __name__ == "__main__":
#     reporte = ReportFinancial(["AAPL", "AMZN", "NFLX", "TSLA", "GOOGL", "ABNB"], "2022-01-01", "2023-03-31", [0.2, 0.1, 0.1, 0.25, 0.25, 0.1], 100000, "Sebastian Urdanegui")
#     reporte.report()
        

        
