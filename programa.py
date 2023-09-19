from turtle import width
import PySimpleGUI as sg
from PIL import Image, ExifTags, ImageFilter
import io
import os
import webbrowser
import requests

image_atual = None
image_anterior = None
image_path = None

def url_download(url):
    global image_atual
    global image_anterior
    try:
        r = requests.get(url, stream=True)
        if r.status_code == 200:
            image_atual = Image.open(io.BytesIO(r.content))
            show_image()
        else:
            sg.popup("Falha ao baixar a imagem. Verifique a URL e tente novamente.")
    except Exception as e:
        sg.popup(f"Erro ao baixar a imagem: {str(e)}")

def show_image():
    global image_atual
    global image_anterior
    try:
        resized_img = resize_image(image_atual)
        #Converte a image PIL para o formato que o PySimpleGUI
        img_bytes = io.BytesIO() #Permite criar objetos semelhantes a arquivos na memÃ³ria RAM
        resized_img.save(img_bytes, format='PNG')
        window['-IMAGE-'].update(data=img_bytes.getvalue())
    except Exception as e:
        sg.popup(f"Erro ao exibir a imagem: {str(e)}")

def resize_image(img):
    try:
        if img.width > img.height:
            ratio = img.height / img.width
            img = img.resize((750, round(750 * ratio)), Image.Resampling.LANCZOS)
        else:
            ratio = img.width / img.height
            img = img.resize((round(750 * ratio), 750), Image.Resampling.LANCZOS)
            
        return img
    except Exception as e:
        sg.popup(f"Erro ao redimensionar a imagem: {str(e)}")

def open_image(filename):
    global image_atual
    global image_anterior
    global image_path
    try:
        image_path = filename
        image_atual = Image.open(filename)    
        show_image()
    except Exception as e:
        sg.popup(f"Erro ao abrir a imagem: {str(e)}")

def save_image(filename):
    global image_atual
    global image_anterior
    try:
        if image_atual:
            with open(filename, 'wb') as file:
                image_atual.save(file)
        else:
            sg.popup("Nenhuma imagem aberta.")
    except Exception as e:
        sg.popup(f"Erro ao salvar a imagem: {str(e)}")

def info_image():
    global image_atual
    global image_anterior
    global image_path
    try:
        if image_atual:
            largura, altura = image_atual.size
            formato = image_atual.format
            tamanho_bytes = os.path.getsize(image_path)
            tamanho_mb = tamanho_bytes / (1024 * 1024)
            sg.popup(f"Tamanho: {largura} x {altura}\nFormato: {formato}\nTamanho em MB: {tamanho_mb:.2f}")
        else:
            sg.popup("Nenhuma imagem aberta.")
    except Exception as e:
        sg.popup(f"Erro ao exibir informações da imagem: {str(e)}")

def exif_data():
    global image_atual
    global image_anterior
    try:
        if image_atual:
            exif = image_atual._getexif() 
            if exif:
                exif_data = ""
                for tag, value in exif.items():
                    if tag in ExifTags.TAGS:
                        if tag == 37500 or tag == 34853: #Remove os dados customizados (37500) e de GPS (34853)
                            continue
                        tag_name = ExifTags.TAGS[tag]
                        exif_data += f"{tag_name}: {value}\n"
                sg.popup("Dados EXIF:", exif_data)
            else:
                sg.popup("A imagem não possui dados EXIF.")
        else:
            sg.popup("Nenhuma imagem aberta.")
    except Exception as e:
        sg.popup(f"Erro ao ler dados EXIF: {str(e)}")

def gps_data():
    global image_atual
    global image_anterior
    try:
        if image_atual:
            exif = image_atual._getexif()
            if exif:
                gps_info = exif.get(34853)  #Tag para informações de GPS
                print (gps_info[1], gps_info[3])
                if gps_info:
                    latitude = int(gps_info[2][0]) + int(gps_info[2][1]) / 60 + int(gps_info[2][2]) / 3600
                    if gps_info[1] == 'S':  #Verifica se a direção é 'S' (sul)
                        latitude = -latitude
                    longitude = int(gps_info[4][0]) + int(gps_info[4][1]) / 60 + int(gps_info[4][2]) / 3600
                    if gps_info[3] == 'W':  #Verifica se a direção é 'W' (oeste)
                        longitude = -longitude
                    sg.popup(f"Latitude: {latitude:.6f}\nLongitude: {longitude:.6f}")
                    open_in_maps_url = f"https://www.google.com/maps?q={latitude},{longitude}"
                    if sg.popup_yes_no("Deseja abrir no Google Maps?") == "Yes":
                        webbrowser.open(open_in_maps_url)
                else:
                    sg.popup("A imagem não possui informações de GPS.")
            else:
                sg.popup("A imagem não possui dados EXIF.")
        else:
            sg.popup("Nenhuma imagem aberta.")
    except Exception as e:
        sg.popup(f"Erro ao ler dados de GPS: {str(e)}")

def filNegativo():
    global image_atual
    global image_anterior
    try:
        if image_atual:
            image_anterior = image_atual.copy()
            auxImage = image_atual.load()
            for x in range(image_atual.width):
                for y in range(image_atual.height):
                    (r,g,b) = image_atual.getpixel((x,y))

                    r = 255 - r
                    g = 255 - g
                    b = 255 - b

                    auxImage[x,y] = (r,g,b)
            show_image()
        else:
            sg.popup("Nenhuma imagem aberta.")
    except Exception as e:
        sg.popup(f"Erro ao aplicar filtro: {str(e)}")

def filCinza():
    global image_atual
    global image_anterior
    try:
        if image_atual:
            image_anterior = image_atual.copy()
            auxImage = image_atual.load()
            for x in range(image_atual.width):
                for y in range(image_atual.height):
                    (r,g,b) = image_atual.getpixel((x,y))

                    r = r * 0.3
                    g = g * 0.6
                    b = b * 0.1
                    c = round(r + g + b)

                    auxImage[x,y] = (c,c,c)
            show_image()
        else:
            sg.popup("Nenhuma imagem aberta.")
    except Exception as e:
        sg.popup(f"Erro ao aplicar filtro: {str(e)}")
    
def filSepia():
    global image_atual
    global image_anterior
    try:
        if image_atual:
            image_anterior = image_atual.copy()
            auxImage = image_atual.load()
            for x in range(image_atual.width):
                for y in range(image_atual.height):
                    (r,g,b) = image_atual.getpixel((x,y))

                    r = r * 0.3
                    g = g * 0.6
                    b = b * 0.1

                    c = round(r + g + b)

                    if(c+100) > 255:
                        r = 255
                    else:
                        r = c+100

                    if(c+50) > 255:
                        g = 255
                    else:
                        g = c+50
                    
                    b = c

                    auxImage[x,y] = (r,g,b)
            show_image()
        else:
            sg.popup("Nenhuma imagem aberta.")
    except Exception as e:
        sg.popup(f"Erro ao aplicar filtro: {str(e)}")

def fil16bits():
    global image_atual
    global image_anterior

    try:
        if image_atual:
            image_anterior = image_atual.copy()
            image_atual = image_atual.convert('P',palette=Image.ADAPTIVE,colors=16)
            show_image()
        else:
            sg.popup("Nenhuma imagem aberta.")
    except Exception as e:
        sg.popup(f"Erro ao aplicar filtro: {str(e)}")

def girarIMG(degrees):
    global image_atual
    global image_anterior
    try:
        if image_atual:
            image_anterior = image_atual.copy()
            image_atual = image_atual.rotate(degrees, expand=True)
            show_image()
        else:
            sg.popup("Nenhuma imagem aberta.")
    except Exception as e:
        sg.popup(f"Erro ao girar a imagem: {str(e)}")

def filBlur():
    global image_atual
    global image_anterior

    radius = sg.popup_get_text("Digite a quantidade de Blur (0 a 20):", default_text="2")
    try:
        radius = int(radius)
        radius = max(0, min(20, radius))
    except ValueError:
        sg.popup("Por favor, insira um valor numérico válido.")
        return
    
    try:
        if image_atual:
            image_anterior = image_atual.copy()
            image_atual = image_atual.filter(ImageFilter.GaussianBlur(radius))
            show_image()
        else:
            sg.popup("Nenhuma imagem aberta.")
    except Exception as e:
        sg.popup(f"Erro ao aplicar o filtro de desfoque: {str(e)}")

def filContorno():
    global image_atual
    global image_anterior
    try:
        if image_atual:
            image_anterior = image_atual.copy()
            image_atual = image_atual.filter(ImageFilter.CONTOUR)
            show_image()
        else:
            sg.popup("Nenhuma imagem aberta.")
    except Exception as e:
        sg.popup(f"Erro ao aplicar o filtro de contorno: {str(e)}")

def filDetalhe():
    global image_atual
    global image_anterior
    try:
        if image_atual:
            image_anterior = image_atual.copy()
            image_atual = image_atual.filter(ImageFilter.DETAIL)
            show_image()
        else:
            sg.popup("Nenhuma imagem aberta.")
    except Exception as e:
        sg.popup(f"Erro ao aplicar o filtro de detalhe: {str(e)}")

def filRealce():
    global image_atual
    global image_anterior
    try:
        if image_atual:
            image_anterior = image_atual.copy()
            image_atual = image_atual.filter(ImageFilter.EDGE_ENHANCE)
            show_image()
        else:
            sg.popup("Nenhuma imagem aberta.")
    except Exception as e:
        sg.popup(f"Erro ao aplicar o filtro de realce de bordas: {str(e)}")

def filRelevo():
    global image_atual
    global image_anterior
    try:
        if image_atual:
            image_anterior = image_atual.copy()
            image_atual = image_atual.filter(ImageFilter.EMBOSS)
            show_image()
        else:
            sg.popup("Nenhuma imagem aberta.")
    except Exception as e:
        sg.popup(f"Erro ao aplicar o filtro de relevo: {str(e)}")

def filAcharBorda():
    global image_atual
    global image_anterior
    try:
        if image_atual:
            image_anterior = image_atual.copy()
            image_atual = image_atual.filter(ImageFilter.FIND_EDGES)
            show_image()
        else:
            sg.popup("Nenhuma imagem aberta.")
    except Exception as e:
        sg.popup(f"Erro ao aplicar o filtro de detectar bordas: {str(e)}")

def filNitidez():
    global image_atual
    global image_anterior
    try:
        if image_atual:
            image_anterior = image_atual.copy()
            image_atual = image_atual.filter(ImageFilter.SHARPEN)
            show_image()
        else:
            sg.popup("Nenhuma imagem aberta.")
    except Exception as e:
        sg.popup(f"Erro ao aplicar o filtro de nitidez: {str(e)}")

def filSuavizar():
    global image_atual
    global image_anterior
    try:
        if image_atual:
            image_anterior = image_atual.copy()
            image_atual = image_atual.filter(ImageFilter.SMOOTH)
            show_image()
        else:
            sg.popup("Nenhuma imagem aberta.")
    except Exception as e:
        sg.popup(f"Erro ao aplicar o filtro de suavizar: {str(e)}")

def filMin():
    global image_atual
    global image_anterior

    size = sg.popup_get_text("Digite a quantidade de filtro (3 a 20):", default_text="3")
    try:
        size = int(size)
        size = max(3, min(20, size))
    except ValueError:
        sg.popup("Por favor, insira um valor numérico válido.")
        return

    try:
        if image_atual:
            image_anterior = image_atual.copy()
            image_atual = image_atual.filter(ImageFilter.MinFilter(size=size))
            show_image()
        else:
            sg.popup("Nenhuma imagem aberta.")
    except Exception as e:
        sg.popup(f"Erro ao aplicar o filtro mínimo: {str(e)}")

def filMax():
    global image_atual
    global image_anterior

    size = sg.popup_get_text("Digite a quantidade de filtro (3 a 20):", default_text="3")
    try:
        size = int(size)
        size = max(3, min(20, size))
    except ValueError:
        sg.popup("Por favor, insira um valor numérico válido.")
        return


    try:
        if image_atual:
            image_anterior = image_atual.copy()
            image_atual = image_atual.filter(ImageFilter.MaxFilter(size=size))
            show_image()
        else:
            sg.popup("Nenhuma imagem aberta.")
    except Exception as e:
        sg.popup(f"Erro ao aplicar o filtro máximo: {str(e)}")


def funDesfazer():
    global image_atual
    global image_anterior

    tmp = image_atual
    image_atual = image_anterior
    image_anterior = tmp

    show_image()
        
layout = [
    [sg.Menu([
            ['&Arquivo', ['&Abrir', 'Abrir URL', 'Salvar', 'Fechar',]],
            ['Imagem', [
                'Girar', ['Girar 90 graus à direita', 'Girar 90 graus à esquerda'], 
                'Filtro', ['Preto e Branco', 'Sépia', 'Negativo', '16bits', 
                           'Blur', 'Contorno', 'Detalhe', 'Realce de bordas',
                           'Relevo', 'Detectar bordas', 'Nitidez', 'Suavizar',
                           'Filtro mínimo', 'Filtro máximo']
            ]],
            ['Sobre a image', ['Informacoes',['Dados simples','Dados avançados','Dados GPS']]], 
            ['Sobre', ['Desenvolvedor']]
        ])],
    [sg.Image(key='-IMAGE-', size=(800, 600))],
]

window = sg.Window('Photo Shoping', layout, finalize=True)
window.bind('<Control-z>', 'Desfazer')


while True:
    event, values = window.read()

    if event in (sg.WINDOW_CLOSED, 'Fechar'):
        break
    elif event == 'Abrir':
        arquivo = sg.popup_get_file('Selecionar image', file_types=(("Imagens", "*.png;*.jpg;*.jpeg;*.gif"),))
        if arquivo:
            open_image(arquivo)
    elif event == 'Abrir URL':
        url = sg.popup_get_text("Digite a url")
        if url:
            url_download(url)
    elif event == 'Salvar':
        if image_atual:
            arquivo = sg.popup_get_file('Salvar image como', save_as=True, file_types=(("Imagens", "*.png;*.jpg;*.jpeg;*.gif"),))
            if arquivo:
                save_image(arquivo)
    elif event == 'Dados simples':
        info_image()
    elif event == 'Dados avançados':
        exif_data()
    elif event == 'Dados GPS':
        gps_data()
    elif event == 'Desenvolvedor':
        sg.popup('Desenvolvido por Bruno Pescarolli - BCC 6º Semestre')
    elif event == 'Girar 90 graus à direita':
        girarIMG(-90)
    elif event == 'Girar 90 graus à esquerda':
        girarIMG(90)
    elif event == 'Negativo':
        filNegativo()
    elif event == 'Preto e Branco':
        filCinza()
    elif event == 'Sépia':
        filSepia()
    elif event == '16bits':
        fil16bits()
    elif event == 'Blur':
        filBlur()
    elif event == 'Contorno':
        filContorno()
    elif event == 'Detalhe':
        filDetalhe()
    elif event == 'Realce de bordas':
        filRealce()
    elif event == 'Relevo':
        filRelevo()
    elif event == 'Detectar bordas':
        filAcharBorda()
    elif event == 'Nitidez':
        filNitidez()
    elif event == 'Suavizar':
        filSuavizar()
    elif event == 'Filtro mínimo':
        filMin()
    elif event == 'Filtro máximo':
        filMax()
    elif event == 'Desfazer':
        funDesfazer()


window.close()