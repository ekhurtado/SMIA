/**
 * SMIA Environment Builder
 * Client-side logic for generating docker-compose and configuration files.
 * v3.0 - Final Release (English, Modern UI, SVG Icons)
 */

document.addEventListener("DOMContentLoaded", () => {
    // Only init if the container exists
    if (document.getElementById("smia-builder-root")) {
        SMIA_Builder.init();
    }
});

/* Embedded SVG Icons for maximum compatibility and performance */
const ICONS = {
    local: `<svg viewBox="0 0 24 24" width="40" height="40" fill="currentColor"><path d="M20 4H4c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 14H4V6h16v12zM8 10H6v2h2v-2zm0-3H6v2h2V7zm2 2h8v2h-8V9zm0-3h4v2h-4V6z"/></svg>`,
    docker: `<svg viewBox="0 0 24 24" width="40" height="40" fill="#0db7ed"><path d="M13.983 11.078h2.119a.186.186 0 00.186-.185V9.006a.186.186 0 00-.186-.186h-2.119a.185.185 0 00-.185.186v1.888c0 .102.083.185.185.185m-2.954-5.43h2.119a.186.186 0 00.186-.186V3.574a.186.186 0 00-.186-.185h-2.119a.185.185 0 00-.185.185v1.888c0 .102.083.186.185.186m-2.955 5.43h2.12a.186.186 0 00.186-.185V9.006a.186.186 0 00-.186-.186h-2.12a.185.185 0 00-.185.186v1.888c0 .102.082.185.185.185m0-2.716h2.12a.186.186 0 00.186-.186V6.289a.186.186 0 00-.186-.185h-2.12a.185.185 0 00-.185.185v1.888c0 .102.082.185.185.185m-2.953 5.43h2.119a.186.186 0 00.186-.185V9.006a.186.186 0 00-.186-.186h-2.119a.186.186 0 00-.186.186v1.888c0 .102.083.185.186.185m0-2.716h2.119a.186.186 0 00.186-.186V6.289a.186.186 0 00-.186-.185h-2.119a.186.186 0 00-.186.185v1.888c0 .102.083.185.186.185M1.38 9.194v1.888c0 .102.082.185.185.185h2.12a.186.186 0 00.186-.185V9.194a.186.186 0 00-.186-.186H1.564a.185.185 0 00-.185.186M23.86 16.31c-.223-1.58-1.22-2.85-2.614-3.528l-1.07-5.242-1.246.253.947 4.636a6.83 6.83 0 00-1.46-.388v-2.09l-1.272.26v1.73a7.127 7.127 0 00-2.074.008v-1.74l-1.271-.258v2.087a6.666 6.666 0 00-1.488.42l.942-4.613-1.247-.255-1.066 5.22a4.91 4.91 0 00-2.6 3.498c-.287 1.406.136 2.768 1.05 3.513.844.686 2.05.86 3.193.52 1.352 1.492 3.755 2.126 6.137 1.64 2.383-.487 3.99-1.928 4.606-3.843 1.144.34 2.35.166 3.193-.52.914-.744 1.336-2.106 1.05-3.513"/></svg>`,
    k8s: `<svg viewBox="0 0 24 24" width="40" height="40" fill="#326ce5"><path d="M11.996 1.092l-1.232 1.068 1.232 1.068 1.232-1.068-1.232-1.068zm-2.033 1.748l-1.412.56 1.42 1.636 1.944-1.128-1.952-1.068zm4.066 0l1.412.56-1.42 1.636-1.944-1.128 1.952-1.068zm-6.176 1.836l-1.356.104.552 2.092 2.12-.664-1.316-1.532zm8.288 0l1.356.104-.552 2.092-2.12-.664 1.316-1.532zm-9.352 2.872l-.996-.34-.404 2.124 1.956.108-.556-1.892zm10.416 0l.996-.34.404 2.124-1.956.108.556-1.892zm-9.524 3.4l-.532-.696-2.06.668 1.48 1.42 1.112-1.392zm8.632 0l.532-.696 2.06.668-1.48 1.42-1.112-1.392zm-4.316.584l-2.052.796.88 2.136 2.348-.908-1.176-2.024zm1.156 2.024l2.348.908.88-2.136-2.052-.796-1.176 2.024z"/></svg>`
};

const SMIA_Builder = {
    state: {
        step: 0,
        envType: null, // 'local', 'docker', 'k8s'

        // Local specific settings
        localSettings: {
            instanceType: 'both' // 'normal', 'extended', 'both'
        },

        // XMPP Configuration
        xmpp: {
            strategy: 'new', // 'new' (deploy ejabberd), 'existing'
            domain: '',
            ip: ''
        },

        // Core Services (Docker/K8s only)
        core: {
            smiakb: false,
            ism: false, // Explicit state for ISM
            aasServer: { type: 'none', ip: '127.0.0.1' } // basyx, external, none
        },

        // Plan & Assets
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
                        Welcome to the configuration wizard. This tool will assist you in generating 
                        the necessary deployment files (Docker Compose / Kubernetes) or the local scaffolding 
                        for your SMIA environment.
                    </p>
                    <button id="btn-start" class="smia-btn primary btn-large">Start Configuration</button>
                </div>

                <div class="smia-step" id="step-1">
                    <h3>Step 1: Base Infrastructure</h3>
                    
                    <label class="section-label">Select Deployment Environment:</label>
                    <div class="env-grid">
                        <div class="env-card" data-env="local">
                            <span class="card-icon">${ICONS.local}</span>
                            <span class="card-title">Local (Python)</span>
                            <span class="card-desc">Container-less development. Direct Python execution scripts.</span>
                        </div>
                        <div class="env-card" data-env="docker">
                            <span class="card-icon">${ICONS.docker}</span>
                            <span class="card-title">Docker Compose</span>
                            <span class="card-desc">Standard containerized deployment for testing or light production.</span>
                        </div>
                        <div class="env-card" data-env="k8s">
                            <span class="card-icon">${ICONS.k8s}</span>
                            <span class="card-title">Kubernetes</span>
                            <span class="card-desc">Distributed, scalable deployment (generates YAMLs for Kompose).</span>
                        </div>
                    </div>
                    <div id="env-error" style="color: var(--color-problematic); display:none; margin-bottom:1rem;">
                        ⚠️ Please select an environment.
                    </div>

                    <div id="dynamic-infra-options" style="display:none; margin-top: 2rem; border-top: 1px solid var(--color-border); padding-top: 1.5rem;">
                        
                        <div id="local-options-group" style="display:none;">
                            <label class="section-label">Local Configuration:</label>
                            
                            <div class="form-group" style="margin-bottom: 1.5rem;">
                                <label for="xmpp-domain-local">XMPP Domain (Required for scripts)</label>
                                <input type="text" id="xmpp-domain-local" placeholder="e.g., localhost or smia.net" class="smia-input">
                            </div>

                            <label class="section-label">Python Scaffolding Type:</label>
                            <div class="env-grid" style="grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); margin-bottom: 0;">
                                <div class="option-card" data-local-type="normal">
                                    <strong>Standard</strong>
                                </div>
                                <div class="option-card" data-local-type="extended">
                                    <strong>Extended</strong>
                                </div>
                                <div class="option-card selected" data-local-type="both">
                                    <strong>Both</strong>
                                </div>
                            </div>
                        </div>

                        <div id="container-xmpp-options" style="display:none;">
                            <label class="section-label">XMPP Server Configuration:</label>
                            <div class="env-grid" style="grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); margin-bottom: 1rem;">
                                <div class="option-card selected" data-xmpp-strat="new">
                                    <span style="font-size:1.5rem; display:block; margin-bottom:0.5rem">📦</span>
                                    <strong>Deploy New</strong>
                                    <small style="display:block; color:var(--color-foreground-secondary)">Ejabberd Container</small>
                                </div>
                                <div class="option-card" data-xmpp-strat="existing">
                                    <span style="font-size:1.5rem; display:block; margin-bottom:0.5rem">🔗</span>
                                    <strong>Use Existing</strong>
                                    <small style="display:block; color:var(--color-foreground-secondary)">External Connection</small>
                                </div>
                            </div>

                            <div id="xmpp-details-section" style="display:none; margin-top: 1.5rem; background: var(--color-background-secondary); padding: 1.5rem; border-radius: 6px;">
                                <label class="section-label" style="margin-bottom: 0.5rem;">Connection Details</label>
                                <div class="form-group">
                                    <label for="xmpp-domain">Domain Name</label>
                                    <input type="text" id="xmpp-domain" placeholder="e.g., smia.net" class="smia-input">
                                </div>
                                <div class="form-group">
                                    <label for="xmpp-ip">Server IP Address</label>
                                    <input type="text" id="xmpp-ip" placeholder="e.g., 192.168.1.50" class="smia-input">
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="smia-step" id="step-2">
                   <h3>Step 2: Core SMIA Services</h3>
                   
                   <label class="section-label">Optional Components</label>
                   <div class="env-grid" style="grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); margin-bottom: 2rem;">
                        <div class="toggle-card" id="card-kb">
                            <div class="toggle-icon">🧠</div>
                            <strong>SMIA-I KB</strong>
                            <span class="toggle-status" id="status-kb">Disabled</span>
                        </div>
                        
                        <div class="toggle-card" id="card-ism">
                            <div class="toggle-icon">🌐</div>
                            <strong>SMIA ISM</strong>
                            <span class="toggle-status" id="status-ism">Disabled</span>
                        </div>
                   </div>

                   <label class="section-label">AAS Server Strategy</label>
                   <div class="env-grid" style="grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 1rem;">
                        <div class="option-card selected" data-aas="basyx">
                            <strong>Deploy Basyx</strong>
                        </div>
                        <div class="option-card" data-aas="external">
                            <strong>Use Existing</strong>
                        </div>
                        <div class="option-card" data-aas="none">
                            <strong>None</strong> (File Mode)
                        </div>
                   </div>
                   
                   <div id="aas-external-inputs" style="display:none; margin-top:1.5rem; padding: 1rem; background: var(--color-background-secondary); border-radius: 6px;">
                        <label>AAS Server IP</label>
                        <input type="text" id="aas-ip" class="smia-input" placeholder="e.g., 10.0.0.5">
                   </div>
                   
                   <div class="info-box" id="ism-auto-notice" style="display:none; margin-top:1.5rem;">
                        ℹ️ <strong>Note:</strong> SMIA ISM has been automatically enabled because SMIA-I KB requires it.
                   </div>
                </div>
                
                <div class="smia-step" id="step-3">
                    <h3 id="step-3-title">Step 3: Assets & Manufacturing</h3>
                    
                    <div id="step-3-intro-local" style="display:none; margin-bottom:1.5rem; color:var(--color-foreground-secondary)">
                        Add a single Asset file to be included in your local environment ZIP.
                    </div>

                    <div class="asset-card" id="plan-card-container">
                        <h4>Manufacturing Plan (Optional)</h4>
                        <label class="modern-checkbox">
                            <input type="checkbox" id="chk-has-plan">
                            <span class="checkmark"></span>
                            Include CSS-enriched Manufacturing Plan
                        </label>
                        
                        <div id="plan-inputs" style="display:none; margin-top: 10px;">
                            <div class="file-upload-wrapper">
                                <input type="file" id="plan-file" class="file-upload-input" onchange="SMIA_Builder.handleFileSelect(this)">
                                <div class="file-upload-label">
                                    <span class="file-text">Click to upload AASX file...</span>
                                    <span class="icon">📂</span>
                                </div>
                            </div>
                            <small style="display:block; margin: 8px 0; color: var(--color-foreground-secondary);">Or manually specify path/ID:</small>
                            <input type="text" id="plan-path" placeholder="/app/models/plan.aasx or AAS-ID" class="smia-input">
                        </div>
                    </div>

                    <label class="section-label" style="margin-top: 2rem;">Production Assets</label>
                    <div id="assets-list"></div>
                    <button class="smia-btn secondary" id="btn-add-asset" style="width:100%">+ Add Asset Instance</button>
                    
                    <hr style="margin: 2rem 0; border: 0; border-top: 1px solid var(--color-border);">
                    
                    <div class="form-group" id="operator-container">
                        <label class="checkbox-container">
                            <input type="checkbox" id="chk-operator"> Include SMIA Operator Dashboard
                        </label>
                    </div>
                </div>

                <div class="smia-step" id="step-4">
                    <h3>Review & Generate</h3>
                    <p>Review your configuration before generating the deployment package.</p>
                    <div id="summary-content"></div>
                </div>

                <div class="smia-controls" id="wizard-controls" style="display:none;">
                    <button id="btn-prev" class="smia-btn">Previous</button>
                    <button id="btn-next" class="smia-btn primary">Next</button>
                    <button id="btn-download" class="smia-btn primary" style="display:none">🚀 Download ZIP</button>
                </div>
            </div>
        `;
    },

    // --- EVENT HANDLING ---

    bindEvents: function() {
        // Start Wizard
        document.getElementById('btn-start').addEventListener('click', () => {
            this.state.step = 1;
            this.updateStepView();
        });

        // --- STEP 1: ENV SELECTION ---
        document.querySelectorAll('.env-card').forEach(card => {
            card.addEventListener('click', (e) => {
                // UI
                document.querySelectorAll('.env-card').forEach(c => c.classList.remove('selected'));
                e.currentTarget.classList.add('selected');
                document.getElementById('env-error').style.display = 'none';

                // Logic
                const env = e.currentTarget.dataset.env;
                this.state.envType = env;
                this.handleEnvChange(env);
            });
        });

        // --- STEP 1: LOCAL OPTIONS ---
        document.querySelectorAll('[data-local-type]').forEach(card => {
            card.addEventListener('click', (e) => {
                document.querySelectorAll('[data-local-type]').forEach(c => c.classList.remove('selected'));
                e.currentTarget.classList.add('selected');
                this.state.localSettings.instanceType = e.currentTarget.dataset.localType;
            });
        });

        // --- STEP 1: CONTAINER XMPP STRATEGY ---
        document.querySelectorAll('[data-xmpp-strat]').forEach(card => {
            card.addEventListener('click', (e) => {
                document.querySelectorAll('[data-xmpp-strat]').forEach(c => c.classList.remove('selected'));
                e.currentTarget.classList.add('selected');

                const strategy = e.currentTarget.dataset.xmppStrat;
                this.state.xmpp.strategy = strategy;

                // Toggle Detail Inputs
                const details = document.getElementById('xmpp-details-section');
                details.style.display = (strategy === 'existing') ? 'block' : 'none';
            });
        });

        // --- STEP 2: TOGGLE CARDS (KB & ISM) ---

        // KB Toggle
        document.getElementById('card-kb').addEventListener('click', () => {
            this.state.core.smiakb = !this.state.core.smiakb;
            this.updateToggleCard('card-kb', this.state.core.smiakb);

            // Auto-enable ISM if KB is ON
            if (this.state.core.smiakb) {
                this.state.core.ism = true;
                this.updateToggleCard('card-ism', true);
                document.getElementById('ism-auto-notice').style.display = 'block';
            } else {
                document.getElementById('ism-auto-notice').style.display = 'none';
            }
        });

        // ISM Toggle
        document.getElementById('card-ism').addEventListener('click', () => {
            // Cannot disable ISM if KB is ON
            if (this.state.core.ism && this.state.core.smiakb) {
                alert("SMIA ISM is required by SMIA-I KB. Disable KB first.");
                return;
            }
            this.state.core.ism = !this.state.core.ism;
            this.updateToggleCard('card-ism', this.state.core.ism);
        });

        // AAS Selection (Cards)
        document.querySelectorAll('[data-aas]').forEach(card => {
            card.addEventListener('click', (e) => {
                document.querySelectorAll('[data-aas]').forEach(c => c.classList.remove('selected'));
                e.currentTarget.classList.add('selected');

                const type = e.currentTarget.dataset.aas;
                this.state.core.aasServer.type = type;
                document.getElementById('aas-external-inputs').style.display = (type === 'external') ? 'block' : 'none';
            });
        });


        // --- NAVIGATION ---
        document.getElementById('btn-next').addEventListener('click', () => this.nextStep());
        document.getElementById('btn-prev').addEventListener('click', () => this.prevStep());
        document.getElementById('btn-download').addEventListener('click', () => this.generateZip());

        // --- STEP 3 LOGIC ---
        document.getElementById('btn-add-asset').addEventListener('click', () => this.addAssetUI());
        document.getElementById('chk-has-plan').addEventListener('change', (e) => {
            document.getElementById('plan-inputs').style.display = e.target.checked ? 'block' : 'none';
        });
    },

    handleEnvChange: function(env) {
        const container = document.getElementById('dynamic-infra-options');
        const localGroup = document.getElementById('local-options-group');
        const dockerGroup = document.getElementById('container-xmpp-options');

        container.style.display = 'block';

        if (env === 'local') {
            // Local UI Setup
            localGroup.style.display = 'block';
            dockerGroup.style.display = 'none';

            // Local implicitly uses "Existing" logic internally (requires domain)
            this.state.xmpp.strategy = 'existing';
        } else {
            // Docker/K8s UI Setup
            localGroup.style.display = 'none';
            dockerGroup.style.display = 'block';

            // Check current selection visibility
            const selectedStratCard = document.querySelector('[data-xmpp-strat].selected');
            const currentStrat = selectedStratCard ? selectedStratCard.dataset.xmppStrat : 'new';
            this.state.xmpp.strategy = currentStrat;
            document.getElementById('xmpp-details-section').style.display = (currentStrat === 'existing') ? 'block' : 'none';
        }
    },

    updateToggleCard: function(id, isActive) {
        const card = document.getElementById(id);
        const status = card.querySelector('.toggle-status');
        if (isActive) {
            card.classList.add('selected');
            status.textContent = "ENABLED";
        } else {
            card.classList.remove('selected');
            status.textContent = "DISABLED";
        }
    },

    // --- NAVIGATION LOGIC ---

    nextStep: function() {
        if(!this.validateStep(this.state.step)) return;
        this.captureStepData(this.state.step);

        // LOGIC JUMP: Fast Track for Local (Step 1 -> Step 3)
        if (this.state.step === 1 && this.state.envType === 'local') {
            this.state.step = 3;
        } else {
            this.state.step++;
        }

        this.updateStepView();
    },

    prevStep: function() {
        // LOGIC JUMP: Back from Step 3 -> Step 1 (If Local)
        if (this.state.step === 3 && this.state.envType === 'local') {
            this.state.step = 1;
        } else if (this.state.step > 1) {
            this.state.step--;
        } else if (this.state.step === 1) {
            this.state.step = 0;
        }
        this.updateStepView();
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
        // Hide all screens
        document.querySelectorAll('.smia-welcome-screen, .smia-step').forEach(el => el.classList.remove('active'));

        if (this.state.step === 0) {
            document.getElementById('step-0').classList.add('active');
            document.getElementById('progress-bar-container').style.display = 'none';
            document.getElementById('wizard-controls').style.display = 'none';
        } else {
            document.getElementById(`step-${this.state.step}`).classList.add('active');
            document.getElementById('progress-bar-container').style.display = 'block';
            document.getElementById('wizard-controls').style.display = 'flex';

            // Progress Bar Logic (Visual)
            let currentVisualStep = this.state.step;
            let totalSteps = 4;

            // Adjust visual progress for local track (1->3->4)
            if (this.state.envType === 'local') {
                if(this.state.step === 3) currentVisualStep = 2; // Step 3 counts as 2nd screen
                if(this.state.step === 4) currentVisualStep = 3; // Step 4 counts as 3rd screen
                totalSteps = 3;
            }
            document.getElementById('progress-fill').style.width = `${(currentVisualStep / totalSteps) * 100}%`;

            // Adjust Step 3 View for Local vs Docker
            if (this.state.step === 3) {
                const isLocal = (this.state.envType === 'local');

                // Title Change
                document.getElementById('step-3-title').textContent = isLocal ? "Add Asset File" : "Step 3: Assets & Manufacturing";

                // Show/Hide Sections
                document.getElementById('step-3-intro-local').style.display = isLocal ? 'block' : 'none';
                document.getElementById('plan-card-container').style.display = isLocal ? 'none' : 'block';
                document.getElementById('operator-container').style.display = isLocal ? 'none' : 'block';

                // Auto-add empty asset card for local if empty
                if (isLocal && document.getElementById('assets-list').children.length === 0) {
                    this.addAssetUI();
                }
            }

            // Buttons State
            document.getElementById('btn-prev').disabled = false;

            if (this.state.step === 4) {
                this.generateSummary();
                document.getElementById('btn-next').style.display = 'none';
                document.getElementById('btn-download').style.display = 'inline-block';
            } else {
                document.getElementById('btn-next').style.display = 'inline-block';
                document.getElementById('btn-download').style.display = 'none';
            }
        }
    },

    captureStepData: function(step) {
        if (step === 1) {
            if (this.state.envType === 'local') {
                this.state.xmpp.domain = document.getElementById('xmpp-domain-local').value || 'localhost';
            } else {
                this.state.xmpp.domain = document.getElementById('xmpp-domain').value || 'localhost';
                this.state.xmpp.ip = document.getElementById('xmpp-ip').value || '127.0.0.1';
            }
        }

        if (step === 2) {
             if (this.state.core.aasServer.type === 'external') {
                 this.state.core.aasServer.ip = document.getElementById('aas-ip').value;
            }
        }

        if (step === 3) {
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
                    path = fileObj.name;
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
        let html = '';

        if (s.envType === 'local') {
             html = `<table class="docutils align-default">
                <thead><tr><th>Configuration</th><th>Value</th></tr></thead>
                <tbody>
                    <tr><td>Environment</td><td><strong>LOCAL (Python)</strong></td></tr>
                    <tr><td>Instance Types</td><td>${s.localSettings.instanceType.toUpperCase()}</td></tr>
                    <tr><td>XMPP Domain</td><td>${s.xmpp.domain || 'N/A'}</td></tr>
                    <tr><td>Assets Attached</td><td>${s.assets.length}</td></tr>
                </tbody>
            </table>
            <div class="info-box">Generated ZIP will contain Python scaffolding scripts.</div>`;
        } else {
            // Docker/K8s Summary
            html = `<table class="docutils align-default">
                <thead><tr><th>Component</th><th>Configuration</th></tr></thead>
                <tbody>
                    <tr><td>Environment</td><td>${s.envType.toUpperCase()}</td></tr>
                    <tr><td>XMPP Server</td><td>${s.xmpp.strategy === 'new' ? 'New Container' : 'Existing'}</td></tr>
                    <tr><td>Core Services</td><td>${s.core.smiakb ? 'KB + ISM' : (s.core.ism ? 'ISM Only' : 'None')} | AAS: ${s.core.aasServer.type}</td></tr>
                    <tr><td>Assets</td><td>${s.assets.length} Defined</td></tr>
                    <tr><td>Operator</td><td>${s.operator ? 'Yes' : 'No'}</td></tr>
                </tbody>
            </table>`;
        }

        document.getElementById('summary-content').innerHTML = html;
    },

    // --- GENERATION LOGIC ---

    generateZip: function() {
        const zip = new JSZip();
        const s = this.state;

        // 1. Generate README
        let readmeContent = `# SMIA Environment - Generated Configuration\n\n`;
        readmeContent += `## Deployment Type: ${s.envType.toUpperCase()}\n\n`;

        if (s.envType === 'local') {
            readmeContent += `### Local Development Setup\n`;
            readmeContent += `You have selected a local environment configuration.\n\n`;
            readmeContent += `**XMPP Configuration:**\n- Domain: ${s.xmpp.domain}\n\n`;
            readmeContent += `**Included Scaffolding:**\n- Type: ${s.localSettings.instanceType}\n\n`;
            readmeContent += `### Instructions:\n1. Install Python dependencies.\n2. Use the scripts in the \`/scripts\` folder to start your instances.\n`;

            // Add Scaffolding
            const scripts = zip.folder("scripts");
            if (s.localSettings.instanceType === 'normal' || s.localSettings.instanceType === 'both') {
                scripts.file("start_normal.py", `# Python script for Standard SMIA Instance\nimport os\n\nXMPP_DOMAIN = "${s.xmpp.domain}"\n# TODO: Add logic`);
            }
            if (s.localSettings.instanceType === 'extended' || s.localSettings.instanceType === 'both') {
                scripts.file("start_extended.py", `# Python script for Extended SMIA Instance\nimport os\n\nXMPP_DOMAIN = "${s.xmpp.domain}"\n# TODO: Add logic`);
            }

        } else {
            // DOCKER / K8S
            const yamlContent = this.buildDockerCompose();
            zip.file("docker-compose.yml", yamlContent);

            readmeContent += `## How to Run\n\n### Docker Compose\n\`\`\`bash\ndocker compose up -d\n\`\`\`\n\n`;

            if (s.envType === 'k8s') {
                readmeContent += `### Kubernetes\nYou selected Kubernetes. Please use Kompose to convert the generated docker-compose.yml to K8s manifests:\n\n`;
                readmeContent += `\`\`\`bash\nkompose convert -f docker-compose.yml\nkubectl apply -f .\n\`\`\`\n`;
            }
        }

        zip.file("README.md", readmeContent);

        // 2. Handle Files (Models)
        // For Local, we also add asset files if user provided them, to root or specific folder
        const targetFolder = s.envType === 'local' ? zip : zip.folder("aas-models");

        // Add Plan File
        if (s.plan.hasPlan && s.plan.file) {
            targetFolder.file(s.plan.file.name, s.plan.file);
        }

        // Add Asset Files
        s.assets.forEach(asset => {
            if (asset.file) {
                targetFolder.file(asset.file.name, asset.file);
            }
        });

        // 3. Download
        zip.generateAsync({type:"blob"}).then(function(content) {
            saveAs(content, `smia-${s.envType}-config.zip`);
        });
    },

    buildDockerCompose: function() {
        const s = this.state;
        const indent = (n) => '  '.repeat(n);

        let yaml = `version: '3.8'\n\nservices:\n`;

        // 1. XMPP (Ejabberd) or External Config
        let xmppHost = '';
        if (s.xmpp.strategy === 'new') {
            xmppHost = 'ejabberd';
            yaml += `${indent(1)}ejabberd:\n`;
            yaml += `${indent(2)}image: ejabberd/ecs\n`;
            yaml += `${indent(2)}ports:\n${indent(3)}- "5222:5222"\n${indent(3)}- "5280:5280"\n`;
            yaml += `${indent(2)}environment:\n${indent(3)}- EJABBERD_DOMAIN=${s.xmpp.domain}\n${indent(3)}- EJABBERD_USER=admin\n${indent(3)}- EJABBERD_PASSWORD=password\n\n`;
        } else {
            xmppHost = s.xmpp.ip || 'host.docker.internal'; // Fallback
        }

        // 2. AAS Server (Basyx)
        if (s.core.aasServer.type === 'basyx') {
            yaml += `${indent(1)}aas-server:\n`;
            yaml += `${indent(2)}image: eclipse/basyx-aas-server:1.0.1\n`;
            yaml += `${indent(2)}ports:\n${indent(3)}- "8081:8081"\n`;
            yaml += `${indent(2)}volumes:\n${indent(3)}- ./aas-models:/usr/share/config/aas\n\n`;
        }

        // 3. SMIA ISM (Dependency check)
        // ISM is added if explicitly toggled OR if KB is ON
        const needsISM = s.core.ism || s.core.smiakb;
        if (needsISM) {
            yaml += `${indent(1)}smia-ism:\n`;
            yaml += `${indent(2)}image: smia/ism-core:latest\n`;
            yaml += `${indent(2)}environment:\n${indent(3)}- XMPP_HOST=${xmppHost}\n${indent(3)}- XMPP_DOMAIN=${s.xmpp.domain}\n\n`;
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
            yaml += `${indent(2)}environment:\n${indent(3)}- AAS_FILE=${s.plan.path}\n${indent(3)}- XMPP_HOST=${xmppHost}\n\n`;
        }

        // 6. Assets
        s.assets.forEach((asset, index) => {
            const serviceName = `asset-${index+1}`;
            yaml += `${indent(1)}${serviceName}:\n`;
            yaml += `${indent(2)}image: ${asset.isExtended ? asset.image : 'smia/standard-asset:latest'}\n`;
            yaml += `${indent(2)}volumes:\n${indent(3)}- ./aas-models:/app/models\n`;
            yaml += `${indent(2)}environment:\n`;
            yaml += `${indent(3)}- AAS_ID=${asset.path}\n`;
            yaml += `${indent(3)}- XMPP_HOST=${xmppHost}\n`;
            if (needsISM) yaml += `${indent(3)}- ISM_HOST=smia-ism\n`;
            yaml += `\n`;
        });

        // 7. Operator
        if (s.operator) {
            yaml += `${indent(1)}smia-operator:\n`;
            yaml += `${indent(2)}image: smia/operator-dashboard:latest\n`;
            yaml += `${indent(2)}ports:\n${indent(3)}- "3000:3000"\n`;
            yaml += `${indent(2)}environment:\n${indent(3)}- XMPP_HOST=${xmppHost}\n\n`;
        }

        return yaml;
    },

    // --- UTILS: Asset UI Generation ---

    addAssetUI: function() {
        const id = Date.now();
        const container = document.getElementById('assets-list');
        const div = document.createElement('div');
        div.className = 'asset-card';
        div.id = `asset-${id}`;

        // SVG Trash Icon
        const trashIcon = `<svg viewBox="0 0 24 24"><path d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z"/></svg>`;

        div.innerHTML = `
            <div class="asset-header">
                <strong>New Asset Instance</strong>
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
                <input type="text" class="asset-image-input smia-input" style="display:none; margin-top:5px;" placeholder="Docker Image Name (e.g., my-repo/asset:v1)">
            </div>
        `;

        // Logic for custom image toggle
        div.querySelector('.chk-extended').addEventListener('change', function(e) {
            div.querySelector('.asset-image-input').style.display = e.target.checked ? 'block' : 'none';
        });

        container.appendChild(div);
    },

    handleFileSelect: function(inputElement) {
        const label = inputElement.nextElementSibling;
        const textSpan = label.querySelector('.file-text');

        if (inputElement.files && inputElement.files.length > 0) {
            textSpan.textContent = inputElement.files[0].name;
            label.classList.add('has-file');
        } else {
            textSpan.textContent = "Upload AASX File";
            label.classList.remove('has-file');
        }
    },
};