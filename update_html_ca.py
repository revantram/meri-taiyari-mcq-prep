with open('/data/user/0/com.termux/files/home/.gemini/antigravity-cli/scratch/meri-taiyari-app/assets/index.html', 'r', encoding='utf-8') as f:
    text = f.read()

start_marker = '<section id="tab-ca" class="view-section active">'
end_marker = '</section>'
start_idx = text.find(start_marker)
end_idx = text.find(end_marker, start_idx) + len(end_marker)

new_tab_ca = """<section id="tab-ca" class="view-section active">
      
      <!-- 1. मुख्य पृष्ठ (केवल 2 मुख्य विकल्प: राष्ट्रीय/अंतरराष्ट्रीय और राजस्थान करंट अफेयर, यहाँ कैलेंडर नहीं दिखेगा) -->
      <div id="ca-main-hub">
        
        <!-- Top Priority Card: आज की क्लास • ऑटो-कैच लाइव -->
        <div class="glass-card today-priority-card">
          <div class="glass-card-header">
            <span class="live-badge">
              <span class="pulse-dot"></span>
              ऑटो-कैच लाइव
            </span>
            <button class="btn btn-secondary btn-sm" data-action="sync-today-class">
              🔄 सिंक करें
            </button>
          </div>
          <div class="today-content-box">
            <div class="today-date-text" id="today-class-date">
              20-नवंबर-2026 (आज की क्लास)
            </div>
            <div class="today-subtext" id="today-class-mcq-count">
              ताज़ा अपडेट: 19-नवंबर के 10 MCQ तैयार हैं • 20-नवंबर लाइव क्लास
            </div>
          </div>
          <div class="card-action-row">
            <button class="btn btn-primary btn-full" data-action="open-today-class">
              ⚡ आज के MCQ हल करें
            </button>
          </div>
        </div>

        <div style="margin: 16px 0 10px 0;">
          <h2 style="font-size: 15px; font-weight: 700; color: var(--text-secondary);">करंट अफेयर्स विषय चुनें:</h2>
        </div>

        <!-- विकल्प 1: राष्ट्रीय एवं अंतरराष्ट्रीय करंट अफेयर -->
        <div class="glass-card subject-card" data-action="open-ca-category" data-category="national_ca" style="padding: 20px; cursor: pointer;">
          <div class="glass-card-header" style="margin-bottom: 8px;">
            <div style="display: flex; align-items: center; gap: 14px;">
              <div style="font-size: 34px; line-height: 1;">🇮🇳</div>
              <div>
                <h3 class="card-title" style="font-size: 17px; margin-bottom: 3px;">
                  राष्ट्रीय एवं अंतरराष्ट्रीय करंट अफेयर
                </h3>
                <p style="font-size: 12px; color: var(--text-muted);">
                  तारीख-वार कैलेंडर एवं दैनिक समसामयिकी प्रश्न
                </p>
              </div>
            </div>
            <span class="badge-count" id="badge-nat-ca-count">1101 प्रश्न • 125 तारीखें</span>
          </div>
          <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 10px; font-size: 12px; color: var(--primary); font-weight: 600;">
            <span>कैलेंडर में तारीख चुनें एवं प्रश्न हल करें →</span>
            <span>📅</span>
          </div>
        </div>

        <!-- विकल्प 2: राजस्थान करंट अफेयर -->
        <div class="glass-card subject-card" data-action="open-ca-category" data-category="rajasthan_ca" style="padding: 20px; cursor: pointer;">
          <div class="glass-card-header" style="margin-bottom: 8px;">
            <div style="display: flex; align-items: center; gap: 14px;">
              <div style="font-size: 34px; line-height: 1;">🏰</div>
              <div>
                <h3 class="card-title" style="font-size: 17px; margin-bottom: 3px;">
                  राजस्थान करंट अफेयर
                </h3>
                <p style="font-size: 12px; color: var(--text-muted);">
                  राजस्थान राज्य विशेष दैनिक तारीख-वार समसामयिकी
                </p>
              </div>
            </div>
            <span class="badge-unlinked" id="badge-raj-ca-count">0 प्रश्न • डॉक्यूमेंट लिंक नहीं है</span>
          </div>
          <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 10px; font-size: 12px; color: var(--primary); font-weight: 600;">
            <span>कैलेंडर में तारीख चुनें एवं प्रश्न हल करें →</span>
            <span>📅</span>
          </div>
        </div>

      </div>

      <!-- 2. समर्पित कैलेंडर व तारीख-वार विवरण स्क्रीन (कैटेगरी पर टैप करने के बाद यहाँ दिखाई देगी) -->
      <div id="ca-category-detail" style="display: none;">
        
        <!-- Header with Back Button and Category Title -->
        <div class="glass-card" style="padding: 14px 16px; margin-bottom: 12px;">
          <div class="glass-card-header" style="margin-bottom: 0;">
            <button class="btn btn-secondary btn-sm" data-action="back-to-ca-hub">
              ← वापस (करंट अफेयर)
            </button>
            <button class="btn btn-secondary btn-sm" data-action="sync-current-affairs">
              🔄 सिंक करें
            </button>
          </div>
          <div style="margin-top: 10px;">
            <h2 id="ca-detail-title" style="font-size: 18px; font-weight: 800; line-height: 1.2;">
              राष्ट्रीय एवं अंतरराष्ट्रीय करंट अफेयर
            </h2>
            <p id="ca-detail-subtitle" style="font-size: 12px; color: var(--text-muted); margin-top: 3px;">
              कैलेंडर में किसी भी तारीख पर टैप करें, उस तारीख के प्रश्न एवं नोट्स ठीक नीचे लोड होंगे
            </p>
          </div>
        </div>

        <!-- Interactive Date-Wise Calendar Card -->
        <div class="glass-card calendar-card" id="calendar-section">
          <div class="calendar-header-nav">
            <div class="calendar-month-title">
              <span>📅</span>
              <select class="form-select" id="cal-month-select" data-action="select-cal-month" style="width: auto; padding: 4px 8px; font-weight: 700;">
                <option value="2026-11">नवंबर 2026</option>
                <option value="2026-10">अक्टूबर 2026</option>
                <option value="2026-09">सितंबर 2026</option>
                <option value="2026-08">अगस्त 2026</option>
                <option value="2026-07">जुलाई 2026</option>
              </select>
            </div>
            <div style="display: flex; gap: 6px; align-items: center;">
              <button class="btn btn-secondary btn-sm" data-action="cal-prev-month">◀</button>
              <button class="btn btn-secondary btn-sm" data-action="cal-next-month">▶</button>
            </div>
          </div>

          <!-- Weekdays Row -->
          <div class="calendar-weekdays">
            <div>सोम</div><div>मंगल</div><div>बुध</div><div>गुरु</div><div>शुक्र</div><div>शनि</div><div>रवि</div>
          </div>

          <!-- 7-Column Days Grid -->
          <div class="calendar-grid" id="calendar-days-grid">
            <!-- Populated dynamically by app.js -->
          </div>
        </div>

        <!-- Date-Range Mega Revision Tests -->
        <div class="glass-card mega-revision-card" style="margin-bottom: 16px;">
          <div class="glass-card-header">
            <h3 class="card-title" style="color: #4f46e5;">
              <span>⚡</span> तारीख-रेंज मेगा रिवीज़न टेस्ट
            </h3>
            <span class="badge-count" style="background: rgba(79, 70, 229, 0.15); color: #4f46e5;">साप्ताहिक व मासिक</span>
          </div>
          <div class="mega-btn-group">
            <button class="btn btn-secondary btn-full" data-action="launch-mega-test" data-type="last_7_days">
              ⏱️ पिछले 7 दिन (साप्ताहिक)
            </button>
            <button class="btn btn-primary btn-full" data-action="launch-mega-test" data-type="full_month">
              🏆 पूरा महीना (1 से 20)
            </button>
          </div>
        </div>

        <!-- Date-Specific Content Directly Below Calendar -->
        <div id="ca-date-content-container">
          <!-- Populated when user taps any date in calendar! -->
        </div>

      </div>

    </section>"""

text = text[:start_idx] + new_tab_ca + text[end_idx:]

with open('/data/user/0/com.termux/files/home/.gemini/antigravity-cli/scratch/meri-taiyari-app/assets/index.html', 'w', encoding='utf-8') as f:
    f.write(text)

print("Updated index.html successfully!")
