from flask import Flask, request, jsonify, send_file, render_template_string
from flask_cors import CORS
import qrcode
import base64
from io import BytesIO
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import json
import os
import re

app = Flask(__name__)
CORS(app)

# Sistema de persistência em arquivo JSON
DATA_FILE = 'crachas_data.json'

def carregar_dados():
    """Carrega dados do arquivo JSON"""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    
    # Dados iniciais de exemplo
    dados_iniciais = [
        {
            'apartamento': '143B',
            'placa': 'ABC1D34',
            'data_hora': '15/09/2025 08:00:00'
        },
        {
            'apartamento': '075A',
            'placa': 'XYZ-9876',
            'data_hora': '15/09/2025 08:15:00'
        }
    ]
    salvar_dados(dados_iniciais)
    return dados_iniciais

def salvar_dados(dados):
    """Salva dados no arquivo JSON"""
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(dados, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"Erro ao salvar dados: {e}")
        return False

def gerar_qr_code(placa, apartamento):
    """Gera QR code para a placa"""
    base_url = os.environ.get('BASE_URL', 'https://crachaverte.insuranceandreinsuranceapps.com')
    url = f"{base_url}/placa/{placa}/{apartamento}"
    
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(url)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    
    return base64.b64encode(buffer.getvalue()).decode()

def gerar_imagem_placa(placa_texto):
    """Gera imagem da placa Mercosul com texto personalizado"""
    # Abrir template da placa
    template_path = 'placa-ABC-768x250.png'
    placa = Image.open(template_path)
    draw = ImageDraw.Draw(placa)
    
    # Normalizar texto da placa (remover hífen se existir)
    placa_texto = placa_texto.upper().replace('-', '')
    
    # Carregar fonte FE-Font (fonte oficial de placas veiculares)
    try:
        font = ImageFont.truetype("FE-FONT.TTF", 148)
    except:
        try:
            font = ImageFont.truetype("LiberationSans-Bold.ttf", 140)
        except:
            font = ImageFont.load_default()
    
    # Apagar texto original da placa (área branca central)
    draw.rectangle([(70, 72), (710, 220)], fill='white')
    
    # Desenhar cada caractere com espaçamento exato da placa original
    x_pos = 96  # Posição inicial X
    y_posicao = 77   # Posição Y (vertical)
    espacamento_letras = 75  # Espaçamento entre letras
    espacamento_numeros = 85  # Espaçamento maior entre letras e números
    
    for i, char in enumerate(placa_texto):
        draw.text((x_pos, y_posicao), char, fill='black', font=font)
        
        # Espaçamento diferente entre letras (ABC) e números (1D34)
        if i == 2:  # Após a letra C (índice 2)
            x_pos += espacamento_numeros
        else:
            x_pos += espacamento_letras
    
    # Converter para base64
    buffer = BytesIO()
    placa.save(buffer, format='PNG')
    buffer.seek(0)
    
    return base64.b64encode(buffer.getvalue()).decode()

def obter_logo_base64():
    """Retorna logo Verte Belém em base64"""
    logo_path = 'logoverte.jpeg'
    if os.path.exists(logo_path):
        with open(logo_path, 'rb') as f:
            return base64.b64encode(f.read()).decode()
    return ''

def gerar_cracha_impressao(apartamento, qr_url="https://crachaverte.insuranceandreinsuranceapps.com"):
    """Gera crachá de impressão no formato 765x1020 pixels (9x12cm)"""
    largura = 765
    altura = 1020
    
    cracha = Image.new('RGB', (largura, altura), 'white')
    draw = ImageDraw.Draw(cracha)
    
    margem_topo = 80
    
    # 1. NÚMERO DO APARTAMENTO (topo) - FONTE GRANDE
    try:
        tamanho_fonte = 250
        fonte_apt = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", tamanho_fonte)
    except:
        try:
            fonte_apt = ImageFont.truetype("LiberationSans-Bold.ttf", 240)
        except:
            fonte_apt = ImageFont.load_default()
    
    bbox = draw.textbbox((0, 0), apartamento, font=fonte_apt)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x_apt = (largura - text_width) // 2
    y_apt = margem_topo
    
    draw.text((x_apt, y_apt), apartamento, fill='black', font=fonte_apt)
    
    # 2. LOGO VERTE BELÉM (centro)
    try:
        logo = Image.open('logoverte.jpeg')
        logo_size = 365
        logo = logo.resize((logo_size, logo_size), Image.Resampling.LANCZOS)
        
        x_logo = (largura - logo_size) // 2
        y_logo = y_apt + text_height + 80
        
        cracha.paste(logo, (x_logo, y_logo))
    except Exception as e:
        print(f"Erro ao carregar logo: {e}")
        logo_size = 365
        y_logo = 350
    
    # 3. QR CODE (parte inferior)
    qr = qrcode.QRCode(version=1, box_size=10, border=2)
    qr.add_data(qr_url)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white")
    
    qr_size = 295
    qr_img = qr_img.resize((qr_size, qr_size), Image.Resampling.LANCZOS)
    
    x_qr = (largura - qr_size) // 2
    y_qr = y_logo + logo_size + 80
    
    cracha.paste(qr_img, (x_qr, y_qr))
    
    buffer = BytesIO()
    cracha.save(buffer, format='PNG')
    buffer.seek(0)
    img_base64 = base64.b64encode(buffer.getvalue()).decode()
    
    return img_base64

def obter_apartamentos():
    """Lista completa de 244 apartamentos - Verte Belém (Blocos A e B)"""
    numeros = [
        '006', '007', '011', '012', '013', '014', '015', '016', '017', '018',
        '021', '022', '023', '024', '025', '026', '027', '028',
        '031', '032', '033', '034', '035', '036', '037', '038',
        '041', '042', '043', '044', '045', '046', '047', '048',
        '051', '052', '053', '054', '055', '056', '057', '058',
        '061', '062', '063', '064', '065', '066', '067', '068',
        '071', '072', '073', '074', '075', '076', '077', '078',
        '081', '082', '083', '084', '085', '086', '087', '088',
        '091', '092', '093', '094', '095', '096', '097', '098',
        '101', '102', '103', '104', '105', '106', '107', '108',
        '111', '112', '113', '114', '115', '116', '117', '118',
        '121', '122', '123', '124', '125', '126', '127', '128',
        '131', '132', '133', '134', '135', '136', '137', '138',
        '141', '142', '143', '144', '145', '146', '147',
