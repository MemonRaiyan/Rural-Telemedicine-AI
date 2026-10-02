/**
 * GramCare AI — Unified Single-Page Application Client
 * Full-stack Academic MVP supporting Patients, Doctors, Hospitals, and Admins.
 */

class GramCareApp {
    constructor() {
        this.token = localStorage.getItem('gc_token') || null;
        this.currentUser = JSON.parse(localStorage.getItem('gc_user') || 'null');
        this.currentRole = this.currentUser ? this.currentUser.role : null;
        this.currentLang = localStorage.getItem('gc_lang') || 'en';
        this.translations = {};
        
        this.isRuralMode = false;
        this.activeDoctor = null;
        this.activeConsultation = null;
        this.selectedRating = 5;
        this.consultationWs = null;
        this.selectedImageFile = null;
        this.currentSpecialtyFilter = 'All';

        this.init();
    }

    async init() {
        // 1. Mount dynamic template sections
        const container = document.getElementById('dynamic-views');
        container.innerHTML = '';
        for (const [id, html] of Object.entries(TEMPLATES)) {
            const section = document.createElement('section');
            section.id = `view-${id}`;
            section.className = 'view-section';
            section.innerHTML = html;
            container.appendChild(section);
        }

        // 2. Load locale pack
        await this.loadLocale(this.currentLang);
        document.getElementById('lang-selector').value = this.currentLang;

        // 3. Restore session or show demo login
        if (this.token && this.currentUser) {
            this.setSession(this.token, this.currentUser);
            this.routeUserToDashboard();
        } else {
            this.navigate('login');
        }
    }

    // ----------------- I18N & LOCALIZATION -----------------
    async loadLocale(lang) {
        try {
            const res = await fetch(`/static/locales/${lang}.json`);
            if (res.ok) {
                this.translations[lang] = await res.json();
                this.applyTranslations();
            }
        } catch (e) {
            console.warn("Error loading locale file:", e);
        }
    }

    async changeLanguage(lang) {
        this.currentLang = lang;
        localStorage.setItem('gc_lang', lang);
        if (!this.translations[lang]) {
            await this.loadLocale(lang);
        }
        this.applyTranslations();
    }

    applyTranslations() {
        const dict = this.translations[this.currentLang] || {};
        document.querySelectorAll('[data-i18n]').forEach(el => {
            const key = el.getAttribute('data-i18n');
            if (dict[key]) {
                el.innerText = dict[key];
            }
        });
    }

    t(key, fallback = "") {
        return (this.translations[this.currentLang] && this.translations[this.currentLang][key]) || fallback || key;
    }

    // ----------------- NAVIGATION & UI -----------------
    navigate(viewId) {
        document.querySelectorAll('.view-section').forEach(el => el.classList.remove('active'));
        const target = document.getElementById(`view-${viewId}`);
        if (target) {
            target.classList.add('active');
            window.scrollTo({ top: 0, behavior: 'smooth' });
        }

        // Handle navigation bar state
        this.updateNavBars(viewId);
        this.onViewLoad(viewId);
    }

    updateNavBars(viewId) {
        const patientNav = document.getElementById('bottom-nav-patient');
        const doctorNav = document.getElementById('bottom-nav-doctor');
        
        if (viewId === 'login' || viewId === 'consultation-room' || viewId === 'rate-consultation') {
            patientNav.classList.add('hidden');
            doctorNav.classList.add('hidden');
            return;
        }

        if (this.currentRole === 'PATIENT') {
            patientNav.classList.remove('hidden');
            doctorNav.classList.add('hidden');
        } else if (this.currentRole === 'DOCTOR') {
            patientNav.classList.add('hidden');
            doctorNav.classList.remove('hidden');
        } else {
            patientNav.classList.add('hidden');
            doctorNav.classList.add('hidden');
        }
    }

    onViewLoad(viewId) {
        if (viewId === 'patient-home') {
            this.loadPatientDashboard();
        } else if (viewId === 'doctor-search') {
            this.loadDoctors(this.currentSpecialtyFilter);
        } else if (viewId === 'health-camps') {
            this.loadCamps();
        } else if (viewId === 'health-records') {
            this.loadHealthRecords();
        } else if (viewId === 'doctor-home') {
            this.loadDoctorDashboard();
        } else if (viewId === 'hospital-home') {
            this.loadHospitalDashboard();
        } else if (viewId === 'admin-home') {
            this.loadAdminDashboard();
        }
    }

    toggleRuralMode() {
        this.isRuralMode = !this.isRuralMode;
        const btnText = document.getElementById('rural-mode-text');
        const indicator = document.getElementById('network-indicator');
        
        if (this.isRuralMode) {
            document.body.classList.add('rural-mode-enabled');
            indicator.classList.remove('hidden');
            btnText.innerText = this.t('rural_mode_active', "Rural: 2G ON");
        } else {
            document.body.classList.remove('rural-mode-enabled');
            indicator.classList.add('hidden');
            btnText.innerText = this.t('rural_mode', "Rural Mode");
        }
    }

    // ----------------- AUTHENTICATION & DEMO LOGIN -----------------
    async loginDemo(roleKey) {
        try {
            const res = await fetch(`/api/auth/demo-login/${roleKey}`, { method: 'POST' });
            const data = await res.json();
            if (data.success) {
                this.setSession(data.access_token, data.user);
                this.routeUserToDashboard();
            } else {
                alert(data.detail || "Demo login failed");
            }
        } catch (e) {
            alert("Error connecting to server. Please ensure backend is running.");
        }
    }

    async handleManualLogin(e) {
        e.preventDefault();
        const email = document.getElementById('auth-email').value;
        const password = document.getElementById('auth-password').value;
        try {
            const res = await fetch('/api/auth/login', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ email, password })
            });
            const data = await res.json();
            if (data.success) {
                this.setSession(data.access_token, data.user);
                this.routeUserToDashboard();
            } else {
                alert(data.detail || "Invalid credentials");
            }
        } catch(err) {
            alert("Login failed. Check server status.");
        }
    }

    async handleManualRegister(e) {
        e.preventDefault();
        const body = {
            full_name: document.getElementById('reg-name').value,
            role: document.getElementById('reg-role').value,
            email: document.getElementById('reg-email').value,
            password: document.getElementById('reg-password').value,
            village: document.getElementById('reg-village').value,
            district: document.getElementById('reg-district').value
        };
        try {
            const res = await fetch('/api/auth/register', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(body)
            });
            const data = await res.json();
            if (data.success) {
                this.setSession(data.access_token, data.user);
                this.routeUserToDashboard();
            } else {
                alert(data.detail || "Registration failed");
            }
        } catch (err) {
            alert("Registration error. Ensure email is unique.");
        }
    }

    switchAuthTab(tab) {
        const tabLogin = document.getElementById('tab-login');
        const tabReg = document.getElementById('tab-register');
        const formLogin = document.getElementById('form-auth-login');
        const formReg = document.getElementById('form-auth-register');

        if (tab === 'login') {
            tabLogin.className = "flex-1 pb-2 font-bold text-sm text-teal-700 border-b-2 border-teal-600";
            tabReg.className = "flex-1 pb-2 font-medium text-sm text-gray-400";
            formLogin.classList.remove('hidden');
            formReg.classList.add('hidden');
        } else {
            tabReg.className = "flex-1 pb-2 font-bold text-sm text-teal-700 border-b-2 border-teal-600";
            tabLogin.className = "flex-1 pb-2 font-medium text-sm text-gray-400";
            formReg.classList.remove('hidden');
            formLogin.classList.add('hidden');
        }
    }

    setSession(token, user) {
        this.token = token;
        this.currentUser = user;
        this.currentRole = user.role;
        localStorage.setItem('gc_token', token);
        localStorage.setItem('gc_user', JSON.stringify(user));

        const greeting = document.getElementById('user-greeting');
        greeting.classList.remove('hidden');
        greeting.innerHTML = `
            <div class="flex justify-between items-center">
                <div>
                    <span>Namaste, <b>${user.full_name}</b></span>
                    <span class="text-[10px] opacity-80 block">${user.role} • Rampura Village, Mehsana</span>
                </div>
                <button class="bg-white/20 hover:bg-white/30 text-[10px] px-2 py-1 rounded border border-white/30" onclick="app.logout()">
                    <i class="fas fa-sign-out-alt"></i> Sign Out
                </button>
            </div>
        `;
    }

    logout() {
        this.token = null;
        this.currentUser = null;
        this.currentRole = null;
        localStorage.removeItem('gc_token');
        localStorage.removeItem('gc_user');
        document.getElementById('user-greeting').classList.add('hidden');
        this.navigate('login');
    }

    routeUserToDashboard() {
        if (this.currentRole === 'PATIENT') this.navigate('patient-home');
        else if (this.currentRole === 'DOCTOR') this.navigate('doctor-home');
        else if (this.currentRole === 'HOSPITAL') this.navigate('hospital-home');
        else if (this.currentRole === 'ADMIN') this.navigate('admin-home');
        else if (this.currentRole === 'COMMUNITY_REP') this.navigate('health-camps');
        else this.navigate('patient-home');
    }

    getAuthHeaders() {
        const h = { 'Content-Type': 'application/json' };
        if (this.token) h['Authorization'] = `Bearer ${this.token}`;
        return h;
    }

    // ----------------- PATIENT FLOWS & DASHBOARD -----------------
    async loadPatientDashboard() {
        // Load upcoming appointment
        try {
            const res = await fetch('/api/appointments', { headers: this.getAuthHeaders() });
            const data = await res.json();
            const upcomingCard = document.getElementById('patient-upcoming-card');
            const appts = data.data || [];
            document.getElementById('patient-appts-count').innerText = appts.length;

            const upcoming = appts.find(a => a.status === 'CONFIRMED' || a.status === 'IN_PROGRESS');
            if (upcoming) {
                upcomingCard.innerHTML = `
                    <div class="soft-card border-l-4 border-teal-500 flex justify-between items-center">
                        <div>
                            <span class="bg-teal-100 text-teal-800 text-[10px] font-bold px-2 py-0.5 rounded">CONFIRMED</span>
                            <h4 class="font-bold text-sm text-gray-800 mt-1">${upcoming.doctor_name}</h4>
                            <p class="text-xs text-gray-500">${upcoming.specialization}</p>
                            <p class="text-[11px] text-teal-700 mt-1 font-semibold">
                                <i class="far fa-calendar-alt mr-1"></i> ${upcoming.appointment_date} • ${upcoming.time_slot}
                            </p>
                        </div>
                        <button class="bg-teal-700 hover:bg-teal-800 text-white text-xs px-3.5 py-2 rounded-xl font-bold shadow-sm transition" onclick="app.joinConsultation('${upcoming.id}', '${upcoming.doctor_name}', '${upcoming.doctor_id}')">
                            <i class="fas fa-video mr-1"></i> Join Call
                        </button>
                    </div>
                `;
            } else {
                upcomingCard.innerHTML = `
                    <div class="soft-card text-center py-4 bg-gray-50 border border-gray-200">
                        <p class="text-xs text-gray-500">No appointments scheduled today.</p>
                        <button class="mt-2 text-xs text-teal-700 font-bold hover:underline" onclick="app.navigate('doctor-search')">
                            + Book a Free Consultation
                        </button>
                    </div>
                `;
            }

            // Load Preview Health Camps
            const campRes = await fetch('/api/camps');
            const campData = await campRes.json();
            const campList = document.getElementById('patient-home-camps-list');
            campList.innerHTML = '';
            (campData.data || []).slice(0, 2).forEach(c => {
                campList.innerHTML += this.renderCampCard(c);
            });
        } catch (e) {
            console.error(e);
        }
    }

    // ----------------- AI SYMPTOM TRIAGE FLOW -----------------
    async executeTriage() {
        const symptoms = document.getElementById('triage-symptoms-input').value.trim();
        const duration = document.getElementById('triage-duration').value;
        const severity = document.getElementById('triage-severity').value;
        const age = parseInt(document.getElementById('triage-age').value) || 38;

        if (!symptoms) {
            alert("Please enter or speak your symptoms.");
            return;
        }

        const btn = document.getElementById('btn-submit-triage');
        btn.disabled = true;
        btn.innerHTML = `<i class="fas fa-spinner fa-spin mr-2"></i> ${this.t('triage_analyzing', "Analyzing with NLP clinical model...")}`;

        try {
            const res = await fetch('/api/ai/triage', {
                method: 'POST',
                headers: this.getAuthHeaders(),
                body: JSON.stringify({ symptoms, duration, severity, age })
            });
            const resp = await res.json();
            const data = resp.data;

            // Check Emergency Alert
            const emergBox = document.getElementById('emergency-alert-banner');
            if (data.emergency_alert) {
                document.getElementById('emergency-alert-text').innerText = data.emergency_alert;
                emergBox.classList.remove('hidden');
            } else {
                emergBox.classList.add('hidden');
            }

            // Populate Results
            document.getElementById('res-suggested-dept').innerText = data.suggested_department;
            document.getElementById('res-symptom-summary').innerText = data.summary;
            document.getElementById('res-recommended-step').innerText = data.recommended_next_step;

            // Urgency Badge
            const badge = document.getElementById('res-urgency-badge');
            const card = document.getElementById('triage-card');
            badge.innerText = `${data.urgency} URGENCY`;
            card.className = "soft-card border-l-4";

            if (data.urgency === 'EMERGENCY') {
                badge.className = "text-xs font-bold px-2.5 py-1 rounded-full uppercase bg-red-100 text-red-800";
                card.classList.add('border-red-600', 'bg-red-50/50');
            } else if (data.urgency === 'HIGH') {
                badge.className = "text-xs font-bold px-2.5 py-1 rounded-full uppercase bg-amber-100 text-amber-800";
                card.classList.add('border-amber-500', 'bg-amber-50/50');
            } else if (data.urgency === 'MODERATE') {
                badge.className = "text-xs font-bold px-2.5 py-1 rounded-full uppercase bg-yellow-100 text-yellow-800";
                card.classList.add('border-yellow-500');
            } else {
                badge.className = "text-xs font-bold px-2.5 py-1 rounded-full uppercase bg-green-100 text-green-800";
                card.classList.add('border-green-500');
            }

            // Questions list
            const qList = document.getElementById('res-questions-list');
            qList.innerHTML = '';
            (data.questions_for_doctor || []).forEach(q => {
                qList.innerHTML += `<li>${q}</li>`;
            });

            document.getElementById('triage-results-container').classList.remove('hidden');
            this.lastTriageDept = data.suggested_department;
        } catch (e) {
            alert("Failed to reach AI Triage service.");
        } finally {
            btn.disabled = false;
            btn.innerHTML = `<i class="fas fa-brain mr-2"></i> Run AI Clinical Triage`;
        }
    }

    findDoctorForDepartment() {
        const dept = this.lastTriageDept || 'General Physician';
        this.navigate('doctor-search');
        this.filterDoctorsBySpec(dept);
    }

    toggleVoiceInput() {
        const vBtn = document.getElementById('voice-input-btn');
        if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
            alert("Voice recognition is not supported in this browser. Please type symptoms.");
            return;
        }

        const SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition;
        const rec = new SpeechRec();
        rec.lang = this.currentLang === 'gu' ? 'gu-IN' : (this.currentLang === 'hi' ? 'hi-IN' : 'en-IN');
        rec.interimResults = false;

        vBtn.classList.add('text-red-600', 'animate-pulse');
        rec.start();

        rec.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            const input = document.getElementById('triage-symptoms-input');
            input.value = input.value ? `${input.value} ${transcript}` : transcript;
            vBtn.classList.remove('text-red-600', 'animate-pulse');
        };

        rec.onerror = () => {
            vBtn.classList.remove('text-red-600', 'animate-pulse');
        };
        rec.onend = () => {
            vBtn.classList.remove('text-red-600', 'animate-pulse');
        };
    }

    // ----------------- MEDICAL IMAGE SCREENING -----------------
    handleImageFileSelect(input) {
        if (input.files && input.files[0]) {
            this.selectedImageFile = input.files[0];
            document.getElementById('upload-file-label').innerText = `Selected: ${this.selectedImageFile.name}`;
            
            const reader = new FileReader();
            reader.onload = (e) => {
                document.getElementById('image-preview-img').src = e.target.result;
                document.getElementById('image-preview-box').classList.remove('hidden');
            };
            reader.readAsDataURL(this.selectedImageFile);
        }
    }

    async executeImageScreening() {
        if (!this.selectedImageFile) {
            alert("Please select a medical image first.");
            return;
        }

        const btn = document.getElementById('btn-run-img-screening');
        btn.disabled = true;
        btn.innerHTML = `<i class="fas fa-spinner fa-spin mr-2"></i> Analyzing Radiographic Features...`;

        const formData = new FormData();
        formData.append('image', this.selectedImageFile);
        formData.append('image_type', document.getElementById('img-modality-select').value);

        try {
            const res = await fetch('/api/ai/image-screening', {
                method: 'POST',
                headers: { 'Authorization': this.token ? `Bearer ${this.token}` : '' },
                body: formData
            });
            const resp = await res.json();
            if (resp.success) {
                const data = resp.data;
                document.getElementById('img-res-category').innerText = data.category;
                document.getElementById('img-res-confidence').innerText = `${data.confidence}% Confidence`;
                document.getElementById('img-res-finding').innerText = data.detected_finding;
                document.getElementById('img-res-recommendation').innerText = data.recommended_action;
                document.getElementById('img-res-limitations').innerText = data.limitations;

                document.getElementById('image-results-container').classList.remove('hidden');
            } else {
                alert(resp.detail || "Screening failed.");
            }
        } catch (e) {
            alert("Error communicating with Computer Vision service.");
        } finally {
            btn.disabled = false;
            btn.innerHTML = `<i class="fas fa-search mr-2"></i> Analyze Image with AI Model`;
        }
    }

    // ----------------- DOCTOR SEARCH & BOOKING -----------------
    async loadDoctors(specialty = 'All') {
        try {
            let url = '/api/doctors';
            if (specialty && specialty !== 'All') {
                url += `?specialty=${encodeURIComponent(specialty)}`;
            }
            const res = await fetch(url);
            const data = await res.json();
            const container = document.getElementById('doctor-cards-list');
            container.innerHTML = '';

            const docs = data.data || [];
            if (docs.length === 0) {
                container.innerHTML = `<p class="text-xs text-gray-500 text-center py-6">No verified doctors available in this category.</p>`;
                return;
            }

            docs.forEach(d => {
                container.innerHTML += `
                    <div class="soft-card hover:border-teal-500 border border-transparent transition">
                        <div class="flex items-start">
                            <div class="w-12 h-12 bg-teal-100 rounded-full flex items-center justify-center text-2xl mr-3">
                                ${d.avatar_emoji || '👨🏽‍⚕️'}
                            </div>
                            <div class="flex-1">
                                <div class="flex items-center justify-between">
                                    <h3 class="font-bold text-sm text-gray-800">${d.full_name}</h3>
                                    <span class="bg-emerald-100 text-emerald-800 text-[10px] font-bold px-2 py-0.5 rounded-full flex items-center">
                                        <i class="fas fa-check-circle mr-1"></i> VERIFIED
                                    </span>
                                </div>
                                <p class="text-xs text-gray-500">${d.specialization} • ${d.experience_years} yrs exp</p>
                                
                                <div class="flex items-center my-1.5">
                                    <span class="bg-yellow-100 text-yellow-800 text-xs px-2 py-0.5 rounded font-bold mr-2 flex items-center">
                                        <i class="fas fa-star text-yellow-500 mr-1"></i> ${d.rating_avg}
                                    </span>
                                    <span class="text-[11px] text-gray-400">(${d.reviews_count} Verified Consultations)</span>
                                </div>

                                <p class="text-[11px] text-gray-500"><i class="fas fa-language mr-1"></i> ${(d.languages_list || []).join(' • ')}</p>

                                <div class="flex justify-between items-center mt-3 pt-2 border-t border-gray-100">
                                    <span class="text-xs font-bold text-emerald-700">₹${d.consultation_fee} / Free Community Care</span>
                                    <div class="space-x-1.5">
                                        <button class="bg-gray-100 hover:bg-gray-200 text-gray-700 text-xs px-3 py-1.5 rounded-lg font-semibold" onclick="app.openDoctorProfile('${d.id}')">
                                            Profile
                                        </button>
                                        <button class="bg-teal-700 hover:bg-teal-800 text-white text-xs px-3 py-1.5 rounded-lg font-bold shadow-xs" onclick="app.openDoctorProfile('${d.id}')">
                                            Book Slot
                                        </button>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                `;
            });
        } catch (e) {
            console.error(e);
        }
    }

    filterDoctorsBySpec(spec, btnEl = null) {
        this.currentSpecialtyFilter = spec;
        if (btnEl) {
            document.querySelectorAll('#specialty-filter-bar button').forEach(b => {
                b.className = "bg-gray-200 text-gray-700 px-3 py-1.5 rounded-full font-semibold whitespace-nowrap hover:bg-gray-300";
            });
            btnEl.className = "bg-teal-700 text-white px-3 py-1.5 rounded-full font-semibold whitespace-nowrap";
        }
        this.loadDoctors(spec);
    }

    async openDoctorProfile(docId) {
        try {
            const res = await fetch(`/api/doctors/${docId}`);
            const data = await res.json();
            const doc = data.data;
            const reviews = data.reviews || [];

            this.selectedDoctorForBooking = doc;

            const headerBox = document.getElementById('doc-profile-header');
            headerBox.innerHTML = `
                <div class="flex items-center space-x-3 mb-3">
                    <div class="w-16 h-16 bg-teal-100 rounded-full flex items-center justify-center text-3xl">
                        ${doc.avatar_emoji || '👨🏽‍⚕️'}
                    </div>
                    <div>
                        <h3 class="font-bold text-base text-gray-900">${doc.full_name}</h3>
                        <p class="text-xs text-teal-700 font-semibold">${doc.specialization} (${doc.qualification})</p>
                        <p class="text-[11px] text-gray-500">${doc.hospital_affiliation || 'Primary Care'}</p>
                    </div>
                </div>
                <div class="bg-gray-50 p-2.5 rounded-xl text-xs text-gray-600 mb-3">
                    <p class="leading-relaxed">${doc.bio || 'Dedicated tele-specialist serving rural communities.'}</p>
                </div>
                <div class="flex justify-between items-center text-xs">
                    <span class="font-semibold text-gray-700">License: ${doc.license_number}</span>
                    <span class="bg-blue-100 text-blue-800 text-xs px-2 py-0.5 rounded font-bold">
                        ⭐ ${doc.rating_avg} / 5 (${doc.reviews_count} Reviews)
                    </span>
                </div>
            `;

            // Set default booking date to tomorrow
            const tomorrow = new Date();
            tomorrow.setDate(tomorrow.getDate() + 1);
            document.getElementById('book-date').value = tomorrow.toISOString().split('T')[0];

            // Render Reviews
            const revList = document.getElementById('doc-profile-reviews-list');
            revList.innerHTML = '';
            if (reviews.length === 0) {
                revList.innerHTML = `<p class="text-gray-400 italic">No reviews yet for this doctor.</p>`;
            } else {
                reviews.forEach(r => {
                    revList.innerHTML += `
                        <div class="p-2.5 bg-gray-50 rounded-xl border border-gray-200">
                            <div class="flex justify-between items-center mb-1">
                                <span class="font-bold text-gray-700">Patient ${r.patient_initials}</span>
                                <span class="text-yellow-500 font-bold">★ ${r.rating}.0</span>
                            </div>
                            <p class="text-gray-600 text-[11px] leading-relaxed">${r.review_text || 'Consultation completed satisfactorily.'}</p>
                            <span class="text-[10px] text-teal-600 font-semibold mt-1 block">
                                <i class="fas fa-check-circle"></i> Verified Teleconsultation
                            </span>
                        </div>
                    `;
                });
            }

            this.navigate('doctor-profile');
        } catch (e) {
            console.error(e);
        }
    }

    async submitAppointmentBooking() {
        if (!this.token) {
            alert("Please sign in or select a demo patient persona to book.");
            this.navigate('login');
            return;
        }
        if (!this.selectedDoctorForBooking) return;

        const date = document.getElementById('book-date').value;
        const slot = document.getElementById('book-slot').value;
        const complaint = document.getElementById('book-complaint').value.trim() || "General health consultation";

        try {
            const res = await fetch('/api/appointments', {
                method: 'POST',
                headers: this.getAuthHeaders(),
                body: JSON.stringify({
                    doctor_id: this.selectedDoctorForBooking.id,
                    appointment_date: date,
                    time_slot: slot,
                    chief_complaint: complaint
                })
            });
            const data = await res.json();
            if (data.success) {
                alert(`Appointment confirmed for ${date} at ${slot}!`);
                this.navigate('patient-home');
            } else {
                alert(data.detail || "Booking failed.");
            }
        } catch (e) {
            alert("Slot booking error. Slot might already be occupied.");
        }
    }

    // ----------------- TELECONSULTATION & REAL-TIME CHAT -----------------
    async joinConsultation(appointmentId, doctorName, doctorId) {
        try {
            const res = await fetch(`/api/consultations/${appointmentId}/start`, {
                method: 'POST',
                headers: this.getAuthHeaders()
            });
            const data = await res.json();
            if (data.success) {
                this.activeConsultation = data.data;
                this.activeDoctor = { id: doctorId, name: doctorName };
                this.openConsultationRoom();
            }
        } catch (e) {
            alert("Unable to initialize teleconsultation session.");
        }
    }

    openConsultationRoom() {
        if (!this.activeConsultation) return;
        const cnsId = this.activeConsultation.id;

        document.getElementById('call-partner-name').innerText = `Consultation with ${this.activeDoctor ? this.activeDoctor.name : 'Patient'}`;
        document.getElementById('call-partner-subname').innerText = this.activeDoctor ? this.activeDoctor.name : 'Patient';
        document.getElementById('chat-messages-container').innerHTML = '';

        // Start Webcam (Simulated real call)
        this.startLocalWebcam();

        // Connect WebSocket
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws/consultation/${cnsId}`;
        this.consultationWs = new WebSocket(wsUrl);

        this.consultationWs.onopen = () => {
            document.getElementById('call-connection-status').innerText = "Encrypted teleconsultation channel live.";
        };

        this.consultationWs.onmessage = (event) => {
            try {
                const msg = JSON.parse(event.data);
                if (msg.type === 'chat') {
                    this.appendChatMessage(msg);
                } else if (msg.type === 'system') {
                    this.appendSystemMessage(msg.message);
                }
            } catch (e) {}
        };

        this.navigate('consultation-room');
    }

    async startLocalWebcam() {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: false });
            this.localStream = stream;
            
            // Try to find the self video element or create one
            let selfView = document.getElementById('self-video-element');
            const selfViewContainer = document.getElementById('self-view-container');
            
            if (selfViewContainer) {
                if (!selfView) {
                    selfView = document.createElement('video');
                    selfView.id = 'self-video-element';
                    selfView.autoplay = true;
                    selfView.muted = true;
                    selfView.className = "w-full h-full object-cover";
                    selfViewContainer.innerHTML = '';
                    selfViewContainer.appendChild(selfView);
                }
                selfView.srcObject = stream;
            }
        } catch (err) {
            console.log("Webcam access denied or unavailable.");
        }
    }

    leaveConsultation() {
        if (this.consultationWs) {
            this.consultationWs.close();
            this.consultationWs = null;
        }
        if (this.localStream) {
            this.localStream.getTracks().forEach(track => track.stop());
            this.localStream = null;
        }
        
        if (this.currentRole === 'DOCTOR') {
            this.navigate('doctor-home');
        } else {
            this.navigate('rate-consultation');
        }
    }

    sendConsultChatMessage() {
        const input = document.getElementById('consult-chat-input');
        const text = input.value.trim();
        if (!text || !this.consultationWs) return;

        const payload = {
            type: 'chat',
            message: text,
            sender_id: this.currentUser ? this.currentUser.id : 'anon',
            sender_name: this.currentUser ? this.currentUser.full_name : 'User',
            sender_role: this.currentRole || 'PATIENT',
            timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        };

        this.consultationWs.send(JSON.stringify(payload));
        input.value = '';
    }

    appendChatMessage(msg) {
        const container = document.getElementById('chat-messages-container');
        const isSelf = this.currentUser && this.currentUser.id === msg.sender_id;
        const div = document.createElement('div');
        div.className = `p-2 rounded-xl text-xs max-w-[85%] ${isSelf ? 'ml-auto bg-teal-800 text-white' : 'mr-auto bg-gray-800 text-gray-200'}`;
        div.innerHTML = `
            <div class="flex justify-between items-center text-[10px] opacity-75 mb-0.5">
                <span class="font-bold">${msg.sender_name}</span>
                <span>${msg.timestamp || ''}</span>
            </div>
            <p>${msg.message}</p>
        `;
        container.appendChild(div);
        container.scrollTop = container.scrollHeight;
    }

    appendSystemMessage(text) {
        const container = document.getElementById('chat-messages-container');
        const div = document.createElement('div');
        div.className = "text-center text-[10px] text-gray-500 italic my-1";
        div.innerText = text;
        container.appendChild(div);
    }

    switchCallTab(tab) {
        const tabChat = document.getElementById('call-tab-chat');
        const tabNotes = document.getElementById('call-tab-notes');
        const paneChat = document.getElementById('call-pane-chat');
        const paneNotes = document.getElementById('call-pane-notes');

        if (tab === 'chat') {
            tabChat.className = "flex-1 py-2 font-bold text-teal-400 border-b-2 border-teal-500";
            tabNotes.className = "flex-1 py-2 font-medium text-gray-400";
            paneChat.classList.remove('hidden');
            paneNotes.classList.add('hidden');
        } else {
            tabNotes.className = "flex-1 py-2 font-bold text-teal-400 border-b-2 border-teal-500";
            tabChat.className = "flex-1 py-2 font-medium text-gray-400";
            paneNotes.classList.remove('hidden');
            paneChat.classList.add('hidden');
        }
    }

    toggleCallMic() {
        const btn = document.getElementById('btn-toggle-mic');
        btn.classList.toggle('text-red-500');
    }

    toggleCallCam() {
        const btn = document.getElementById('btn-toggle-cam');
        btn.classList.toggle('text-red-500');
    }

    toggleConsultationAudioFirst() {
        const area = document.getElementById('video-display-area');
        alert("Audio-First mode active: Video frames paused to save bandwidth on weak connection.");
    }

    async doctorFinishConsultation() {
        if (!this.activeConsultation) return;
        const diagnosis = document.getElementById('call-doc-diagnosis').value.trim() || "Upper Respiratory Tract Infection";
        const notes = document.getElementById('call-doc-notes').value.trim() || "Hydration, symptomatic treatment prescribed.";

        const medications = [
            { name: "Paracetamol 500mg", dosage: "1 tab", timing: "SOS", duration: "3 days" },
            { name: "Warm Saline Gargle", dosage: "Twice daily", timing: "Morning & Night", duration: "5 days" }
        ];

        try {
            const res = await fetch(`/api/consultations/${this.activeConsultation.id}/complete`, {
                method: 'POST',
                headers: this.getAuthHeaders(),
                body: JSON.stringify({ clinical_notes: notes, diagnosis, medications })
            });
            const data = await res.json();
            if (data.success) {
                alert("Consultation finalized & prescription generated.");
                this.leaveConsultation();
            }
        } catch (e) {
            alert("Error completing consultation.");
        }
    }

    leaveConsultation() {
        if (this.consultationWs) {
            this.consultationWs.close();
            this.consultationWs = null;
        }

        if (this.currentRole === 'PATIENT' && this.activeDoctor) {
            document.getElementById('rate-doctor-name').innerText = this.activeDoctor.name;
            this.selectedRating = 5;
            this.setStarRating(5);
            this.navigate('rate-consultation');
        } else {
            this.routeUserToDashboard();
        }
    }

    // ----------------- DOCTOR TRUST & RATING -----------------
    setStarRating(val) {
        this.selectedRating = val;
        const stars = document.getElementById('star-rating-selector').children;
        for (let i = 0; i < 5; i++) {
            if (i < val) {
                stars[i].className = "fas fa-star cursor-pointer text-yellow-400 transition";
            } else {
                stars[i].className = "fas fa-star cursor-pointer text-gray-300 transition";
            }
        }
    }

    async submitDoctorRating() {
        if (!this.activeConsultation || !this.activeDoctor) {
            this.navigate('patient-home');
            return;
        }

        const reviewText = document.getElementById('rate-review-text').value.trim();
        const comm = parseInt(document.getElementById('score-comm').value) || 5;
        const punct = parseInt(document.getElementById('score-punct').value) || 5;
        const exp = parseInt(document.getElementById('score-exp').value) || 5;

        try {
            const res = await fetch('/api/reviews', {
                method: 'POST',
                headers: this.getAuthHeaders(),
                body: JSON.stringify({
                    doctor_id: this.activeDoctor.id,
                    consultation_id: this.activeConsultation.id,
                    rating: this.selectedRating,
                    communication_score: comm,
                    punctuality_score: punct,
                    explanation_score: exp,
                    review_text: reviewText
                })
            });
            const data = await res.json();
            if (data.success) {
                alert("Thank you! Your verified consultation review was recorded and doctor trust score updated.");
            }
        } catch (e) {
            console.warn(e);
        } finally {
            this.navigate('patient-home');
        }
    }

    // ----------------- COMMUNITY HEALTH CAMPS -----------------
    async loadCamps() {
        try {
            const res = await fetch('/api/camps');
            const data = await res.json();
            const container = document.getElementById('pane-camps-list');
            if (container) {
                container.innerHTML = '';
                (data.data || []).forEach(c => {
                    container.innerHTML += this.renderCampCard(c);
                });
            }
        } catch (e) {
            console.error(e);
        }
    }

    renderCampCard(camp) {
        const isFull = camp.registered_count >= camp.capacity;
        const isCompleted = camp.status === 'COMPLETED';
        return `
            <div class="soft-card border border-gray-100">
                <div class="flex justify-between items-center mb-1.5">
                    <span class="bg-emerald-100 text-emerald-800 text-[10px] font-bold px-2 py-0.5 rounded uppercase">
                        ${isCompleted ? 'COMPLETED' : 'FREE COMMUNITY CAMP'}
                    </span>
                    <span class="text-xs font-bold ${isFull ? 'text-red-600' : 'text-teal-700'}">
                        ${camp.registered_count} / ${camp.capacity} Seats Registered
                    </span>
                </div>
                <h3 class="font-bold text-sm text-gray-900 mt-1">${camp.title}</h3>
                <p class="text-[11px] text-gray-500 mb-2">Organized by: <span class="font-semibold text-gray-700">${camp.organizer_name}</span></p>

                <div class="grid grid-cols-2 gap-1.5 text-xs text-gray-600 my-2 bg-gray-50 p-2 rounded-lg">
                    <div><i class="fas fa-map-marker-alt text-teal-600 mr-1"></i> ${camp.location}</div>
                    <div><i class="far fa-calendar-alt text-teal-600 mr-1"></i> ${camp.date}</div>
                    <div><i class="far fa-clock text-teal-600 mr-1"></i> ${camp.time}</div>
                    <div><i class="fas fa-city text-teal-600 mr-1"></i> ${camp.village}, ${camp.district}</div>
                </div>

                <div class="flex flex-wrap gap-1 mb-3">
                    ${(camp.services_list || []).map(s => `<span class="bg-white border border-gray-200 text-gray-600 text-[10px] px-2 py-0.5 rounded">${s}</span>`).join('')}
                </div>

                ${isCompleted && camp.impact_report ? `
                    <div class="bg-blue-50 border border-blue-200 p-2.5 rounded-xl text-xs text-blue-900 mb-3">
                        <p class="font-bold mb-1"><i class="fas fa-chart-line mr-1"></i> Social Impact Report:</p>
                        <div class="grid grid-cols-2 gap-1 text-[11px]">
                            <span>Villagers Attended: <b>${camp.impact_report.patients_attended}</b></span>
                            <span>Screenings: <b>${camp.impact_report.screenings_completed}</b></span>
                            <span>Hospital Referrals: <b>${camp.impact_report.referrals_to_hospital}</b></span>
                            <span>Medicines Given: <b>${camp.impact_report.medicines_distributed}</b></span>
                        </div>
                    </div>
                ` : `
                    <button class="w-full ${isFull ? 'bg-gray-300 text-gray-500 cursor-not-allowed' : 'bg-emerald-700 hover:bg-emerald-800 text-white'} font-bold py-2.5 rounded-xl text-xs transition shadow-xs" 
                            ${isFull ? 'disabled' : ''} onclick="app.registerForCamp('${camp.id}')">
                        ${isFull ? 'Camp Registration Full' : 'Register for Free Camp Seat'}
                    </button>
                `}
            </div>
        `;
    }

    async registerForCamp(campId) {
        if (!this.token) {
            alert("Please sign in as a Patient to register.");
            this.navigate('login');
            return;
        }
        try {
            const res = await fetch(`/api/camps/${campId}/register`, {
                method: 'POST',
                headers: this.getAuthHeaders()
            });
            const data = await res.json();
            if (data.success) {
                alert(data.message);
                this.loadCamps();
            } else {
                alert(data.detail || "Registration failed.");
            }
        } catch (e) {
            alert("Error registering for camp.");
        }
    }

    switchCampTab(tab) {
        const tabList = document.getElementById('tab-camps-list');
        const tabReq = document.getElementById('tab-camps-request');
        const paneList = document.getElementById('pane-camps-list');
        const paneReq = document.getElementById('pane-camps-request');

        if (tab === 'list') {
            tabList.className = "flex-1 bg-teal-700 text-white py-2 rounded-xl text-xs font-bold shadow-xs";
            tabReq.className = "flex-1 bg-white border border-teal-600 text-teal-700 py-2 rounded-xl text-xs font-bold";
            paneList.classList.remove('hidden');
            paneReq.classList.add('hidden');
            this.loadCamps();
        } else {
            tabReq.className = "flex-1 bg-teal-700 text-white py-2 rounded-xl text-xs font-bold shadow-xs";
            tabList.className = "flex-1 bg-white border border-teal-600 text-teal-700 py-2 rounded-xl text-xs font-bold";
            paneReq.classList.remove('hidden');
            paneList.classList.add('hidden');
        }
    }

    async handleCampRequestSubmit(e) {
        e.preventDefault();
        const payload = {
            village: document.getElementById('creq-village').value,
            district: document.getElementById('creq-district').value,
            contact_person: document.getElementById('creq-person').value,
            contact_phone: document.getElementById('creq-phone').value,
            camp_type: document.getElementById('creq-type').value,
            expected_patients: parseInt(document.getElementById('creq-count').value) || 100,
            preferred_date: document.getElementById('creq-date').value,
            description: document.getElementById('creq-desc').value,
            required_services: ["General Physician", "Vitals Screening", "Medicines"]
        };

        try {
            const res = await fetch('/api/camp-requests', {
                method: 'POST',
                headers: this.getAuthHeaders(),
                body: JSON.stringify(payload)
            });
            const data = await res.json();
            if (data.success) {
                alert("Village health camp request submitted! Healthcare partners will be notified.");
                this.switchCampTab('list');
            }
        } catch (e) {
            alert("Error submitting request.");
        }
    }

    // ----------------- ABDM & HEALTH RECORDS -----------------
    async loadHealthRecords() {
        try {
            const res = await fetch('/api/health-records', { headers: this.getAuthHeaders() });
            const data = await res.json();
            const container = document.getElementById('records-list-container');
            container.innerHTML = '';

            const records = data.data || [];
            if (records.length === 0) {
                container.innerHTML = `<p class="text-xs text-gray-400 italic">No health records uploaded yet.</p>`;
                return;
            }

            records.forEach(r => {
                container.innerHTML += `
                    <div class="soft-card !p-3 flex items-center justify-between">
                        <div class="flex items-center space-x-3">
                            <div class="w-10 h-10 bg-teal-100 text-teal-700 rounded-lg flex items-center justify-center text-lg">
                                <i class="fas fa-file-medical-alt"></i>
                            </div>
                            <div>
                                <h4 class="font-bold text-xs text-gray-800">${r.title}</h4>
                                <p class="text-[10px] text-gray-500">${r.record_type} • ${r.date_recorded} • ${r.uploaded_by}</p>
                            </div>
                        </div>
                        <span class="text-xs text-teal-600 font-bold bg-teal-50 px-2 py-1 rounded">
                            <i class="fas fa-check-circle mr-1"></i> ABDM Ready
                        </span>
                    </div>
                `;
            });

            this.viewAbdmConsents();
        } catch (e) {}
    }

    async viewAbdmConsents() {
        try {
            const res = await fetch('/api/abdm/consents', { headers: this.getAuthHeaders() });
            const data = await res.json();
            const container = document.getElementById('consents-list-container');
            const badge = document.getElementById('consent-count-badge');
            container.innerHTML = '';

            const consents = data.data || [];
            badge.innerText = consents.length;

            if (consents.length === 0) {
                container.innerHTML = `<p class="text-gray-500 italic">No active consent requests pending.</p>`;
                return;
            }

            consents.forEach(c => {
                const isPending = c.consent_status === 'PENDING';
                container.innerHTML += `
                    <div class="p-2.5 bg-white rounded-lg border border-blue-100 flex justify-between items-center">
                        <div>
                            <p class="font-bold text-gray-800">${c.doctor_name || 'Attending Physician'}</p>
                            <p class="text-[10px] text-gray-500">Purpose: ${c.purpose}</p>
                            <span class="text-[9px] font-mono text-gray-400">Status: ${c.consent_status}</span>
                        </div>
                        ${isPending ? `
                            <div class="space-x-1">
                                <button class="bg-emerald-600 text-white text-[10px] px-2 py-1 rounded font-bold" onclick="app.updateConsent('${c.id}', 'GRANTED')">Grant</button>
                                <button class="bg-gray-200 text-gray-700 text-[10px] px-2 py-1 rounded font-bold" onclick="app.updateConsent('${c.id}', 'DENIED')">Deny</button>
                            </div>
                        ` : `
                            <span class="text-[10px] font-bold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded">${c.consent_status}</span>
                        `}
                    </div>
                `;
            });
        } catch (e) {}
    }

    async updateConsent(consentId, status) {
        try {
            const res = await fetch(`/api/abdm/consents/${consentId}`, {
                method: 'PATCH',
                headers: this.getAuthHeaders(),
                body: JSON.stringify({ status })
            });
            const data = await res.json();
            if (data.success) {
                alert(`ABDM Consent ${status}!`);
                this.viewAbdmConsents();
            }
        } catch (e) {}
    }

    async simulateAbhaOtp() {
        try {
            const res = await fetch('/api/abdm/link-abha', {
                method: 'POST',
                headers: this.getAuthHeaders(),
                body: JSON.stringify({})
            });
            const data = await res.json();
            if (data.success) {
                alert(`ABHA ID Verified & Linked: ${data.data.abha_number}`);
                this.loadPatientDashboard();
            }
        } catch (e) {}
    }

    // ----------------- DOCTOR DASHBOARD -----------------
    async loadDoctorDashboard() {
        try {
            // 1. Load doctor profile
            const meRes = await fetch('/api/auth/me', { headers: this.getAuthHeaders() });
            const meData = await meRes.json();
            if (meData.success && meData.doctor_profile) {
                const doc = meData.doctor_profile;
                const user = meData.user;
                document.getElementById('doc-greeting').innerText = `${user.full_name} (${doc.specialization || 'General Physician'})`;
                
                const badge = document.getElementById('doc-verification-badge');
                if (doc.verification_status === 'VERIFIED') {
                    badge.className = "bg-emerald-100 text-emerald-800 text-[10px] font-bold px-2.5 py-1 rounded-full flex items-center";
                    badge.innerHTML = `<i class="fas fa-check-circle mr-1"></i> VERIFIED GMC`;
                } else {
                    badge.className = "bg-amber-100 text-amber-800 text-[10px] font-bold px-2.5 py-1 rounded-full flex items-center";
                    badge.innerHTML = `<i class="fas fa-hourglass-half mr-1"></i> PENDING VERIFICATION`;
                }
                
                document.getElementById('doc-metric-rating').innerHTML = `<i class="fas fa-star text-yellow-400 mr-1 text-lg"></i> ${doc.rating_avg || 5.0}`;
                document.getElementById('doc-metric-reviews-count').innerText = `${doc.reviews_count || 0} Verified Consultations`;
            }

            // 2. Load Appointments Queue
            const res = await fetch('/api/appointments', { headers: this.getAuthHeaders() });
            const data = await res.json();
            const container = document.getElementById('doctor-queue-list');
            container.innerHTML = '';

            const queue = data.data || [];
            document.getElementById('doc-queue-badge').innerText = `${queue.length} Total`;
            document.getElementById('doc-metric-today').innerText = queue.length;

            if (queue.length === 0) {
                container.innerHTML = `<div class="p-6 text-center bg-gray-50 rounded-xl border border-dashed border-gray-300">
                    <i class="fas fa-calendar-check text-3xl text-gray-400 mb-2"></i>
                    <p class="text-sm text-gray-500 font-semibold">Your queue is currently clear.</p>
                    <p class="text-[10px] text-gray-400 mt-1">New appointments will appear here.</p>
                </div>`;
            } else {
                queue.forEach(a => {
                    container.innerHTML += `
                        <div class="soft-card border-l-4 border-blue-600 mb-3 bg-white p-3 rounded-lg shadow-sm border border-gray-100">
                            <div class="flex justify-between items-start mb-2">
                                <div>
                                    <h4 class="font-bold text-sm text-gray-900">${a.patient_name} <span class="text-xs font-normal text-gray-500">(${a.age || '--'}y, ${a.gender || '--'})</span></h4>
                                    <p class="text-xs text-gray-500"><i class="fas fa-map-marker-alt text-blue-500 mr-1"></i> ${a.village || 'Unknown'}, ${a.district || ''} • <span class="font-semibold text-blue-700">Slot: ${a.time_slot}</span></p>
                                </div>
                                <button class="bg-blue-600 hover:bg-blue-700 text-white text-xs px-4 py-2 rounded-lg font-bold transition shadow-sm flex items-center" onclick="app.joinConsultation('${a.id}', '${a.patient_name}', '${this.currentUser.id}')">
                                    <i class="fas fa-video mr-1.5"></i> Consult
                                </button>
                            </div>
                            <div class="bg-blue-50/50 p-2.5 rounded-lg text-xs border border-blue-100 mt-2">
                                <span class="font-bold text-blue-800"><i class="fas fa-stethoscope mr-1"></i> Complaint:</span>
                                <span class="text-gray-700 font-medium ml-1">${a.chief_complaint || 'General Consultation'}</span>
                            </div>
                        </div>
                    `;
                });
            }

            // 3. Load camp requests
            const reqRes = await fetch('/api/camp-requests');
            const reqData = await reqRes.json();
            const reqBox = document.getElementById('doc-camp-requests-list');
            reqBox.innerHTML = '';
            (reqData.data || []).slice(0, 2).forEach(r => {
                reqBox.innerHTML += `
                    <div class="p-3 bg-white rounded-lg flex justify-between items-center border border-gray-200 mb-2 shadow-sm">
                        <div>
                            <span class="font-bold text-gray-800 text-sm"><i class="fas fa-users text-blue-600 mr-1"></i> ${r.village}</span>
                            <span class="text-[10px] text-gray-500 ml-1">(${r.expected_patients} expected)</span>
                            <p class="text-[11px] text-gray-600 mt-0.5"><i class="far fa-calendar-alt text-gray-400 mr-1"></i> ${r.preferred_date}</p>
                        </div>
                        <button class="bg-blue-100 text-blue-700 text-xs px-3 py-1.5 rounded-lg font-bold hover:bg-blue-200 transition" onclick="app.acceptCampRequest('${r.id}')">
                            <i class="fas fa-check mr-1"></i> Accept
                        </button>
                    </div>
                `;
            });
        } catch (e) {
            console.error(e);
        }
    }

    async openDoctorProfileEdit() {
        try {
            const res = await fetch('/api/auth/me', { headers: this.getAuthHeaders() });
            const data = await res.json();
            if (data.success && data.doctor_profile) {
                const doc = data.doctor_profile;
                const user = data.user;
                document.getElementById('edit-doc-name').value = user.full_name || '';
                document.getElementById('edit-doc-qual').value = doc.qualification || '';
                document.getElementById('edit-doc-spec').value = doc.specialization || '';
                document.getElementById('edit-doc-exp').value = doc.experience_years || 0;
                document.getElementById('edit-doc-fee').value = doc.consultation_fee || 0;
                document.getElementById('edit-doc-languages').value = doc.languages_spoken ? JSON.parse(doc.languages_spoken).join(', ') : 'English, Hindi, Gujarati';
                document.getElementById('edit-doc-hospital').value = doc.hospital_affiliation || '';
                document.getElementById('edit-doc-bio').value = doc.bio || '';
                this.navigate('doctor-profile-edit');
            }
        } catch (e) {
            alert("Error loading doctor profile for editing.");
        }
    }

    async saveDoctorProfile(e) {
        e.preventDefault();
        const languagesRaw = document.getElementById('edit-doc-languages').value;
        const languagesList = languagesRaw.split(',').map(s => s.trim()).filter(Boolean);
        
        const payload = {
            full_name: document.getElementById('edit-doc-name').value,
            qualification: document.getElementById('edit-doc-qual').value,
            specialization: document.getElementById('edit-doc-spec').value,
            experience_years: parseInt(document.getElementById('edit-doc-exp').value) || 0,
            consultation_fee: parseFloat(document.getElementById('edit-doc-fee').value) || 0.0,
            languages_spoken: languagesList,
            hospital_affiliation: document.getElementById('edit-doc-hospital').value,
            bio: document.getElementById('edit-doc-bio').value
        };

        const btn = document.getElementById('btn-save-doc-profile');
        btn.disabled = true;
        btn.innerHTML = `<i class="fas fa-spinner fa-spin mr-1.5"></i> Saving Changes...`;

        try {
            const res = await fetch('/api/doctors/profile', {
                method: 'PATCH',
                headers: this.getAuthHeaders(),
                body: JSON.stringify(payload)
            });
            const data = await res.json();
            if (data.success) {
                alert("Doctor profile successfully updated and saved to database!");
                if (this.currentUser) {
                    this.currentUser.full_name = payload.full_name;
                    localStorage.setItem('gc_user', JSON.stringify(this.currentUser));
                }
                this.navigate('doctor-home');
            } else {
                alert(data.detail || "Failed to update profile.");
            }
        } catch (err) {
            alert("Error saving doctor profile.");
        } finally {
            btn.disabled = false;
            btn.innerHTML = `<i class="fas fa-save mr-1.5"></i> Save Profile Changes`;
        }
    }

    async openPatientProfileEdit() {
        try {
            const res = await fetch('/api/auth/me', { headers: this.getAuthHeaders() });
            const data = await res.json();
            if (data.success && data.patient_profile) {
                const pat = data.patient_profile;
                const user = data.user;
                document.getElementById('edit-pat-name').value = user.full_name || '';
                document.getElementById('edit-pat-age').value = pat.age || 30;
                document.getElementById('edit-pat-gender').value = pat.gender || 'Other';
                document.getElementById('edit-pat-village').value = pat.village || '';
                document.getElementById('edit-pat-district').value = pat.district || '';
                document.getElementById('edit-pat-blood').value = pat.blood_group || '';
                document.getElementById('edit-pat-emergency').value = pat.emergency_contact || '';
                document.getElementById('edit-pat-allergies').value = pat.allergies || '';
                document.getElementById('edit-pat-chronic').value = pat.chronic_conditions || '';
                this.navigate('patient-profile-edit');
            }
        } catch (e) {
            alert("Error loading patient health profile.");
        }
    }

    async savePatientProfile(e) {
        e.preventDefault();
        const payload = {
            full_name: document.getElementById('edit-pat-name').value,
            age: parseInt(document.getElementById('edit-pat-age').value) || 30,
            gender: document.getElementById('edit-pat-gender').value,
            village: document.getElementById('edit-pat-village').value,
            district: document.getElementById('edit-pat-district').value,
            blood_group: document.getElementById('edit-pat-blood').value,
            emergency_contact: document.getElementById('edit-pat-emergency').value,
            allergies: document.getElementById('edit-pat-allergies').value,
            chronic_conditions: document.getElementById('edit-pat-chronic').value
        };

        const btn = document.getElementById('btn-save-pat-profile');
        btn.disabled = true;
        btn.innerHTML = `<i class="fas fa-spinner fa-spin mr-1.5"></i> Saving...`;

        try {
            const res = await fetch('/api/patients/profile', {
                method: 'PATCH',
                headers: this.getAuthHeaders(),
                body: JSON.stringify(payload)
            });
            const data = await res.json();
            if (data.success) {
                alert("Health profile successfully updated!");
                if (this.currentUser) {
                    this.currentUser.full_name = payload.full_name;
                    localStorage.setItem('gc_user', JSON.stringify(this.currentUser));
                }
                this.navigate('patient-home');
            } else {
                alert(data.detail || "Failed to update profile.");
            }
        } catch (err) {
            alert("Error saving patient profile.");
        } finally {
            btn.disabled = false;
            btn.innerHTML = `<i class="fas fa-save mr-1.5"></i> Save Health Profile`;
        }
    }

    // ----------------- HOSPITAL DASHBOARD -----------------
    async loadHospitalDashboard() {
        try {
            const res = await fetch('/api/camp-requests');
            const data = await res.json();
            const container = document.getElementById('hospital-camp-requests-container');
            container.innerHTML = '';

            const requests = data.data || [];
            if (requests.length === 0) {
                container.innerHTML = `<p class="text-gray-400 italic">No pending requests from villages.</p>`;
                return;
            }

            requests.forEach(r => {
                container.innerHTML += `
                    <div class="p-3 bg-gray-50 rounded-xl border border-gray-200">
                        <div class="flex justify-between items-start mb-1">
                            <div>
                                <h4 class="font-bold text-teal-800">${r.village} Village (${r.district})</h4>
                                <p class="text-gray-600">${r.camp_type} • ${r.expected_patients} Expected Villagers</p>
                            </div>
                            <span class="bg-amber-100 text-amber-800 text-[10px] font-bold px-2 py-0.5 rounded">${r.status}</span>
                        </div>
                        <p class="text-[11px] text-gray-500 mb-2">${r.description || 'Community health camp request.'}</p>
                        <button class="bg-emerald-700 hover:bg-emerald-800 text-white text-xs px-3 py-1.5 rounded-lg font-bold" onclick="app.acceptCampRequest('${r.id}')">
                            Accept & Schedule Camp
                        </button>
                    </div>
                `;
            });
        } catch (e) {}
    }

    async acceptCampRequest(reqId) {
        try {
            const res = await fetch(`/api/camp-requests/${reqId}/accept`, {
                method: 'POST',
                headers: this.getAuthHeaders()
            });
            const data = await res.json();
            if (data.success) {
                alert("Village camp request accepted! The camp has been scheduled on the public directory.");
                if (this.currentRole === 'HOSPITAL') this.loadHospitalDashboard();
                else this.loadDoctorDashboard();
            }
        } catch (e) {
            alert("Error accepting camp request.");
        }
    }

    showPublishCampModal() {
        const title = prompt("Camp Title:", "Rural Multi-Specialty Health Screening");
        if (!title) return;
        const village = prompt("Target Village:", "Rampura");
        const date = prompt("Camp Date (YYYY-MM-DD):", "2026-10-15");

        fetch('/api/camps', {
            method: 'POST',
            headers: this.getAuthHeaders(),
            body: JSON.stringify({
                title,
                camp_type: "General Health",
                description: "Proactively organized rural community health camp.",
                location: `${village} Community Hall`,
                village: village || "Rampura",
                district: "Mehsana",
                date: date || "2026-10-15",
                time: "09:00 AM - 02:00 PM",
                capacity: 150,
                services: ["Vitals", "Eye Screening", "Free Medicines"],
                is_free: true
            })
        }).then(res => res.json()).then(data => {
            alert("Health camp published!");
            this.loadHospitalDashboard();
        });
    }

    // ----------------- ADMIN DASHBOARD & AUDIT -----------------
    async loadAdminDashboard() {
        try {
            const statsRes = await fetch('/api/admin/stats', { headers: this.getAuthHeaders() });
            const statsData = await statsRes.json();
            const s = statsData.data || {};

            const grid = document.getElementById('admin-metrics-grid');
            grid.innerHTML = `
                <div class="soft-card !p-3 bg-purple-50 border border-purple-200">
                    <p class="text-purple-700 font-bold uppercase text-[10px]">Total Patients</p>
                    <h3 class="text-xl font-black text-purple-950 mt-1">${s.total_patients}</h3>
                </div>
                <div class="soft-card !p-3 bg-teal-50 border border-teal-200">
                    <p class="text-teal-700 font-bold uppercase text-[10px]">Verified Doctors</p>
                    <h3 class="text-xl font-black text-teal-950 mt-1">${s.total_doctors}</h3>
                </div>
                <div class="soft-card !p-3 bg-emerald-50 border border-emerald-200">
                    <p class="text-emerald-700 font-bold uppercase text-[10px]">Health Camps</p>
                    <h3 class="text-xl font-black text-emerald-950 mt-1">${s.total_camps}</h3>
                </div>
                <div class="soft-card !p-3 bg-amber-50 border border-amber-200">
                    <p class="text-amber-700 font-bold uppercase text-[10px]">Avg Trust Score</p>
                    <h3 class="text-xl font-black text-amber-950 mt-1 flex items-center">
                        ★ ${s.average_doctor_rating}
                    </h3>
                </div>
            `;

            // Load audit logs
            const auditRes = await fetch('/api/admin/audit-logs', { headers: this.getAuthHeaders() });
            const auditData = await auditRes.json();
            const logBox = document.getElementById('admin-audit-logs-container');
            logBox.innerHTML = '';
            (auditData.data || []).forEach(l => {
                logBox.innerHTML += `
                    <div class="p-2 bg-gray-50 rounded border border-gray-200">
                        <div class="flex justify-between items-center text-[10px] text-gray-400">
                            <span>${l.action}</span>
                            <span>${l.timestamp}</span>
                        </div>
                        <p class="text-gray-700 mt-0.5">${l.details || l.resource}</p>
                    </div>
                `;
            });
        } catch (e) {
            console.error(e);
        }
    }

    async adminResetDemo() {
        if (!confirm("Reset all databases and tables to initial academic demo seed data?")) return;
        try {
            const res = await fetch('/api/admin/reset-demo', {
                method: 'POST',
                headers: this.getAuthHeaders()
            });
            const data = await res.json();
            if (data.success) {
                alert("Demo database reset successfully.");
                this.loadAdminDashboard();
            }
        } catch (e) {
            alert("Reset error.");
        }
    }
    // ============================================================
    // MOBILE / PWA ENHANCEMENTS
    // ============================================================

    /**
     * Show a non-blocking toast notification.
     */
    showToast(message, type = '', duration = 3500) {
        let container = document.getElementById('toast-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'toast-container';
            document.body.appendChild(container);
        }
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        const iconMap = { success: '✅', error: '❌', warning: '⚠️', '': 'ℹ️' };
        toast.innerHTML = `<span>${iconMap[type] || 'ℹ️'}</span><span>${message}</span>`;
        container.appendChild(toast);
        if (duration > 0) {
            setTimeout(() => {
                toast.style.transition = 'opacity 0.2s ease, transform 0.2s ease';
                toast.style.opacity = '0';
                toast.style.transform = 'translateY(8px)';
                setTimeout(() => toast.remove(), 220);
            }, duration);
        }
        return toast;
    }

    /** Debounce helper for search inputs */
    debounce(fn, delay = 350) {
        let timer;
        return (...args) => { clearTimeout(timer); timer = setTimeout(() => fn.apply(this, args), delay); };
    }

    /** Register service worker & install prompt */
    initPWA() {
        if ('serviceWorker' in navigator) {
            navigator.serviceWorker.register('/static/sw.js', { scope: '/' })
                .then(reg => {
                    reg.addEventListener('updatefound', () => {
                        const nw = reg.installing;
                        nw.addEventListener('statechange', () => {
                            if (nw.state === 'installed' && navigator.serviceWorker.controller) {
                                this.showToast('App updated — reload for latest version', 'success', 6000);
                            }
                        });
                    });
                })
                .catch(err => console.warn('[GramCare] SW:', err));
        }

        this._deferredInstallPrompt = null;
        window.addEventListener('beforeinstallprompt', e => {
            e.preventDefault();
            this._deferredInstallPrompt = e;
            const banner = document.getElementById('install-banner');
            if (banner) banner.classList.remove('hidden');
        });
        window.addEventListener('appinstalled', () => {
            const banner = document.getElementById('install-banner');
            if (banner) banner.classList.add('hidden');
            this._deferredInstallPrompt = null;
            this.showToast('GramCare AI installed!', 'success');
        });

        this._setupNetworkDetection();
    }

    async installPWA() {
        if (!this._deferredInstallPrompt) {
            this.showToast('Use Chrome on Android for one-tap install', 'warning');
            return;
        }
        this._deferredInstallPrompt.prompt();
        const { outcome } = await this._deferredInstallPrompt.userChoice;
        if (outcome === 'accepted') this._deferredInstallPrompt = null;
    }

    _setupNetworkDetection() {
        const banner = document.getElementById('offline-banner');
        window.addEventListener('offline', () => {
            if (banner) banner.classList.remove('hidden');
            this.showToast('You are offline — cached data only', 'warning', 5000);
        });
        window.addEventListener('online', () => {
            if (banner) banner.classList.add('hidden');
            this.showToast('Back online!', 'success', 2500);
        });
        if (!navigator.onLine && banner) banner.classList.remove('hidden');
    }

    toggleRuralModeEnhanced() {
        this.isRuralMode = !this.isRuralMode;
        const btn = document.getElementById('btn-rural-mode');
        const indicator = document.getElementById('network-indicator');
        if (this.isRuralMode) {
            document.body.classList.add('rural-mode-enabled');
            if (indicator) indicator.classList.remove('hidden');
            if (btn) btn.setAttribute('aria-pressed', 'true');
            this.showToast('Rural Mode ON — 2G optimizations active', '', 2500);
        } else {
            document.body.classList.remove('rural-mode-enabled');
            if (indicator) indicator.classList.add('hidden');
            if (btn) btn.setAttribute('aria-pressed', 'false');
            this.showToast('Rural Mode OFF', '', 2000);
        }
    }

    _setupKeyboardNav() {
        document.addEventListener('keydown', e => {
            if ((e.key === 'Enter' || e.key === ' ') && e.target.getAttribute('role') === 'button') {
                e.preventDefault();
                e.target.click();
            }
        });
    }

    /** Lazy-reveal cards as they scroll into view */
    initLazyReveal() {
        if (!('IntersectionObserver' in window)) return;
        if (!document.getElementById('lazy-reveal-style')) {
            const s = document.createElement('style');
            s.id = 'lazy-reveal-style';
            s.textContent = '.soft-card.card-lazy { opacity: 0; transform: translateY(12px); transition: opacity 0.3s ease, transform 0.3s ease; } .soft-card.revealed { opacity: 1 !important; transform: none !important; }';
            document.head.appendChild(s);
        }
        const io = new IntersectionObserver(entries => {
            entries.forEach(entry => {
                if (entry.isIntersecting) { entry.target.classList.add('revealed'); io.unobserve(entry.target); }
            });
        }, { threshold: 0.08, rootMargin: '0px 0px -32px 0px' });
        document.querySelectorAll('.soft-card:not(.revealed)').forEach(card => {
            card.classList.add('card-lazy');
            io.observe(card);
        });
    }
}

// ============================================================
// Global App Instance + Post-Init Mobile Setup
// ============================================================
const app = new GramCareApp();

document.addEventListener('DOMContentLoaded', () => {
    app.initPWA();
    app._setupKeyboardNav();
});

// Patch toggleRuralMode with the enhanced version
GramCareApp.prototype.toggleRuralMode = GramCareApp.prototype.toggleRuralModeEnhanced;
