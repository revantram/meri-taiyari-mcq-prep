with open('/data/user/0/com.termux/files/home/.gemini/antigravity-cli/scratch/meri-taiyari-app/assets/app.js', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Update AppState
state_target = """  // State
  const AppState = {
    theme: 'light',
    currentTab: 'tab-ca',
    streakDays: 6,
    lastPracticeDate: null,
    db: null, // Initialized from localStorage or window.INITIAL_DATA"""

state_replacement = """  // State
  const AppState = {
    theme: 'light',
    currentTab: 'tab-ca',
    streakDays: 6,
    lastPracticeDate: null,
    db: null, // Initialized from localStorage or window.INITIAL_DATA
    
    // Current Affairs Category & Calendar State
    currentCaCategory: 'national_ca', // 'national_ca' or 'rajasthan_ca'
    isInsideCaDetail: false,
    activeCaDateKey: null,"""

if state_target in text:
    text = text.replace(state_target, state_replacement)
    print("AppState updated.")

# 2. Update renderCurrentAffairsTab, renderInteractiveCalendar, handleCalendarDateTap, openCaCategory, backToCaHub
ca_target_block = """  function renderCurrentAffairsTab() {
    setupTodayLiveCard();
    renderCaSubjectCards();
    renderInteractiveCalendar();
  }

  function renderCaSubjectCards() {
    const natCountBadge = document.getElementById('badge-nat-ca-count');
    const rajCountBadge = document.getElementById('badge-raj-ca-count');

    // National CA count
    const natDates = AppState.db.national_ca.dates || {};
    let totalNatQ = 0;
    let totalNatD = Object.keys(natDates).length;
    Object.values(natDates).forEach(d => { totalNatQ += (d.questions || []).length; });

    if (natCountBadge) {
      natCountBadge.textContent = `${totalNatQ} प्रश्न • ${totalNatD} तारीखें`;
    }

    // Rajasthan CA (Unlinked by default)
    const rajData = AppState.db.rajasthan_ca || { linked: false };
    if (rajCountBadge) {
      if (rajData.linked && rajData.dates && Object.keys(rajData.dates).length > 0) {
        let rajQ = 0;
        Object.values(rajData.dates).forEach(d => { rajQ += (d.questions || []).length; });
        rajCountBadge.className = 'badge-count';
        rajCountBadge.textContent = `${rajQ} प्रश्न उपलब्ध`;
      } else {
        rajCountBadge.className = 'badge-unlinked';
        rajCountBadge.textContent = '0 प्रश्न • डॉक्यूमेंट लिंक नहीं है';
      }
    }
  }

  function renderInteractiveCalendar() {
    const gridEl = document.getElementById('calendar-days-grid');
    const monthSelectEl = document.getElementById('cal-month-select');
    if (!gridEl) return;

    if (monthSelectEl) {
      monthSelectEl.value = selectedCaMonth;
    }

    const [yearStr, monthStr] = selectedCaMonth.split('-');
    const year = parseInt(yearStr, 10);
    const month = parseInt(monthStr, 10); // 1-12

    // Get number of days in month
    const daysInMonth = new Date(year, month, 0).getDate();
    // First day of month (0=Sun, 1=Mon, ..., 6=Sat)
    const firstDayIndex = new Date(year, month - 1, 1).getDay();
    // Shift so Mon is index 0
    const startOffset = (firstDayIndex === 0 ? 6 : firstDayIndex - 1);

    const activeDates = AppState.db.national_ca.dates || {};

    let html = '';

    // Empty offset cells
    for (let i = 0; i < startOffset; i++) {
      html += `<div class="calendar-cell" style="opacity: 0.15; cursor: default;"></div>`;
    }

    // Day cells (1 to daysInMonth)
    for (let day = 1; day <= daysInMonth; day++) {
      const dayPad = String(day).padStart(2, '0');
      const dateKey = `${year}-${String(month).padStart(2, '0')}-${dayPad}`;
      const dayData = activeDates[dateKey];
      const qCount = dayData ? dayData.questions.length : 0;
      
      const hasQ = qCount > 0;
      const isToday = (dateKey === '2026-11-20');
      const isSelected = (AppState.activeContext.dateKey === dateKey);

      const cellClasses = [
        'calendar-cell',
        hasQ ? 'has-questions' : '',
        isToday ? 'is-today' : '',
        isSelected ? 'selected' : ''
      ].filter(Boolean).join(' ');

      html += `
        <div class="${cellClasses}" data-action="select-calendar-date" data-date="${dateKey}" data-has-q="${hasQ}">
          <span class="cell-day-num">${day}</span>
          <span class="cell-q-count ${qCount === 0 ? 'zero' : ''}">${qCount > 0 ? qCount + ' Q' : '0'}</span>
        </div>
      `;
    }

    gridEl.innerHTML = html;
  }"""

ca_replacement_block = """  function renderCurrentAffairsTab() {
    setupTodayLiveCard();
    renderCaSubjectCards();
    
    // Main hub vs detail view management
    const hubEl = document.getElementById('ca-main-hub');
    const detailEl = document.getElementById('ca-category-detail');
    
    if (AppState.isInsideCaDetail) {
      if (hubEl) hubEl.style.display = 'none';
      if (detailEl) detailEl.style.display = 'block';
      renderInteractiveCalendar();
      if (AppState.activeCaDateKey) {
        handleCalendarDateTap(AppState.activeCaDateKey);
      }
    } else {
      if (hubEl) hubEl.style.display = 'block';
      if (detailEl) detailEl.style.display = 'none';
    }
  }

  function renderCaSubjectCards() {
    const natCountBadge = document.getElementById('badge-nat-ca-count');
    const rajCountBadge = document.getElementById('badge-raj-ca-count');

    // National CA count
    const natDates = (AppState.db.national_ca && AppState.db.national_ca.dates) || {};
    let totalNatQ = 0;
    let totalNatD = Object.keys(natDates).length;
    Object.values(natDates).forEach(d => { totalNatQ += (d.questions || []).length; });

    if (natCountBadge) {
      natCountBadge.textContent = `${totalNatQ} प्रश्न • ${totalNatD} तारीखें`;
    }

    // Rajasthan CA count
    const rajObj = AppState.db.rajasthan_ca || { linked: false };
    if (rajCountBadge) {
      if (rajObj.linked && rajObj.dates && Object.keys(rajObj.dates).length > 0) {
        let rajQ = 0;
        let rajD = Object.keys(rajObj.dates).length;
        Object.values(rajObj.dates).forEach(d => { rajQ += (d.questions || []).length; });
        rajCountBadge.className = 'badge-count';
        rajCountBadge.textContent = `${rajQ} प्रश्न • ${rajD} तारीखें`;
      } else {
        rajCountBadge.className = 'badge-unlinked';
        rajCountBadge.textContent = '0 प्रश्न • डॉक्यूमेंट लिंक नहीं है';
      }
    }
  }

  function openCaCategory(categoryKey) {
    AppState.currentCaCategory = categoryKey;
    AppState.isInsideCaDetail = true;

    const hubEl = document.getElementById('ca-main-hub');
    const detailEl = document.getElementById('ca-category-detail');
    const titleEl = document.getElementById('ca-detail-title');
    const subTitleEl = document.getElementById('ca-detail-subtitle');

    if (hubEl) hubEl.style.display = 'none';
    if (detailEl) detailEl.style.display = 'block';

    if (categoryKey === 'national_ca') {
      if (titleEl) titleEl.textContent = '🇮🇳 राष्ट्रीय एवं अंतरराष्ट्रीय करंट अफेयर';
      if (subTitleEl) subTitleEl.textContent = 'तारीख पर टैप करें, उस तारीख के प्रश्न एवं समाचार नीचे लोड होंगे';
    } else {
      if (titleEl) titleEl.textContent = '🏰 राजस्थान करंट अफेयर';
      if (subTitleEl) subTitleEl.textContent = 'राजस्थान राज्य विशेष दैनिक समसामयिकी कैलेंडर';
    }

    renderInteractiveCalendar();

    // Determine default date to open
    const targetObj = AppState.db[categoryKey] || {};
    const datesMap = targetObj.dates || {};
    const sortedDates = Object.keys(datesMap).sort();
    
    let defaultDate = '2026-11-20';
    if (datesMap[defaultDate] && datesMap[defaultDate].questions && datesMap[defaultDate].questions.length > 0) {
      defaultDate = '2026-11-20';
    } else if (sortedDates.length > 0) {
      defaultDate = sortedDates[sortedDates.length - 1]; // latest date with content (e.g. 19-Nov)
    }

    handleCalendarDateTap(defaultDate);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  function backToCaHub() {
    AppState.isInsideCaDetail = false;
    AppState.activeCaDateKey = null;

    const hubEl = document.getElementById('ca-main-hub');
    const detailEl = document.getElementById('ca-category-detail');
    const contentBox = document.getElementById('ca-date-content-container');

    if (detailEl) detailEl.style.display = 'none';
    if (hubEl) hubEl.style.display = 'block';
    if (contentBox) contentBox.innerHTML = '';

    renderCaSubjectCards();
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  function renderInteractiveCalendar() {
    const gridEl = document.getElementById('calendar-days-grid');
    const monthSelectEl = document.getElementById('cal-month-select');
    if (!gridEl) return;

    if (monthSelectEl) {
      monthSelectEl.value = selectedCaMonth;
    }

    const [yearStr, monthStr] = selectedCaMonth.split('-');
    const year = parseInt(yearStr, 10);
    const month = parseInt(monthStr, 10);

    const daysInMonth = new Date(year, month, 0).getDate();
    const firstDayIndex = new Date(year, month - 1, 1).getDay();
    const startOffset = (firstDayIndex === 0 ? 6 : firstDayIndex - 1);

    const catKey = AppState.currentCaCategory || 'national_ca';
    const activeDates = (AppState.db[catKey] && AppState.db[catKey].dates) || {};

    let html = '';

    for (let i = 0; i < startOffset; i++) {
      html += `<div class="calendar-cell" style="opacity: 0.15; cursor: default;"></div>`;
    }

    for (let day = 1; day <= daysInMonth; day++) {
      const dayPad = String(day).padStart(2, '0');
      const dateKey = `${year}-${String(month).padStart(2, '0')}-${dayPad}`;
      const dayData = activeDates[dateKey];
      const qCount = dayData ? dayData.questions.length : 0;
      
      const hasQ = qCount > 0;
      const isToday = (dateKey === '2026-11-20');
      const isSelected = (AppState.activeCaDateKey === dateKey);

      const cellClasses = [
        'calendar-cell',
        hasQ ? 'has-questions' : '',
        isToday ? 'is-today' : '',
        isSelected ? 'selected' : ''
      ].filter(Boolean).join(' ');

      html += `
        <div class="${cellClasses}" data-action="select-calendar-date" data-date="${dateKey}" data-has-q="${hasQ}">
          <span class="cell-day-num">${day}</span>
          <span class="cell-q-count ${qCount === 0 ? 'zero' : ''}">${qCount > 0 ? qCount + ' Q' : '0'}</span>
        </div>
      `;
    }

    gridEl.innerHTML = html;
  }"""

if ca_target_block in text:
    text = text.replace(ca_target_block, ca_replacement_block)
    print("Calendar and navigation functions replaced.")
else:
    print("Warning: ca_target_block not found exactly!")

with open('/data/user/0/com.termux/files/home/.gemini/antigravity-cli/scratch/meri-taiyari-app/assets/app.js', 'w', encoding='utf-8') as f:
    f.write(text)
