/**
 * Team Management System
 * Team capacity planning, calendar, velocity tracking, workload balancing
 */

class TeamManagement {
    constructor() {
        this.teams = [];
        this.members = [];
        this.selectedTeam = null;
        this.calendar = null;
        
        this.init();
    }

    init() {
        this.createModal();
        this.setupEventListeners();
    }

    createModal() {
        const modalHTML = `
            <div id="teamManagementModal" class="team-modal" style="display: none;">
                <div class="team-modal-backdrop"></div>
                <div class="team-modal-container">
                    <div class="team-modal-header">
                        <h2>Team Management</h2>
                        <button class="btn-icon" id="closeTeamModal">
                            <i data-lucide="x"></i>
                        </button>
                    </div>

                    <div class="team-modal-body">
                        <!-- Teams Sidebar -->
                        <div class="teams-sidebar">
                            <div class="sidebar-header">
                                <h3>Teams</h3>
                                <button class="btn-icon-sm" id="createTeamBtn" title="Create Team">
                                    <i data-lucide="plus"></i>
                                </button>
                            </div>
                            <div class="teams-list" id="teamsList">
                                <!-- Populated by JS -->
                            </div>
                        </div>

                        <!-- Team Content -->
                        <div class="team-content" id="teamContent">
                            <div class="empty-state">
                                <i data-lucide="users"></i>
                                <p>Select a team to view details</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Create/Edit Team Dialog -->
            <div id="teamDialog" class="team-dialog" style="display: none;">
                <div class="team-dialog-backdrop"></div>
                <div class="team-dialog-container">
                    <div class="team-dialog-header">
                        <h3 id="teamDialogTitle">Create Team</h3>
                        <button class="btn-icon-sm" onclick="teamManagement.closeTeamDialog()">
                            <i data-lucide="x"></i>
                        </button>
                    </div>
                    <div class="team-dialog-body">
                        <div class="form-group">
                            <label>Team Name</label>
                            <input type="text" class="form-input" id="teamName" placeholder="e.g., Frontend Team">
                        </div>
                        <div class="form-group">
                            <label>Description</label>
                            <textarea class="form-input" id="teamDescription" rows="3" 
                                      placeholder="Brief description of the team's role"></textarea>
                        </div>
                    </div>
                    <div class="team-dialog-footer">
                        <button class="btn btn-ghost" onclick="teamManagement.closeTeamDialog()">Cancel</button>
                        <button class="btn btn-primary" id="saveTeamBtn">Save Team</button>
                    </div>
                </div>
            </div>

            <!-- Add Member Dialog -->
            <div id="memberDialog" class="team-dialog" style="display: none;">
                <div class="team-dialog-backdrop"></div>
                <div class="team-dialog-container">
                    <div class="team-dialog-header">
                        <h3>Add Team Member</h3>
                        <button class="btn-icon-sm" onclick="teamManagement.closeMemberDialog()">
                            <i data-lucide="x"></i>
                        </button>
                    </div>
                    <div class="team-dialog-body">
                        <div class="form-group">
                            <label>User</label>
                            <select class="form-input" id="memberUser">
                                <option value="">Select user...</option>
                                <!-- Populated by JS -->
                            </select>
                        </div>
                        <div class="form-group">
                            <label>Role</label>
                            <select class="form-input" id="memberRole">
                                <optgroup label="Executive Leadership">
                                    <option value="ceo">CEO</option>
                                    <option value="coo">COO</option>
                                    <option value="cto">CTO</option>
                                    <option value="vp_engineering">VP Engineering</option>
                                    <option value="vp_product">VP Product</option>
                                </optgroup>
                                <optgroup label="Directors">
                                    <option value="engineering_director">Engineering Director</option>
                                    <option value="product_director">Product Director</option>
                                    <option value="sales_director">Sales Director</option>
                                </optgroup>
                                <optgroup label="Software Engineering">
                                    <option value="software_architect">Software Architect</option>
                                    <option value="principal_software_engineer">Principal Software Engineer</option>
                                    <option value="staff_software_engineer">Staff Software Engineer</option>
                                    <option value="software_team_lead">Software Team Lead</option>
                                    <option value="senior_software_engineer_l4">Senior Software Engineer (L4)</option>
                                    <option value="senior_software_engineer_l3">Senior Software Engineer (L3)</option>
                                    <option value="software_engineer_l2">Software Engineer (L2)</option>
                                    <option value="junior_software_engineer_l1">Junior Software Engineer (L1)</option>
                                    <option value="get_software">GET - Software</option>
                                    <option value="software_intern">Software Intern</option>
                                </optgroup>
                                <optgroup label="Frontend Development">
                                    <option value="frontend_architect">Frontend Architect</option>
                                    <option value="frontend_team_lead">Frontend Team Lead</option>
                                    <option value="senior_frontend_engineer">Senior Frontend Engineer</option>
                                    <option value="frontend_engineer">Frontend Engineer</option>
                                    <option value="junior_frontend_engineer">Junior Frontend Engineer</option>
                                    <option value="get_frontend">GET - Frontend</option>
                                </optgroup>
                                <optgroup label="Backend Development">
                                    <option value="backend_architect">Backend Architect</option>
                                    <option value="backend_team_lead">Backend Team Lead</option>
                                    <option value="senior_backend_engineer">Senior Backend Engineer</option>
                                    <option value="backend_engineer">Backend Engineer</option>
                                    <option value="junior_backend_engineer">Junior Backend Engineer</option>
                                    <option value="get_backend">GET - Backend</option>
                                </optgroup>
                                <optgroup label="Fullstack Development">
                                    <option value="fullstack_architect">Fullstack Architect</option>
                                    <option value="fullstack_team_lead">Fullstack Team Lead</option>
                                    <option value="senior_fullstack_engineer">Senior Fullstack Engineer</option>
                                    <option value="fullstack_engineer">Fullstack Engineer</option>
                                    <option value="junior_fullstack_engineer">Junior Fullstack Engineer</option>
                                    <option value="get_fullstack">GET - Fullstack</option>
                                </optgroup>
                                <optgroup label="Embedded Software">
                                    <option value="embedded_software_architect">Embedded Software Architect</option>
                                    <option value="embedded_team_lead">Embedded Team Lead</option>
                                    <option value="senior_embedded_engineer_l4">Senior Embedded Engineer (L4)</option>
                                    <option value="senior_embedded_engineer_l3">Senior Embedded Engineer (L3)</option>
                                    <option value="embedded_engineer_l2">Embedded Engineer (L2)</option>
                                    <option value="junior_embedded_engineer_l1">Junior Embedded Engineer (L1)</option>
                                    <option value="get_embedded">GET - Embedded</option>
                                </optgroup>
                                <optgroup label="Firmware">
                                    <option value="firmware_architect">Firmware Architect</option>
                                    <option value="firmware_team_lead">Firmware Team Lead</option>
                                    <option value="senior_firmware_engineer">Senior Firmware Engineer</option>
                                    <option value="firmware_engineer">Firmware Engineer</option>
                                    <option value="junior_firmware_engineer">Junior Firmware Engineer</option>
                                    <option value="get_firmware">GET - Firmware</option>
                                    <option value="rtos_developer">RTOS Developer</option>
                                </optgroup>
                                <optgroup label="Linux BSP">
                                    <option value="linux_bsp_architect">Linux BSP Architect</option>
                                    <option value="bsp_team_lead">BSP Team Lead</option>
                                    <option value="senior_bsp_engineer">Senior BSP Engineer</option>
                                    <option value="bsp_engineer">BSP Engineer</option>
                                    <option value="junior_bsp_engineer">Junior BSP Engineer</option>
                                    <option value="get_bsp">GET - BSP</option>
                                    <option value="linux_kernel_engineer">Linux Kernel Engineer</option>
                                    <option value="linux_driver_developer">Linux Driver Developer</option>
                                    <option value="platform_engineer">Platform Engineer</option>
                                </optgroup>
                                <optgroup label="Hardware Engineering">
                                    <option value="hardware_architect">Hardware Architect</option>
                                    <option value="hardware_team_lead">Hardware Team Lead</option>
                                    <option value="senior_hardware_engineer_l4">Senior Hardware Engineer (L4)</option>
                                    <option value="senior_hardware_engineer_l3">Senior Hardware Engineer (L3)</option>
                                    <option value="hardware_engineer_l2">Hardware Engineer (L2)</option>
                                    <option value="junior_hardware_engineer_l1">Junior Hardware Engineer (L1)</option>
                                    <option value="get_hardware">GET - Hardware</option>
                                </optgroup>
                                <optgroup label="PCB Design">
                                    <option value="pcb_architect">PCB Architect</option>
                                    <option value="pcb_team_lead">PCB Team Lead</option>
                                    <option value="senior_pcb_designer">Senior PCB Designer</option>
                                    <option value="pcb_designer">PCB Designer</option>
                                    <option value="junior_pcb_designer">Junior PCB Designer</option>
                                    <option value="get_pcb">GET - PCB</option>
                                </optgroup>
                                <optgroup label="FPGA/ASIC">
                                    <option value="fpga_architect">FPGA Architect</option>
                                    <option value="fpga_team_lead">FPGA Team Lead</option>
                                    <option value="senior_fpga_engineer">Senior FPGA Engineer</option>
                                    <option value="fpga_engineer">FPGA Engineer</option>
                                    <option value="junior_fpga_engineer">Junior FPGA Engineer</option>
                                    <option value="get_fpga">GET - FPGA</option>
                                    <option value="asic_engineer">ASIC Engineer</option>
                                </optgroup>
                                <optgroup label="RF Engineering">
                                    <option value="rf_architect">RF Architect</option>
                                    <option value="rf_team_lead">RF Team Lead</option>
                                    <option value="senior_rf_engineer">Senior RF Engineer</option>
                                    <option value="rf_engineer">RF Engineer</option>
                                    <option value="junior_rf_engineer">Junior RF Engineer</option>
                                    <option value="get_rf">GET - RF</option>
                                </optgroup>
                                <optgroup label="Power Electronics">
                                    <option value="power_architect">Power Architect</option>
                                    <option value="power_team_lead">Power Team Lead</option>
                                    <option value="senior_power_engineer">Senior Power Engineer</option>
                                    <option value="power_engineer">Power Engineer</option>
                                    <option value="junior_power_engineer">Junior Power Engineer</option>
                                    <option value="get_power">GET - Power</option>
                                </optgroup>
                                <optgroup label="Mechanical Engineering">
                                    <option value="mechanical_architect">Mechanical Architect</option>
                                    <option value="mechanical_team_lead">Mechanical Team Lead</option>
                                    <option value="senior_mechanical_engineer_l4">Senior Mechanical Engineer (L4)</option>
                                    <option value="senior_mechanical_engineer_l3">Senior Mechanical Engineer (L3)</option>
                                    <option value="mechanical_engineer_l2">Mechanical Engineer (L2)</option>
                                    <option value="junior_mechanical_engineer_l1">Junior Mechanical Engineer (L1)</option>
                                    <option value="get_mechanical">GET - Mechanical</option>
                                </optgroup>
                                <optgroup label="CAD Design">
                                    <option value="cad_architect">CAD Architect</option>
                                    <option value="cad_team_lead">CAD Team Lead</option>
                                    <option value="senior_cad_designer">Senior CAD Designer</option>
                                    <option value="cad_designer">CAD Designer</option>
                                    <option value="junior_cad_designer">Junior CAD Designer</option>
                                    <option value="get_cad">GET - CAD</option>
                                </optgroup>
                                <optgroup label="Thermal Engineering">
                                    <option value="thermal_architect">Thermal Architect</option>
                                    <option value="thermal_team_lead">Thermal Team Lead</option>
                                    <option value="senior_thermal_engineer">Senior Thermal Engineer</option>
                                    <option value="thermal_engineer">Thermal Engineer</option>
                                    <option value="junior_thermal_engineer">Junior Thermal Engineer</option>
                                </optgroup>
                                <optgroup label="Manufacturing">
                                    <option value="manufacturing_manager">Manufacturing Manager</option>
                                    <option value="manufacturing_team_lead">Manufacturing Team Lead</option>
                                    <option value="senior_manufacturing_engineer">Senior Manufacturing Engineer</option>
                                    <option value="manufacturing_engineer">Manufacturing Engineer</option>
                                    <option value="junior_manufacturing_engineer">Junior Manufacturing Engineer</option>
                                    <option value="get_manufacturing">GET - Manufacturing</option>
                                    <option value="production_supervisor">Production Supervisor</option>
                                </optgroup>
                                <optgroup label="AI/ML Engineering">
                                    <option value="ml_architect">ML Architect</option>
                                    <option value="ml_team_lead">ML Team Lead</option>
                                    <option value="senior_ml_engineer_l4">Senior ML Engineer (L4)</option>
                                    <option value="senior_ml_engineer_l3">Senior ML Engineer (L3)</option>
                                    <option value="ml_engineer_l2">ML Engineer (L2)</option>
                                    <option value="junior_ml_engineer_l1">Junior ML Engineer (L1)</option>
                                    <option value="get_ml">GET - ML</option>
                                    <option value="ai_researcher">AI Researcher</option>
                                    <option value="nlp_engineer">NLP Engineer</option>
                                    <option value="computer_vision_engineer">Computer Vision Engineer</option>
                                </optgroup>
                                <optgroup label="Data Science">
                                    <option value="data_science_architect">Data Science Architect</option>
                                    <option value="data_science_team_lead">Data Science Team Lead</option>
                                    <option value="senior_data_scientist">Senior Data Scientist</option>
                                    <option value="data_scientist">Data Scientist</option>
                                    <option value="junior_data_scientist">Junior Data Scientist</option>
                                    <option value="get_data_science">GET - Data Science</option>
                                </optgroup>
                                <optgroup label="Data Engineering">
                                    <option value="data_architect">Data Architect</option>
                                    <option value="data_engineering_team_lead">Data Engineering Team Lead</option>
                                    <option value="senior_data_engineer">Senior Data Engineer</option>
                                    <option value="data_engineer">Data Engineer</option>
                                    <option value="junior_data_engineer">Junior Data Engineer</option>
                                    <option value="get_data_engineering">GET - Data Engineering</option>
                                </optgroup>
                                <optgroup label="DevOps/Cloud">
                                    <option value="devops_architect">DevOps Architect</option>
                                    <option value="devops_team_lead">DevOps Team Lead</option>
                                    <option value="senior_devops_engineer">Senior DevOps Engineer</option>
                                    <option value="devops_engineer">DevOps Engineer</option>
                                    <option value="junior_devops_engineer">Junior DevOps Engineer</option>
                                    <option value="get_devops">GET - DevOps</option>
                                    <option value="cloud_architect">Cloud Architect</option>
                                    <option value="cloud_engineer">Cloud Engineer</option>
                                    <option value="sre_engineer">SRE Engineer</option>
                                </optgroup>
                                <optgroup label="QA/Testing">
                                    <option value="qa_architect">QA Architect</option>
                                    <option value="qa_team_lead">QA Team Lead</option>
                                    <option value="senior_qa_engineer_l4">Senior QA Engineer (L4)</option>
                                    <option value="senior_qa_engineer_l3">Senior QA Engineer (L3)</option>
                                    <option value="qa_engineer_l2">QA Engineer (L2)</option>
                                    <option value="junior_qa_engineer_l1">Junior QA Engineer (L1)</option>
                                    <option value="get_qa">GET - QA</option>
                                    <option value="automation_team_lead">Automation Team Lead</option>
                                    <option value="senior_automation_engineer">Senior Automation Engineer</option>
                                    <option value="automation_engineer">Automation Engineer</option>
                                    <option value="hardware_test_engineer">Hardware Test Engineer</option>
                                </optgroup>
                                <optgroup label="Security">
                                    <option value="security_architect">Security Architect</option>
                                    <option value="security_team_lead">Security Team Lead</option>
                                    <option value="senior_security_engineer">Senior Security Engineer</option>
                                    <option value="security_engineer">Security Engineer</option>
                                    <option value="junior_security_engineer">Junior Security Engineer</option>
                                </optgroup>
                                <optgroup label="UI/UX Design">
                                    <option value="design_director">Design Director</option>
                                    <option value="design_team_lead">Design Team Lead</option>
                                    <option value="senior_ui_designer">Senior UI Designer</option>
                                    <option value="ui_designer">UI Designer</option>
                                    <option value="junior_ui_designer">Junior UI Designer</option>
                                    <option value="senior_ux_designer">Senior UX Designer</option>
                                    <option value="ux_designer">UX Designer</option>
                                    <option value="junior_ux_designer">Junior UX Designer</option>
                                    <option value="product_designer">Product Designer</option>
                                </optgroup>
                                <optgroup label="Industrial Design">
                                    <option value="industrial_design_lead">Industrial Design Lead</option>
                                    <option value="senior_industrial_designer">Senior Industrial Designer</option>
                                    <option value="industrial_designer">Industrial Designer</option>
                                    <option value="junior_industrial_designer">Junior Industrial Designer</option>
                                </optgroup>
                                <optgroup label="Product Management">
                                    <option value="chief_product_officer">Chief Product Officer</option>
                                    <option value="senior_product_manager">Senior Product Manager</option>
                                    <option value="product_manager">Product Manager</option>
                                    <option value="associate_product_manager">Associate Product Manager</option>
                                    <option value="product_owner">Product Owner</option>
                                </optgroup>
                                <optgroup label="Project Management">
                                    <option value="program_director">Program Director</option>
                                    <option value="senior_program_manager">Senior Program Manager</option>
                                    <option value="program_manager">Program Manager</option>
                                    <option value="senior_project_manager">Senior Project Manager</option>
                                    <option value="project_manager">Project Manager</option>
                                    <option value="associate_project_manager">Associate Project Manager</option>
                                    <option value="scrum_master">Scrum Master</option>
                                    <option value="agile_coach">Agile Coach</option>
                                    <option value="delivery_manager">Delivery Manager</option>
                                </optgroup>
                                <optgroup label="Business Analysis">
                                    <option value="senior_business_analyst">Senior Business Analyst</option>
                                    <option value="business_analyst">Business Analyst</option>
                                    <option value="junior_business_analyst">Junior Business Analyst</option>
                                </optgroup>
                                <optgroup label="Sales">
                                    <option value="sales_director">Sales Director</option>
                                    <option value="sales_manager">Sales Manager</option>
                                    <option value="sales_team_lead">Sales Team Lead</option>
                                    <option value="senior_sales_executive">Senior Sales Executive</option>
                                    <option value="sales_executive">Sales Executive</option>
                                    <option value="junior_sales_executive">Junior Sales Executive</option>
                                    <option value="sales_trainee">Sales Trainee</option>
                                    <option value="key_account_manager">Key Account Manager</option>
                                    <option value="business_development_manager">Business Development Manager</option>
                                    <option value="business_development_executive">Business Development Executive</option>
                                    <option value="pre_sales_engineer">Pre-Sales Engineer</option>
                                </optgroup>
                                <optgroup label="Marketing">
                                    <option value="marketing_director">Marketing Director</option>
                                    <option value="marketing_manager">Marketing Manager</option>
                                    <option value="marketing_team_lead">Marketing Team Lead</option>
                                    <option value="senior_marketing_executive">Senior Marketing Executive</option>
                                    <option value="marketing_executive">Marketing Executive</option>
                                    <option value="digital_marketing_manager">Digital Marketing Manager</option>
                                    <option value="content_writer">Content Writer</option>
                                    <option value="seo_specialist">SEO Specialist</option>
                                </optgroup>
                                <optgroup label="Customer Success">
                                    <option value="customer_success_director">Customer Success Director</option>
                                    <option value="customer_success_manager">Customer Success Manager</option>
                                    <option value="customer_success_team_lead">Customer Success Team Lead</option>
                                    <option value="customer_support_manager">Customer Support Manager</option>
                                    <option value="customer_support_team_lead">Customer Support Team Lead</option>
                                    <option value="senior_support_engineer">Senior Support Engineer</option>
                                    <option value="support_engineer">Support Engineer</option>
                                </optgroup>
                                <optgroup label="Vendor Management">
                                    <option value="vendor_management_director">Vendor Management Director</option>
                                    <option value="vendor_manager">Vendor Manager</option>
                                    <option value="vendor_team_lead">Vendor Team Lead</option>
                                    <option value="senior_vendor_coordinator">Senior Vendor Coordinator</option>
                                    <option value="vendor_coordinator">Vendor Coordinator</option>
                                    <option value="procurement_manager">Procurement Manager</option>
                                    <option value="procurement_executive">Procurement Executive</option>
                                    <option value="supply_chain_manager">Supply Chain Manager</option>
                                </optgroup>
                                <optgroup label="Human Resources">
                                    <option value="hr_director">HR Director</option>
                                    <option value="hr_manager">HR Manager</option>
                                    <option value="hr_team_lead">HR Team Lead</option>
                                    <option value="senior_hr_executive">Senior HR Executive</option>
                                    <option value="hr_executive">HR Executive</option>
                                    <option value="talent_acquisition_manager">Talent Acquisition Manager</option>
                                    <option value="senior_recruiter">Senior Recruiter</option>
                                    <option value="recruiter">Recruiter</option>
                                </optgroup>
                                <optgroup label="Finance">
                                    <option value="finance_director">Finance Director</option>
                                    <option value="finance_manager">Finance Manager</option>
                                    <option value="finance_team_lead">Finance Team Lead</option>
                                    <option value="senior_finance_executive">Senior Finance Executive</option>
                                    <option value="finance_executive">Finance Executive</option>
                                    <option value="accountant">Accountant</option>
                                </optgroup>
                                <optgroup label="Operations">
                                    <option value="operations_director">Operations Director</option>
                                    <option value="operations_manager">Operations Manager</option>
                                    <option value="operations_team_lead">Operations Team Lead</option>
                                    <option value="senior_operations_executive">Senior Operations Executive</option>
                                    <option value="operations_executive">Operations Executive</option>
                                    <option value="facilities_manager">Facilities Manager</option>
                                </optgroup>
                                <optgroup label="Legal & Compliance">
                                    <option value="legal_director">Legal Director</option>
                                    <option value="legal_manager">Legal Manager</option>
                                    <option value="legal_counsel">Legal Counsel</option>
                                    <option value="compliance_manager">Compliance Manager</option>
                                    <option value="compliance_officer">Compliance Officer</option>
                                </optgroup>
                                <optgroup label="Technical Writing">
                                    <option value="technical_writing_lead">Technical Writing Lead</option>
                                    <option value="senior_technical_writer">Senior Technical Writer</option>
                                    <option value="technical_writer">Technical Writer</option>
                                    <option value="junior_technical_writer">Junior Technical Writer</option>
                                </optgroup>
                                <optgroup label="Training">
                                    <option value="training_manager">Training Manager</option>
                                    <option value="training_lead">Training Lead</option>
                                    <option value="senior_trainer">Senior Trainer</option>
                                    <option value="trainer">Trainer</option>
                                </optgroup>
                                <optgroup label="IT Support">
                                    <option value="it_manager">IT Manager</option>
                                    <option value="it_team_lead">IT Team Lead</option>
                                    <option value="senior_it_administrator">Senior IT Administrator</option>
                                    <option value="it_administrator">IT Administrator</option>
                                    <option value="it_support_engineer">IT Support Engineer</option>
                                    <option value="network_administrator">Network Administrator</option>
                                    <option value="database_administrator">Database Administrator</option>
                                </optgroup>
                                <optgroup label="Other">
                                    <option value="get">GET (Graduate Engineer Trainee)</option>
                                    <option value="management_trainee">Management Trainee</option>
                                    <option value="intern">Intern</option>
                                    <option value="trainee">Trainee</option>
                                    <option value="contractor">Contractor</option>
                                    <option value="consultant">Consultant</option>
                                    <option value="vendor_resource">Vendor Resource</option>
                                    <option value="viewer">Viewer</option>
                                    <option value="admin">System Admin</option>
                                </optgroup>
                            </select>
                        </div>
                        <div class="form-group">
                            <label>Weekly Capacity (hours)</label>
                            <input type="number" class="form-input" id="memberCapacity" value="40" min="0" max="60">
                        </div>
                    </div>
                    <div class="team-dialog-footer">
                        <button class="btn btn-ghost" onclick="teamManagement.closeMemberDialog()">Cancel</button>
                        <button class="btn btn-primary" id="addMemberBtn">Add Member</button>
                    </div>
                </div>
            </div>
        `;

        document.body.insertAdjacentHTML('beforeend', modalHTML);

        if (window.lucide) {
            lucide.createIcons();
        }
    }

    setupEventListeners() {
        document.getElementById('closeTeamModal')?.addEventListener('click', () => {
            this.closeModal();
        });

        document.getElementById('createTeamBtn')?.addEventListener('click', () => {
            this.openTeamDialog();
        });

        document.getElementById('saveTeamBtn')?.addEventListener('click', () => {
            this.saveTeam();
        });

        document.getElementById('addMemberBtn')?.addEventListener('click', () => {
            this.addMember();
        });
    }

    openModal() {
        document.getElementById('teamManagementModal').style.display = 'block';
        this.loadTeams();
    }

    closeModal() {
        document.getElementById('teamManagementModal').style.display = 'none';
    }

    async loadTeams() {
        try {
            const response = await fetch('/api/teams');
            if (response.ok) {
                this.teams = await response.json();
                this.renderTeamsList();
                
                if (this.teams.length > 0 && !this.selectedTeam) {
                    this.selectTeam(this.teams[0].id);
                }
            }
        } catch (error) {
            console.error('Failed to load teams:', error);
        }
    }

    renderTeamsList() {
        const container = document.getElementById('teamsList');
        
        if (this.teams.length === 0) {
            container.innerHTML = `
                <div class="empty-sidebar">
                    <p>No teams yet</p>
                    <button class="btn btn-primary btn-sm" onclick="teamManagement.openTeamDialog()">
                        <i data-lucide="plus"></i>
                        Create Team
                    </button>
                </div>
            `;
            if (window.lucide) lucide.createIcons();
            return;
        }

        container.innerHTML = this.teams.map(team => `
            <div class="team-item ${this.selectedTeam === team.id ? 'active' : ''}" 
                 onclick="teamManagement.selectTeam('${team.id}')">
                <div class="team-icon">
                    <i data-lucide="users"></i>
                </div>
                <div class="team-info">
                    <div class="team-name">${team.name}</div>
                    <div class="team-meta">${team.members?.length || 0} members</div>
                </div>
            </div>
        `).join('');

        if (window.lucide) {
            lucide.createIcons();
        }
    }

    selectTeam(teamId) {
        this.selectedTeam = teamId;
        this.renderTeamsList();
        this.renderTeamDetails();
    }

    async renderTeamDetails() {
        const team = this.teams.find(t => t.id === this.selectedTeam);
        if (!team) return;

        const contentHTML = `
            <div class="team-details">
                <div class="team-header">
                    <div class="team-title">
                        <h2>${team.name}</h2>
                        <p class="team-description">${team.description || 'No description'}</p>
                    </div>
                    <div class="team-actions">
                        <button class="btn btn-ghost btn-sm" onclick="teamManagement.openTeamDialog('${team.id}')">
                            <i data-lucide="edit"></i>
                            Edit Team
                        </button>
                    </div>
                </div>

                <!-- Tab Navigation -->
                <div class="team-tabs">
                    <button class="team-tab active" data-tab="members">
                        <i data-lucide="users"></i>
                        Members
                    </button>
                    <button class="team-tab" data-tab="capacity">
                        <i data-lucide="calendar"></i>
                        Capacity
                    </button>
                    <button class="team-tab" data-tab="velocity">
                        <i data-lucide="trending-up"></i>
                        Velocity
                    </button>
                    <button class="team-tab" data-tab="workload">
                        <i data-lucide="bar-chart-2"></i>
                        Workload
                    </button>
                </div>

                <!-- Tab Content -->
                <div class="team-tab-content">
                    <div class="tab-pane active" data-pane="members" id="membersPane">
                        ${this.renderMembersPane(team)}
                    </div>
                    <div class="tab-pane" data-pane="capacity" id="capacityPane">
                        ${this.renderCapacityPane(team)}
                    </div>
                    <div class="tab-pane" data-pane="velocity" id="velocityPane">
                        ${this.renderVelocityPane(team)}
                    </div>
                    <div class="tab-pane" data-pane="workload" id="workloadPane">
                        ${this.renderWorkloadPane(team)}
                    </div>
                </div>
            </div>
        `;

        document.getElementById('teamContent').innerHTML = contentHTML;

        // Setup tab switching
        document.querySelectorAll('.team-tab').forEach(tab => {
            tab.addEventListener('click', (e) => {
                const tabName = e.currentTarget.dataset.tab;
                this.switchTab(tabName);
            });
        });

        if (window.lucide) {
            lucide.createIcons();
        }

        // Render charts
        this.renderVelocityChart(team);
        this.renderWorkloadChart(team);
    }

    renderMembersPane(team) {
        const members = team.members || [];
        
        return `
            <div class="members-header">
                <h3>Team Members (${members.length})</h3>
                <button class="btn btn-primary btn-sm" onclick="teamManagement.openMemberDialog()">
                    <i data-lucide="plus"></i>
                    Add Member
                </button>
            </div>

            <div class="members-list">
                ${members.length === 0 ? `
                    <div class="empty-state-small">
                        <i data-lucide="user-plus"></i>
                        <p>No members yet. Add your first team member.</p>
                    </div>
                ` : members.map(member => `
                    <div class="member-card">
                        <div class="member-avatar">
                            ${this.getInitials(member.name)}
                        </div>
                        <div class="member-info">
                            <div class="member-name">${member.name}</div>
                            <div class="member-role">${member.role}</div>
                        </div>
                        <div class="member-capacity">
                            <span class="capacity-label">${member.capacity || 40}h/week</span>
                        </div>
                        <button class="btn-icon-sm" onclick="teamManagement.removeMember('${team.id}', '${member.id}')">
                            <i data-lucide="x"></i>
                        </button>
                    </div>
                `).join('')}
            </div>
        `;
    }

    renderCapacityPane(team) {
        const members = team.members || [];
        const totalCapacity = members.reduce((sum, m) => sum + (m.capacity || 40), 0);
        const currentLoad = members.reduce((sum, m) => sum + (m.currentLoad || 0), 0);
        const utilization = totalCapacity > 0 ? ((currentLoad / totalCapacity) * 100).toFixed(1) : 0;

        return `
            <div class="capacity-overview">
                <div class="capacity-stats">
                    <div class="capacity-stat">
                        <div class="stat-label">Total Capacity</div>
                        <div class="stat-value">${totalCapacity}h</div>
                    </div>
                    <div class="capacity-stat">
                        <div class="stat-label">Current Load</div>
                        <div class="stat-value">${currentLoad}h</div>
                    </div>
                    <div class="capacity-stat">
                        <div class="stat-label">Utilization</div>
                        <div class="stat-value">${utilization}%</div>
                    </div>
                </div>

                <div class="capacity-calendar">
                    <div class="calendar-header">
                        <h3>Team Calendar</h3>
                        <button class="btn btn-ghost btn-sm" onclick="teamManagement.addTimeOff()">
                            <i data-lucide="calendar-plus"></i>
                            Add Time Off
                        </button>
                    </div>
                    <div id="teamCalendar" class="calendar-grid">
                        <!-- Calendar will be rendered here -->
                        <div class="calendar-placeholder">
                            <i data-lucide="calendar"></i>
                            <p>Calendar view coming soon</p>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    renderVelocityPane(team) {
        return `
            <div class="velocity-content">
                <div class="velocity-summary">
                    <div class="velocity-stat-card">
                        <div class="stat-icon">
                            <i data-lucide="trending-up"></i>
                        </div>
                        <div class="stat-content">
                            <div class="stat-label">Average Velocity</div>
                            <div class="stat-value">${team.avgVelocity || 24} SP</div>
                            <div class="stat-subtitle">Last 6 sprints</div>
                        </div>
                    </div>
                    <div class="velocity-stat-card">
                        <div class="stat-icon">
                            <i data-lucide="target"></i>
                        </div>
                        <div class="stat-content">
                            <div class="stat-label">Committed</div>
                            <div class="stat-value">${team.committed || 28} SP</div>
                            <div class="stat-subtitle">Current sprint</div>
                        </div>
                    </div>
                    <div class="velocity-stat-card">
                        <div class="stat-icon">
                            <i data-lucide="check-circle"></i>
                        </div>
                        <div class="stat-content">
                            <div class="stat-label">Completed</div>
                            <div class="stat-value">${team.completed || 22} SP</div>
                            <div class="stat-subtitle">Current sprint</div>
                        </div>
                    </div>
                </div>

                <div class="velocity-chart-card">
                    <h3>Velocity Trend</h3>
                    <div class="chart-container">
                        <canvas id="velocityChart"></canvas>
                    </div>
                </div>
            </div>
        `;
    }

    renderWorkloadPane(team) {
        return `
            <div class="workload-content">
                <div class="workload-header">
                    <h3>Team Workload Balance</h3>
                    <select class="form-input" id="workloadView">
                        <option value="current">Current Sprint</option>
                        <option value="next">Next Sprint</option>
                        <option value="week">This Week</option>
                    </select>
                </div>

                <div class="workload-chart-card">
                    <canvas id="workloadChart"></canvas>
                </div>

                <div class="workload-list">
                    ${(team.members || []).map(member => {
                        const load = member.currentLoad || 0;
                        const capacity = member.capacity || 40;
                        const percentage = capacity > 0 ? (load / capacity) * 100 : 0;
                        const status = percentage > 100 ? 'overloaded' : percentage > 80 ? 'high' : 'normal';

                        return `
                            <div class="workload-item">
                                <div class="workload-member">
                                    <div class="member-avatar small">
                                        ${this.getInitials(member.name)}
                                    </div>
                                    <div class="member-name">${member.name}</div>
                                </div>
                                <div class="workload-bar-container">
                                    <div class="workload-bar">
                                        <div class="workload-fill ${status}" style="width: ${Math.min(percentage, 100)}%"></div>
                                    </div>
                                    <div class="workload-label">${load}h / ${capacity}h</div>
                                </div>
                            </div>
                        `;
                    }).join('')}
                </div>
            </div>
        `;
    }

    switchTab(tabName) {
        document.querySelectorAll('.team-tab').forEach(tab => {
            tab.classList.toggle('active', tab.dataset.tab === tabName);
        });
        document.querySelectorAll('.tab-pane').forEach(pane => {
            pane.classList.toggle('active', pane.dataset.pane === tabName);
        });
    }

    renderVelocityChart(team) {
        const ctx = document.getElementById('velocityChart');
        if (!ctx) return;

        new Chart(ctx, {
            type: 'line',
            data: {
                labels: ['Sprint 1', 'Sprint 2', 'Sprint 3', 'Sprint 4', 'Sprint 5', 'Sprint 6'],
                datasets: [{
                    label: 'Completed',
                    data: team.velocityData || [20, 24, 22, 26, 23, 28],
                    borderColor: '#10B981',
                    backgroundColor: 'rgba(16, 185, 129, 0.1)',
                    fill: true,
                    tension: 0.4
                }, {
                    label: 'Committed',
                    data: [22, 26, 24, 28, 25, 30],
                    borderColor: '#3B82F6',
                    backgroundColor: 'rgba(59, 130, 246, 0.1)',
                    fill: true,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }

    renderWorkloadChart(team) {
        const ctx = document.getElementById('workloadChart');
        if (!ctx) return;

        const members = team.members || [];
        
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: members.map(m => m.name),
                datasets: [{
                    label: 'Current Load',
                    data: members.map(m => m.currentLoad || 0),
                    backgroundColor: '#3B82F6'
                }, {
                    label: 'Capacity',
                    data: members.map(m => m.capacity || 40),
                    backgroundColor: '#E5E7EB'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }

    getInitials(name) {
        return name.split(' ').map(n => n[0]).join('').toUpperCase();
    }

    openTeamDialog(teamId = null) {
        const dialog = document.getElementById('teamDialog');
        const title = document.getElementById('teamDialogTitle');
        
        if (teamId) {
            const team = this.teams.find(t => t.id === teamId);
            title.textContent = 'Edit Team';
            document.getElementById('teamName').value = team.name;
            document.getElementById('teamDescription').value = team.description || '';
        } else {
            title.textContent = 'Create Team';
            document.getElementById('teamName').value = '';
            document.getElementById('teamDescription').value = '';
        }

        dialog.style.display = 'block';
        if (window.lucide) lucide.createIcons();
    }

    closeTeamDialog() {
        document.getElementById('teamDialog').style.display = 'none';
    }

    async saveTeam() {
        const name = document.getElementById('teamName').value;
        const description = document.getElementById('teamDescription').value;

        if (!name) return;

        try {
            const response = await fetch('/api/teams', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name, description })
            });

            if (response.ok) {
                this.closeTeamDialog();
                this.loadTeams();
            }
        } catch (error) {
            console.error('Failed to save team:', error);
        }
    }

    openMemberDialog() {
        document.getElementById('memberDialog').style.display = 'block';
        this.loadAvailableUsers();
        if (window.lucide) lucide.createIcons();
    }

    closeMemberDialog() {
        document.getElementById('memberDialog').style.display = 'none';
    }

    async loadAvailableUsers() {
        try {
            const response = await fetch('/api/users');
            if (response.ok) {
                const users = await response.json();
                const select = document.getElementById('memberUser');
                select.innerHTML = '<option value="">Select user...</option>' +
                    users.map(u => `<option value="${u.id}">${u.name}</option>`).join('');
            }
        } catch (error) {
            console.error('Failed to load users:', error);
        }
    }

    async addMember() {
        const userId = document.getElementById('memberUser').value;
        const role = document.getElementById('memberRole').value;
        const capacity = parseInt(document.getElementById('memberCapacity').value);

        if (!userId) return;

        try {
            const response = await fetch(`/api/teams/${this.selectedTeam}/members`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ userId, role, capacity })
            });

            if (response.ok) {
                this.closeMemberDialog();
                this.loadTeams();
                this.renderTeamDetails();
            }
        } catch (error) {
            console.error('Failed to add member:', error);
        }
    }

    async removeMember(teamId, memberId) {
        if (!confirm('Remove this member from the team?')) return;

        try {
            const response = await fetch(`/api/teams/${teamId}/members/${memberId}`, {
                method: 'DELETE'
            });

            if (response.ok) {
                this.loadTeams();
                this.renderTeamDetails();
            }
        } catch (error) {
            console.error('Failed to remove member:', error);
        }
    }

    addTimeOff() {
        alert('Time off management coming soon!');
    }
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    window.teamManagement = new TeamManagement();
});

// Global function
function openTeamManagement() {
    window.teamManagement?.openModal();
}
