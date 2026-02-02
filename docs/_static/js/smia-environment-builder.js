/**
 * SMIA Environment Builder
 * Client-side logic for generating docker-compose and configuration files.
 */

document.addEventListener("DOMContentLoaded", () => {
    // Only init if the container exists
    if (document.getElementById("smia-builder-root")) {
        SMIA_Builder.init();
    }
});

const SMIA_Builder = {
    state: {
        step: 0,
        envType: 'null', // local, docker, k8s
        xmpp: { type: 'new', domain: 'localhost', ip: '127.0.0.1' }, // new, existing
        core: {
            smiakb: false,
            aasServer: { type: 'basyx', ip: '127.0.0.1', folder: './aas-models' } // basyx, external
        },
        plan: { hasPlan: false, file: null, path: '' },
        assets: [], // Array of objects { id, file: null, customImage: '' }
        operator: false
    },

    init: function() {
        this.renderInitialState();
        this.bindEvents();
    },

    // --- RENDER LOGIC ---

    renderInitialState: function() {
        const root = document.getElementById("smia-builder-root");
        root.innerHTML = `
            <div class="smia-wizard-container">
                <div class="smia-progress-bar" id="progress-bar-container" style="display:none;">
                    <div class="progress-fill" id="progress-fill" style="width: 0%"></div>
                </div>

                <div class="smia-welcome-screen active" id="step-0">
                    <span class="welcome-icon">🚀</span>
                    <h2 class="welcome-title">SMIA Environment Builder</h2>
                    <p class="welcome-text">
                        Bienvenido al asistente de configuración. Esta herramienta te ayudará a generar 
                        los archivos de despliegue necesarios (Docker Compose / K8s) o la estructura local 
                        para tu entorno SMIA.
                    </p>
                    <button id="btn-start" class="smia-btn primary btn-large">Comenzar Configuración</button>
                </div>

                <div class="smia-step" id="step-1">
                    <h3>Paso 1: Infraestructura Base</h3>
                    
                    <label class="section-label">Selecciona tu entorno de despliegue:</label>
                    <div class="env-grid">
                        <div class="env-card" data-env="local">
                            <span class="card-icon">💻</span>
                            <span class="card-title">Local (Python)</span>
                            <span class="card-desc">Desarrollo sin contenedores. Scripts de arranque Python directos.</span>
                        </div>
                        <div class="env-card" data-env="docker">
                            <span class="card-icon">🐳</span>
                            <span class="card-title">Docker Compose</span>
                            <span class="card-desc">Despliegue estándar en contenedores para pruebas o producción ligera.</span>
                        </div>
                        <div class="env-card" data-env="k8s">
                            <span class="card-icon">☸️</span>
                            <span class="card-title">Kubernetes</span>
                            <span class="card-desc">Despliegue escalable distribuido (genera YAMLs para Kompose).</span>
                        </div>
                    </div>
                    <div id="env-error" style="color: var(--color-problematic); display:none; margin-bottom:1rem;">
                        ⚠️ Por favor, selecciona un entorno.
                    </div>

                    <div id="xmpp-section" style="display:none; margin-top: 2rem; border-top: 1px solid var(--color-border); padding-top: 1rem;">
                        <label class="section-label">Configuración Servidor XMPP</label>
                        
                        <div id="xmpp-deploy-options" class="radio-group" style="margin-bottom: 1rem;">
                            <label><input type="radio" name="xmpp-type" value="new" checked> Desplegar Nuevo (Ejabberd Container)</label>
                            <label><input type="radio" name="xmpp-type" value="existing"> Usar Existente</label>
                        </div>

                        <div id="xmpp-local-info" style="margin-bottom: 1rem; color: var(--color-foreground-secondary);">
                            <small>Para entorno local, debes proporcionar los datos de tu servidor XMPP existente.</small>
                        </div>

                        <div id="xmpp-inputs">
                            <input type="text" id="xmpp-domain" placeholder="Nombre de Dominio (ej. smia.net)" class="smia-input">
                            <input type="text" id="xmpp-ip" placeholder="Dirección IP (ej. 192.168.1.50)" class="smia-input" style="margin-top: 10px;">
                        </div>
                    </div>
                </div>

                <div class="smia-step" id="step-2">
                   <h3>Paso 2: Servicios Core SMIA</h3>
                   <div class="form-group">
                        <label class="checkbox-container">
                            <input type="checkbox" id="chk-smia-kb"> Include SMIA-I KB Service
                        </label>
                    </div>
                    <div class="form-group">
                        <label class="section-label">AAS Server</label>
                        <select id="aas-type-select" class="smia-input">
                            <option value="basyx">Deploy New (Basyx)</option>
                            <option value="external">Use Existing</option>
                            <option value="none">None (File based)</option>
                        </select>
                        <div id="aas-external-inputs" style="display:none; margin-top:10px;">
                             <input type="text" id="aas-ip" placeholder="AAS Server IP" class="smia-input">
                        </div>
                    </div>
                    <div class="info-box" id="ism-notice" style="display:none">
                        ℹ️ <strong>SMIA ISM</strong> will be added automatically.
                    </div>
                </div>
                
                <div class="smia-step" id="step-3">
                    <h3>Paso 3: Activos</h3>
                    <div class="asset-card">
                        <h4>Manufacturing Plan (Optional)</h4>
                        <label class="modern-checkbox">
                            <input type="checkbox" id="chk-has-plan">
                            <span class="checkmark"></span>
                            Include CSS-enriched Plan
                        </label>
                        
                        <div id="plan-inputs" style="display:none; margin-top: 10px;">
                            <div class="file-upload-wrapper">
                                <input type="file" id="plan-file" class="file-upload-input" onchange="SMIA_Builder.handleFileSelect(this)">
                                <div class="file-upload-label">
                                    <span class="file-text">Click to upload AASX file...</span>
                                    <span class="icon">📂</span>
                                </div>
                            </div>
                            <small style="display:block; margin: 8px 0;">Or manually specify path:</small>
                            <input type="text" id="plan-path" placeholder="/app/models/plan.aasx" class="smia-input">
                        </div>
                    </div>
                    <div id="assets-list"></div>
                    <button class="smia-btn secondary" id="btn-add-asset">+ Add Asset</button>
                    <hr>
                    <div class="form-group">
                        <label class="checkbox-container"><input type="checkbox" id="chk-operator"> Include Operator</label>
                    </div>
                </div>

                <div class="smia-step" id="step-4">
                    <h3>Resumen</h3>
                    <div id="summary-content"></div>
                </div>

                <div class="smia-controls" id="wizard-controls" style="display:none;">
                    <button id="btn-prev" class="smia-btn">Anterior</button>
                    <button id="btn-next" class="smia-btn primary">Siguiente</button>
                    <button id="btn-download" class="smia-btn primary" style="display:none">🚀 Descargar ZIP</button>
                </div>
            </div>
        `;
        this.updateDynamicUI();
    },

    // --- EVENT HANDLING ---

    bindEvents: function() {
        // --- Evento Inicio ---
        document.getElementById('btn-start').addEventListener('click', () => {
            this.state.step = 1;
            this.updateStepView();
        });

        // --- Evento Selección de Tarjetas (Entorno) ---
        document.querySelectorAll('.env-card').forEach(card => {
            card.addEventListener('click', (e) => {
                // Visual selection
                document.querySelectorAll('.env-card').forEach(c => c.classList.remove('selected'));
                e.currentTarget.classList.add('selected');

                // Logic update
                const env = e.currentTarget.dataset.env;
                this.state.envType = env;
                document.getElementById('env-error').style.display = 'none';

                // Trigger XMPP Logic update immediately
                this.updateXMPPVisibility(env);
            });
        });

        // --- Eventos Navegación Standard ---
        document.getElementById('btn-next').addEventListener('click', () => this.nextStep());
        document.getElementById('btn-prev').addEventListener('click', () => this.prevStep());
        document.getElementById('btn-download').addEventListener('click', () => this.generateZip());

        // --- Eventos Dinámicos XMPP ---
        document.querySelectorAll('input[name="xmpp-type"]').forEach(el => {
            el.addEventListener('change', (e) => {
                this.state.xmpp.type = e.target.value;
                this.toggleXMPPInputs(e.target.value === 'existing');
            });
        });

        // ... (Mantén los eventos existentes para AAS, Activos, etc.) ...
        document.getElementById('btn-add-asset').addEventListener('click', () => this.addAssetUI());
        document.getElementById('aas-type-select').addEventListener('change', (e) => { /*...*/ this.checkISMDependency(); });
        document.getElementById('chk-smia-kb').addEventListener('change', (e) => { this.state.core.smiakb = e.target.checked; this.checkISMDependency(); });
        document.getElementById('chk-has-plan').addEventListener('change', (e) => document.getElementById('plan-inputs').style.display = e.target.checked ? 'block' : 'none');
    },

    // --- Nueva Función Auxiliar para lógica XMPP ---
    updateXMPPVisibility: function(env) {
        const section = document.getElementById('xmpp-section');
        const deployOptions = document.getElementById('xmpp-deploy-options');
        const localInfo = document.getElementById('xmpp-local-info');
        const inputs = document.getElementById('xmpp-inputs');

        section.style.display = 'block'; // Mostrar la sección entera

        if (env === 'local') {
            // Caso Local: No se puede desplegar contenedor Ejabberd.
            deployOptions.style.display = 'none'; // Ocultar opción de "Nuevo"
            localInfo.style.display = 'block';    // Mostrar aviso
            inputs.style.display = 'block';       // Mostrar inputs obligatoriamente
            this.state.xmpp.type = 'existing';    // Forzar estado interno
        } else {
            // Caso Docker/K8s
            deployOptions.style.display = 'block'; // Mostrar toggle
            localInfo.style.display = 'none';

            // Respetar la selección actual del radio button
            const isExisting = document.querySelector('input[name="xmpp-type"]:checked').value === 'existing';
            inputs.style.display = isExisting ? 'block' : 'none';
        }
    },

    toggleXMPPInputs: function(show) {
        document.getElementById('xmpp-inputs').style.display = show ? 'block' : 'none';
    },

    checkISMDependency: function() {
        // Show ISM notice if KB is true OR AAS is active
        const show = this.state.core.smiakb || this.state.core.aasServer.type !== 'none';
        document.getElementById('ism-notice').style.display = show ? 'block' : 'none';
    },

    updateDynamicUI: function() {
        // Any specific re-renders
    },


    // --- NAVIGATION LOGIC ---

    nextStep: function() {
        if(this.state.step < 4) {
            if(!this.validateStep(this.state.step)) return;
            this.captureStepData(this.state.step);
            this.state.step++;
            this.updateStepView();
        }
    },

    validateStep: function(step) {
        if (step === 1) {
            if (!this.state.envType) {
                document.getElementById('env-error').style.display = 'block';
                return false;
            }
        }
        return true;
    },

    updateStepView: function() {
        // Ocultar todo
        document.querySelectorAll('.smia-welcome-screen, .smia-step').forEach(el => el.classList.remove('active'));

        if (this.state.step === 0) {
            // Mostrar Welcome
            document.getElementById('step-0').classList.add('active');
            document.getElementById('progress-bar-container').style.display = 'none';
            document.getElementById('wizard-controls').style.display = 'none';
        } else {
            // Mostrar Wizard normal
            document.getElementById(`step-${this.state.step}`).classList.add('active');
            document.getElementById('progress-bar-container').style.display = 'block';
            document.getElementById('wizard-controls').style.display = 'flex'; // Flex para alinear botones

            // Actualizar Barra (Pasos 1 a 4)
            const pct = (this.state.step / 4) * 100;
            document.getElementById('progress-fill').style.width = `${pct}%`;

            // Gestión Botones
            document.getElementById('btn-prev').disabled = (this.state.step === 1); // Desactivar "Anterior" en paso 1 (para no volver a Welcome accidentalmente, o permitirlo si prefieres)

            if (this.state.step === 4) { // Paso final
                this.generateSummary();
                document.getElementById('btn-next').style.display = 'none';
                document.getElementById('btn-download').style.display = 'inline-block';
            } else {
                document.getElementById('btn-next').style.display = 'inline-block';
                document.getElementById('btn-download').style.display = 'none';
            }
        }
    },

    // En prevStep, permitir volver a start si estamos en paso 1
    prevStep: function() {
        if(this.state.step > 1) {
            this.state.step--;
            this.updateStepView();
        } else if (this.state.step === 1) {
            this.state.step = 0; // Volver a Welcome
            this.updateStepView();
        }
    },

    captureStepData: function(step) {
        if (step === 0) {
            this.state.xmpp.domain = document.getElementById('xmpp-domain').value || 'localhost';
            this.state.xmpp.ip = document.getElementById('xmpp-ip').value || '127.0.0.1';
        }
        if (step === 2) {
            // Capture Plan
            const planFileEl = document.getElementById('plan-file');
            this.state.plan.hasPlan = document.getElementById('chk-has-plan').checked;
            if (planFileEl.files.length > 0) {
                this.state.plan.file = planFileEl.files[0];
                this.state.plan.path = planFileEl.files[0].name;
            } else {
                this.state.plan.path = document.getElementById('plan-path').value;
            }
            this.state.operator = document.getElementById('chk-operator').checked;

            // Capture Assets
            this.state.assets = [];
            document.querySelectorAll('#assets-list .asset-card').forEach(card => {
                const isExtended = card.querySelector('.chk-extended').checked;
                const fileInput = card.querySelector('.asset-file-input');
                let path = card.querySelector('.asset-id-input').value;
                let fileObj = null;

                if (fileInput.files.length > 0) {
                    fileObj = fileInput.files[0];
                    path = fileObj.name; // Use filename as default path
                }

                this.state.assets.push({
                    path: path,
                    file: fileObj,
                    isExtended: isExtended,
                    image: isExtended ? card.querySelector('.asset-image-input').value : 'smia/standard-asset:latest'
                });
            });
        }
    },

    generateSummary: function() {
        const s = this.state;
        let html = `<table class="docutils align-default">
            <thead><tr><th>Component</th><th>Configuration</th></tr></thead>
            <tbody>
                <tr><td>Environment</td><td>${s.envType.toUpperCase()}</td></tr>
                <tr><td>XMPP Server</td><td>${s.xmpp.type === 'new' ? 'New Container (Ejabberd)' : 'Existing (' + s.xmpp.ip + ')'}</td></tr>
                <tr><td>Core Services</td><td>${s.core.smiakb ? 'SMIA-KB, ' : ''} ${s.core.aasServer.type !== 'none' ? 'AAS Server' : 'No AAS Server'}</td></tr>
                <tr><td>Assets</td><td>${s.assets.length} Defined</td></tr>
                <tr><td>Operator</td><td>${s.operator ? 'Included' : 'Not Included'}</td></tr>
            </tbody>
        </table>`;
        document.getElementById('summary-content').innerHTML = html;
    },

    // --- GENERATION LOGIC (YAML) ---

    generateZip: function() {
        const zip = new JSZip();
        const s = this.state;

        // 1. Generate README
        let readmeContent = `# SMIA Environment - Generated Configuration\n\n`;
        readmeContent += `## Deployment: ${s.envType.toUpperCase()}\n\n`;

        if (s.envType === 'local') {
            readmeContent += `Since you selected LOCAL environment:\n1. Install Python dependencies.\n2. Run the provided scripts in /scripts folder.\n`;
            zip.folder("scripts").file("startup.py", "# Python startup placeholder");
        } else {
            // DOCKER / K8S
            const yamlContent = this.buildDockerCompose();
            zip.file("docker-compose.yml", yamlContent);

            readmeContent += `## How to run\n\n### Docker Compose\n\`\`\`bash\ndocker compose up -d\n\`\`\`\n\n`;

            if (s.envType === 'k8s') {
                readmeContent += `### Kubernetes\nYou selected Kubernetes. Please use Kompose to convert the generated docker-compose.yml:\n\n`;
                readmeContent += `\`\`\`bash\nkompose convert -f docker-compose.yml\nkubectl apply -f .\n\`\`\`\n`;
            }
        }

        zip.file("README.md", readmeContent);

        // 2. Handle Files (Models)
        const modelsFolder = zip.folder("aas-models");

        // Add Plan File if exists
        if (s.plan.hasPlan && s.plan.file) {
            modelsFolder.file(s.plan.file.name, s.plan.file);
        }

        // Add Asset Files
        s.assets.forEach(asset => {
            if (asset.file) {
                modelsFolder.file(asset.file.name, asset.file);
            }
        });

        // 3. Download
        zip.generateAsync({type:"blob"}).then(function(content) {
            saveAs(content, "smia-environment-kit.zip");
        });
    },

    buildDockerCompose: function() {
        const s = this.state;
        const indent = (n) => '  '.repeat(n);

        let yaml = `version: '3.8'\n\nservices:\n`;

        // 1. XMPP (Ejabberd)
        if (s.xmpp.type === 'new') {
            yaml += `${indent(1)}ejabberd:\n`;
            yaml += `${indent(2)}image: ejabberd/ecs\n`;
            yaml += `${indent(2)}ports:\n${indent(3)}- "5222:5222"\n${indent(3)}- "5280:5280"\n`;
            yaml += `${indent(2)}environment:\n${indent(3)}- EJABBERD_DOMAIN=${s.xmpp.domain}\n${indent(3)}- EJABBERD_USER=admin\n${indent(3)}- EJABBERD_PASSWORD=password\n\n`;
        }

        // 2. AAS Server (Basyx)
        if (s.core.aasServer.type === 'basyx') {
            yaml += `${indent(1)}aas-server:\n`;
            yaml += `${indent(2)}image: eclipse/basyx-aas-server:1.0.1\n`;
            yaml += `${indent(2)}ports:\n${indent(3)}- "8081:8081"\n`;
            yaml += `${indent(2)}volumes:\n${indent(3)}- ./aas-models:/usr/share/config/aas\n\n`;
        }

        // 3. SMIA ISM (Dependency)
        const needsISM = s.core.smiakb || s.core.aasServer.type !== 'none';
        if (needsISM) {
            yaml += `${indent(1)}smia-ism:\n`;
            yaml += `${indent(2)}image: smia/ism-core:latest\n`;
            yaml += `${indent(2)}environment:\n${indent(3)}- XMPP_HOST=${s.xmpp.type === 'new' ? 'ejabberd' : s.xmpp.ip}\n\n`;
        }

        // 4. SMIA-I KB
        if (s.core.smiakb) {
            yaml += `${indent(1)}smia-kb:\n`;
            yaml += `${indent(2)}image: smia/knowledge-base:latest\n`;
            yaml += `${indent(2)}depends_on:\n${indent(3)}- smia-ism\n\n`;
        }

        // 5. PE (Plan)
        if (s.plan.hasPlan) {
            yaml += `${indent(1)}smia-pe-manager:\n`;
            yaml += `${indent(2)}image: smia/pe-manager:latest\n`;
            yaml += `${indent(2)}volumes:\n${indent(3)}- ./aas-models:/app/models\n`;
            yaml += `${indent(2)}environment:\n${indent(3)}- AAS_FILE=${s.plan.path}\n\n`;
        }

        // 6. Assets
        s.assets.forEach((asset, index) => {
            const serviceName = `asset-${index+1}`;
            yaml += `${indent(1)}${serviceName}:\n`;
            // Use custom image if extended, else standard
            yaml += `${indent(2)}image: ${asset.isExtended ? asset.image : 'smia/standard-asset:latest'}\n`;
            yaml += `${indent(2)}volumes:\n${indent(3)}- ./aas-models:/app/models\n`;
            yaml += `${indent(2)}environment:\n`;
            yaml += `${indent(3)}- AAS_ID=${asset.path}\n`; // Assuming path is ID/Filename
            if (needsISM) yaml += `${indent(3)}- ISM_HOST=smia-ism\n`;
            yaml += `\n`;
        });

        // 7. Operator
        if (s.operator) {
            yaml += `${indent(1)}smia-operator:\n`;
            yaml += `${indent(2)}image: smia/operator-dashboard:latest\n`;
            yaml += `${indent(2)}ports:\n${indent(3)}- "3000:3000"\n\n`;
        }

        return yaml;
    },

    addAssetUI: function() {
        const id = Date.now();
        const container = document.getElementById('assets-list');
        const div = document.createElement('div');
        div.className = 'asset-card';
        div.id = `asset-${id}`;

        // SVG para el icono de basura
        const trashIcon = `<svg viewBox="0 0 24 24"><path d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z"/></svg>`;

        div.innerHTML = `
            <div class="asset-header">
                <strong>New Asset</strong>
                <button class="btn-icon-danger" onclick="document.getElementById('asset-${id}').remove()" title="Remove Asset">
                    ${trashIcon}
                </button>
            </div>
            
            <div class="form-group">
                <label>AAS Model Source</label>
                <div class="file-upload-wrapper">
                    <input type="file" class="asset-file-input file-upload-input" onchange="SMIA_Builder.handleFileSelect(this)">
                    <div class="file-upload-label">
                        <span class="file-text">Upload AASX File</span>
                        <span class="icon">📎</span>
                    </div>
                </div>
                <input type="text" class="asset-id-input smia-input" placeholder="Or enter AAS ID manually" style="margin-top:10px;">
            </div>

            <div class="form-group">
                <label class="modern-checkbox">
                    <input type="checkbox" class="chk-extended">
                    <span class="checkmark"></span>
                    Extended SMIA (Custom Docker Image)
                </label>
                <input type="text" class="asset-image-input smia-input" style="display:none" placeholder="Docker Image Name (e.g., my-repo/asset:v1)">
            </div>
        `;

        // Lógica local para mostrar input de imagen docker
        div.querySelector('.chk-extended').addEventListener('change', function(e) {
            div.querySelector('.asset-image-input').style.display = e.target.checked ? 'block' : 'none';
        });

        container.appendChild(div);
    },

    // --- NUEVA FUNCIÓN AUXILIAR PARA UX ---
    // Cambia el texto del botón cuando se selecciona un archivo
    handleFileSelect: function(inputElement) {
        const label = inputElement.nextElementSibling;
        const textSpan = label.querySelector('.file-text');

        if (inputElement.files && inputElement.files.length > 0) {
            textSpan.textContent = inputElement.files[0].name; // Muestra nombre del archivo
            label.classList.add('has-file');
        } else {
            textSpan.textContent = "Upload AASX File";
            label.classList.remove('has-file');
        }
    },
};