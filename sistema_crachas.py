from flask import Flask, render_template_string, request, jsonify
from flask_cors import CORS
import json
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Lista completa de apartamentos (244 unidades)
apartamentos = [
    # BLOCO A
    "006A", "007A", "011A", "012A", "013A", "014A", "015A", "016A", "017A", "018A",
    "021A", "022A", "023A", "024A", "025A", "026A", "027A", "028A",
    "031A", "032A", "033A", "034A", "035A", "036A", "037A", "038A",
    "041A", "042A", "043A", "044A", "045A", "046A", "047A", "048A",
    "051A", "052A", "053A", "054A", "055A", "056A", "057A", "058A",
    "061A", "062A", "063A", "064A", "065A", "066A", "067A", "068A",
    "071A", "072A", "073A", "074A", "075A", "076A", "077A", "078A",
    "081A", "082A", "083A", "084A", "085A", "086A", "087A", "088A",
    "091A", "092A", "093A", "094A", "095A", "096A", "097A", "098A",
    "101A", "102A", "103A", "104A", "105A", "106A", "107A", "108A",
    "111A", "112A", "113A", "114A", "115A", "116A", "117A", "118A",
    "121A", "122A", "123A", "124A", "125A", "126A", "127A", "128A",
    "131A", "132A", "133A", "134A", "135A", "136A", "137A", "138A",
    "141A", "142A", "143A", "144A", "145A", "146A", "147A", "148A",
    "151A", "152A", "153A", "154A", "155A", "156A", "157A", "158A",
    # BLOCO B
    "006B", "007B", "011B", "012B", "013B", "014B", "015B", "016B", "017B", "018B",
    "021B", "022B", "023B", "024B", "025B", "026B", "027B", "028B",
    "031B", "032B", "033B", "034B", "035B", "036B", "037B", "038B",
    "041B", "042B", "043B", "044B", "045B", "046B", "047B", "048B",
    "051B", "052B", "053B", "054B", "055B", "056B", "057B", "058B",
    "061B", "062B", "063B", "064B", "065B", "066B", "067B", "068B",
    "071B", "072B", "073B", "074B", "075B", "076B", "077B", "078B",
    "081B", "082B", "083B", "084B", "085B", "086B", "087B", "088B",
    "091B", "092B", "093B", "094B", "095B", "096B", "097B", "098B",
    "101B", "102B", "103B", "104B", "105B", "106B", "107B", "108B",
    "111B", "112B", "113B", "114B", "115B", "116B", "117B", "118B",
    "121B", "122B", "123B", "124B", "125B", "126B", "127B", "128B",
    "131B", "132B", "133B", "134B", "135B", "136B", "137B", "138B",
    "141B", "142B", "143B", "144B", "145B", "146B", "147B", "148B",
    "151B", "152B", "153B", "154B", "155B", "156B", "157B", "158B"
]

@app.route('/')
def index():
    return render_template_string('''
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sistema Premium de Crachás - Verte Belém</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh; padding: 20px;
            animation: backgroundShift 10s ease-in-out infinite alternate;
        }
        
        @keyframes backgroundShift {
            0% { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
            100% { background: linear-gradient(135deg, #764ba2 0%, #667eea 100%); }
        }
        
        .container {
            max-width: 900px; margin: 0 auto; background: rgba(255,255,255,0.95);
            border-radius: 25px; padding: 40px; 
            box-shadow: 0 30px 80px rgba(0,0,0,0.15);
            backdrop-filter: blur(20px);
            animation: slideUp 0.8s ease-out;
        }
        
        @keyframes slideUp {
            from { opacity: 0; transform: translateY(50px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .titulo {
            text-align: center; background: linear-gradient(45deg, #B91C3C, #DC2626);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
            font-size: 32px; font-weight: 900; margin-bottom: 40px;
            text-shadow: 0 4px 8px rgba(185, 28, 60, 0.3);
            animation: titleGlow 2s ease-in-out infinite alternate;
        }
        
        @keyframes titleGlow {
            from { filter: drop-shadow(0 0 5px rgba(185, 28, 60, 0.5)); }
            to { filter: drop-shadow(0 0 15px rgba(185, 28, 60, 0.8)); }
        }
        
        .form-group { 
            margin-bottom: 25px; 
            animation: fadeInLeft 0.6s ease-out forwards;
            opacity: 0;
        }
        
        .form-group:nth-child(1) { animation-delay: 0.2s; }
        .form-group:nth-child(2) { animation-delay: 0.4s; }
        .form-group:nth-child(3) { animation-delay: 0.6s; }
        
        @keyframes fadeInLeft {
            from { opacity: 0; transform: translateX(-30px); }
            to { opacity: 1; transform: translateX(0); }
        }
        
        label { 
            display: block; font-weight: 700; color: #1f2937;
            margin-bottom: 10px; font-size: 16px;
            text-transform: uppercase; letter-spacing: 0.5px;
        }
        
        select, input {
            width: 100%; padding: 16px 20px; border: 3px solid #e5e7eb;
            border-radius: 15px; font-size: 16px; font-weight: 500;
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            background: linear-gradient(145deg, #ffffff, #f8fafc);
        }
        
        select:focus, input:focus {
            outline: none; border-color: #B91C3C; 
            box-shadow: 0 0 0 4px rgba(185, 28, 60, 0.15);
            transform: translateY(-2px);
            background: #ffffff;
        }
        
        .btn {
            background: linear-gradient(145deg, #B91C3C, #DC2626);
            color: white; border: none; padding: 16px 32px;
            border-radius: 15px; font-size: 16px; font-weight: 700;
            cursor: pointer; margin: 8px; position: relative;
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            text-transform: uppercase; letter-spacing: 1px;
            overflow: hidden;
        }
        
        .btn::before {
            content: ''; position: absolute; top: 0; left: -100%;
            width: 100%; height: 100%; 
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
            transition: left 0.6s;
        }
        
        .btn:hover {
            transform: translateY(-3px) scale(1.02);
            box-shadow: 0 15px 35px rgba(185, 28, 60, 0.4);
        }
        
        .btn:hover::before { left: 100%; }
        
        .btn:active { transform: translateY(-1px) scale(0.98); }
        
        .btn-secondary { 
            background: linear-gradient(145deg, #6b7280, #4b5563);
        }
        .btn-secondary:hover { 
            box-shadow: 0 15px 35px rgba(107, 114, 128, 0.4);
        }
        
        .btn-success { 
            background: linear-gradient(145deg, #059669, #047857);
        }
        .btn-success:hover { 
            box-shadow: 0 15px 35px rgba(5, 150, 105, 0.4);
        }
        
        .success-message {
            background: linear-gradient(145deg, #10b981, #059669);
            color: white; padding: 20px; border-radius: 15px;
            margin: 25px 0; text-align: center; font-weight: 700;
            font-size: 18px; box-shadow: 0 10px 25px rgba(16, 185, 129, 0.3);
            animation: successPulse 0.6s ease-out;
        }
        
        @keyframes successPulse {
            0% { transform: scale(0.8); opacity: 0; }
            50% { transform: scale(1.05); }
            100% { transform: scale(1); opacity: 1; }
        }
        
        .cracha-container {
            background: linear-gradient(145deg, #f9fafb, #ffffff);
            border: 3px solid #e5e7eb; border-radius: 20px;
            padding: 40px; margin: 30px 0; text-align: center;
            display: none; position: relative; overflow: hidden;
            box-shadow: 0 20px 50px rgba(0,0,0,0.1);
        }
        
        .cracha-container::before {
            content: ''; position: absolute; top: -50%; left: -50%;
            width: 200%; height: 200%; 
            background: conic-gradient(from 0deg, transparent, rgba(185, 28, 60, 0.1), transparent);
            animation: rotate 4s linear infinite;
        }
        
        @keyframes rotate {
            100% { transform: rotate(360deg); }
        }
        
        .cracha-content {
            position: relative; z-index: 1; background: white;
            border-radius: 15px; padding: 20px;
        }
        
        .apartamento-numero {
            font-size: 56px; font-weight: 900; 
            background: linear-gradient(45deg, #1f2937, #374151);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
            margin-bottom: 25px; animation: numberFloat 3s ease-in-out infinite;
        }
        
        @keyframes numberFloat {
            0%, 100% { transform: translateY(0px); }
            50% { transform: translateY(-5px); }
        }
        
        .logo-verte-img {
            width: 140px; height: 140px; 
            border-radius: 50%; margin: 25px auto; display: block;
            box-shadow: 0 15px 35px rgba(185, 28, 60, 0.4);
            animation: logoSpin 6s ease-in-out infinite;
            object-fit: cover;
        }
        
        @keyframes logoSpin {
            0%, 100% { transform: rotate(0deg) scale(1); }
            25% { transform: rotate(5deg) scale(1.05); }
            50% { transform: rotate(0deg) scale(1); }
            75% { transform: rotate(-5deg) scale(1.05); }
        }
        
        .qr-code {
            width: 140px; height: 140px; margin: 25px auto;
            border: 3px solid #e5e7eb; border-radius: 15px;
            transition: transform 0.3s ease;
            box-shadow: 0 10px 25px rgba(0,0,0,0.1);
        }
        
        .qr-code:hover {
            transform: scale(1.1) rotate(2deg);
        }
        
        .relatorio-section { 
            margin-top: 50px; 
            animation: fadeInUp 0.8s ease-out 0.8s both;
        }
        
        @keyframes fadeInUp {
            from { opacity: 0; transform: translateY(30px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .relatorio-titulo {
            font-size: 24px; font-weight: 900; 
            background: linear-gradient(45deg, #1f2937, #374151);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
            margin-bottom: 25px; display: flex; align-items: center;
        }
        
        .relatorio-tabela {
            width: 100%; border-collapse: collapse; margin-top: 20px;
            background: white; border-radius: 15px; overflow: hidden;
            box-shadow: 0 15px 40px rgba(0,0,0,0.1);
        }
        
        .relatorio-tabela th {
            background: linear-gradient(145deg, #B91C3C, #DC2626);
            color: white; padding: 20px; text-align: left; 
            font-weight: 700; font-size: 16px;
            text-transform: uppercase; letter-spacing: 0.5px;
        }
        
        .relatorio-tabela td {
            padding: 18px 20px; border-bottom: 1px solid #f3f4f6;
            font-weight: 500; transition: background 0.3s ease;
        }
        
        .relatorio-tabela tr:hover { 
            background: linear-gradient(145deg, #f9fafb, #f3f4f6);
            transform: scale(1.01);
        }
        
        .btn-excluir {
            background: linear-gradient(145deg, #dc2626, #b91c1c);
            color: white; border: none; padding: 8px 16px;
            border-radius: 10px; cursor: pointer; font-size: 12px;
            font-weight: 600; transition: all 0.3s ease;
        }
        
        .btn-excluir:hover { 
            background: linear-gradient(145deg, #b91c1c, #991b1b);
            transform: scale(1.1);
            box-shadow: 0 5px 15px rgba(220, 38, 38, 0.4);
        }
        
        .total-registros {
            margin-top: 20px; font-weight: 700; font-size: 18px;
            text-align: center; padding: 15px;
            background: linear-gradient(145deg, #f3f4f6, #e5e7eb);
            border-radius: 15px; color: #374151;
        }
        
        .placa-container-real {
            width: 100%; display: flex; justify-content: center; 
            margin: 40px 0; perspective: 1000px;
        }
        
        .placa-mercosul-real {
            width: 500px; height: 250px;
            background-image: url('https://files.manuscdn.com/user_upload_by_module/session_file/310419663029166562/nXacdBCozrTTswlB.png');
            background-size: cover; background-position: center; background-repeat: no-repeat;
            position: relative; border-radius: 20px; 
            box-shadow: 0 25px 60px rgba(0,0,0,0.3);
            margin: 30px auto; display: flex; align-items: center; justify-content: center;
            transform: perspective(1000px) rotateX(10deg) rotateY(-3deg);
            transition: all 0.6s cubic-bezier(0.4, 0, 0.2, 1);
            animation: plateFloat 4s ease-in-out infinite;
        }
        
        @keyframes plateFloat {
            0%, 100% { transform: perspective(1000px) rotateX(10deg) rotateY(-3deg) translateY(0px); }
            50% { transform: perspective(1000px) rotateX(10deg) rotateY(-3deg) translateY(-10px); }
        }
        
        .placa-mercosul-real:hover {
            transform: perspective(1000px) rotateX(0deg) rotateY(0deg) scale(1.08);
            box-shadow: 0 40px 80px rgba(0,0,0,0.4);
        }
        
        .placa-numero-overlay {
            position: absolute; top: 58%; left: 50%;
            transform: translate(-50%, -50%); font-size: 52px;
            font-weight: 900; color: #000;
            font-family: 'Arial Black', Arial, sans-serif;
            letter-spacing: 4px; 
            text-shadow: 0 3px 6px rgba(255,255,255,0.8);
            z-index: 10; animation: textGlow 2s ease-in-out infinite alternate;
        }
        
        @keyframes textGlow {
            from { text-shadow: 0 3px 6px rgba(255,255,255,0.8); }
            to { text-shadow: 0 3px 6px rgba(255,255,255,0.8), 0 0 20px rgba(0,0,0,0.3); }
        }
        
        #placaGerada { 
            display: none; 
            animation: slideInFromBottom 0.8s ease-out;
        }
        
        @keyframes slideInFromBottom {
            from { opacity: 0; transform: translateY(50px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .loading {
            display: inline-block; width: 20px; height: 20px;
            border: 3px solid rgba(255,255,255,0.3);
            border-radius: 50%; border-top-color: #fff;
            animation: spin 1s ease-in-out infinite;
        }
        
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
        
        .status-indicator {
            position: fixed; top: 20px; right: 20px;
            padding: 10px 20px; border-radius: 25px;
            background: linear-gradient(145deg, #10b981, #059669);
            color: white; font-weight: 600; font-size: 14px;
            box-shadow: 0 10px 25px rgba(16, 185, 129, 0.3);
            z-index: 1000; animation: slideInRight 0.5s ease-out;
        }
        
        @keyframes slideInRight {
            from { opacity: 0; transform: translateX(100px); }
            to { opacity: 1; transform: translateX(0); }
        }
        
        .offline { 
            background: linear-gradient(145deg, #dc2626, #b91c1c);
            box-shadow: 0 10px 25px rgba(220, 38, 38, 0.3);
        }
        
        @media (max-width: 768px) {
            .container { padding: 20px; margin: 10px; }
            .titulo { font-size: 24px; }
            .apartamento-numero { font-size: 42px; }
            .placa-mercosul-real { width: 100%; max-width: 400px; height: 200px; }
            .placa-numero-overlay { font-size: 48px; }
        }
    </style>
</head>
<body>
    <div class="status-indicator" id="statusIndicator">
        🟢 Sistema Online
    </div>

    <div class="container">
        <h1 class="titulo">🏢 Sistema Premium de Crachás - Verte Belém</h1>
        
        <div class="form-group">
            <label for="apartamento">🏢 Apartamento:</label>
            <select id="apartamento">
                <option value="">Selecione o apartamento</option>
                {% for apt in apartamentos %}
                <option value="{{ apt }}">{{ apt }}</option>
                {% endfor %}
            </select>
        </div>
        
        <div class="form-group">
            <label for="placa">🚗 Placa do Veículo:</label>
            <input type="text" id="placa" placeholder="Ex: ABC1D34 ou ABC-1234" maxlength="8">
        </div>
        
        <div class="form-group">
            <button class="btn" onclick="gerarCracha()" id="btnGerar">
                🎫 Gerar Crachá Premium
            </button>
        </div>
        
        <div id="successMessage" style="display: none;" class="success-message">
            ✅ Crachá gerado com sucesso e salvo permanentemente!
        </div>
        
        <div id="crachaGerado" class="cracha-container">
            <div class="cracha-content">
                <div id="apartamentoNumero" class="apartamento-numero"></div>
                <img src="https://files.manuscdn.com/user_upload_by_module/session_file/310419663029166562/GnYRAlDfopOgFVRq.jpeg" 
                     alt="Verte Belém" class="logo-verte-img">
                <img id="qrcode" class="qr-code" alt="QR Code">
            </div>
        </div>
        
        <div style="text-align: center; margin: 30px 0;">
            <button class="btn" onclick="imprimirCracha()">🖨️ Imprimir Premium</button>
            <button class="btn btn-secondary" onclick="testarQR()">📱 Testar QR</button>
            <button class="btn btn-success" onclick="gerarPlacaReal()">🖼️ Placa Real 3D</button>
        </div>
        
        <div id="placaGerada">
            <h3 style="text-align: center; color: #B91C3C; margin: 30px 0; font-size: 24px; font-weight: 900;">
                🚗 Placa Mercosul Real 3D:
            </h3>
            <div id="placaContainer"></div>
        </div>
        
        <div class="relatorio-section">
            <div class="relatorio-titulo">
                📊 Relatório Premium de Crachás
                <button class="btn btn-secondary" onclick="atualizarRelatorio()" style="margin-left: auto;">
                    📋 Atualizar Relatório
                </button>
                <button class="btn btn-success" onclick="exportarCSV()">📄 Exportar Excel</button>
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
            
            <div id="totalRegistros" class="total-registros">📊 Total: 0 registros</div>
        </div>
    </div>

    <script>
        // Sistema Premium de Persistência Híbrida
        class SistemaPremium {
            constructor() {
                this.storageKey = 'verteBelem_crachas_premium';
                this.apartamentosOrdem = {{ apartamentos | tojson }};
                this.inicializar();
            }
            
            inicializar() {
                console.log('🚀 [SISTEMA PREMIUM] Inicializando...');
                this.carregarDados();
                this.atualizarInterface();
                this.configurarEventos();
                this.mostrarStatus('🟢 Sistema Premium Online');
            }
            
            carregarDados() {
                try {
                    const dados = localStorage.getItem(this.storageKey);
                    if (dados) {
                        this.registros = JSON.parse(dados);
                        console.log(`✅ [PREMIUM] ${this.registros.length} registros carregados do localStorage`);
                    } else {
                        // Dados iniciais premium
                        this.registros = [
                            {
                                apartamento: '075A',
                                placa: 'XYZ-9876',
                                data_hora: '15/09/2025 08:15:00',
                                id: this.gerarId()
                            },
                            {
                                apartamento: '143B',
                                placa: 'ABC1D34',
                                data_hora: '15/09/2025 08:00:00',
                                id: this.gerarId()
                            }
                        ];
                        this.salvarDados();
                        console.log('🎯 [PREMIUM] Dados iniciais criados');
                    }
                } catch (error) {
                    console.error('❌ [PREMIUM] Erro ao carregar dados:', error);
                    this.registros = [];
                }
            }
            
            salvarDados() {
                try {
                    localStorage.setItem(this.storageKey, JSON.stringify(this.registros));
                    console.log(`💾 [PREMIUM] ${this.registros.length} registros salvos no localStorage`);
                    
                    // Backup em sessionStorage
                    sessionStorage.setItem(this.storageKey + '_backup', JSON.stringify(this.registros));
                    
                    // Trigger evento para sincronização entre abas
                    window.dispatchEvent(new CustomEvent('dadosAtualizados', { 
                        detail: { total: this.registros.length } 
                    }));
                    
                    return true;
                } catch (error) {
                    console.error('❌ [PREMIUM] Erro ao salvar dados:', error);
                    return false;
                }
            }
            
            adicionarRegistro(apartamento, placa) {
                const novoRegistro = {
                    apartamento,
                    placa: placa.toUpperCase(),
                    data_hora: new Date().toLocaleString('pt-BR'),
                    id: this.gerarId()
                };
                
                this.registros.push(novoRegistro);
                const sucesso = this.salvarDados();
                
                if (sucesso) {
                    console.log('✅ [PREMIUM] Registro adicionado:', novoRegistro);
                    this.mostrarStatus('✅ Crachá salvo com sucesso!');
                    return true;
                } else {
                    console.error('❌ [PREMIUM] Falha ao salvar registro');
                    this.mostrarStatus('❌ Erro ao salvar', true);
                    return false;
                }
            }
            
            removerRegistro(index) {
                const registrosOrdenados = this.obterRegistrosOrdenados();
                if (index >= 0 && index < registrosOrdenados.length) {
                    const registroParaRemover = registrosOrdenados[index];
                    const indexOriginal = this.registros.findIndex(r => r.id === registroParaRemover.id);
                    
                    if (indexOriginal !== -1) {
                        const removido = this.registros.splice(indexOriginal, 1)[0];
                        this.salvarDados();
                        console.log('🗑️ [PREMIUM] Registro removido:', removido);
                        this.mostrarStatus('🗑️ Registro excluído');
                        return true;
                    }
                }
                return false;
            }
            
            obterRegistrosOrdenados() {
                return this.registros.sort((a, b) => {
                    const indexA = this.apartamentosOrdem.indexOf(a.apartamento);
                    const indexB = this.apartamentosOrdem.indexOf(b.apartamento);
                    
                    if (indexA === -1) return 1;
                    if (indexB === -1) return -1;
                    return indexA - indexB;
                });
            }
            
            atualizarInterface() {
                const registrosOrdenados = this.obterRegistrosOrdenados();
                const tbody = document.getElementById('relatorioBody');
                
                if (!tbody) return;
                
                tbody.innerHTML = '';
                
                registrosOrdenados.forEach((registro, index) => {
                    const row = tbody.insertRow();
                    row.style.animation = `fadeInUp 0.5s ease-out ${index * 0.1}s both`;
                    row.innerHTML = `
                        <td><strong>${registro.data_hora}</strong></td>
                        <td><span style="color: #B91C3C; font-weight: 900; font-size: 16px;">${registro.apartamento}</span></td>
                        <td><span style="font-family: monospace; font-weight: 700;">${registro.placa}</span></td>
                        <td>
                            <button class="btn-excluir" onclick="sistema.excluirComConfirmacao(${index})">
                                🗑️ Excluir
                            </button>
                        </td>
                    `;
                });
                
                const total = this.registros.length;
                document.getElementById('totalRegistros').innerHTML = `
                    📊 Total: <strong style="color: #B91C3C;">${total}</strong> registros salvos permanentemente
                `;
                
                console.log(`📊 [PREMIUM] Interface atualizada: ${total} registros`);
            }
            
            excluirComConfirmacao(index) {
                const registrosOrdenados = this.obterRegistrosOrdenados();
                const registro = registrosOrdenados[index];
                
                if (confirm(`🗑️ Deseja realmente excluir o registro:\\n\\n🏢 Apartamento: ${registro.apartamento}\\n🚗 Placa: ${registro.placa}\\n📅 Data: ${registro.data_hora}`)) {
                    if (this.removerRegistro(index)) {
                        this.atualizarInterface();
                    }
                }
            }
            
            gerarId() {
                return Date.now().toString(36) + Math.random().toString(36).substr(2);
            }
            
            mostrarStatus(mensagem, erro = false) {
                const indicator = document.getElementById('statusIndicator');
                if (indicator) {
                    indicator.textContent = mensagem;
                    indicator.className = 'status-indicator' + (erro ? ' offline' : '');
                    
                    if (!erro) {
                        setTimeout(() => {
                            indicator.textContent = '🟢 Sistema Premium Online';
                            indicator.className = 'status-indicator';
                        }, 3000);
                    }
                }
            }
            
            configurarEventos() {
                // Sincronização entre abas
                window.addEventListener('dadosAtualizados', (e) => {
                    console.log('🔄 [PREMIUM] Sincronizando dados entre abas');
                    this.carregarDados();
                    this.atualizarInterface();
                });
                
                // Backup automático a cada 30 segundos
                setInterval(() => {
                    this.salvarDados();
                }, 30000);
            }
            
            exportarCSV() {
                const registrosOrdenados = this.obterRegistrosOrdenados();
                let csv = 'Data/Hora,Apartamento,Placa\\n';
                
                registrosOrdenados.forEach(registro => {
                    csv += `"${registro.data_hora}","${registro.apartamento}","${registro.placa}"\\n`;
                });
                
                const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `relatorio_crachas_verte_belem_${new Date().toISOString().split('T')[0]}.csv`;
                a.click();
                window.URL.revokeObjectURL(url);
                
                this.mostrarStatus('📄 CSV exportado com sucesso!');
            }
        }
        
        // Instância global do sistema premium
        const sistema = new SistemaPremium();
        let dadosUltimoCracha = {};
        
        // Funções da interface
        async function gerarCracha() {
            const apartamento = document.getElementById('apartamento').value;
            const placa = document.getElementById('placa').value.toUpperCase().trim();
            
            if (!apartamento || !placa) {
                alert('🚨 Preencha todos os campos!');
                return;
            }
            
            // Animação de loading
            const btn = document.getElementById('btnGerar');
            const textoOriginal = btn.innerHTML;
            btn.innerHTML = '<span class="loading"></span> Gerando...';
            btn.disabled = true;
            
            try {
                // Salvar no sistema premium
                const sucesso = sistema.adicionarRegistro(apartamento, placa);
                
                if (sucesso) {
                    // Mostrar crachá com animação
                    document.getElementById('apartamentoNumero').textContent = apartamento;
                    const qrUrl = `https://api.qrserver.com/v1/create-qr-code/?size=140x140&data=${encodeURIComponent(window.location.origin + '/placa/' + placa + '/' + apartamento)}`;
                    document.getElementById('qrcode').src = qrUrl;
                    
                    // Animações
                    document.getElementById('crachaGerado').style.display = 'block';
                    document.getElementById('successMessage').style.display = 'block';
                    
                    dadosUltimoCracha = { apartamento, placa };
                    
                    // Atualizar interface
                    setTimeout(() => {
                        sistema.atualizarInterface();
                    }, 500);
                    
                    // Limpar formulário
                    document.getElementById('apartamento').value = '';
                    document.getElementById('placa').value = '';
                    
                    // Esconder mensagem
                    setTimeout(() => {
                        document.getElementById('successMessage').style.display = 'none';
                    }, 4000);
                } else {
                    alert('❌ Erro ao salvar o crachá. Tente novamente.');
                }
            } catch (error) {
                console.error('❌ Erro ao gerar crachá:', error);
                alert('❌ Erro inesperado. Tente novamente.');
            } finally {
                // Restaurar botão
                btn.innerHTML = textoOriginal;
                btn.disabled = false;
            }
        }
        
        function atualizarRelatorio() {
            sistema.atualizarInterface();
            sistema.mostrarStatus('🔄 Relatório sincronizado!');
        }
        
        function testarQR() {
            if (!dadosUltimoCracha.apartamento || !dadosUltimoCracha.placa) {
                alert('🚨 Gere um crachá primeiro!');
                return;
            }
            const { apartamento, placa } = dadosUltimoCracha;
            window.open(`/placa/${placa}/${apartamento}`, '_blank');
        }
        
        function gerarPlacaReal() {
            if (!dadosUltimoCracha.apartamento || !dadosUltimoCracha.placa) {
                alert('🚨 Gere um crachá primeiro!');
                return;
            }
            
            const { apartamento, placa } = dadosUltimoCracha;
            
            document.getElementById('placaContainer').innerHTML = `
                <div class="placa-container-real">
                    <div class="placa-mercosul-real">
                        <div class="placa-numero-overlay">${placa}</div>
                    </div>
                </div>
            `;
            document.getElementById('placaGerada').style.display = 'block';
            
            sistema.mostrarStatus('🖼️ Placa 3D gerada!');
        }
        
        function imprimirCracha() {
            if (!dadosUltimoCracha.apartamento || !dadosUltimoCracha.placa) {
                alert('🚨 Gere um crachá primeiro!');
                return;
            }
            
            const { apartamento, placa } = dadosUltimoCracha;
            const qrUrl = `https://api.qrserver.com/v1/create-qr-code/?size=140x140&data=${encodeURIComponent(window.location.origin + '/placa/' + placa + '/' + apartamento)}`;
            
            const printWindow = window.open('', '_blank');
            printWindow.document.write(`
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Crachá Premium - ${apartamento}</title>
                    <style>
                        @page { size: 18cm 12cm; margin: 0; }
                        body { 
                            width: 18cm; height: 12cm; margin: 0; padding: 0; 
                            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                            display: flex; background: white;
                        }
                        .cracha-frente {
                            width: 9cm; height: 12cm; padding: 0.8cm;
                            display: flex; flex-direction: column; align-items: center; justify-content: space-evenly;
                            border-right: 2px dashed #B91C3C;
                            background: linear-gradient(145deg, #ffffff, #f8fafc);
                        }
                        .cracha-verso {
                            width: 9cm; height: 12cm; padding: 1cm;
                            display: flex; flex-direction: column; justify-content: center;
                            background: linear-gradient(145deg, #f8fafc, #ffffff);
                        }
                        .apartamento-numero { 
                            font-size: 48px; font-weight: 900; 
                            color: #000000;
                        }
                        .logo-verte { 
                            width: 130px; height: 130px; 
                            background: linear-gradient(145deg, #B91C3C, #DC2626);
                            border-radius: 50%; display: flex; flex-direction: column; 
                            align-items: center; justify-content: center;
                            color: white; font-size: 30px; font-weight: 300;
                            box-shadow: 0 10px 25px rgba(185, 28, 60, 0.3);
                        }
                        .qr-code { 
                            width: 140px; height: 140px; 
                            border: 3px solid #B91C3C; border-radius: 15px;
                            box-shadow: 0 8px 20px rgba(185, 28, 60, 0.2);
                        }
                        .verso-titulo { 
                            font-size: 20px; font-weight: 900; color: #B91C3C; 
                            text-align: center; margin-bottom: 25px;
                            text-transform: uppercase; letter-spacing: 1px;
                        }
                        .verso-paragrafo { 
                            font-size: 13px; line-height: 1.5; color: #1f2937; 
                            margin-bottom: 18px; text-align: justify; 
                            padding-left: 15px; position: relative; font-weight: 500;
                        }
                        .verso-paragrafo::before { 
                            content: "•"; color: #B91C3C; font-weight: 900; 
                            position: absolute; left: 0; font-size: 16px;
                        }
                        * { -webkit-print-color-adjust: exact !important; color-adjust: exact !important; }
                    </style>
                </head>
                <body>
                    <div class="cracha-frente">
                        <div class="apartamento-numero">${apartamento}</div>
                        <img src="https://files.manuscdn.com/user_upload_by_module/session_file/310419663029166562/GnYRAlDfopOgFVRq.jpeg" 
                             alt="Verte Belém" style="width: 130px; height: 130px; border-radius: 50%; object-fit: cover; box-shadow: 0 10px 25px rgba(185, 28, 60, 0.3);">
                        <img class="qr-code" src="${qrUrl}" alt="QR Code">
                    </div>
                    <div class="cracha-verso">
                        <div class="verso-titulo">Instruções Premium de Uso</div>
                        <div class="verso-paragrafo">Este crachá é individual e intransferível</div>
                        <div class="verso-paragrafo">Mantenha esta identificação pendurada no retrovisor interno enquanto estiver dentro do condomínio</div>
                        <div class="verso-paragrafo">Extravio do mesmo deverá ser comunicado ao Administrador do Condomínio imediatamente</div>
                        <div class="verso-paragrafo">Qualquer alteração no cadastro do veículo, deverá ser comunicada à Administração do Condomínio</div>
                    </div>
                </body>
                </html>
            `);
            printWindow.document.close();
            
            setTimeout(() => {
                printWindow.print();
            }, 500);
            
            sistema.mostrarStatus('🖨️ Enviado para impressão!');
        }
        
        function exportarCSV() {
            sistema.exportarCSV();
        }
        
        // Inicialização da página
        window.addEventListener('load', () => {
            console.log('🎉 [PREMIUM] Sistema carregado com sucesso!');
            sistema.atualizarInterface();
        });
        
        // Prevenir perda de dados
        window.addEventListener('beforeunload', (e) => {
            sistema.salvarDados();
        });
    </script>
</body>
</html>
    ''', apartamentos=apartamentos)

@app.route('/placa/<placa>/<apartamento>')
def placa_info(placa, apartamento):
    return render_template_string('''
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Placa {{ placa }} - Apartamento {{ apartamento }}</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh; display: flex; align-items: center; justify-content: center;
            margin: 0; padding: 20px;
            animation: backgroundShift 8s ease-in-out infinite alternate;
        }
        
        @keyframes backgroundShift {
            0% { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
            100% { background: linear-gradient(135deg, #764ba2 0%, #667eea 100%); }
        }
        
        .info-card {
            background: rgba(255,255,255,0.95); border-radius: 25px; padding: 50px;
            box-shadow: 0 30px 80px rgba(0,0,0,0.15); text-align: center;
            max-width: 500px; width: 100%; backdrop-filter: blur(20px);
            animation: slideUp 0.8s ease-out;
        }
        
        @keyframes slideUp {
            from { opacity: 0; transform: translateY(50px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .titulo {
            background: linear-gradient(45deg, #B91C3C, #DC2626);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
            font-size: 28px; font-weight: 900; margin-bottom: 40px;
            display: flex; align-items: center; justify-content: center; gap: 15px;
            animation: titleGlow 2s ease-in-out infinite alternate;
        }
        
        @keyframes titleGlow {
            from { filter: drop-shadow(0 0 5px rgba(185, 28, 60, 0.5)); }
            to { filter: drop-shadow(0 0 15px rgba(185, 28, 60, 0.8)); }
        }
        
        .info-item {
            margin: 30px 0; padding: 25px; 
            background: linear-gradient(145deg, #f9fafb, #ffffff);
            border-radius: 20px; border-left: 5px solid #B91C3C;
            box-shadow: 0 10px 25px rgba(0,0,0,0.05);
            animation: fadeInLeft 0.6s ease-out forwards;
            opacity: 0;
        }
        
        .info-item:nth-child(2) { animation-delay: 0.2s; }
        .info-item:nth-child(3) { animation-delay: 0.4s; }
        .info-item:nth-child(4) { animation-delay: 0.6s; }
        
        @keyframes fadeInLeft {
            from { opacity: 0; transform: translateX(-30px); }
            to { opacity: 1; transform: translateX(0); }
        }
        
        .info-label {
            font-size: 16px; color: #6b7280; font-weight: 700;
            text-transform: uppercase; letter-spacing: 1px; margin-bottom: 10px;
        }
        
        .info-value {
            font-size: 32px; font-weight: 900; margin-top: 10px;
            font-family: 'Arial Black', Arial, sans-serif;
        }
        
        .placa-value { 
            color: #1f2937; letter-spacing: 3px;
            animation: numberFloat 3s ease-in-out infinite;
        }
        
        .apartamento-value { 
            background: linear-gradient(45deg, #B91C3C, #DC2626);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
            animation: numberFloat 3s ease-in-out infinite 0.5s;
        }
        
        @keyframes numberFloat {
            0%, 100% { transform: translateY(0px); }
            50% { transform: translateY(-3px); }
        }
        
        .status {
            background: linear-gradient(145deg, #10b981, #059669);
            color: white; padding: 20px 30px; border-radius: 20px; 
            font-weight: 700; font-size: 16px; margin-top: 30px;
            display: flex; align-items: center; justify-content: center; gap: 12px;
            box-shadow: 0 15px 35px rgba(16, 185, 129, 0.3);
            animation: successPulse 0.8s ease-out 0.8s both;
        }
        
        @keyframes successPulse {
            0% { transform: scale(0.8); opacity: 0; }
            50% { transform: scale(1.05); }
            100% { transform: scale(1); opacity: 1; }
        }
        
        .placa-container-real {
            width: 100%; display: flex; justify-content: center; 
            margin: 40px 0; perspective: 1000px;
        }
        
        .placa-mercosul-real {
            width: 450px; height: 225px;
            background-image: url('https://files.manuscdn.com/user_upload_by_module/session_file/310419663029166562/nXacdBCozrTTswlB.png');
            background-size: cover; background-position: center; background-repeat: no-repeat;
            position: relative; border-radius: 20px; 
            box-shadow: 0 25px 60px rgba(0,0,0,0.3);
            margin: 30px auto; display: flex; align-items: center; justify-content: center;
            transform: perspective(1000px) rotateX(10deg) rotateY(-3deg);
            transition: all 0.6s cubic-bezier(0.4, 0, 0.2, 1);
            animation: plateFloat 4s ease-in-out infinite;
        }
        
        @keyframes plateFloat {
            0%, 100% { transform: perspective(1000px) rotateX(10deg) rotateY(-3deg) translateY(0px); }
            50% { transform: perspective(1000px) rotateX(10deg) rotateY(-3deg) translateY(-10px); }
        }
        
        .placa-mercosul-real:hover {
            transform: perspective(1000px) rotateX(0deg) rotateY(0deg) scale(1.08);
            box-shadow: 0 40px 80px rgba(0,0,0,0.4);
        }
        
        .placa-numero-overlay {
            position: absolute; top: 58%; left: 50%;
            transform: translate(-50%, -50%); font-size: 48px;
            font-weight: 900; color: #000;
            font-family: 'Arial Black', Arial, sans-serif;
            letter-spacing: 4px; 
            text-shadow: 0 3px 6px rgba(255,255,255,0.8);
            z-index: 10; animation: textGlow 2s ease-in-out infinite alternate;
        }
        
        @keyframes textGlow {
            from { text-shadow: 0 3px 6px rgba(255,255,255,0.8); }
            to { text-shadow: 0 3px 6px rgba(255,255,255,0.8), 0 0 20px rgba(0,0,0,0.3); }
        }
        
        @media (max-width: 768px) {
            .info-card { padding: 30px; margin: 15px; }
            .titulo { font-size: 22px; }
            .info-value { font-size: 26px; }
            .placa-mercosul-real { width: 100%; max-width: 350px; height: 175px; }
            .placa-numero-overlay { font-size: 36px; }
        }
    </style>
</head>
<body>
    <div class="info-card">
        <div class="titulo">
            🚗 Informações Premium do Veículo
        </div>
        
        <div class="info-item">
            <div class="info-label">Placa do Veículo:</div>
            <div class="info-value placa-value">{{ placa }}</div>
        </div>
        
        <div class="info-item">
            <div class="info-label">Apartamento:</div>
            <div class="info-value apartamento-value">{{ apartamento }}</div>
        </div>
        
        <div class="info-item">
            <div class="info-label">Placa Mercosul Real 3D:</div>
            <div class="placa-container-real">
                <div class="placa-mercosul-real">
                    <div class="placa-numero-overlay">{{ placa }}</div>
                </div>
            </div>
        </div>
        
        <div class="status">
            ✅ Veículo autorizado no Condomínio Verte Belém
        </div>
    </div>
</body>
</html>
    ''', placa=placa, apartamento=apartamento)

if __name__ == '__main__':
    print("🚀 [SISTEMA PREMIUM] Iniciando Sistema Premium de Crachás Verte Belém")
    print(f"🏢 [PREMIUM] Total de apartamentos: {len(apartamentos)}")
    app.run(host='0.0.0.0', port=5000, debug=True)

