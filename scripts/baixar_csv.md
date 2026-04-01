<html lang="pt-BR"><head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SNCR - Sistema Nacional de Cadastro Rural</title>
    <link rel="stylesheet" href="static/css/style.css">
</head>
<body>
    <!-- Header Gov -->
    <header class="gov-header">
        <div class="gov-header-top">
            <div class="container">
                <span class="gov-label">Ministério da Agricultura e Pecuária</span>
            </div>
        </div>
        <div class="gov-header-main">
            <div class="container header-content">
                <div class="header-brand">
                    <div class="brand-icon">⚙</div>
                    <div>
                        <h1>SNCR</h1>
                        <p>Sistema Nacional de Cadastro Rural</p>
                    </div>
                </div>
                <nav class="header-nav">
                    <a href="#" class="nav-link" data-page="home">Início</a>
                    <a href="#" class="nav-link active" data-page="dados-abertos">Dados Abertos</a>
                    <a href="#" class="nav-link" data-page="consulta">Consulta de Imóvel</a>
                </nav>
            </div>
        </div>
    </header>

    <!-- Main content -->
    <main class="container main-content">

        <!-- HOME -->
        <section id="page-home" class="page">

            <!-- Banner Certificação -->
            <div class="promo-banner">
                <div class="promo-overlay">
                    <div class="promo-badge">PROGRAMA NACIONAL</div>
                    <h3>Certificação de Imóveis Rurais - CIR</h3>
                    <p>Garanta a regularização fundiária da sua propriedade. O certificado digital do SNCR é obrigatório para acesso a linhas de crédito rural e programas de incentivo do Governo Federal.</p>
                    <div class="promo-stats">
                        <div class="promo-stat">
                            <strong>2,4 mi</strong>
                            <span>imóveis certificados</span>
                        </div>
                        <div class="promo-stat">
                            <strong>850 mil</strong>
                            <span>produtores atendidos</span>
                        </div>
                        <div class="promo-stat">
                            <strong>27 UFs</strong>
                            <span>cobertura nacional</span>
                        </div>
                    </div>
                    <a href="#" class="promo-cta">Saiba mais sobre o programa</a>
                </div>
            </div>

            <div class="cards-grid">
                <div class="card" onclick="navigateTo('dados-abertos')">
                    <div class="card-icon">📊</div>
                    <h3>Dados Abertos</h3>
                    <p>Exporte dados de imóveis rurais por estado e município em formato CSV.</p>
                    <span class="card-link">Acessar →</span>
                </div>
                <div class="card" onclick="navigateTo('consulta')">
                    <div class="card-icon">🔍</div>
                    <h3>Consulta de Imóvel</h3>
                    <p>Consulte dados detalhados de proprietários e arrendatários por código INCRA.</p>
                    <span class="card-link">Acessar →</span>
                </div>
            </div>
        </section>

        <!-- DADOS ABERTOS -->
        <section id="page-dados-abertos" class="page active">
            <h2>Dados Abertos - Exportação de Imóveis Rurais</h2>
            <p class="page-description">Selecione o estado e, opcionalmente, o município para exportar os dados cadastrais em formato CSV.</p>

            <div class="form-panel">
                <div class="form-row">
                    <div class="form-group">
                        <label for="select-uf">Estado (UF) <span class="required">*</span></label>
                        <select id="select-uf">
                            <option value="">Selecione o estado...</option>
                        <option value="AC">AC - Acre</option><option value="AL">AL - Alagoas</option><option value="AP">AP - Amapá</option><option value="AM">AM - Amazonas</option><option value="BA">BA - Bahia</option><option value="CE">CE - Ceará</option><option value="DF">DF - Distrito Federal</option><option value="ES">ES - Espírito Santo</option><option value="GO">GO - Goiás</option><option value="MA">MA - Maranhão</option><option value="MT">MT - Mato Grosso</option><option value="MS">MS - Mato Grosso do Sul</option><option value="MG">MG - Minas Gerais</option><option value="PR">PR - Paraná</option><option value="PB">PB - Paraíba</option><option value="PA">PA - Pará</option><option value="PE">PE - Pernambuco</option><option value="PI">PI - Piauí</option><option value="RN">RN - Rio Grande do Norte</option><option value="RS">RS - Rio Grande do Sul</option><option value="RJ">RJ - Rio de Janeiro</option><option value="RO">RO - Rondônia</option><option value="RR">RR - Roraima</option><option value="SC">SC - Santa Catarina</option><option value="SE">SE - Sergipe</option><option value="SP">SP - São Paulo</option><option value="TO">TO - Tocantins</option></select>
                    </div>
                    <div class="form-group">
                        <label for="select-municipio">Município</label>
                        <select id="select-municipio" disabled="">
                            <option value="">Todos os municípios</option>
                        </select>
                    </div>
                </div>

                <div class="captcha-section">
                    <label>Verificação de segurança <span class="required">*</span></label>
                    <div class="captcha-box">
                        <div class="captcha-display" id="captcha-display-export">
                            <span class="captcha-text" id="captcha-text-export">4  8  9  2  7</span>
                            <button class="captcha-refresh" id="btn-refresh-captcha-export" title="Gerar novo captcha">↻</button>
                        </div>
                        <input type="text" id="captcha-input-export" placeholder="Digite os 5 dígitos acima" maxlength="5">
                    </div>
                    <input type="hidden" id="captcha-id-export" value="8750097bac558533583b0a7bfd6f02f2">
                </div>

                <div class="form-actions">
                    <button class="btn btn-primary" id="btn-exportar" disabled="">
                        ⬇ Baixar CSV
                    </button>
                </div>

                <div class="alert alert-error hidden" id="alert-export"></div>
            </div>
        </section>

        <!-- CONSULTA IMÓVEL -->
        <section id="page-consulta" class="page">
            <h2>Consulta de Imóvel Rural</h2>
            <p class="page-description">Informe o código INCRA do imóvel para consultar os dados de proprietários e arrendatários.</p>

            <div class="form-panel">
                <div class="form-row">
                    <div class="form-group full-width">
                        <label for="input-incra">Código INCRA <span class="required">*</span></label>
                        <input type="text" id="input-incra" placeholder="Ex: 01001000003">
                    </div>
                </div>

                <div class="captcha-section">
                    <label>Verificação de segurança <span class="required">*</span></label>
                    <div class="captcha-box">
                        <div class="captcha-display" id="captcha-display-consulta">
                            <span class="captcha-text" id="captcha-text-consulta">5  1  3  2  6</span>
                            <button class="captcha-refresh" id="btn-refresh-captcha-consulta" title="Gerar novo captcha">↻</button>
                        </div>
                        <input type="text" id="captcha-input-consulta" placeholder="Digite os 5 dígitos acima" maxlength="5">
                    </div>
                    <input type="hidden" id="captcha-id-consulta" value="45bd7960faafbb3716e83c703f74157d">
                </div>

                <div class="form-actions">
                    <button class="btn btn-primary" id="btn-consultar" disabled="">
                        🔍 Obter dados de proprietários
                    </button>
                </div>

                <div class="alert alert-error hidden" id="alert-consulta"></div>

                <!-- Resultado -->
                <div id="resultado-consulta" class="hidden">
                    <div class="resultado-header">
                        <h3 id="resultado-denominacao"></h3>
                        <div class="resultado-info">
                            <span><strong>Código INCRA:</strong> <span id="resultado-codigo"></span></span>
                            <span><strong>Área:</strong> <span id="resultado-area"></span> ha</span>
                            <span><strong>Situação:</strong> <span id="resultado-situacao"></span></span>
                        </div>
                    </div>

                    <h4>Proprietários e Arrendatários</h4>
                    <table class="data-table">
                        <thead>
                            <tr>
                                <th>Nome</th>
                                <th>CPF</th>
                                <th>Vínculo</th>
                                <th>% Participação</th>
                            </tr>
                        </thead>
                        <tbody id="tabela-proprietarios">
                        </tbody>
                    </table>
                </div>
            </div>
        </section>
    </main>

    <!-- Footer -->
    <footer class="gov-footer">
        <div class="container">
            <p>SNCR - Sistema Nacional de Cadastro Rural © 2026</p>
            <p class="footer-note">Ministério da Agricultura e Pecuária - Dados simulados para fins de avaliação</p>
        </div>
    </footer>

    <script src="static/js/app.js"></script>


</body></html>