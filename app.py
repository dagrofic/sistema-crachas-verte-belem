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
    """Lista completa de 244 apartamentos - Verte Belém"""
    apartamentos = []
    
    # BLOCO A - Apartamentos 006A até 158A
    for andar in range(0, 16):  # 0 a 15
        for apt in range(6, 9):  # 6, 7, 8
            if andar == 0:
                apartamentos.append(f"{apt:03d}A")
            else:
                apartamentos.append(f"{andar}{apt}A")
    
    # BLOCO B - Apartamentos 006B até 158B  
    for andar in range(0, 16):  # 0 a 15
        for apt in range(6, 9):  # 6, 7, 8
            if andar == 0:
                apartamentos.append(f"{apt:03d}B")
            else:
                apartamentos.append(f"{andar}{apt}B")
    
    return sorted(apartamentos)

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
    
    qr_code = gerar_qr_code(placa, apartamento)
    
    return jsonify({
        'success': True,
        'qr_code': qr_code
    })

@app.route('/salvar_cracha', methods=['POST'])
def salvar_cracha():
    data = request.get_json()
    
    dados = carregar_dados()
    dados.append({
        'apartamento': data.get('apartamento'),
        'placa': data.get('placa'),
        'data_hora': data.get('data_hora')
    })
    
    if salvar_dados(dados):
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'error': 'Erro ao salvar dados'})

@app.route('/relatorio')
def relatorio():
    dados = carregar_dados()
    # Ordenar por apartamento
    dados.sort(key=lambda x: x['apartamento'])
    
    return jsonify({
        'success': True,
        'dados': dados,
        'total': len(dados)
    })

@app.route('/excluir_cracha', methods=['POST'])
def excluir_cracha():
    data = request.get_json()
    index = data.get('index')
    
    dados = carregar_dados()
    if 0 <= index < len(dados):
        dados.pop(index)
        if salvar_dados(dados):
            return jsonify({'success': True})
    
    return jsonify({'success': False, 'error': 'Erro ao excluir registro'})

@app.route('/placa/<placa>/<apartamento>')
def mostrar_placa(placa, apartamento):
    return render_template_string(PLACA_TEMPLATE, placa=placa, apartamento=apartamento)

# Template HTML principal
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
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 15px;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
        }
        h1 {
            text-align: center;
            color: #333;
            margin-bottom: 30px;
            font-size: 28px;
            font-weight: 700;
        }
        .form-group {
            margin-bottom: 20px;
        }
        .form-group label {
            display: block;
            margin-bottom: 8px;
            font-weight: 600;
            color: #555;
            font-size: 16px;
        }
        .form-control {
            width: 100%;
            padding: 12px;
            border: 2px solid #ddd;
            border-radius: 10px;
            font-size: 16px;
            transition: all 0.3s;
        }
        .form-control:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }
        .btn {
            padding: 12px 24px;
            border: none;
            border-radius: 10px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            margin: 5px;
        }
        .btn-primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
        }
        .btn-secondary {
            background: #6c757d;
            color: white;
        }
        .btn-success {
            background: #28a745;
            color: white;
        }
        .btn-danger {
            background: #dc3545;
            color: white;
            padding: 8px 16px;
            font-size: 14px;
        }
        .relatorio-section {
            margin-top: 40px;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 15px;
        }
        .relatorio-titulo {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 20px;
            font-size: 20px;
            font-weight: 700;
            color: #333;
        }
        .relatorio-tabela {
            width: 100%;
            border-collapse: collapse;
            background: white;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        .relatorio-tabela th {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px;
            text-align: left;
            font-weight: 600;
        }
        .relatorio-tabela td {
            padding: 15px;
            border-bottom: 1px solid #eee;
        }
        .relatorio-tabela tr:hover {
            background: #f8f9fa;
        }
        .total-registros {
            text-align: center;
            margin-top: 15px;
            padding: 10px;
            background: #e7f3ff;
            border-radius: 10px;
            font-weight: 600;
            color: #0066cc;
        }
        .success-message {
            background: #d4edda;
            color: #155724;
            padding: 15px;
            border-radius: 10px;
            margin: 20px 0;
            text-align: center;
            font-weight: 600;
        }
        .cracha-container {
            display: none;
            margin: 30px auto;
            text-align: center;
        }
        .cracha-content {
            width: 340px;
            height: 454px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            border: 2px solid #ddd;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }
        .apartamento-numero {
            font-size: 64px;
            font-weight: 900;
            text-align: center;
            color: #333;
            margin-bottom: 20px;
        }
        .logo-verte {
            width: 140px;
            height: 140px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 50%;
            margin: 20px auto;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 32px;
            font-weight: 300;
        }
        .qr-code {
            width: 120px;
            height: 120px;
            margin: 20px auto;
            border: 2px solid #667eea;
            border-radius: 10px;
        }
        @media (max-width: 768px) {
            .container {
                padding: 15px;
            }
            h1 {
                font-size: 22px;
            }
            .cracha-content {
                width: 280px;
                height: 374px;
                padding: 20px;
            }
            .apartamento-numero {
                font-size: 48px;
            }
            .logo-verte {
                width: 100px;
                height: 100px;
                font-size: 24px;
            }
            .qr-code {
                width: 90px;
                height: 90px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🏢 Sistema Final - Crachás Verte Belém</h1>
        
        <div class="form-group">
            <label for="apartamento">🏠 Apartamento:</label>
            <select id="apartamento" class="form-control">
                <option value="">Selecione o apartamento</option>
                {{ apartamentos_options|safe }}
            </select>
        </div>
        
        <div class="form-group">
            <label for="placa">🚗 Placa do Veículo:</label>
            <input type="text" id="placa" class="form-control" 
                   placeholder="Ex: ABC1D34 ou ABC-1234" maxlength="8">
            <small style="color: #666; margin-top: 5px; display: block;">
                Formatos aceitos: ABC1D34 (Mercosul) ou ABC-1234 (Antigo)
            </small>
        </div>
        
        <button class="btn btn-primary" onclick="gerarCracha()">
            🎫 Gerar Crachá
        </button>
        
        <div id="successMessage"></div>
        
        <div id="crachaGerado" class="cracha-container">
            <div class="cracha-content">
                <div id="apartamentoNumero" class="apartamento-numero"></div>
                <div class="logo-verte">
                    <div>verte</div>
                    <div style="font-size: 14px;">Belém</div>
                </div>
                <img id="qrcode" class="qr-code" alt="QR Code">
            </div>
            
            <div style="margin-top: 20px;">
                <button class="btn btn-primary" onclick="imprimirCracha()">🖨️ Imprimir</button>
                <button class="btn btn-secondary" onclick="testarQR()">📱 Testar QR</button>
            </div>
        </div>
        
        <div class="relatorio-section">
            <div class="relatorio-titulo">
                <span>📊 Relatório de Crachás</span>
                <div>
                    <button class="btn btn-secondary" onclick="atualizarRelatorio()">
                        📋 Atualizar Relatório
                    </button>
                    <button class="btn btn-success" onclick="exportarCSV()">
                        📄 Exportar CSV
                    </button>
                </div>
            </div>
            
            <table class="relatorio-tabela">
                <thead>
                    <tr>
                        <th>Data/Hora</th>
                        <th>Apartamento</th>
                        <th>Placa</th>
                        <th>Ações</th>
                    </tr>
                </thead>
                <tbody id="relatorioBody">
                </tbody>
            </table>
            
            <div id="totalRegistros" class="total-registros"></div>
        </div>
    </div>

    <script>
        function gerarCracha() {
            const apartamento = document.getElementById('apartamento').value;
            const placa = document.getElementById('placa').value.toUpperCase();
            
            if (!apartamento || !placa) {
                alert('Por favor, preencha todos os campos!');
                return;
            }
            
            // Validar formato da placa
            const formatoMercosul = /^[A-Z]{3}[0-9][A-Z][0-9]{2}$/;
            const formatoAntigo = /^[A-Z]{3}-?[0-9]{4}$/;
            
            if (!formatoMercosul.test(placa) && !formatoAntigo.test(placa)) {
                alert('Formato de placa inválido! Use: ABC1D34 ou ABC-1234');
                return;
            }
            
            // Gerar QR Code
            fetch('/gerar_qr', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ placa: placa, apartamento: apartamento })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Exibir crachá
                    document.getElementById('apartamentoNumero').textContent = apartamento;
                    document.getElementById('qrcode').src = 'data:image/png;base64,' + data.qr_code;
                    document.getElementById('crachaGerado').style.display = 'block';
                    
                    // Salvar no servidor
                    return fetch('/salvar_cracha', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ 
                            placa: placa, 
                            apartamento: apartamento,
                            data_hora: new Date().toLocaleString('pt-BR')
                        })
                    });
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Mensagem de sucesso
                    document.getElementById('successMessage').innerHTML = 
                        '<div class="success-message">✅ Crachá gerado e salvo com sucesso!</div>';
                    
                    // Atualizar relatório
                    setTimeout(atualizarRelatorio, 500);
                    
                    // Limpar campos
                    document.getElementById('apartamento').value = '';
                    document.getElementById('placa').value = '';
                }
            })
            .catch(error => {
                console.error('Erro:', error);
                alert('Erro ao gerar crachá!');
            });
        }
        
        function atualizarRelatorio() {
            fetch('/relatorio')
            .then(response => response.json())
            .then(data => {
                const tbody = document.getElementById('relatorioBody');
                tbody.innerHTML = '';
                
                data.dados.forEach((item, index) => {
                    const row = tbody.insertRow();
                    row.innerHTML = `
                        <td>${item.data_hora}</td>
                        <td style="font-weight: 600;">${item.apartamento}</td>
                        <td style="font-family: monospace;">${item.placa}</td>
                        <td>
                            <button class="btn btn-danger" onclick="excluirRegistro(${index})">
                                🗑️ Excluir
                            </button>
                        </td>
                    `;
                });
                
                document.getElementById('totalRegistros').innerHTML = 
                    `📊 Total de registros: ${data.total}`;
            })
            .catch(error => {
                console.error('Erro ao carregar relatório:', error);
            });
        }
        
        function excluirRegistro(index) {
            if (confirm('Tem certeza que deseja excluir este registro?')) {
                fetch('/excluir_cracha', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ index: index })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        atualizarRelatorio();
                    }
                })
                .catch(error => {
                    console.error('Erro ao excluir:', error);
                });
            }
        }
        
        function exportarCSV() {
            fetch('/relatorio')
            .then(response => response.json())
            .then(data => {
                let csv = 'Data/Hora,Apartamento,Placa\\n';
                data.dados.forEach(item => {
                    csv += `${item.data_hora},${item.apartamento},${item.placa}\\n`;
                });
                
                const blob = new Blob([csv], { type: 'text/csv' });
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `crachas_verte_${new Date().toISOString().split('T')[0]}.csv`;
                a.click();
                window.URL.revokeObjectURL(url);
            });
        }
        
        function testarQR() {
            const apartamento = document.getElementById('apartamentoNumero').textContent;
            const placa = document.getElementById('placa').value || 'TEST123';
            window.open(`/placa/${placa}/${apartamento}`, '_blank');
        }
        
        function imprimirCracha() {
            const apartamento = document.getElementById('apartamentoNumero').textContent;
            const qrUrl = document.getElementById('qrcode').src;
            
            const printWindow = window.open('', '_blank');
            printWindow.document.write(`
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Crachá ${apartamento}</title>
                    <style>
                        @page { size: 18cm 12cm; margin: 0; }
                        body { margin: 0; padding: 0; font-family: Arial, sans-serif; }
                        .print-container { 
                            width: 18cm; height: 12cm; display: flex;
                            page-break-after: always;
                        }
                        .cracha-frente, .cracha-verso { 
                            width: 9cm; height: 12cm; padding: 1cm;
                            display: flex; flex-direction: column; justify-content: center;
                            background: white;
                        }
                        .apartamento-numero { 
                            font-size: 48px; font-weight: 900; 
                            color: #000; text-align: center; margin-bottom: 20px;
                        }
                        .logo-verte { 
                            width: 130px; height: 130px; 
                            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                            border-radius: 50%; margin: 15px auto;
                            display: flex; flex-direction: column; align-items: center; justify-content: center;
                            color: white; font-size: 28px; font-weight: 300;
                        }
                        .qr-code { width: 100px; height: 100px; margin: 15px auto; }
                        .verso-titulo { 
                            font-size: 16px; font-weight: 700; color: #667eea;
                            text-align: center; margin-bottom: 20px;
                        }
                        .verso-instrucoes { 
                            font-size: 12px; line-height: 1.6; color: #333;
                        }
                        .verso-instrucoes li { margin-bottom: 10px; }
                        .linha-corte { 
                            position: absolute; left: 9cm; top: 0; bottom: 0;
                            width: 2px; border-left: 2px dashed #ccc;
                        }
                    </style>
                </head>
                <body>
                    <div class="print-container">
                        <div class="cracha-frente">
                            <div class="apartamento-numero">${apartamento}</div>
                            <div class="logo-verte">
                                <div>verte</div>
                                <div style="font-size: 14px;">Belém</div>
                            </div>
                            <img class="qr-code" src="${qrUrl}" alt="QR Code">
                        </div>
                        <div class="cracha-verso">
                            <div class="verso-titulo">Instruções de Uso</div>
                            <ul class="verso-instrucoes">
                                <li>• Este crachá é individual e intransferível</li>
                                <li>• Mantenha esta identificação pendurada no retrovisor interno</li>
                                <li>• Extravio deve ser comunicado imediatamente</li>
                                <li>• Alterações no cadastro devem ser informadas à Administração</li>
                            </ul>
                        </div>
                        <div class="linha-corte"></div>
                    </div>
                </body>
                </html>
            `);
            
            printWindow.document.close();
            setTimeout(() => {
                printWindow.print();
                printWindow.close();
            }, 500);
        }
        
        // Carregar relatório ao iniciar
        document.addEventListener('DOMContentLoaded', function() {
            atualizarRelatorio();
        });
    </script>
</body>
</html>
'''

# Template da página de visualização de placa
PLACA_TEMPLATE = '''
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Veículo {{ placa }} - Verte Belém</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh; display: flex; align-items: center; justify-content: center;
            padding: 20px;
        }
        .container { 
            background: white; border-radius: 20px; padding: 40px; text-align: center;
            box-shadow: 0 20px 40px rgba(0,0,0,0.2); max-width: 600px; width: 100%;
        }
        .header { 
            color: #667eea; font-size: 28px; font-weight: 700;
            margin-bottom: 30px;
        }
        .info-card { 
            background: #f8f9fa; border-radius: 15px; padding: 25px; margin: 20px 0;
            border-left: 5px solid #667eea;
        }
        .info-label { 
            font-size: 14px; color: #666; margin-bottom: 8px;
            text-transform: uppercase; letter-spacing: 1px;
        }
        .info-value { 
            font-size: 32px; font-weight: 900; color: #333;
            font-family: monospace;
        }
        .apartamento-value { 
            font-size: 36px; font-weight: 900; color: #667eea;
        }
        .status-badge { 
            background: #28a745; color: white; padding: 15px 25px; border-radius: 50px;
            font-weight: 600; margin-top: 25px; display: inline-block;
        }
        .placa-mercosul {
            width: 400px; height: 200px; margin: 30px auto;
            background: linear-gradient(to bottom, #4169E1 0%, #4169E1 25%, #f5f5f5 25%, #f5f5f5 100%);
            position: relative; border-radius: 15px;
            box-shadow: 0 15px 35px rgba(0, 0, 0, 0.3);
            border: 3px solid #333;
        }
        .placa-mercosul::before {
            content: 'MERCOSUL'; position: absolute; top: 8px; left: 20px;
            color: white; font-size: 14px; font-weight: bold;
        }
        .placa-mercosul::after {
            content: 'BRASIL'; position: absolute; top: 8px; right: 80px;
            color: white; font-size: 18px; font-weight: bold;
        }
        .placa-numero {
            position: absolute; top: 58%; left: 50%;
            transform: translate(-50%, -50%);
            font-size: 48px; font-weight: 900; color: #000;
            letter-spacing: 4px;
        }
        @media (max-width: 768px) {
            .container { padding: 20px; }
            .header { font-size: 22px; }
            .info-value { font-size: 24px; }
            .placa-mercosul { width: 300px; height: 150px; }
            .placa-numero { font-size: 32px; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">🚗 Informações do Veículo</div>
        
        <div class="info-card">
            <div class="info-label">PLACA:</div>
            <div class="info-value">{{ placa }}</div>
        </div>
        
        <div class="placa-mercosul">
            <div class="placa-numero">{{ placa }}</div>
        </div>
        
        <div class="info-card">
            <div class="info-label">APARTAMENTO:</div>
            <div class="apartamento-value">{{ apartamento }}</div>
        </div>
        
        <div class="status-badge">
            ✅ Veículo autorizado - Condomínio Verte Belém
        </div>
    </div>
</body>
</html>
'''

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
