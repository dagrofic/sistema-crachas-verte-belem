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
    """Lista completa de 236 apartamentos - Verte Belém (Blocos A e B)"""
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
    <title>Sistema Final - Crachás Verte Belém</title>
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
        <h1>🏢 Sistema Final - Crachás Verte Belém</h1>
        
        <div class="form-group">
            <label for="apartamento">🏠 Apartamento:</label>
            <select id="apartamento" required>
                <option value="">Selecione o apartamento</option>
                {{ apartamentos_options|safe }}
            </select>
        </div>
        
        <div class="form-group">
            <label for="placa">🚗 Placa do Veículo:</label>
            <input type="text" id="placa" placeholder="Ex: ABC1D34 ou ABC-1234" required>
            <div class="format-hint">Formatos aceitos: ABC1D34 (Mercosul) ou ABC-1234 (Antigo)</div>
        </div>
        
        <button onclick="gerarCracha()">🎫 Gerar Crachá</button>
        
        <div id="resultado">
            <h2>✅ Crachá Gerado com Sucesso!</h2>
            <img id="qrcode" src="" alt="QR Code">
            <p><strong>Apartamento:</strong> <span id="apt-resultado"></span></p>
            <p><strong>Placa:</strong> <span id="placa-resultado"></span></p>
        </div>
        
        <div class="relatorio">
            <h2>
                📊 Relatório de Crachás
                <div class="btn-group">
                    <button class="btn-secondary" onclick="atualizarRelatorio()">🔄 Atualizar Relatório</button>
                    <button class="btn-secondary" onclick="exportarCSV()">📄 Exportar CSV</button>
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
                </tbody>
            </table>
            <div class="total" id="total-registros"></div>
        </div>
    </div>
    
    <script>
        function gerarCracha() {
            const apartamento = document.getElementById('apartamento').value;
            const placa = document.getElementById('placa').value;
            
            if (!apartamento || !placa) {
                alert('Por favor, preencha todos os campos!');
                return;
            }
            
            fetch('/gerar_qr', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ apartamento, placa })
            })
            .then(response => response.json())
            .then(data => {
                document.getElementById('qrcode').src = 'data:image/png;base64,' + data.qr_code;
                document.getElementById('apt-resultado').textContent = data.apartamento;
                document.getElementById('placa-resultado').textContent = data.placa;
                document.getElementById('resultado').style.display = 'block';
                
                // Limpar formulário
                document.getElementById('apartamento').value = '';
                document.getElementById('placa').value = '';
                
                // Atualizar relatório
                atualizarRelatorio();
            })
            .catch(error => {
                alert('Erro ao gerar crachá: ' + error);
            });
        }
        
        function atualizarRelatorio() {
            fetch('/relatorio')
            .then(response => response.json())
            .then(data => {
                const tbody = document.getElementById('corpo-tabela');
                tbody.innerHTML = '';
                
                data.forEach((item, index) => {
                    const tr = document.createElement('tr');
                    tr.innerHTML = `
                        <td>${item.data_hora}</td>
                        <td>${item.apartamento}</td>
                        <td>${item.placa}</td>
                        <td><button class="btn-excluir" onclick="excluirRegistro(${index})">🗑️ Excluir</button></td>
                    `;
                    tbody.appendChild(tr);
                });
                
                document.getElementById('total-registros').textContent = `📊 Total de registros: ${data.length}`;
            });
        }
        
        function excluirRegistro(index) {
            if (confirm('Deseja realmente excluir este registro?')) {
                fetch(`/excluir/${index}`, {
                    method: 'DELETE'
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        atualizarRelatorio();
                    }
                });
            }
        }
        
        function exportarCSV() {
            window.location.href = '/exportar_csv';
        }
        
        // Carregar relatório ao iniciar
        atualizarRelatorio();
    </script>
</body>
</html>
'''

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
