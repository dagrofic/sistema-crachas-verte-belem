from flask import Flask, request, jsonify, send_file, render_template_string
from flask_cors import CORS
import qrcode
import base64
from io import BytesIO
from datetime import datetime
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
    base_url = os.environ.get('BASE_URL', 'https://crachainsuranceandreinsuranceapps.com')
    url = f"{base_url}/placa/{placa}/{apartamento}"
    
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(url)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    
    return base64.b64encode(buffer.getvalue()).decode()

def obter_apartamentos():
    """Lista completa de 242 apartamentos - Verte Belém (Blocos A e B) - Conforme PDF Oficial"""
    # BLOCO A: 122 apartamentos (006A até 158A)
    bloco_a = [
        '006A', '007A', '011A', '012A', '013A', '014A', '015A', '016A', '017A', '018A',
        '021A', '022A', '023A', '024A', '025A', '026A', '027A', '028A', '031A', '032A',
        '033A', '034A', '035A', '036A', '037A', '038A', '041A', '042A', '043A', '044A',
        '045A', '046A', '047A', '048A', '051A', '052A', '053A', '054A', '055A', '056A',
        '057A', '058A', '061A', '062A', '063A', '064A', '065A', '066A', '067A', '068A',
        '071A', '072A', '073A', '074A', '075A', '076A', '077A', '078A', '081A', '082A',
        '083A', '084A', '085A', '086A', '087A', '088A', '091A', '092A', '093A', '094A',
        '095A', '096A', '097A', '098A', '101A', '102A', '103A', '104A', '105A', '106A',
        '107A', '108A', '111A', '112A', '113A', '114A', '115A', '116A', '117A', '118A',
        '121A', '122A', '123A', '124A', '125A', '126A', '127A', '128A', '131A', '132A',
        '133A', '134A', '135A', '136A', '137A', '138A', '141A', '142A', '143A', '144A',
        '145A', '146A', '147A', '148A', '151A', '152A', '153A', '154A', '155A', '156A',
        '157A', '158A'
    ]
    
    # BLOCO B: 120 apartamentos (006B até 158B, faltam 157B e 158B está duplicado no PDF como último)
    bloco_b = [
        '006B', '007B', '011B', '012B', '013B', '014B', '015B', '016B', '017B', '018B',
        '021B', '022B', '023B', '024B', '025B', '026B', '027B', '028B', '031B', '032B',
        '033B', '034B', '035B', '036B', '037B', '038B', '041B', '042B', '043B', '044B',
        '045B', '046B', '047B', '048B', '051B', '052B', '053B', '054B', '055B', '056B',
        '057B', '058B', '061B', '062B', '063B', '064B', '065B', '066B', '067B', '068B',
        '071B', '072B', '073B', '074B', '075B', '076B', '077B', '078B', '081B', '082B',
        '083B', '084B', '085B', '086B', '087B', '088B', '091B', '092B', '093B', '094B',
        '095B', '096B', '097B', '098B', '101B', '102B', '103B', '104B', '105B', '106B',
        '107B', '108B', '111B', '112B', '113B', '114B', '115B', '116B', '117B', '118B',
        '121B', '122B', '123B', '124B', '125B', '126B', '127B', '128B', '131B', '132B',
        '133B', '134B', '135B', '136B', '137B', '138B', '141B', '142B', '143B', '144B',
        '145B', '146B', '147B', '148B', '151B', '152B', '153B', '154B', '155B', '156B',
        '157B', '158B'
    ]
    
    # Retornar lista completa em ordem
    return bloco_a + bloco_b

@app.route('/')
def index():
    apartamentos = obter_apartamentos()
    apartamentos_options = ''.join([f'<option value="{apt}">{apt}</option>' for apt in apartamentos])
    
    return render_template_string(HTML_TEMPLATE, apartamentos_options=apartamentos_options)

@app.route('/gerar_qr', methods=['POST'])
def gerar_qr():
    data = request.get_json()
    placa = data.get('placa')
    apartamento = data.get('apartamento')
    
    if not placa or not apartamento:
        return jsonify({'error': 'Placa e apartamento são obrigatórios'}), 400
    
    # Gerar QR code
    qr_code_base64 = gerar_qr_code(placa, apartamento)
    
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
        'apartamento': apartamento
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

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sistema de Crachás - Verte Belém</title>
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
            max-width: 800px;
            width: 100%;
        }
        
        h1 {
            text-align: center;
            color: #667eea;
            margin-bottom: 30px;
            font-size: 28px;
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
            text-align: center;
            display: none;
        }
        
        #resultado img {
            max-width: 300px;
            border: 3px solid #667eea;
            border-radius: 10px;
            margin: 20px 0;
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
            padding: 8px 16px;
            font-size: 14px;
            width: auto;
            cursor: pointer;
        }
        
        .btn-excluir:hover {
            transform: translateY(-1px);
        }
        
        @media (max-width: 768px) {
            .container {
                padding: 20px;
            }
            
            h1 {
                font-size: 24px;
            }
            
            table {
                font-size: 14px;
            }
            
            th, td {
                padding: 10px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚗 Sistema de Crachás Veiculares<br>Condomínio Verte Belém</h1>
        
        <form id="crachaForm">
            <div class="form-group">
                <label for="apartamento">Apartamento (242 unidades - Blocos A e B)</label>
                <select id="apartamento" name="apartamento" required>
                    <option value="">Selecione o apartamento</option>
                    {{ apartamentos_options|safe }}
                </select>
            </div>
            
            <div class="form-group">
                <label for="placa">Placa do Veículo</label>
                <input type="text" id="placa" name="placa" placeholder="ABC1D23 ou ABC-1234" required>
                <div class="format-hint">Formatos aceitos: Mercosul (ABC1D23) ou Antigo (ABC-1234)</div>
            </div>
            
            <button type="submit">Gerar Crachá com QR Code</button>
        </form>
        
        <div id="resultado">
            <h2>✅ Crachá Gerado com Sucesso!</h2>
            <p><strong>Apartamento:</strong> <span id="resultApt"></span></p>
            <p><strong>Placa:</strong> <span id="resultPlaca"></span></p>
            <img id="qrcode" src="" alt="QR Code">
            <button onclick="imprimirQRCode()">🖨️ Imprimir Crachá</button>
        </div>
        
        <div class="relatorio">
            <h2>
                📋 Relatório de Crachás
                <div class="btn-group">
                    <button class="btn-secondary" onclick="atualizarRelatorio()">🔄 Atualizar</button>
                    <button class="btn-secondary" onclick="exportarCSV()">📥 Exportar CSV</button>
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
                <tbody id="corpoTabela">
                    <tr>
                        <td colspan="4" style="text-align: center;">Carregando...</td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>
    
    <script>
        document.getElementById('crachaForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const apartamento = document.getElementById('apartamento').value;
            const placa = document.getElementById('placa').value.toUpperCase();
            
            try {
                const response = await fetch('/gerar_qr', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ apartamento, placa })
                });
                
                const data = await response.json();
                
                if (response.ok) {
                    document.getElementById('resultApt').textContent = data.apartamento;
                    document.getElementById('resultPlaca').textContent = data.placa;
                    document.getElementById('qrcode').src = 'data:image/png;base64,' + data.qr_code;
                    document.getElementById('resultado').style.display = 'block';
                    
                    // Atualizar relatório
                    atualizarRelatorio();
                    
                    // Limpar formulário
                    document.getElementById('crachaForm').reset();
                } else {
                    alert('Erro: ' + data.error);
                }
            } catch (error) {
                alert('Erro ao gerar crachá: ' + error.message);
            }
        });
        
        async function atualizarRelatorio() {
            try {
                const response = await fetch('/relatorio');
                const dados = await response.json();
                
                const tbody = document.getElementById('corpoTabela');
                tbody.innerHTML = '';
                
                if (dados.length === 0) {
                    tbody.innerHTML = '<tr><td colspan="4" style="text-align: center;">Nenhum crachá cadastrado</td></tr>';
                } else {
                    dados.reverse().forEach((item, index) => {
                        const tr = document.createElement('tr');
                        tr.innerHTML = `
                            <td>${item.data_hora}</td>
                            <td>${item.apartamento}</td>
                            <td>${item.placa}</td>
                            <td><button class="btn-excluir" onclick="excluirCracha(${dados.length - 1 - index})">🗑️ Excluir</button></td>
                        `;
                        tbody.appendChild(tr);
                    });
                }
            } catch (error) {
                console.error('Erro ao carregar relatório:', error);
            }
        }
        
        async function excluirCracha(index) {
            if (confirm('Tem certeza que deseja excluir este crachá?')) {
                try {
                    const response = await fetch(`/excluir/${index}`, {
                        method: 'DELETE'
                    });
                    
                    if (response.ok) {
                        atualizarRelatorio();
                    } else {
                        alert('Erro ao excluir crachá');
                    }
                } catch (error) {
                    alert('Erro: ' + error.message);
                }
            }
        }
        
        function exportarCSV() {
            window.location.href = '/exportar_csv';
        }
        
        function imprimirQRCode() {
            window.print();
        }
        
        // Carregar relatório ao iniciar
        atualizarRelatorio();
    </script>
</body>
</html>
'''

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
