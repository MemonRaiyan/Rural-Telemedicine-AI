const TEMPLATES = {
  // 1. LOGIN & DEMO SELECTION VIEW
  'login': `
    <div class="text-center mb-6 mt-4">
        <div class="inline-flex items-center justify-center w-16 h-16 bg-teal-100 text-teal-700 rounded-full mb-3 text-3xl">
            <i class="fas fa-heartbeat"></i>
        </div>
        <h2 class="text-2xl font-bold text-teal-800" data-i18n="app_name">GramCare AI</h2>
        <p class="text-gray-500 text-xs mt-1" data-i18n="app_subtitle">AI-Powered Rural Telemedicine & Community Healthcare</p>
    </div>
    
    <!-- 🎓 1-Click Demo Evaluation Mode -->
    <div class="bg-gradient-to-br from-blue-50 to-teal-50 border border-blue-200 rounded-2xl p-5 mb-6 shadow-sm">
        <div class="flex items-center justify-between mb-2">
            <h3 class="font-bold text-blue-900 text-sm flex items-center">
                <i class="fas fa-graduation-cap text-teal-600 mr-2"></i> 🎓 Project Demo Evaluation Mode
            </h3>
            <span class="bg-blue-200 text-blue-800 text-[10px] font-bold px-2 py-0.5 rounded-full">One-Click Access</span>
        </div>
        <p class="text-xs text-blue-700 mb-4">Select an academic demo persona to evaluate the full end-to-end workflows:</p>
        
        <div class="grid grid-cols-2 gap-3">
            <button class="bg-white border border-teal-200 p-3 rounded-xl shadow-xs text-left hover:border-teal-500 hover:shadow-md transition flex flex-col" onclick="app.loginDemo('patient')">
                <span class="text-2xl mb-1">👨🏽‍🌾</span>
                <span class="font-bold text-xs text-gray-800">Patient</span>
                <span class="text-[10px] text-gray-500">Ramesh Patel (Rampura)</span>
            </button>
            <button class="bg-white border border-teal-200 p-3 rounded-xl shadow-xs text-left hover:border-teal-500 hover:shadow-md transition flex flex-col" onclick="app.loginDemo('doctor')">
                <span class="text-2xl mb-1">👩🏽‍⚕️</span>
                <span class="font-bold text-xs text-gray-800">Doctor</span>
                <span class="text-[10px] text-gray-500">Dr. Anjali Patel (Physician)</span>
            </button>
            <button class="bg-white border border-teal-200 p-3 rounded-xl shadow-xs text-left hover:border-teal-500 hover:shadow-md transition flex flex-col" onclick="app.loginDemo('hospital')">
                <span class="text-2xl mb-1">🏥</span>
                <span class="font-bold text-xs text-gray-800">Hospital / NGO</span>
                <span class="text-[10px] text-gray-500">Shakti Community Hospital</span>
            </button>
            <button class="bg-white border border-teal-200 p-3 rounded-xl shadow-xs text-left hover:border-teal-500 hover:shadow-md transition flex flex-col" onclick="app.loginDemo('admin')">
                <span class="text-2xl mb-1">🛡️</span>
                <span class="font-bold text-xs text-gray-800">Administrator</span>
                <span class="text-[10px] text-gray-500">System Admin & Audit</span>
            </button>
        </div>
        <div class="mt-3 text-center">
            <button class="text-[11px] text-teal-700 font-semibold hover:underline" onclick="app.loginDemo('community_rep')">
                <i class="fas fa-landmark mr-1"></i> Or test as Village Representative (Sarpanch)
            </button>
        </div>
    </div>

    <!-- Manual Credential Login / Register Toggle -->
    <div class="soft-card">
        <div class="flex border-b border-gray-200 mb-4">
            <button id="tab-login" class="flex-1 pb-2 font-bold text-sm text-teal-700 border-b-2 border-teal-600" onclick="app.switchAuthTab('login')">Sign In</button>
            <button id="tab-register" class="flex-1 pb-2 font-medium text-sm text-gray-400" onclick="app.switchAuthTab('register')">Register New</button>
        </div>

        <form id="form-auth-login" onsubmit="app.handleManualLogin(event)" class="space-y-3">
            <div>
                <label class="block text-xs font-semibold text-gray-600 mb-1">Email or Phone</label>
                <input type="email" id="auth-email" required class="w-full border border-gray-300 rounded-lg p-2.5 text-sm focus:ring-2 focus:ring-teal-500" placeholder="patient@gramcare.in">
            </div>
            <div>
                <label class="block text-xs font-semibold text-gray-600 mb-1">Password</label>
                <input type="password" id="auth-password" required class="w-full border border-gray-300 rounded-lg p-2.5 text-sm focus:ring-2 focus:ring-teal-500" placeholder="••••••••">
            </div>
            <button type="submit" class="w-full bg-teal-700 text-white font-bold py-2.5 rounded-lg text-sm hover:bg-teal-800 transition">
                Sign In to GramCare
            </button>
        </form>

        <form id="form-auth-register" onsubmit="app.handleManualRegister(event)" class="space-y-3 hidden">
            <div>
                <label class="block text-xs font-semibold text-gray-600 mb-1">Full Name</label>
                <input type="text" id="reg-name" required class="w-full border border-gray-300 rounded-lg p-2 text-sm" placeholder="e.g. Ramesh Patel">
            </div>
            <div>
                <label class="block text-xs font-semibold text-gray-600 mb-1">Account Role</label>
                <select id="reg-role" class="w-full border border-gray-300 rounded-lg p-2 text-sm">
                    <option value="PATIENT">Patient / Rural User</option>
                    <option value="DOCTOR">Doctor</option>
                    <option value="HOSPITAL">Hospital / NGO</option>
                    <option value="COMMUNITY_REP">Village Representative</option>
                </select>
            </div>
            <div>
                <label class="block text-xs font-semibold text-gray-600 mb-1">Email</label>
                <input type="email" id="reg-email" required class="w-full border border-gray-300 rounded-lg p-2 text-sm" placeholder="user@example.com">
            </div>
            <div>
                <label class="block text-xs font-semibold text-gray-600 mb-1">Password</label>
                <input type="password" id="reg-password" required class="w-full border border-gray-300 rounded-lg p-2 text-sm" placeholder="Minimum 6 characters">
            </div>
            <div class="grid grid-cols-2 gap-2">
                <div>
                    <label class="block text-xs font-semibold text-gray-600 mb-1">Village / City</label>
                    <input type="text" id="reg-village" class="w-full border border-gray-300 rounded-lg p-2 text-sm" placeholder="Rampura">
                </div>
                <div>
                    <label class="block text-xs font-semibold text-gray-600 mb-1">District</label>
                    <input type="text" id="reg-district" class="w-full border border-gray-300 rounded-lg p-2 text-sm" placeholder="Mehsana">
                </div>
            </div>
            <button type="submit" class="w-full bg-emerald-600 text-white font-bold py-2.5 rounded-lg text-sm hover:bg-emerald-700 transition">
                Create Account
            </button>
        </form>
    </div>
  `,

  // 2. PATIENT DASHBOARD VIEW
  'patient-home': `
    <!-- Top Action Cards -->
    <div class="grid grid-cols-2 gap-3 mb-5">
        <button class="soft-card flex flex-col items-center justify-center p-4 text-teal-800 hover:border-teal-500 border border-transparent transition" onclick="app.navigate('ai-triage')">
            <div class="bg-teal-100 p-3 rounded-2xl mb-2 text-teal-700 text-2xl">
                <i class="fas fa-robot"></i>
            </div>
            <span class="font-bold text-xs text-center" data-i18n="action_ai_check">AI Symptom Check</span>
            <span class="text-[10px] text-teal-600 mt-0.5">Triage & Guidance</span>
        </button>

        <button class="soft-card flex flex-col items-center justify-center p-4 text-blue-800 hover:border-blue-500 border border-transparent transition" onclick="app.navigate('doctor-search')">
            <div class="bg-blue-100 p-3 rounded-2xl mb-2 text-blue-700 text-2xl">
                <i class="fas fa-stethoscope"></i>
            </div>
            <span class="font-bold text-xs text-center" data-i18n="action_talk_doctor">Talk to Doctor</span>
            <span class="text-[10px] text-blue-600 mt-0.5">Verified Tele-care</span>
        </button>

        <button class="soft-card flex flex-col items-center justify-center p-4 text-emerald-800 hover:border-emerald-500 border border-transparent transition" onclick="app.navigate('health-camps')">
            <div class="bg-emerald-100 p-3 rounded-2xl mb-2 text-emerald-700 text-2xl">
                <i class="fas fa-campground"></i>
            </div>
            <span class="font-bold text-xs text-center" data-i18n="action_health_camps">Health Camps</span>
            <span class="text-[10px] text-emerald-600 mt-0.5">Free Village Camps</span>
        </button>

        <button class="soft-card flex flex-col items-center justify-center p-4 text-indigo-800 hover:border-indigo-500 border border-transparent transition" onclick="app.navigate('image-screening')">
            <div class="bg-indigo-100 p-3 rounded-2xl mb-2 text-indigo-700 text-2xl">
                <i class="fas fa-x-ray"></i>
            </div>
            <span class="font-bold text-xs text-center" data-i18n="action_image_screen">Medical Image AI</span>
            <span class="text-[10px] text-indigo-600 mt-0.5">X-Ray & Skin Check</span>
        </button>
    </div>

    <!-- Active / Upcoming Appointment -->
    <div class="mb-5">
        <div class="flex justify-between items-center mb-2">
            <h3 class="font-bold text-sm text-gray-800 flex items-center" data-i18n="card_upcoming_consultation">
                <i class="far fa-calendar-check text-teal-600 mr-1.5"></i> Upcoming Consultation
            </h3>
            <span class="text-xs text-teal-600 font-semibold cursor-pointer" onclick="app.navigate('patient-appointments')">All ( <span id="patient-appts-count">0</span> )</span>
        </div>
        <div id="patient-upcoming-card">
            <!-- Dynamic Card Loaded via JS -->
        </div>
    </div>

    <!-- ABHA / ABDM Profile Summary -->
    <div class="soft-card bg-gradient-to-r from-teal-900 to-emerald-900 text-white p-4 rounded-2xl mb-5 shadow-sm">
        <div class="flex justify-between items-start mb-2">
            <div>
                <span class="text-[10px] text-emerald-300 font-bold uppercase tracking-wider">Ayushman Bharat (ABDM Sandbox)</span>
                <h4 class="font-bold text-base mt-0.5" id="patient-abha-name">Ramesh Patel</h4>
            </div>
            <div class="flex items-center space-x-1.5">
                <button class="bg-white/20 hover:bg-white/30 text-[10px] px-2 py-0.5 rounded text-white font-semibold" onclick="app.openPatientProfileEdit()">
                    <i class="fas fa-edit mr-0.5"></i> Edit Profile
                </button>
                <span id="patient-abha-badge" class="bg-emerald-400 text-teal-950 text-[10px] font-extrabold px-2 py-0.5 rounded-full flex items-center">
                    <i class="fas fa-check-circle mr-1"></i> LINKED
                </span>
            </div>
        </div>
        <div class="flex items-center justify-between text-xs font-mono opacity-90 mt-1 mb-3">
            <span id="patient-abha-id">14-2394-3948-2938</span>
            <span class="text-[10px] font-sans opacity-75">HIE-CM Ready</span>
        </div>
        <div class="flex space-x-2">
            <button class="flex-1 bg-white/20 hover:bg-white/30 text-white text-xs py-1.5 rounded-lg font-medium transition" onclick="app.navigate('health-records')">
                <i class="fas fa-file-medical mr-1"></i> Records
            </button>
            <button class="flex-1 bg-emerald-500 hover:bg-emerald-400 text-teal-950 text-xs py-1.5 rounded-lg font-bold transition" onclick="app.viewAbdmConsents()">
                <i class="fas fa-key mr-1"></i> Consents
            </button>
        </div>
    </div>

    <!-- Health Camps Preview -->
    <div class="mb-4">
        <div class="flex justify-between items-center mb-2">
            <h3 class="font-bold text-sm text-gray-800" data-i18n="card_nearby_camps">Nearby Health Camps</h3>
            <button class="text-teal-600 text-xs font-semibold" onclick="app.navigate('health-camps')">See All Camps</button>
        </div>
        <div id="patient-home-camps-list" class="space-y-3">
            <!-- Dynamic Camps Loaded via JS -->
        </div>
    </div>
  `,

  // 3. AI SYMPTOM TRIAGE VIEW
  'ai-triage': `
    <div class="mb-4 flex items-center justify-between">
        <button class="text-teal-700 text-sm font-semibold flex items-center" onclick="app.navigate('patient-home')">
            <i class="fas fa-arrow-left mr-1.5"></i> Back
        </button>
        <h2 class="font-bold text-base text-gray-800" data-i18n="triage_title">AI Symptom Triage</h2>
        <span class="bg-teal-100 text-teal-800 text-[10px] font-bold px-2 py-0.5 rounded-full">NLP Clinical</span>
    </div>

    <!-- Medical Safety Warning Banner -->
    <div class="bg-amber-50 border-l-4 border-amber-500 p-3 rounded-r-xl text-xs text-amber-900 mb-4">
        <p class="font-bold flex items-center"><i class="fas fa-shield-alt text-amber-600 mr-1.5"></i> Important Medical Safety Rule:</p>
        <p class="mt-0.5 opacity-90" data-i18n="triage_disclaimer">
            This is a preliminary health assessment and does not replace diagnosis or advice from a qualified healthcare professional.
        </p>
    </div>

    <!-- Emergency Alert Box (Hidden unless triggered) -->
    <div id="emergency-alert-banner" class="hidden bg-red-100 border-2 border-red-500 p-4 rounded-xl text-red-950 mb-4 animate-pulse">
        <div class="flex items-start">
            <i class="fas fa-exclamation-triangle text-2xl text-red-600 mr-3 mt-0.5"></i>
            <div>
                <h4 class="font-bold text-sm text-red-800" data-i18n="emergency_warning">EMERGENCY ALERT: Immediate medical care required!</h4>
                <p id="emergency-alert-text" class="text-xs mt-1 text-red-900 leading-relaxed"></p>
                <div class="mt-3 flex space-x-2">
                    <a href="tel:108" class="bg-red-600 text-white font-bold text-xs px-3 py-1.5 rounded-lg shadow-sm flex items-center">
                        <i class="fas fa-phone-alt mr-1.5"></i> Call 108 Ambulance
                    </a>
                    <a href="tel:112" class="bg-gray-800 text-white font-bold text-xs px-3 py-1.5 rounded-lg shadow-sm flex items-center">
                        <i class="fas fa-phone-alt mr-1.5"></i> National 112
                    </a>
                </div>
            </div>
        </div>
    </div>

    <div class="soft-card">
        <label class="block text-xs font-bold text-gray-700 mb-1" data-i18n="triage_prompt">What problem are you experiencing?</label>
        <p class="text-[11px] text-gray-500 mb-2">You can type in English, हिन्दी, or ગુજરાતી. Voice input is also supported.</p>
        
        <div class="relative">
            <textarea id="triage-symptoms-input" rows="4" class="w-full border border-gray-300 rounded-xl p-3 text-sm focus:ring-2 focus:ring-teal-500" placeholder="e.g. 2 દિવસથી તાવ અને ગળામાં દુખાવો છે, અથવા 3 days high fever and dry cough..."></textarea>
            <button id="voice-input-btn" type="button" class="absolute right-3 bottom-3 text-teal-600 hover:text-teal-800 p-2 rounded-full bg-teal-50 border border-teal-200" onclick="app.toggleVoiceInput()" title="Voice Input">
                <i class="fas fa-microphone"></i>
            </button>
        </div>

        <div class="grid grid-cols-3 gap-2 mt-3">
            <div>
                <label class="block text-[11px] font-semibold text-gray-600 mb-1">Duration</label>
                <select id="triage-duration" class="w-full border border-gray-300 rounded-lg p-2 text-xs">
                    <option value="1-2 days">1-2 days</option>
                    <option value="3-5 days" selected>3-5 days</option>
                    <option value="1-2 weeks">1-2 weeks</option>
                    <option value="More than 2 weeks">> 2 weeks</option>
                </select>
            </div>
            <div>
                <label class="block text-[11px] font-semibold text-gray-600 mb-1">Severity</label>
                <select id="triage-severity" class="w-full border border-gray-300 rounded-lg p-2 text-xs">
                    <option value="Mild">Mild</option>
                    <option value="Moderate" selected>Moderate</option>
                    <option value="Severe">Severe</option>
                </select>
            </div>
            <div>
                <label class="block text-[11px] font-semibold text-gray-600 mb-1">Age</label>
                <input type="number" id="triage-age" value="38" class="w-full border border-gray-300 rounded-lg p-2 text-xs">
            </div>
        </div>

        <button id="btn-submit-triage" class="w-full bg-teal-700 text-white font-bold py-3 rounded-xl mt-4 flex items-center justify-center hover:bg-teal-800 shadow-sm transition" onclick="app.executeTriage()">
            <i class="fas fa-brain mr-2"></i> Run AI Clinical Triage
        </button>
    </div>

    <!-- Triage Assessment Results Container -->
    <div id="triage-results-container" class="hidden mt-4">
        <h3 class="font-bold text-sm text-gray-800 mb-2 flex items-center">
            <i class="fas fa-poll-h text-teal-600 mr-1.5"></i> Preliminary AI Assessment
        </h3>
        <div id="triage-card" class="soft-card border-l-4">
            <div class="flex justify-between items-center mb-3">
                <span class="text-xs text-gray-500 font-semibold" data-i18n="triage_urgency">Urgency Level:</span>
                <span id="res-urgency-badge" class="text-xs font-bold px-2.5 py-1 rounded-full uppercase"></span>
            </div>
            <div class="mb-3">
                <span class="text-[11px] text-gray-500 uppercase font-semibold" data-i18n="triage_department">Suggested Department</span>
                <h4 id="res-suggested-dept" class="font-bold text-base text-teal-800"></h4>
            </div>
            <div class="mb-3 bg-gray-50 p-3 rounded-lg text-xs text-gray-700">
                <p class="font-semibold text-gray-800 mb-1">Symptom Summary:</p>
                <p id="res-symptom-summary" class="leading-relaxed"></p>
            </div>
            <div class="mb-3 text-xs">
                <p class="font-semibold text-gray-800 mb-1">Recommended Next Step:</p>
                <p id="res-recommended-step" class="text-gray-600 leading-relaxed"></p>
            </div>
            <div class="bg-blue-50 border border-blue-200 p-2.5 rounded-lg text-[11px] text-blue-900">
                <p class="font-semibold mb-0.5"><i class="fas fa-question-circle mr-1"></i> Questions to Discuss with Doctor:</p>
                <ul id="res-questions-list" class="list-disc pl-4 space-y-0.5 text-blue-800"></ul>
            </div>
        </div>

        <button class="w-full bg-blue-700 hover:bg-blue-800 text-white font-bold py-3 rounded-xl mt-3 flex items-center justify-center shadow-md transition" onclick="app.findDoctorForDepartment()">
            <i class="fas fa-user-md mr-2"></i> Find Suitable Doctor Now
        </button>
    </div>
  `,

  // 4. MEDICAL IMAGE SCREENING VIEW
  'image-screening': `
    <div class="mb-4 flex items-center justify-between">
        <button class="text-teal-700 text-sm font-semibold flex items-center" onclick="app.navigate('patient-home')">
            <i class="fas fa-arrow-left mr-1.5"></i> Back
        </button>
        <h2 class="font-bold text-base text-gray-800" data-i18n="image_screening_title">Medical Image AI Screening</h2>
        <span class="bg-indigo-100 text-indigo-800 text-[10px] font-bold px-2 py-0.5 rounded-full">Computer Vision</span>
    </div>

    <div class="bg-indigo-50 border-l-4 border-indigo-600 p-3 rounded-r-xl text-xs text-indigo-900 mb-4">
        <p class="font-bold flex items-center"><i class="fas fa-microscope text-indigo-700 mr-1.5"></i> Diagnostic Screening Prototype:</p>
        <p class="mt-0.5 opacity-90" data-i18n="image_screening_disclaimer">
            AI-assisted screening only. This is not a medical diagnosis. Final interpretation must be performed by a qualified healthcare professional.
        </p>
    </div>

    <div class="soft-card">
        <div class="space-y-3">
            <div>
                <label class="block text-xs font-bold text-gray-700 mb-1">Image Modality Category</label>
                <select id="img-modality-select" class="w-full border border-gray-300 rounded-lg p-2.5 text-xs font-medium">
                    <option value="CHEST_XRAY">Chest Radiography (Chest X-Ray / Pulmonary)</option>
                    <option value="DERMATOLOGY">Dermatology (Skin Rash / Cutaneous Lesion)</option>
                </select>
            </div>

            <div>
                <label class="block text-xs font-bold text-gray-700 mb-1" data-i18n="image_screening_upload">Select Image File</label>
                <div class="border-2 border-dashed border-gray-300 rounded-xl p-4 text-center hover:border-indigo-500 cursor-pointer bg-gray-50" onclick="document.getElementById('medical-file-input').click()">
                    <i class="fas fa-cloud-upload-alt text-3xl text-gray-400 mb-1"></i>
                    <p class="text-xs font-semibold text-gray-700" id="upload-file-label">Click to upload X-ray or Skin photo (PNG, JPG)</p>
                    <p class="text-[10px] text-gray-400 mt-0.5">Maximum file size: 10MB</p>
                </div>
                <input type="file" id="medical-file-input" accept="image/*" class="hidden" onchange="app.handleImageFileSelect(this)">
            </div>

            <div id="image-preview-box" class="hidden text-center mt-2">
                <img id="image-preview-img" class="max-h-48 mx-auto rounded-lg border border-gray-200 shadow-xs" src="" alt="Preview">
            </div>

            <button id="btn-run-img-screening" class="w-full bg-indigo-700 text-white font-bold py-3 rounded-xl mt-2 flex items-center justify-center hover:bg-indigo-800 shadow-sm transition" onclick="app.executeImageScreening()">
                <i class="fas fa-search mr-2"></i> Analyze Image with AI Model
            </button>
        </div>
    </div>

    <!-- Screening Output Card -->
    <div id="image-results-container" class="hidden mt-4">
        <div class="soft-card border-l-4 border-indigo-600">
            <div class="flex justify-between items-center mb-2">
                <span class="text-xs text-gray-500 font-bold uppercase" id="img-res-category">Chest Radiography</span>
                <span id="img-res-confidence" class="bg-indigo-100 text-indigo-800 text-xs font-extrabold px-2 py-0.5 rounded-full"></span>
            </div>
            <div class="mb-3">
                <p class="text-[11px] text-gray-400 uppercase font-semibold">Detected Algorithmic Finding</p>
                <h4 id="img-res-finding" class="font-bold text-sm text-gray-900 mt-0.5 leading-snug"></h4>
            </div>
            <div class="bg-gray-50 p-3 rounded-lg text-xs mb-3">
                <p class="font-semibold text-gray-800 mb-1">Action Recommendation:</p>
                <p id="img-res-recommendation" class="text-gray-600"></p>
            </div>
            <p class="text-[10px] text-gray-400 italic">
                <span class="font-bold">Model Limitations:</span> <span id="img-res-limitations"></span>
            </p>
            <div class="mt-4 pt-3 border-t border-gray-200 flex justify-between items-center">
                <span class="text-xs text-amber-700 font-semibold flex items-center">
                    <i class="fas fa-clock mr-1"></i> Status: Pending Doctor Sign-off
                </span>
                <button class="bg-teal-700 text-white text-xs px-3 py-1.5 rounded-lg font-bold" onclick="app.navigate('doctor-search')">
                    Consult Specialist
                </button>
            </div>
        </div>
    </div>
  `,

  // 5. DOCTOR SEARCH & DIRECTORY VIEW
  'doctor-search': `
    <div class="mb-4">
        <div class="flex items-center justify-between mb-2">
            <button class="text-teal-700 text-sm font-semibold flex items-center" onclick="app.navigate('patient-home')">
                <i class="fas fa-arrow-left mr-1.5"></i> Back
            </button>
            <h2 class="font-bold text-base text-gray-800">Verified Doctor Directory</h2>
            <div class="w-6"></div>
        </div>

        <!-- Specialty Filter Tabs -->
        <div class="flex space-x-2 overflow-x-auto pb-2 scrollbar-hide text-xs" id="specialty-filter-bar">
            <button class="bg-teal-700 text-white px-3 py-1.5 rounded-full font-semibold whitespace-nowrap" onclick="app.filterDoctorsBySpec('All', this)">All</button>
            <button class="bg-gray-200 text-gray-700 px-3 py-1.5 rounded-full font-semibold whitespace-nowrap hover:bg-gray-300" onclick="app.filterDoctorsBySpec('General Physician', this)">General Physician</button>
            <button class="bg-gray-200 text-gray-700 px-3 py-1.5 rounded-full font-semibold whitespace-nowrap hover:bg-gray-300" onclick="app.filterDoctorsBySpec('Pediatrician', this)">Pediatrician</button>
            <button class="bg-gray-200 text-gray-700 px-3 py-1.5 rounded-full font-semibold whitespace-nowrap hover:bg-gray-300" onclick="app.filterDoctorsBySpec('Dermatologist', this)">Dermatologist</button>
            <button class="bg-gray-200 text-gray-700 px-3 py-1.5 rounded-full font-semibold whitespace-nowrap hover:bg-gray-300" onclick="app.filterDoctorsBySpec('Gynecologist', this)">Gynecologist</button>
        </div>
    </div>

    <!-- Doctor Cards List -->
    <div id="doctor-cards-list" class="space-y-3">
        <!-- Loaded dynamically via JS -->
    </div>
  `,

  // 6. DOCTOR PROFILE & BOOKING MODAL VIEW
  'doctor-profile': `
    <div class="mb-4 flex items-center justify-between">
        <button class="text-teal-700 text-sm font-semibold flex items-center" onclick="app.navigate('doctor-search')">
            <i class="fas fa-arrow-left mr-1.5"></i> Back to Doctors
        </button>
        <span class="bg-emerald-100 text-emerald-800 text-[10px] font-bold px-2 py-0.5 rounded-full flex items-center">
            <i class="fas fa-check-circle mr-1"></i> VERIFIED GMC
        </span>
    </div>

    <div class="soft-card mb-4" id="doc-profile-header">
        <!-- Dynamically rendered -->
    </div>

    <!-- Booking Form Card -->
    <div class="soft-card mb-4 border-2 border-teal-500">
        <h3 class="font-bold text-sm text-teal-900 mb-2 flex items-center">
            <i class="far fa-calendar-alt text-teal-600 mr-2"></i> Book Online Consultation
        </h3>
        <div class="space-y-3">
            <div>
                <label class="block text-xs font-semibold text-gray-600 mb-1">Select Date</label>
                <input type="date" id="book-date" class="w-full border border-gray-300 rounded-lg p-2 text-xs">
            </div>
            <div>
                <label class="block text-xs font-semibold text-gray-600 mb-1">Available Time Slot</label>
                <select id="book-slot" class="w-full border border-gray-300 rounded-lg p-2 text-xs">
                    <option value="10:00 AM - 10:30 AM">10:00 AM - 10:30 AM</option>
                    <option value="11:00 AM - 11:30 AM">11:00 AM - 11:30 AM</option>
                    <option value="04:00 PM - 04:30 PM">04:00 PM - 04:30 PM</option>
                    <option value="05:00 PM - 05:30 PM">05:00 PM - 05:30 PM</option>
                    <option value="06:00 PM - 06:30 PM">06:00 PM - 06:30 PM</option>
                </select>
            </div>
            <div>
                <label class="block text-xs font-semibold text-gray-600 mb-1">Chief Complaint</label>
                <input type="text" id="book-complaint" class="w-full border border-gray-300 rounded-lg p-2 text-xs" placeholder="e.g. Fever, cough, and throat irritation">
            </div>
            <button class="w-full bg-teal-700 hover:bg-teal-800 text-white font-bold py-2.5 rounded-xl text-xs transition shadow-sm" onclick="app.submitAppointmentBooking()">
                Confirm Free Rural Consultation
            </button>
        </div>
    </div>

    <!-- Verified Patient Reviews Section -->
    <div class="soft-card">
        <h3 class="font-bold text-sm text-gray-800 mb-3 flex items-center justify-between">
            <span>Verified Consultation Reviews</span>
            <span class="text-xs text-gray-500 font-normal">Privacy Protected</span>
        </h3>
        <div id="doc-profile-reviews-list" class="space-y-3 text-xs">
            <!-- Dynamic reviews -->
        </div>
    </div>
  `,

  // 7. REAL-TIME TELECONSULTATION & WEBRTC ROOM
  'consultation-room': `
    <div class="fixed inset-0 bg-gray-950 text-white z-50 flex flex-col">
        <!-- Room Header -->
        <div class="p-3 bg-gray-900 border-b border-gray-800 flex justify-between items-center">
            <div class="flex items-center space-x-2">
                <span class="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-ping"></span>
                <div>
                    <h3 class="font-bold text-xs" id="call-partner-name">Teleconsultation</h3>
                    <p class="text-[10px] text-gray-400" id="call-connection-status">Connecting WebRTC P2P encrypted line...</p>
                </div>
            </div>
            <div class="flex items-center space-x-2">
                <button id="btn-audio-first-mode" class="text-[11px] bg-gray-800 hover:bg-gray-700 px-2 py-1 rounded border border-gray-700" onclick="app.toggleConsultationAudioFirst()">
                    <i class="fas fa-signal"></i> Audio-First
                </button>
                <button class="bg-red-600 hover:bg-red-700 text-white text-xs px-3 py-1 rounded-lg font-bold" onclick="app.leaveConsultation()">
                    Leave
                </button>
            </div>
        </div>

        <!-- Video Stage & Interactive Overlay -->
        <div class="flex-1 relative flex flex-col md:flex-row overflow-hidden">
            <!-- Video Area -->
            <div class="flex-1 bg-gray-900 flex items-center justify-center relative p-4" id="video-display-area">
                <div class="text-center" id="remote-video-placeholder">
                    <div class="w-24 h-24 bg-gray-800 rounded-full flex items-center justify-center text-4xl mx-auto mb-3 border border-gray-700">
                        <span id="call-partner-avatar">👨🏽‍⚕️</span>
                    </div>
                    <h4 class="font-bold text-sm text-gray-200" id="call-partner-subname">Dr. Anjali Patel</h4>
                    <p class="text-xs text-emerald-400 mt-1"><i class="fas fa-lock"></i> End-to-End Encrypted Session</p>
                    <p class="text-[11px] text-gray-500 mt-0.5">Low-latency rural telemedicine signaling active</p>
                </div>

                <!-- Self View (PIP) -->
                <div id="self-view-container" class="absolute bottom-4 right-4 w-28 h-36 bg-gray-800 rounded-xl border border-gray-700 shadow-xl overflow-hidden flex flex-col items-center justify-center">
                    <i class="fas fa-user text-2xl text-gray-600 mb-1"></i>
                    <span class="text-[9px] text-gray-400">You (Self)</span>
                </div>
            </div>

            <!-- Side Panel: Real-time Chat & Doctor Clinical Notes -->
            <div class="w-full md:w-80 bg-gray-900 border-t md:border-t-0 md:border-l border-gray-800 flex flex-col h-64 md:h-full">
                <!-- Tab Controls -->
                <div class="flex border-b border-gray-800 text-xs">
                    <button id="call-tab-chat" class="flex-1 py-2 font-bold text-teal-400 border-b-2 border-teal-500" onclick="app.switchCallTab('chat')">Live Chat</button>
                    <button id="call-tab-notes" class="flex-1 py-2 font-medium text-gray-400" onclick="app.switchCallTab('notes')">Clinical Notes</button>
                </div>

                <!-- Chat Messages Pane -->
                <div id="call-pane-chat" class="flex-1 p-3 overflow-y-auto space-y-2 text-xs flex flex-col">
                    <div id="chat-messages-container" class="flex-1 space-y-2">
                        <!-- Dynamic Messages -->
                    </div>
                    <div class="flex space-x-2 pt-2 border-t border-gray-800">
                        <input type="text" id="consult-chat-input" class="flex-1 bg-gray-800 border border-gray-700 rounded-lg p-2 text-xs text-white" placeholder="Type message...">
                        <button class="bg-teal-600 text-white px-3 py-1.5 rounded-lg text-xs font-bold" onclick="app.sendConsultChatMessage()">
                            <i class="fas fa-paper-plane"></i>
                        </button>
                    </div>
                </div>

                <!-- Doctor Notes & Prescription Pane -->
                <div id="call-pane-notes" class="flex-1 p-3 overflow-y-auto space-y-3 text-xs hidden">
                    <div class="bg-gray-800 p-2.5 rounded-lg">
                        <p class="text-[10px] text-teal-400 font-bold uppercase">AI Symptom Summary</p>
                        <p class="text-gray-300 mt-1" id="call-ai-summary">Fever and dry cough persisting 4 days. Moderate urgency.</p>
                    </div>
                    <div>
                        <label class="block text-[10px] text-gray-400 uppercase font-bold mb-1">Doctor Clinical Diagnosis</label>
                        <input type="text" id="call-doc-diagnosis" class="w-full bg-gray-800 border border-gray-700 rounded p-1.5 text-xs text-white" placeholder="e.g. Acute Viral Bronchitis">
                    </div>
                    <div>
                        <label class="block text-[10px] text-gray-400 uppercase font-bold mb-1">Clinical Notes & Advice</label>
                        <textarea id="call-doc-notes" rows="3" class="w-full bg-gray-800 border border-gray-700 rounded p-1.5 text-xs text-white" placeholder="Examination notes, dosage advice, hydration..."></textarea>
                    </div>
                    <button class="w-full bg-emerald-600 hover:bg-emerald-700 text-white font-bold py-2 rounded-lg text-xs" onclick="app.doctorFinishConsultation()">
                        Complete & Issue Prescription
                    </button>
                </div>
            </div>
        </div>

        <!-- Controls Bar -->
        <div class="p-3 bg-gray-900 border-t border-gray-800 flex justify-center space-x-4">
            <button id="btn-toggle-mic" class="w-11 h-11 rounded-full bg-gray-800 border border-gray-700 flex items-center justify-center hover:bg-gray-700" onclick="app.toggleCallMic()">
                <i class="fas fa-microphone"></i>
            </button>
            <button id="btn-toggle-cam" class="w-11 h-11 rounded-full bg-gray-800 border border-gray-700 flex items-center justify-center hover:bg-gray-700" onclick="app.toggleCallCam()">
                <i class="fas fa-video"></i>
            </button>
            <button class="w-11 h-11 rounded-full bg-red-600 text-white flex items-center justify-center hover:bg-red-700 shadow-md" onclick="app.leaveConsultation()">
                <i class="fas fa-phone-slash"></i>
            </button>
        </div>
    </div>
  `,

  // 8. DOCTOR RATING & TRUST SYSTEM VIEW
  'rate-consultation': `
    <div class="mb-4 mt-6 text-center">
        <h2 class="text-xl font-bold text-gray-800" data-i18n="rating_title">Rate Your Consultation</h2>
        <p class="text-gray-500 text-xs mt-1" data-i18n="rating_subtitle">
            Ratings are linked to completed consultations to create a more trustworthy doctor-discovery system for rural users.
        </p>
    </div>

    <div class="soft-card text-center p-6">
        <div class="w-16 h-16 bg-teal-100 rounded-full flex items-center justify-center mx-auto mb-2 text-3xl">
            👩🏽‍⚕️
        </div>
        <h3 class="font-bold text-sm text-gray-800" id="rate-doctor-name">Dr. Anjali Patel</h3>
        <p class="text-[11px] text-gray-500 mb-4" id="rate-doctor-spec">General Physician</p>

        <!-- Overall Star Rating -->
        <p class="text-xs font-bold text-gray-700 mb-2">Overall Experience Rating</p>
        <div class="flex justify-center space-x-2 text-3xl text-gray-300 mb-6" id="star-rating-selector">
            <i class="fas fa-star cursor-pointer hover:text-yellow-400 transition" onclick="app.setStarRating(1)"></i>
            <i class="fas fa-star cursor-pointer hover:text-yellow-400 transition" onclick="app.setStarRating(2)"></i>
            <i class="fas fa-star cursor-pointer hover:text-yellow-400 transition" onclick="app.setStarRating(3)"></i>
            <i class="fas fa-star cursor-pointer hover:text-yellow-400 transition" onclick="app.setStarRating(4)"></i>
            <i class="fas fa-star cursor-pointer hover:text-yellow-400 transition" onclick="app.setStarRating(5)"></i>
        </div>

        <!-- Multi-Category Ratings -->
        <div class="space-y-3 text-left mb-5 border-t border-b border-gray-100 py-3">
            <div class="flex justify-between items-center text-xs">
                <span class="text-gray-600" data-i18n="rating_communication">Communication in Vernacular</span>
                <select id="score-comm" class="border border-gray-300 rounded p-1 text-xs">
                    <option value="5">★★★★★ 5</option>
                    <option value="4">★★★★☆ 4</option>
                    <option value="3">★★★☆☆ 3</option>
                </select>
            </div>
            <div class="flex justify-between items-center text-xs">
                <span class="text-gray-600" data-i18n="rating_punctuality">Punctuality & Waiting Time</span>
                <select id="score-punct" class="border border-gray-300 rounded p-1 text-xs">
                    <option value="5">★★★★★ 5</option>
                    <option value="4">★★★★☆ 4</option>
                    <option value="3">★★★☆☆ 3</option>
                </select>
            </div>
            <div class="flex justify-between items-center text-xs">
                <span class="text-gray-600" data-i18n="rating_explanation">Explanation of Medicines</span>
                <select id="score-exp" class="border border-gray-300 rounded p-1 text-xs">
                    <option value="5">★★★★★ 5</option>
                    <option value="4">★★★★☆ 4</option>
                    <option value="3">★★★☆☆ 3</option>
                </select>
            </div>
        </div>

        <textarea id="rate-review-text" rows="3" class="w-full border border-gray-300 rounded-xl p-3 text-xs mb-4 focus:ring-2 focus:ring-teal-500" placeholder="Share your experience (Patient identity remains confidential)..."></textarea>

        <button class="w-full bg-teal-700 hover:bg-teal-800 text-white font-bold py-3 rounded-xl text-xs transition shadow-sm" onclick="app.submitDoctorRating()">
            Submit Verified Rating
        </button>
        <button class="w-full text-gray-400 text-xs mt-3 hover:text-gray-600" onclick="app.navigate('patient-home')">
            Skip for now
        </button>
    </div>
  `,

  // 9. COMMUNITY HEALTH CAMP NETWORK
  'health-camps': `
    <div class="mb-4">
        <div class="flex items-center justify-between mb-2">
            <button class="text-teal-700 text-sm font-semibold flex items-center" onclick="app.navigate('patient-home')">
                <i class="fas fa-arrow-left mr-1.5"></i> Back
            </button>
            <h2 class="font-bold text-base text-gray-800" data-i18n="action_health_camps">Community Health Camps</h2>
            <div class="w-6"></div>
        </div>
        <p class="text-xs text-gray-500">Free medical checkups and screenings organized directly in rural villages.</p>
    </div>

    <!-- Toggle Camps vs Request Camp -->
    <div class="flex space-x-2 mb-4">
        <button id="tab-camps-list" class="flex-1 bg-teal-700 text-white py-2 rounded-xl text-xs font-bold shadow-xs" onclick="app.switchCampTab('list')">Available Camps</button>
        <button id="tab-camps-request" class="flex-1 bg-white border border-teal-600 text-teal-700 py-2 rounded-xl text-xs font-bold" onclick="app.switchCampTab('request')">Request a Camp</button>
    </div>

    <!-- Pane 1: Camps List -->
    <div id="pane-camps-list" class="space-y-4">
        <!-- Dynamic Camps -->
    </div>

    <!-- Pane 2: Request a Camp Form -->
    <div id="pane-camps-request" class="hidden soft-card">
        <h3 class="font-bold text-sm text-teal-900 mb-1" data-i18n="btn_request_camp">Request a Health Camp</h3>
        <p class="text-xs text-gray-500 mb-3">Villages, Panchayats, or Community NGOs can request healthcare providers to organize a camp.</p>

        <form onsubmit="app.handleCampRequestSubmit(event)" class="space-y-3">
            <div class="grid grid-cols-2 gap-2">
                <div>
                    <label class="block text-xs font-semibold text-gray-600 mb-1">Village Name</label>
                    <input type="text" id="creq-village" required class="w-full border border-gray-300 rounded-lg p-2 text-xs" placeholder="e.g. Rampura">
                </div>
                <div>
                    <label class="block text-xs font-semibold text-gray-600 mb-1">District</label>
                    <input type="text" id="creq-district" required class="w-full border border-gray-300 rounded-lg p-2 text-xs" placeholder="e.g. Mehsana">
                </div>
            </div>

            <div class="grid grid-cols-2 gap-2">
                <div>
                    <label class="block text-xs font-semibold text-gray-600 mb-1">Contact Person</label>
                    <input type="text" id="creq-person" required class="w-full border border-gray-300 rounded-lg p-2 text-xs" placeholder="Sarpanch / Leader">
                </div>
                <div>
                    <label class="block text-xs font-semibold text-gray-600 mb-1">Contact Phone</label>
                    <input type="tel" id="creq-phone" required class="w-full border border-gray-300 rounded-lg p-2 text-xs" placeholder="+91 98765 00000">
                </div>
            </div>

            <div class="grid grid-cols-2 gap-2">
                <div>
                    <label class="block text-xs font-semibold text-gray-600 mb-1">Camp Type Needed</label>
                    <select id="creq-type" class="w-full border border-gray-300 rounded-lg p-2 text-xs">
                        <option>General Health Checkup</option>
                        <option>Eye Care Camp</option>
                        <option>Women's Health Camp</option>
                        <option>Pediatric & Child Wellness</option>
                        <option>Diabetes & BP Screening</option>
                    </select>
                </div>
                <div>
                    <label class="block text-xs font-semibold text-gray-600 mb-1">Expected Population</label>
                    <input type="number" id="creq-count" value="150" class="w-full border border-gray-300 rounded-lg p-2 text-xs">
                </div>
            </div>

            <div>
                <label class="block text-xs font-semibold text-gray-600 mb-1">Preferred Date</label>
                <input type="date" id="creq-date" required class="w-full border border-gray-300 rounded-lg p-2 text-xs">
            </div>

            <div>
                <label class="block text-xs font-semibold text-gray-600 mb-1">Description & Local Needs</label>
                <textarea id="creq-desc" rows="2" class="w-full border border-gray-300 rounded-lg p-2 text-xs" placeholder="Detail what your village community needs most..."></textarea>
            </div>

            <button type="submit" class="w-full bg-emerald-700 hover:bg-emerald-800 text-white font-bold py-2.5 rounded-xl text-xs transition">
                Submit Health Camp Request
            </button>
        </form>
    </div>
  `,

  // 10. HEALTH RECORDS & ABDM VIEW
  'health-records': `
    <div class="mb-4 flex items-center justify-between">
        <button class="text-teal-700 text-sm font-semibold flex items-center" onclick="app.navigate('patient-home')">
            <i class="fas fa-arrow-left mr-1.5"></i> Back
        </button>
        <h2 class="font-bold text-base text-gray-800">Digital Health Records</h2>
        <span class="bg-blue-100 text-blue-800 text-[10px] font-bold px-2 py-0.5 rounded-full">ABDM Sandbox</span>
    </div>

    <!-- ABHA Card -->
    <div class="soft-card bg-gradient-to-br from-teal-800 to-teal-950 text-white p-4 rounded-2xl mb-4">
        <div class="flex justify-between items-center mb-1">
            <span class="text-[10px] text-teal-300 font-bold uppercase tracking-wider">Ayushman Bharat Digital Health Profile</span>
            <span class="bg-emerald-500 text-teal-950 text-[10px] font-bold px-2 py-0.5 rounded">SANDBOX ACTIVE</span>
        </div>
        <h3 class="font-bold text-lg" id="hr-abha-name">Ramesh Patel</h3>
        <p class="font-mono text-xs opacity-90 tracking-wider mb-3" id="hr-abha-number">14-2394-3948-2938</p>
        <div class="flex space-x-2">
            <button class="bg-white/20 text-white text-xs px-3 py-1.5 rounded-lg font-semibold hover:bg-white/30" onclick="app.simulateAbhaOtp()">
                <i class="fas fa-sync-alt mr-1"></i> Refresh ABHA
            </button>
            <button class="bg-emerald-500 text-teal-950 text-xs px-3 py-1.5 rounded-lg font-bold hover:bg-emerald-400" onclick="app.viewAbdmConsents()">
                <i class="fas fa-shield-alt mr-1"></i> Consent Manager
            </button>
        </div>
    </div>

    <!-- Active Consents Section -->
    <div id="active-consents-box" class="soft-card mb-4 border border-blue-200 bg-blue-50/50">
        <h4 class="font-bold text-xs text-blue-900 mb-2 flex items-center justify-between">
            <span><i class="fas fa-key text-blue-600 mr-1.5"></i> ABDM Consent Requests (HIE-CM)</span>
            <span id="consent-count-badge" class="bg-blue-200 text-blue-800 text-[10px] px-2 py-0.5 rounded-full">0</span>
        </h4>
        <div id="consents-list-container" class="space-y-2 text-xs">
            <!-- Dynamic Consents -->
        </div>
    </div>

    <!-- Records List -->
    <div class="flex justify-between items-center mb-2">
        <h3 class="font-bold text-sm text-gray-800">Stored Medical Records</h3>
        <button class="text-xs bg-teal-700 text-white px-2.5 py-1 rounded-lg font-semibold" onclick="alert('Upload medical report simulation')">
            <i class="fas fa-plus mr-1"></i> Upload
        </button>
    </div>
    <div id="records-list-container" class="space-y-3 text-xs">
        <!-- Dynamic Records -->
    </div>
  `,

  // 11. DOCTOR DASHBOARD VIEW
  'doctor-home': `
    <div class="mb-4 flex items-center justify-between">
        <div>
            <h2 class="font-bold text-base text-gray-800">Doctor Clinical Dashboard</h2>
            <p class="text-xs text-teal-700 font-semibold" id="doc-greeting">Doctor Dashboard</p>
        </div>
        <div class="flex items-center space-x-2">
            <button class="bg-teal-50 text-teal-700 border border-teal-200 text-xs px-2.5 py-1 rounded-lg font-semibold hover:bg-teal-100" onclick="app.openDoctorProfileEdit()">
                <i class="fas fa-user-edit mr-1"></i> Edit Profile
            </button>
            <span id="doc-verification-badge" class="bg-emerald-100 text-emerald-800 text-[10px] font-bold px-2.5 py-1 rounded-full flex items-center">
                <i class="fas fa-check-circle mr-1"></i> VERIFIED
            </span>
        </div>
    </div>

    <!-- Metric Cards -->
    <div class="grid grid-cols-2 gap-3 mb-4">
        <div class="soft-card !p-3.5 bg-teal-50 border border-teal-200">
            <p class="text-[10px] text-teal-700 font-bold uppercase tracking-wider">Today's Consultations</p>
            <h3 class="text-2xl font-black text-teal-900 mt-1" id="doc-metric-today">--</h3>
            <p class="text-[10px] text-teal-600 mt-0.5" id="doc-metric-queue-text">Patient Queue Live</p>
        </div>
        <div class="soft-card !p-3.5 bg-blue-50 border border-blue-200">
            <p class="text-[10px] text-blue-700 font-bold uppercase tracking-wider">Doctor Trust Score</p>
            <h3 class="text-2xl font-black text-blue-900 mt-1 flex items-center" id="doc-metric-rating">
                <i class="fas fa-star text-yellow-400 mr-1 text-lg"></i> 5.0
            </h3>
            <p class="text-[10px] text-blue-600 mt-0.5" id="doc-metric-reviews-count">Verified Reviews</p>
        </div>
    </div>

    <!-- Patient Queue -->
    <div class="mb-4">
        <div class="flex justify-between items-center mb-2">
            <h3 class="font-bold text-sm text-gray-800">Waiting Patient Queue</h3>
            <span class="bg-blue-100 text-blue-700 text-xs font-bold px-2 py-0.5 rounded-full" id="doc-queue-badge">0 Total</span>
        </div>
        <div id="doctor-queue-list" class="space-y-3">
            <!-- Dynamic Queue Cards -->
        </div>
    </div>

    <!-- Community Camp Requests Waiting For Doctor -->
    <div class="soft-card">
        <div class="flex justify-between items-center mb-2">
            <h3 class="font-bold text-sm text-gray-800">Nearby Village Camp Requests</h3>
            <button class="text-xs text-teal-600 font-semibold" onclick="app.navigate('health-camps')">View All</button>
        </div>
        <div id="doc-camp-requests-list" class="space-y-2 text-xs">
            <!-- Dynamic Requests -->
        </div>
    </div>
  `,

  // 11b. DOCTOR PROFILE EDIT VIEW
  'doctor-profile-edit': `
    <div class="mb-4 flex items-center justify-between">
        <button class="text-teal-700 text-sm font-semibold flex items-center" onclick="app.navigate('doctor-home')">
            <i class="fas fa-arrow-left mr-1.5"></i> Back to Dashboard
        </button>
        <h2 class="font-bold text-base text-gray-800">Edit Professional Profile</h2>
        <span class="bg-blue-100 text-blue-800 text-[10px] font-bold px-2 py-0.5 rounded-full">Doctor</span>
    </div>

    <div class="soft-card">
        <form onsubmit="app.saveDoctorProfile(event)" class="space-y-3">
            <div>
                <label class="block text-xs font-semibold text-gray-700 mb-1">Full Name</label>
                <input type="text" id="edit-doc-name" required class="w-full border border-gray-300 rounded-lg p-2.5 text-xs">
            </div>
            <div class="grid grid-cols-2 gap-2">
                <div>
                    <label class="block text-xs font-semibold text-gray-700 mb-1">Qualification</label>
                    <input type="text" id="edit-doc-qual" placeholder="MBBS, MD" required class="w-full border border-gray-300 rounded-lg p-2.5 text-xs">
                </div>
                <div>
                    <label class="block text-xs font-semibold text-gray-700 mb-1">Specialization</label>
                    <input type="text" id="edit-doc-spec" placeholder="General Physician" required class="w-full border border-gray-300 rounded-lg p-2.5 text-xs">
                </div>
            </div>
            <div class="grid grid-cols-2 gap-2">
                <div>
                    <label class="block text-xs font-semibold text-gray-700 mb-1">Experience (Years)</label>
                    <input type="number" id="edit-doc-exp" min="0" max="60" class="w-full border border-gray-300 rounded-lg p-2.5 text-xs">
                </div>
                <div>
                    <label class="block text-xs font-semibold text-gray-700 mb-1">Consultation Fee (₹)</label>
                    <input type="number" id="edit-doc-fee" min="0" class="w-full border border-gray-300 rounded-lg p-2.5 text-xs">
                </div>
            </div>
            <div>
                <label class="block text-xs font-semibold text-gray-700 mb-1">Languages Spoken (comma-separated)</label>
                <input type="text" id="edit-doc-languages" placeholder="English, Hindi, Gujarati" class="w-full border border-gray-300 rounded-lg p-2.5 text-xs">
            </div>
            <div>
                <label class="block text-xs font-semibold text-gray-700 mb-1">Hospital / Clinic Affiliation</label>
                <input type="text" id="edit-doc-hospital" placeholder="Primary Health Center / Hospital" class="w-full border border-gray-300 rounded-lg p-2.5 text-xs">
            </div>
            <div>
                <label class="block text-xs font-semibold text-gray-700 mb-1">Professional Bio</label>
                <textarea id="edit-doc-bio" rows="3" class="w-full border border-gray-300 rounded-lg p-2.5 text-xs" placeholder="Dedicated healthcare professional providing tele-care to rural communities..."></textarea>
            </div>
            <button type="submit" id="btn-save-doc-profile" class="w-full bg-teal-700 hover:bg-teal-800 text-white font-bold py-2.5 rounded-xl text-xs shadow-sm transition">
                <i class="fas fa-save mr-1.5"></i> Save Profile Changes
            </button>
        </form>
    </div>
  `,

  // 11c. PATIENT PROFILE EDIT VIEW
  'patient-profile-edit': `
    <div class="mb-4 flex items-center justify-between">
        <button class="text-teal-700 text-sm font-semibold flex items-center" onclick="app.navigate('patient-home')">
            <i class="fas fa-arrow-left mr-1.5"></i> Back to Dashboard
        </button>
        <h2 class="font-bold text-base text-gray-800">Edit Health Profile</h2>
        <span class="bg-teal-100 text-teal-800 text-[10px] font-bold px-2 py-0.5 rounded-full">Patient</span>
    </div>

    <div class="soft-card">
        <form onsubmit="app.savePatientProfile(event)" class="space-y-3">
            <div>
                <label class="block text-xs font-semibold text-gray-700 mb-1">Full Name</label>
                <input type="text" id="edit-pat-name" required class="w-full border border-gray-300 rounded-lg p-2.5 text-xs">
            </div>
            <div class="grid grid-cols-2 gap-2">
                <div>
                    <label class="block text-xs font-semibold text-gray-700 mb-1">Age</label>
                    <input type="number" id="edit-pat-age" min="1" max="120" class="w-full border border-gray-300 rounded-lg p-2.5 text-xs">
                </div>
                <div>
                    <label class="block text-xs font-semibold text-gray-700 mb-1">Gender</label>
                    <select id="edit-pat-gender" class="w-full border border-gray-300 rounded-lg p-2.5 text-xs">
                        <option value="Male">Male</option>
                        <option value="Female">Female</option>
                        <option value="Other">Other</option>
                    </select>
                </div>
            </div>
            <div class="grid grid-cols-2 gap-2">
                <div>
                    <label class="block text-xs font-semibold text-gray-700 mb-1">Village</label>
                    <input type="text" id="edit-pat-village" class="w-full border border-gray-300 rounded-lg p-2.5 text-xs">
                </div>
                <div>
                    <label class="block text-xs font-semibold text-gray-700 mb-1">District</label>
                    <input type="text" id="edit-pat-district" class="w-full border border-gray-300 rounded-lg p-2.5 text-xs">
                </div>
            </div>
            <div class="grid grid-cols-2 gap-2">
                <div>
                    <label class="block text-xs font-semibold text-gray-700 mb-1">Blood Group</label>
                    <input type="text" id="edit-pat-blood" placeholder="e.g. B+, O+" class="w-full border border-gray-300 rounded-lg p-2.5 text-xs">
                </div>
                <div>
                    <label class="block text-xs font-semibold text-gray-700 mb-1">Emergency Contact</label>
                    <input type="tel" id="edit-pat-emergency" placeholder="+91..." class="w-full border border-gray-300 rounded-lg p-2.5 text-xs">
                </div>
            </div>
            <div>
                <label class="block text-xs font-semibold text-gray-700 mb-1">Known Allergies</label>
                <input type="text" id="edit-pat-allergies" placeholder="e.g. None, Penicillin, Peanuts" class="w-full border border-gray-300 rounded-lg p-2.5 text-xs">
            </div>
            <div>
                <label class="block text-xs font-semibold text-gray-700 mb-1">Chronic Health Conditions</label>
                <input type="text" id="edit-pat-chronic" placeholder="e.g. Diabetes, Hypertension, Asthma" class="w-full border border-gray-300 rounded-lg p-2.5 text-xs">
            </div>
            <button type="submit" id="btn-save-pat-profile" class="w-full bg-teal-700 hover:bg-teal-800 text-white font-bold py-2.5 rounded-xl text-xs shadow-sm transition">
                <i class="fas fa-save mr-1.5"></i> Save Health Profile
            </button>
        </form>
    </div>
  `,

  // 12. HOSPITAL / ORGANIZATION DASHBOARD
  'hospital-home': `
    <div class="mb-4">
        <div class="flex items-center justify-between">
            <h2 class="font-bold text-base text-gray-800">Hospital / NGO Dashboard</h2>
            <span class="bg-blue-100 text-blue-800 text-[10px] font-bold px-2 py-0.5 rounded-full">NABH Registered</span>
        </div>
        <p class="text-xs text-teal-700 font-semibold" id="org-name-header">Shakti Community Hospital (Mehsana)</p>
    </div>

    <div class="grid grid-cols-2 gap-3 mb-4">
        <div class="soft-card !p-3 bg-emerald-50 border border-emerald-200">
            <p class="text-[10px] text-emerald-700 font-bold uppercase">Organized Camps</p>
            <h3 class="text-xl font-bold text-emerald-900 mt-0.5">3 Camps</h3>
        </div>
        <div class="soft-card !p-3 bg-purple-50 border border-purple-200">
            <p class="text-[10px] text-purple-700 font-bold uppercase">Villagers Screened</p>
            <h3 class="text-xl font-bold text-purple-900 mt-0.5">380+</h3>
        </div>
    </div>

    <!-- Camp Requests from Villages -->
    <div class="soft-card mb-4">
        <h3 class="font-bold text-sm text-gray-800 mb-2">Incoming Village Camp Requests</h3>
        <div id="hospital-camp-requests-container" class="space-y-3 text-xs">
            <!-- Dynamic requests with Accept button -->
        </div>
    </div>

    <!-- Publish Camp Button -->
    <button class="w-full bg-teal-700 hover:bg-teal-800 text-white font-bold py-3 rounded-xl text-xs shadow-sm transition" onclick="app.showPublishCampModal()">
        <i class="fas fa-plus-circle mr-1.5"></i> Publish New Proactive Health Camp
    </button>
  `,

  // 13. ADMIN DASHBOARD & ANALYTICS
  'admin-home': `
    <div class="mb-4 flex items-center justify-between">
        <div>
            <h2 class="font-bold text-base text-gray-800">System Admin & Analytics</h2>
            <p class="text-xs text-gray-500">GramCare AI Governance & Audit</p>
        </div>
        <button class="bg-red-50 text-red-700 border border-red-200 text-xs px-2.5 py-1 rounded-lg font-semibold hover:bg-red-100" onclick="app.adminResetDemo()">
            <i class="fas fa-undo mr-1"></i> Reset Demo Data
        </button>
    </div>

    <!-- Core Metrics Grid -->
    <div class="grid grid-cols-2 gap-3 mb-4 text-xs" id="admin-metrics-grid">
        <!-- Loaded via JS -->
    </div>

    <!-- Moderation Controls -->
    <div class="soft-card mb-4">
        <h3 class="font-bold text-xs text-gray-800 mb-2">Governance & Verification Tasks</h3>
        <div class="space-y-2 text-xs">
            <div class="flex justify-between items-center p-2 bg-gray-50 rounded-lg">
                <span>Doctor Verifications (Pending)</span>
                <span class="bg-amber-100 text-amber-800 px-2 py-0.5 rounded font-bold">0 Pending</span>
            </div>
            <div class="flex justify-between items-center p-2 bg-gray-50 rounded-lg">
                <span>Review Moderation Queue</span>
                <span class="bg-green-100 text-green-800 px-2 py-0.5 rounded font-bold">Clean</span>
            </div>
        </div>
    </div>

    <!-- Security Audit Logs -->
    <div class="soft-card">
        <h3 class="font-bold text-xs text-gray-800 mb-2 flex items-center justify-between">
            <span><i class="fas fa-shield-alt text-teal-600 mr-1"></i> Security & ABDM Access Audit Log</span>
            <span class="text-[10px] text-gray-400">Immutable Log</span>
        </h3>
        <div id="admin-audit-logs-container" class="space-y-2 text-[11px] max-h-48 overflow-y-auto">
            <!-- Dynamic audit rows -->
        </div>
    </div>
  `
};
