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
    base_url = os.environ.get('BASE_URL', 'https://sistema-crachas-verte-belem.onrender.com')
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

def gerar_cracha_frente(apartamento, qr_url):
    """Gera crachá FRENTE (21.5cm x 9.5cm) - Exatamente como PDF Crachá-011A.pdf"""
    # Dimensões em pixels para 21.5cm x 9.5cm (300 DPI)
    largura = 2550  # 21.5cm
    altura = 1134   # 9.5cm
    
    cracha = Image.new('RGB', (largura, altura), 'white')
    draw = ImageDraw.Draw(cracha)
    
    # 1. NÚMERO DO APARTAMENTO (topo, centralizado, PRETO GRANDE)
    try:
        fonte_apt = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 400)
    except:
        try:
            fonte_apt = ImageFont.truetype("LiberationSans-Bold.ttf", 400)
        except:
            fonte_apt = ImageFont.load_default()
    
    bbox = draw.textbbox((0, 0), apartamento, font=fonte_apt)
    text_width = bbox[2] - bbox[0]
    x_apt = (largura - text_width) // 2
    y_apt = 80
    draw.text((x_apt, y_apt), apartamento, fill='black', font=fonte_apt)
    
    # 2. LOGO VERTE BELÉM (centro)
    try:
        logo = Image.open('logoverte.jpeg')
        logo_size = 600
        logo = logo.resize((logo_size, logo_size), Image.Resampling.LANCZOS)
        x_logo = (largura - logo_size) // 2
        y_logo = (altura - logo_size) // 2 - 50
        cracha.paste(logo, (x_logo, y_logo))
    except Exception as e:
        print(f"Erro ao carregar logo: {e}")
    
    # 3. QR CODE (centro-baixo, grande)
    qr = qrcode.QRCode(version=2, box_size=12, border=3)
    qr.add_data(qr_url)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white")
    
    qr_size = 500
    qr_img = qr_img.resize((qr_size, qr_size), Image.Resampling.LANCZOS)
    x_qr = (largura - qr_size) // 2
    y_qr = altura - qr_size - 100
    cracha.paste(qr_img, (x_qr, y_qr))
    
    buffer = BytesIO()
    cracha.save(buffer, format='PNG')
    buffer.seek(0)
    img_base64 = base64.b64encode(buffer.getvalue()).decode()
    
    return img_base64

def gerar_cracha_verso(apartamento, qr_url):
    """Gera verso do crachá com instruções - Exatamente como PDF CracháPremium-143B.pdf"""
    # Dimensões em pixels para 21.5cm x 9.5cm (300 DPI)
    largura = 2550  # 21.5cm
    altura = 1134   # 9.5cm
    
    cracha = Image.new('RGB', (largura, altura), 'white')
    draw = ImageDraw.Draw(cracha)
    
    # LADO ESQUERDO: Apartamento + Logo + QR Code
    # 1. NÚMERO DO APARTAMENTO (topo esquerdo)
    try:
        fonte_apt = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 300)
    except:
        fonte_apt = ImageFont.load_default()
    
    draw.text((100, 80), apartamento, fill='black', font=fonte_apt)
    
    # 2. LOGO VERTE BELÉM (esquerda, círculo vermelho)
    try:
        logo = Image.open('logoverte.jpeg')
        logo_size = 400
        logo = logo.resize((logo_size, logo_size), Image.Resampling.LANCZOS)
        x_logo = 150
        y_logo = (altura - logo_size) // 2 - 50
        cracha.paste(logo, (x_logo, y_logo))
    except:
        pass
    
    # 3. QR CODE COM BORDA VERMELHA (esquerda-baixo)
    qr = qrcode.QRCode(version=2, box_size=10, border=2)
    qr.add_data(qr_url)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white")
    
    qr_size = 350
    qr_img = qr_img.resize((qr_size, qr_size), Image.Resampling.LANCZOS)
    x_qr = 150
    y_qr = altura - qr_size - 80
    
    # Desenhar borda vermelha ao redor do QR
    draw.rectangle([(x_qr - 20, y_qr - 20), (x_qr + qr_size + 20, y_qr + qr_size + 20)], outline='#B91C3C', width=15)
    cracha.paste(qr_img, (x_qr, y_qr))
    
    # LINHA PONTILHADA VERMELHA (separador)
    linha_x = largura // 2
    for y in range(0, altura, 60):
        draw.line([(linha_x, y), (linha_x, y + 30)], fill='#B91C3C', width=8)
    
    # LADO DIREITO: INSTRUÇÕES PREMIUM DE USO
    try:
        fonte_titulo = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 80)
        fonte_texto = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 50)
    except:
        fonte_titulo = ImageFont.load_default()
        fonte_texto = ImageFont.load_default()
    
    x_direita = linha_x + 150
    y_texto = 100
    
    # Título
    draw.text((x_direita, y_texto), "INSTRUÇÕES", fill='#B91C3C', font=fonte_titulo)
    draw.text((x_direita, y_texto + 100), "PREMIUM DE USO", fill='#B91C3C', font=fonte_titulo)
    
    # Instruções
    y_texto = 350
    instrucoes = [
        "• Este crachá é individual",
        "  e intransferível",
        "",
        "• Mantenha pendurado no",
        "  retrovisor interno",
        "",
        "• Extravio: comunique ao",
        "  Administrador",
        "",
        "• Alterações: comunique à",
        "  Administração"
    ]
    
    for instrucao in instrucoes:
        draw.text((x_direita, y_texto), instrucao, fill='black', font=fonte_texto)
        y_texto += 70
    
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
        '141', '142', '143', '144', '145', '146', '147', '148',
        '151', '152', '153', '154', '155', '156', '157', '158'
    ]
    
    apartamentos = []
    for num in numeros:
        apartamentos.append(f'{num}A')
        apartamentos.append(f'{num}B')
    
    return apartamentos

@app.route('/')
def index():
    apartamentos = obter_apartamentos()
    apartamentos_options = ''.join([f'<option value="{apt}">{apt}</option>' for apt in apartamentos])
    logo_base64 = obter_logo_base64()
    
    return render_template_string(HTML_TEMPLATE, apartamentos_options=apartamentos_options, logo_base64=logo_base64)

@app.route('/gerar_qr', methods=['POST'])
def gerar_qr():
    data = request.get_json()
    placa = data.get('placa', '').upper().replace('-', '')
    apartamento = data.get('apartamento')
    
    if not placa or not apartamento:
        return jsonify({'error': 'Placa e apartamento são obrigatórios'}), 400
    
    if not re.match(r'^[A-Z]{3}[0-9][A-Z][0-9]{2}$|^[A-Z]{3}[0-9]{4}$', placa):
        return jsonify({'error': 'Formato de placa inválido. Use ABC1D34 ou ABC1234'}), 400
    
    qr_url = f"{os.environ.get('BASE_URL', 'https://sistema-crachas-verte-belem.onrender.com')}/placa/{placa}/{apartamento}"
    
    qr_code_base64 = gerar_qr_code(placa, apartamento)
    placa_imagem_base64 = gerar_imagem_placa(placa)
    cracha_frente_base64 = gerar_cracha_frente(apartamento, qr_url)
    cracha_verso_base64 = gerar_cracha_verso(apartamento, qr_url)
    
    dados = carregar_dados()
    novo_cracha = {
        'apartamento': apartamento,
        'placa': placa.upper(),
        'data_hora': datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    }
    dados.append(novo_cracha)
    salvar_dados(dados)
    
    return jsonify({
        'qr_code': qr_code_base64,
        'placa': placa.upper(),
        'placa_imagem': placa_imagem_base64,
        'apartamento': apartamento,
        'cracha_frente': cracha_frente_base64,
        'cracha_verso': cracha_verso_base64
    })

@app.route('/relatorio', methods=['GET'])
def relatorio():
    dados = carregar_dados()
    return jsonify(dados)

@app.route('/excluir/<int:index>', methods=['DELETE'])
def excluir(index):
    dados = carregar_dados()
    if 0 <= index < len(dados):
        dados.pop(index)
        salvar_dados(dados)
        return jsonify({'success': True})
    return jsonify({'error': 'Índice inválido'}), 400

@app.route('/exportar_csv', methods=['GET'])
def exportar_csv():
    dados = carregar_dados()
    csv_content = "Data/Hora,Apartamento,Placa\n"
    for item in dados:
        csv_content += f"{item['data_hora']},{item['apartamento']},{item['placa']}\n"
    
    return csv_content, 200, {
        'Content-Type': 'text/csv; charset=utf-8',
        'Content-Disposition': 'attachment; filename=crachas_verte_belem.csv'
    }

@app.route('/placa/<placa>/<apartamento>')
def visualizar_placa(placa, apartamento):
    """Página de visualização da placa"""
    dados = carregar_dados()
    registro = next((item for item in dados if item['placa'] == placa.upper() and item['apartamento'] == apartamento), None)
    
    if not registro:
        return "Placa não encontrada", 404
    
    logo_base64 = obter_logo_base64()
    placa_imagem_base64 = gerar_imagem_placa(placa)
    
    return render_template_string(VISUALIZACAO_TEMPLATE, 
                                   apartamento=apartamento,
                                   placa=placa.upper(),
                                   data_hora=registro['data_hora'],
                                   logo_base64=logo_base64,
                                   placa_imagem_base64=placa_imagem_base64)

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sistema de Crachás - Condomínio Verte Belém</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        .container {
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            padding: 40px;
            max-width: 900px;
            width: 100%;
        }
        .header { text-align: center; margin-bottom: 30px; }
        .header img { max-width: 150px; margin-bottom: 15px; }
        h1 { text-align: center; color: #667eea; margin-bottom: 10px; font-size: 28px; }
        .subtitle { text-align: center; color: #666; font-size: 14px; margin-bottom: 30px; }
        .form-group { margin-bottom: 25px; }
        label { display: block; margin-bottom: 8px; color: #333; font-weight: 600; font-size: 16px; }
        select, input {
            width: 100%;
            padding: 12px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 16px;
            transition: all 0.3s;
        }
        select:focus, input:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }
        .format-hint { font-size: 12px; color: #666; margin-top: 5px; }
        button {
            width: 100%;
            padding: 15px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 18px;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
            margin-top: 10px;
        }
        button:hover { transform: translateY(-2px); box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3); }
        button:active { transform: translateY(0); }
        #resultado { margin-top: 30px; display: none; }
        .cracha {
            background: white;
            border: 3px solid #667eea;
            border-radius: 15px;
            padding: 30px;
            text-align: center;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        .cracha-header { margin-bottom: 20px; }
        .cracha-header img { max-width: 120px; margin-bottom: 10px; }
        .cracha-apartamento { font-size: 32px; font-weight: bold; color: #667eea; margin: 15px 0; }
        .cracha-placa-img { margin: 20px 0; }
        .cracha-placa-img img { max-width: 100%; height: auto; border-radius: 8px; }
        .cracha-qr { margin: 20px 0; }
        .cracha-qr img { max-width: 200px; border: 2px solid #e0e0e0; border-radius: 8px; }
        .cracha-info { font-size: 14px; color: #666; margin-top: 15px; }
        .btn-imprimir {
            background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
            margin-top: 20px;
        }
        .relatorio { margin-top: 40px; }
        .relatorio h2 { color: #667eea; margin-bottom: 20px; display: flex; align-items: center; justify-content: space-between; }
        .btn-group { display: flex; gap: 10px; }
        .btn-secondary {
            background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
            padding: 10px 20px;
            font-size: 14px;
            width: auto;
        }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; background: white; border-radius: 8px; overflow: hidden; }
        th { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 15px; text-align: left; font-weight: 600; }
        td { padding: 12px 15px; border-bottom: 1px solid #e0e0e0; }
        tr:hover { background: #f5f5f5; }
        .btn-excluir {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            padding: 6px 12px;
            font-size: 12px;
            width: auto;
            margin: 0;
        }
        .total { text-align: center; margin-top: 15px; padding: 15px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 8px; font-weight: 600; }
        @media print {
            body { background: white; }
            .container { box-shadow: none; padding: 0; max-width: 100%; }
            .form-group, .relatorio, .btn-imprimir, button { display: none; }
            #resultado { display: block; margin: 0; }
            .cracha { border: none; box-shadow: none; padding: 0; page-break-inside: avoid; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            {% if logo_base64 %}
            <img src="data:image/jpeg;base64,{{ logo_base64 }}" alt="Logo Verte Belém">
            {% endif %}
            <h1>Sistema de Crachás Veiculares</h1>
            <p class="subtitle">Condomínio Verte Belém - 244 Apartamentos</p>
        </div>

        <div class="form-group">
            <label for="apartamento">Apartamento:</label>
            <select id="apartamento">
                <option value="">Selecione um apartamento...</option>
                {{ apartamentos_options }}
            </select>
        </div>

        <div class="form-group">
            <label for="placa">Placa Veicular (Mercosul):</label>
            <input type="text" id="placa" placeholder="ABC1D34" maxlength="7">
            <div class="format-hint">Formato: ABC1D34 (3 letras + 1 número + 1 letra + 2 números)</div>
        </div>

        <button onclick="gerarCracha()">🎫 Gerar Crachá</button>

        <div id="resultado">
            <div class="cracha">
                <div class="cracha-header">
                    {% if logo_base64 %}
                    <img src="data:image/jpeg;base64,{{ logo_base64 }}" alt="Logo Verte Belém">
                    {% endif %}
                </div>
                <div class="cracha-apartamento" id="apartamentoDisplay"></div>
                <div class="cracha-placa-img">
                    <img id="placaImg" src="" alt="Placa">
                </div>
                <div class="cracha-qr">
                    <img id="qrCodeImg" src="" alt="QR Code">
                </div>
                <div class="cracha-info">
                    <p>Placa: <strong id="placaDisplay"></strong></p>
                    <p>Escaneie o QR Code para verificar</p>
                </div>
            </div>
            <button class="btn-imprimir" onclick="window.print()">🖨️ Imprimir Crachá</button>
        </div>

        <div class="relatorio">
            <h2>
                📋 Relatório de Crachás
                <div class="btn-group">
                    <button class="btn-secondary" onclick="atualizarRelatorio()">📋 Atualizar Relatório</button>
                    <button class="btn-secondary" onclick="exportarCSV()">📄 Exportar Excel</button>
                </div>
            </h2>
            <table id="tabelaRelatorio">
                <thead>
                    <tr>
                        <th>Data/Hora</th>
                        <th>Apartamento</th>
                        <th>Placa</th>
                        <th>Ação</th>
                    </tr>
                </thead>
                <tbody id="tabelaCorpo"></tbody>
            </table>
            <div class="total" id="totalCrachas"></div>
        </div>
    </div>

    <script>
        function gerarCracha() {
            const apartamento = document.getElementById('apartamento').value;
            const placa = document.getElementById('placa').value;

            if (!apartamento || !placa) {
                alert('Por favor, preencha todos os campos');
                return;
            }

            fetch('/gerar_qr', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ apartamento, placa })
            })
            .then(r => r.json())
            .then(data => {
                if (data.error) {
                    alert('Erro: ' + data.error);
                    return;
                }
                document.getElementById('apartamentoDisplay').textContent = apartamento;
                document.getElementById('placaDisplay').textContent = data.placa;
                document.getElementById('placaImg').src = 'data:image/png;base64,' + data.placa_imagem;
                document.getElementById('qrCodeImg').src = 'data:image/png;base64,' + data.qr_code;
                document.getElementById('resultado').style.display = 'block';
                atualizarRelatorio();
            })
            .catch(e => alert('Erro ao gerar crachá: ' + e));
        }

        function atualizarRelatorio() {
            fetch('/relatorio')
            .then(r => r.json())
            .then(dados => {
                const tbody = document.getElementById('tabelaCorpo');
                tbody.innerHTML = '';
                dados.sort((a, b) => {
                    const numA = parseInt(a.apartamento.match(/\d+/)[0]);
                    const numB = parseInt(b.apartamento.match(/\d+/)[0]);
                    return numA - numB;
                });
                dados.forEach((item, index) => {
                    const tr = document.createElement('tr');
                    tr.innerHTML = `
                        <td>${item.data_hora}</td>
                        <td>${item.apartamento}</td>
                        <td>${item.placa}</td>
                        <td><button class="btn-excluir" onclick="excluirCracha(${index})">🗑️ Deletar</button></td>
                    `;
                    tbody.appendChild(tr);
                });
                document.getElementById('totalCrachas').textContent = `Total de Crachás: ${dados.length}`;
            });
        }

        function excluirCracha(index) {
            if (!confirm('Tem certeza que deseja deletar este crachá?')) return;
            fetch(`/excluir/${index}`, { method: 'DELETE' })
            .then(r => r.json())
            .then(data => {
                if (data.success) {
                    atualizarRelatorio();
                } else {
                    alert('Erro ao deletar');
                }
            });
        }

        function exportarCSV() {
            window.location.href = '/exportar_csv';
        }

        document.getElementById('placa').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') gerarCracha();
        });

        atualizarRelatorio();
    </script>
</body>
</html>
'''

VISUALIZACAO_TEMPLATE = '''
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Crachá Veicular - {{ apartamento }}</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        .cracha-container {
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            padding: 40px;
            max-width: 600px;
            width: 100%;
            text-align: center;
        }
        .logo { max-width: 150px; margin-bottom: 20px; }
        h1 { color: #667eea; margin-bottom: 10px; font-size: 24px; }
        .apartamento { font-size: 48px; font-weight: bold; color: #667eea; margin: 20px 0; }
        .placa-imagem { margin: 30px 0; }
        .placa-imagem img { max-width: 100%; height: auto; border-radius: 10px; box-shadow: 0 5px 15px rgba(0,0,0,0.2); }
        .info { background: #f5f5f5; padding: 20px; border-radius: 10px; margin-top: 20px; }
        .info p { margin: 10px 0; color: #333; font-size: 16px; }
        .data-hora { color: #666; font-size: 14px; margin-top: 20px; }
    </style>
</head>
<body>
    <div class="cracha-container">
        {% if logo_base64 %}
        <img src="data:image/jpeg;base64,{{ logo_base64 }}" alt="Logo Verte Belém" class="logo">
        {% endif %}
        
        <h1>Condomínio Verte Belém</h1>
        
        <div class="apartamento">Apartamento {{ apartamento }}</div>
        
        <div class="placa-imagem">
            <img src="data:image/png;base64,{{ placa_imagem_base64 }}" alt="Placa {{ placa }}">
        </div>
        
        <div class="info">
            <p><strong>Placa:</strong> {{ placa }}</p>
            <p><strong>Apartamento:</strong> {{ apartamento }}</p>
            <p class="data-hora">Registrado em: {{ data_hora }}</p>
        </div>
    </div>
</body>
</html>
'''

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
