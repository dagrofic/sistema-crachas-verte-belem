from flask import Flask, request, jsonify, send_file, render_template_string
from flask_cors import CORS
import qrcode
import base64
from io import BytesIO
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import json
import os

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
    base_url = os.environ.get('BASE_URL', 'https://cracha.insuranceandreinsuranceapps.com')
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
    
    # Converter formato antigo ABC1234 para Mercosul ABC1D34
    if len(placa_texto) == 7 and placa_texto[3].isdigit():
        # Formato antigo detectado, manter como está mas exibir em formato Mercosul
        pass
    
    # Carregar fonte FE-Font (fonte oficial de placas veiculares)
    try:
        # Tentar carregar fonte FE-Font do repositório
        font = ImageFont.truetype("FE-FONT.TTF", 148)
    except:
        try:
            # Fallback: Liberation Sans Bold
            font = ImageFont.truetype("LiberationSans-Bold.ttf", 140)
        except:
            # Último fallback: fonte padrão
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
            x_pos += espacamento_numeros  # Espaçamento maior antes do número
        else:
            x_pos += espacamento_letras  # Espaçamento normal
    
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

def gerar_cracha_impressao(apartamento, qr_url="https://cracha.insuranceandreinsuranceapps.com"):
    """Gera crachá de impressão no formato 765x1020 pixels (9x12cm)"""
    # Dimensões do crachá (255x340 pts = ~765x1020 pixels em 300 DPI)
    largura = 765
    altura = 1020
    
    # Criar imagem branca
    cracha = Image.new('RGB', (largura, altura), 'white')
    draw = ImageDraw.Draw(cracha)
    
    # 1. NÚMERO DO APARTAMENTO (topo) - GIGANTE
    try:
        fonte_apt = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 180)
    except:
        fonte_apt = ImageFont.load_default()
    
    # Calcular posição central do texto
    bbox = draw.textbbox((0, 0), apartamento, font=fonte_apt)
    text_width = bbox[2] - bbox[0]
    x_apt = (largura - text_width) // 2
    y_apt = 60
    
    draw.text((x_apt, y_apt), apartamento, fill='black', font=fonte_apt)
    
    # 2. LOGO VERTE BELÉM (centro) - GRANDE E ALTA QUALIDADE
    try:
        logo = Image.open('logoverte.jpeg')
        logo_size = 420
        logo = logo.resize((logo_size, logo_size), Image.Resampling.LANCZOS)
        
        x_logo = (largura - logo_size) // 2
        y_logo = 310
        
        cracha.paste(logo, (x_logo, y_logo))
    except Exception as e:
        print(f"Erro ao carregar logo: {e}")
    
    # 3. QR CODE (parte inferior) - GRANDE
    qr = qrcode.QRCode(version=1, box_size=10, border=2)
    qr.add_data(qr_url)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white")
    
    qr_size = 280
    qr_img = qr_img.resize((qr_size, qr_size), Image.Resampling.LANCZOS)
    
    x_qr = (largura - qr_size) // 2
    y_qr = 720
    
    cracha.paste(qr_img, (x_qr, y_qr))
    
    # Converter para base64
    buffer = BytesIO()
    cracha.save(buffer, format='PNG')
    buffer.seek(0)
    img_base64 = base64.b64encode(buffer.getvalue()).decode()
    
    return img_base64

def obter_apartamentos():
    """Lista completa de 244 apartamentos - Verte Belém (Blocos A e B)"""
    # Números dos apartamentos conforme PDF oficial
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
    # Gerar apartamentos para Bloco A e B em ordem
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
    placa = data.get('placa')
    apartamento = data.get('apartamento')
    
    if not placa or not apartamento:
        return jsonify({'error': 'Placa e apartamento são obrigatórios'}), 400
    
    # Gerar QR code
    qr_code_base64 = gerar_qr_code(placa, apartamento)
    
    # Gerar imagem da placa
    placa_imagem_base64 = gerar_imagem_placa(placa)
    
    # Gerar crachá de impressão
    cracha_impressao_base64 = gerar_cracha_impressao(apartamento)
    
    # Salvar no arquivo JSON
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
        'cracha_impressao': cracha_impressao_base64
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
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
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
        
        .header {
            text-align: center;
            margin-bottom: 30px;
        }
        
        .header img {
            max-width: 150px;
            margin-bottom: 15px;
        }
        
        h1 {
            text-align: center;
            color: #667eea;
            margin-bottom: 10px;
            font-size: 28px;
        }
        
        .subtitle {
            text-align: center;
            color: #666;
            font-size: 14px;
            margin-bottom: 30px;
        }
        
        .form-group {
            margin-bottom: 25px;
        }
        
        label {
            display: block;
            margin-bottom: 8px;
            color: #333;
            font-weight: 600;
            font-size: 16px;
        }
        
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
        
        .format-hint {
            font-size: 12px;
            color: #666;
            margin-top: 5px;
        }
        
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
        
        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
        }
        
        button:active {
            transform: translateY(0);
        }
        
        #resultado {
            margin-top: 30px;
            display: none;
        }
        
        .cracha {
            background: white;
            border: 3px solid #667eea;
            border-radius: 15px;
            padding: 30px;
            text-align: center;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        
        .cracha-header {
            margin-bottom: 20px;
        }
        
        .cracha-header img {
            max-width: 120px;
            margin-bottom: 10px;
        }
        
        .cracha-apartamento {
            font-size: 32px;
            font-weight: bold;
            color: #667eea;
            margin: 15px 0;
        }
        
        .cracha-placa-img {
            margin: 20px 0;
        }
        
        .cracha-placa-img img {
            max-width: 100%;
            height: auto;
            border-radius: 8px;
        }
        
        .cracha-qr {
            margin: 20px 0;
        }
        
        .cracha-qr img {
            max-width: 200px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
        }
        
        .cracha-info {
            font-size: 14px;
            color: #666;
            margin-top: 15px;
        }
        
        .btn-imprimir {
            background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
            margin-top: 20px;
        }
        
        .relatorio {
            margin-top: 40px;
        }
        
        .relatorio h2 {
            color: #667eea;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }
        
        .btn-group {
            display: flex;
            gap: 10px;
        }
        
        .btn-secondary {
            background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
            padding: 10px 20px;
            font-size: 14px;
            width: auto;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
            background: white;
            border-radius: 8px;
            overflow: hidden;
        }
        
        th {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px;
            text-align: left;
            font-weight: 600;
        }
        
        td {
            padding: 12px 15px;
            border-bottom: 1px solid #e0e0e0;
        }
        
        tr:hover {
            background: #f5f5f5;
        }
        
        .btn-excluir {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            padding: 6px 12px;
            font-size: 12px;
            width: auto;
            margin: 0;
        }
        
        .total {
            text-align: center;
            margin-top: 15px;
            padding: 15px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 8px;
            font-weight: 600;
        }
        
        @media print {
            body {
                background: white;
            }
            
            .container {
                box-shadow: none;
                padding: 0;
            }
            
            .form-group, .relatorio, button:not(.btn-imprimir) {
                display: none !important;
            }
            
            #resultado {
                display: block !important;
            }
            
            .btn-imprimir {
                display: none !important;
            }
        }
        
        @media (max-width: 600px) {
            .container {
                padding: 20px;
            }
            
            h1 {
                font-size: 22px;
            }
            
            table {
                font-size: 14px;
            }
            
            th, td {
                padding: 8px;
            }
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
            <div class="subtitle">Condomínio Verte Belém - 244 Apartamentos</div>
        </div>
        
        <div class="form-group">
            <label for="apartamento">Apartamento:</label>
            <select id="apartamento" name="apartamento">
                {{ apartamentos_options|safe }}
            </select>
        </div>
        
        <div class="form-group">
            <label for="placa">Placa do Veículo:</label>
            <input type="text" id="placa" name="placa" placeholder="ABC1D34 ou ABC-1234" maxlength="8">
            <div class="format-hint">Formatos aceitos: Mercosul (ABC1D34) ou Antigo (ABC-1234)</div>
        </div>
        
        <button onclick="gerarCracha()">Gerar Crachá</button>
        
        <div id="resultado">
            <div class="cracha" id="cracha-print">
                <div class="cracha-header">
                    {% if logo_base64 %}
                    <img src="data:image/jpeg;base64,{{ logo_base64 }}" alt="Logo Verte Belém">
                    {% endif %}
                    <div class="cracha-apartamento">Apartamento: <span id="apt-numero"></span></div>
                </div>
                
                <div class="cracha-placa-img">
                    <img id="placa-imagem" src="" alt="Placa do Veículo">
                </div>
                
                <div class="cracha-qr">
                    <img id="qr-code" src="" alt="QR Code">
                </div>
                
                <div class="cracha-info">
                    <p><strong>Placa:</strong> <span id="placa-texto"></span></p>
                    <p><strong>Escaneie o QR Code para verificar</strong></p>
                </div>
            </div>
            
            <div style="display: flex; gap: 10px; justify-content: center;">
                <button class="btn-imprimir" onclick="window.print()">🖨️ Imprimir Crachá</button>
                <button class="btn-imprimir" onclick="baixarCrachaImpressao()" id="btn-download-cracha" style="background: #27ae60;">💾 Baixar Crachá para Corte</button>
            </div>
        </div>
        
        <div class="relatorio">
            <h2>
                <span>Crachás Gerados</span>
                <div class="btn-group">
                    <button class="btn-secondary" onclick="carregarRelatorio()">🔄 Atualizar</button>
                    <button class="btn-secondary" onclick="exportarCSV()">📥 Exportar CSV</button>
                </div>
            </h2>
            
            <table id="tabela-relatorio">
                <thead>
                    <tr>
                        <th>Data/Hora</th>
                        <th>Apartamento</th>
                        <th>Placa</th>
                        <th>Ações</th>
                    </tr>
                </thead>
                <tbody id="corpo-tabela">
                    <tr>
                        <td colspan="4" style="text-align: center;">Carregando...</td>
                    </tr>
                </tbody>
            </table>
            
            <div class="total" id="total-crachas">Total: 0 crachás</div>
        </div>
    </div>
    
    <script>
        async function gerarCracha() {
            const apartamento = document.getElementById('apartamento').value;
            const placa = document.getElementById('placa').value.trim();
            
            if (!placa) {
                alert('Por favor, informe a placa do veículo');
                return;
            }
            
            try {
                const response = await fetch('/gerar_qr', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ placa, apartamento })
                });
                
                const data = await response.json();
                
                if (data.error) {
                    alert(data.error);
                    return;
                }
                
                // Atualizar crachá
                document.getElementById('apt-numero').textContent = data.apartamento;
                document.getElementById('placa-texto').textContent = data.placa;
                document.getElementById('qr-code').src = 'data:image/png;base64,' + data.qr_code;
                document.getElementById('placa-imagem').src = 'data:image/png;base64,' + data.placa_imagem;
                
                // Armazenar crachá de impressão para download
                window.crachaImpressaoBase64 = data.cracha_impressao;
                window.crachaApartamento = data.apartamento;
                
                // Mostrar resultado
                document.getElementById('resultado').style.display = 'block';
                
                // Atualizar relatório
                carregarRelatorio();
                
                // Scroll suave para o resultado
                document.getElementById('resultado').scrollIntoView({ behavior: 'smooth' });
                
            } catch (error) {
                alert('Erro ao gerar crachá: ' + error.message);
            }
        }
        
        async function carregarRelatorio() {
            try {
                const response = await fetch('/relatorio');
                const dados = await response.json();
                
                const tbody = document.getElementById('corpo-tabela');
                tbody.innerHTML = '';
                
                if (dados.length === 0) {
                    tbody.innerHTML = '<tr><td colspan="4" style="text-align: center;">Nenhum crachá gerado ainda</td></tr>';
                } else {
                    dados.reverse().forEach((item, index) => {
                        const tr = document.createElement('tr');
                        tr.innerHTML = `
                            <td>${item.data_hora}</td>
                            <td>${item.apartamento}</td>
                            <td>${item.placa}</td>
                            <td>
                                <button class="btn-excluir" onclick="excluirCracha(${dados.length - 1 - index})">🗑️ Excluir</button>
                            </td>
                        `;
                        tbody.appendChild(tr);
                    });
                }
                
                document.getElementById('total-crachas').textContent = `Total: ${dados.length} crachás`;
                
            } catch (error) {
                console.error('Erro ao carregar relatório:', error);
            }
        }
        
        async function excluirCracha(index) {
            if (!confirm('Deseja realmente excluir este crachá?')) {
                return;
            }
            
            try {
                const response = await fetch(`/excluir/${index}`, {
                    method: 'DELETE'
                });
                
                if (response.ok) {
                    carregarRelatorio();
                } else {
                    alert('Erro ao excluir crachá');
                }
            } catch (error) {
                alert('Erro ao excluir crachá: ' + error.message);
            }
        }
        
        function exportarCSV() {
            window.location.href = '/exportar_csv';
        }
        
        function baixarCrachaImpressao() {
            if (!window.crachaImpressaoBase64) {
                alert('Gere um crachá primeiro!');
                return;
            }
            
            // Criar link de download
            const link = document.createElement('a');
            link.href = 'data:image/png;base64,' + window.crachaImpressaoBase64;
            link.download = 'Cracha-' + window.crachaApartamento + '.png';
            link.click();
        }
        
        // Carregar relatório ao iniciar
        carregarRelatorio();
        
        // Permitir Enter para gerar crachá
        document.getElementById('placa').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                gerarCracha();
            }
        });
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
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
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
        
        .logo {
            max-width: 150px;
            margin-bottom: 20px;
        }
        
        h1 {
            color: #667eea;
            margin-bottom: 10px;
            font-size: 24px;
        }
        
        .apartamento {
            font-size: 48px;
            font-weight: bold;
            color: #667eea;
            margin: 20px 0;
        }
        
        .placa-imagem {
            margin: 30px 0;
        }
        
        .placa-imagem img {
            max-width: 100%;
            height: auto;
            border-radius: 10px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }
        
        .info {
            background: #f5f5f5;
            padding: 20px;
            border-radius: 10px;
            margin-top: 20px;
        }
        
        .info p {
            margin: 10px 0;
            color: #333;
            font-size: 16px;
        }
        
        .data-hora {
            color: #666;
            font-size: 14px;
            margin-top: 20px;
        }
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
