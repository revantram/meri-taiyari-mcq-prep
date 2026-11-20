/**
 * "मेरी तैयारी (MCQ Prep)" - Core Application Controller
 * High-performance, offline-first, iOS 18 Liquid Glass engine
 */

(function () {
  'use strict';

  // State
  const AppState = {
    theme: 'light',
    currentTab: 'tab-ca',
    streakDays: 6,
    lastPracticeDate: null,
    db: null, // Initialized from localStorage or window.INITIAL_DATA
    
    // Current Affairs Category & Calendar State
    currentCaCategory: 'national_ca', // 'national_ca' or 'rajasthan_ca'
    isInsideCaDetail: false,
    activeCaDateKey: null,
    
    // Quiz Workspace State
    activeContext: {
      type: 'ca', // 'ca', 'gk', 'lsa', 'vault', 'bookmarks', 'mega'
      subCategory: 'national_ca',
      dateKey: null,
      chapterId: null,
      title: '',
      questions: []
    },
    quizView: 'mcq', // 'mcq' or 'oneliner'
    quizMode: 'practice', // 'practice' or 'exam'
    
    // Practice & Exam Tracking
    practiceAnswers: {}, // qId -> selectedOptionIdx
    examAnswers: {}, // qId -> selectedOptionIdx
    examTimeRemaining: 0,
    examTimerId: null,
    
    // Vault & Bookmarks
    wrongVault: {}, // qId -> { questionObj, userWrongIdx, timestamp }
    bookmarks: {}, // qId -> questionObj
    masteryStats: {} // dateKey/chapterId -> { totalAttempted, correct }
  };

  // Persistence Keys
  const STORAGE_KEYS = {
    THEME: 'mt_theme',
    DB: 'mt_database_v2',
    STREAK: 'mt_streak_info',
    VAULT: 'mt_wrong_vault',
    BOOKMARKS: 'mt_bookmarks',
    MASTERY: 'mt_mastery_stats'
  };

  // DOM Elements
  const DOM = {};

  function init() {
    cacheDomElements();
    loadPersistedData();
    applyTheme(AppState.theme);
    bindEvents();
    checkNetworkStatus();
    updateStreakDisplay();
    renderCurrentTab();
    setupTodayLiveCard();
  }

  function cacheDomElements() {
    DOM.headerStreak = document.getElementById('header-streak-badge');
    DOM.headerSyncStatus = document.getElementById('header-sync-status');
    DOM.tabViews = document.querySelectorAll('.view-section');
    DOM.navTabs = document.querySelectorAll('.nav-tab-btn');
    
    // Views
    DOM.viewCa = document.getElementById('view-ca');
    DOM.viewGk = document.getElementById('view-gk');
    DOM.viewLsa = document.getElementById('view-lsa');
    DOM.viewSettings = document.getElementById('view-settings');
    DOM.viewWorkspace = document.getElementById('view-workspace');
    
    // Modals
    DOM.scorecardModal = document.getElementById('scorecard-modal');
    DOM.printModal = document.getElementById('print-modal');
    DOM.streakModal = document.getElementById('streak-modal');
  }

  function loadPersistedData() {
    // Theme
    AppState.theme = localStorage.getItem(STORAGE_KEYS.THEME) || 'light';

    // Streak
    try {
      const streakData = JSON.parse(localStorage.getItem(STORAGE_KEYS.STREAK) || '{}');
      AppState.streakDays = streakData.days || 6;
      AppState.lastPracticeDate = streakData.lastDate || null;
    } catch (e) {
      AppState.streakDays = 6;
    }

    // Vault & Bookmarks
    try {
      AppState.wrongVault = JSON.parse(localStorage.getItem(STORAGE_KEYS.VAULT) || '{}');
      AppState.bookmarks = JSON.parse(localStorage.getItem(STORAGE_KEYS.BOOKMARKS) || '{}');
      AppState.masteryStats = JSON.parse(localStorage.getItem(STORAGE_KEYS.MASTERY) || '{}');
    } catch (e) {
      AppState.wrongVault = {};
      AppState.bookmarks = {};
      AppState.masteryStats = {};
    }

    // Database
    try {
      const savedDbStr = localStorage.getItem(STORAGE_KEYS.DB);
      let needsReset = false;
      const requiredVersion = (window.INITIAL_DATA && window.INITIAL_DATA.config && window.INITIAL_DATA.config.version) || "3.2.0";
      if (savedDbStr) {
        const parsed = JSON.parse(savedDbStr);
        if (!parsed.config || parsed.config.version !== requiredVersion) {
          needsReset = true;
        } else {
          AppState.db = parsed;
        }
      }
      if (!savedDbStr || needsReset) {
        if (window.INITIAL_DATA) {
          AppState.db = JSON.parse(JSON.stringify(window.INITIAL_DATA));
          saveDatabase();
        }
      }

      // Ensure all dates and curated subjects are always present
      if (window.INITIAL_DATA) {
        ['national_ca', 'rajasthan_ca'].forEach(cat => {
          if (window.INITIAL_DATA[cat] && window.INITIAL_DATA[cat].dates) {
            if (!AppState.db[cat]) AppState.db[cat] = JSON.parse(JSON.stringify(window.INITIAL_DATA[cat]));
            if (!AppState.db[cat].dates) AppState.db[cat].dates = {};
            const initDates = window.INITIAL_DATA[cat].dates;
            for (let d in initDates) {
              if (!AppState.db[cat].dates[d] || !AppState.db[cat].dates[d].questions || AppState.db[cat].dates[d].questions.length === 0) {
                AppState.db[cat].dates[d] = JSON.parse(JSON.stringify(initDates[d]));
              }
            }
            if (window.INITIAL_DATA[cat].doc_url && !AppState.db[cat].doc_url) {
              AppState.db[cat].doc_url = window.INITIAL_DATA[cat].doc_url;
              AppState.db[cat].linked = true;
            }
          }
        });
        saveDatabase();
      }
    } catch (e) {
      console.warn("Error loading stored DB, falling back to INITIAL_DATA:", e);
      AppState.db = window.INITIAL_DATA ? JSON.parse(JSON.stringify(window.INITIAL_DATA)) : {};
    }
  }

  function saveDatabase() {
    try {
      localStorage.setItem(STORAGE_KEYS.DB, JSON.stringify(AppState.db));
      updateStorageStatsUI();
    } catch (e) {
      console.warn("Storage quota exceeded or error saving DB:", e);
    }
  }

  function saveVault() {
    localStorage.setItem(STORAGE_KEYS.VAULT, JSON.stringify(AppState.wrongVault));
    updateVaultBadge();
  }

  function saveBookmarks() {
    localStorage.setItem(STORAGE_KEYS.BOOKMARKS, JSON.stringify(AppState.bookmarks));
    updateBookmarksBadge();
  }

  function saveMastery() {
    localStorage.setItem(STORAGE_KEYS.MASTERY, JSON.stringify(AppState.masteryStats));
  }

  function applyTheme(theme) {
    AppState.theme = theme;
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem(STORAGE_KEYS.THEME, theme);
    const themeSelect = document.getElementById('settings-theme-select');
    if (themeSelect) themeSelect.value = theme;
  }

  function checkNetworkStatus() {
    function updateBadge() {
      if (navigator.onLine) {
        DOM.headerSyncStatus.innerHTML = `<span class="sync-dot"></span><span>⚡ ऑनलाइन</span>`;
      } else {
        DOM.headerSyncStatus.innerHTML = `<span class="sync-dot" style="background:#10b981;box-shadow:0 0 6px #10b981;"></span><span>🟢 ऑफलाइन तैयार</span>`;
      }
    }
    window.addEventListener('online', updateBadge);
    window.addEventListener('offline', updateBadge);
    updateBadge();
  }

  function updateStreakDisplay() {
    if (DOM.headerStreak) {
      DOM.headerStreak.innerHTML = `🔥 <span>${AppState.streakDays} दिन स्ट्रीक</span>`;
    }
  }

  function markStreakActivity() {
    const todayStr = new Date().toISOString().split('T')[0];
    if (AppState.lastPracticeDate !== todayStr) {
      AppState.streakDays += 1;
      AppState.lastPracticeDate = todayStr;
      localStorage.setItem(STORAGE_KEYS.STREAK, JSON.stringify({
        days: AppState.streakDays,
        lastDate: AppState.lastPracticeDate
      }));
      updateStreakDisplay();
    }
  }

  // Event Delegation
  function bindEvents() {
    // Navigation Tabs
    DOM.navTabs.forEach(tab => {
      tab.addEventListener('click', function () {
        const targetTab = this.getAttribute('data-tab');
        switchTab(targetTab);
      });
    });

    // Delegated actions
    document.addEventListener('click', function (e) {
      const actionEl = e.target.closest('[data-action]');
      if (!actionEl) return;
      const action = actionEl.getAttribute('data-action');
      handleAction(action, actionEl, e);
    });

    // Theme selector
    const themeSelect = document.getElementById('settings-theme-select');
    if (themeSelect) {
      themeSelect.addEventListener('change', function () {
        applyTheme(this.value);
      });
    }

    // Google Doc Form Submission
    const addDocBtn = document.getElementById('btn-save-doc');
    if (addDocBtn) {
      addDocBtn.addEventListener('click', handleAddOrSyncDoc);
    }
  }

  function switchTab(tabId, pushHistory = true) {
    AppState.currentTab = tabId;
    if (pushHistory && tabId !== 'tab-ca') {
      try { history.pushState({ screen: 'tab', tabId }, ''); } catch(e) {}
    }
    DOM.navTabs.forEach(t => {
      t.classList.toggle('active', t.getAttribute('data-tab') === tabId);
    });

    // Hide workspace view when tab is switched
    if (DOM.viewWorkspace) DOM.viewWorkspace.classList.remove('active');

    DOM.tabViews.forEach(v => {
      v.classList.remove('active');
    });

    const activeView = document.getElementById(tabId);
    if (activeView) activeView.classList.add('active');

    // Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });

    renderCurrentTab();
  }

  function renderCurrentTab() {
    switch (AppState.currentTab) {
      case 'tab-ca':
        renderCurrentAffairsTab();
        break;
      case 'tab-gk':
        renderRajasthanGkTab();
        break;
      case 'tab-lsa':
        renderLsaTab();
        break;
      case 'tab-settings':
        renderSettingsTab();
        break;
    }
  }

  // ================= TAB 1: CURRENT AFFAIRS =================
  let selectedCaMonth = '2026-11'; // default November 2026

  function setupTodayLiveCard() {
    const todayCardDate = document.getElementById('today-class-date');
    const todayCardCount = document.getElementById('today-class-mcq-count');
    if (!todayCardDate) return;

    const todayDateKey = '2026-11-20'; // Reference time today
    const novDates = AppState.db.national_ca.dates || {};
    const todayObj = novDates[todayDateKey];
    
    // Check if 20-Nov has questions or show latest class
    if (todayObj && todayObj.questions && todayObj.questions.length > 0) {
      todayCardDate.textContent = '20-नवंबर-2026 (आज की क्लास)';
      todayCardCount.textContent = `⚡ ${todayObj.questions.length} प्रश्न उपलब्ध • 1-टैप में अभ्यास करें`;
    } else {
      // Find latest date with questions (e.g. 19-Nov)
      const sortedKeys = Object.keys(novDates).sort();
      const latestKey = sortedKeys.length > 0 ? sortedKeys[sortedKeys.length - 1] : todayDateKey;
      const latestObj = novDates[latestKey];
      const count = latestObj ? latestObj.questions.length : 0;
      todayCardDate.textContent = '20-नवंबर-2026 (आज की लाइव क्लास)';
      todayCardCount.textContent = `ताज़ा अपडेट: 19-नवंबर के ${count} MCQ तैयार हैं • 20-नवंबर नोट्स सिंक करें`;
    }
  }

  function renderCurrentAffairsTab() {
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

  function openCaCategory(categoryKey, pushHistory = true) {
    AppState.currentCaCategory = categoryKey;
    AppState.isInsideCaDetail = true;
    if (pushHistory) {
      try { history.pushState({ screen: 'ca_detail', categoryKey }, ''); } catch(e) {}
    }

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
  }

  // ================= TAB 2: RAJASTHAN GK =================
  let currentGkSubcategory = 'geography';

  function renderRajasthanGkTab() {
    const listContainer = document.getElementById('gk-chapters-list');
    const emptyState = document.getElementById('gk-empty-state');
    if (!listContainer) return;

    const catData = AppState.db.rajasthan_gk[currentGkSubcategory];
    const isLinked = catData && catData.linked && catData.chapters && catData.chapters.length > 0;

    if (!isLinked) {
      listContainer.style.display = 'none';
      emptyState.style.display = 'block';
      const emptyCatName = document.getElementById('gk-empty-category-name');
      if (emptyCatName) emptyCatName.textContent = catData ? catData.title : 'राजस्थान सामान्य ज्ञान';
    } else {
      emptyState.style.display = 'none';
      listContainer.style.display = 'block';
      
      let html = '';
      catData.chapters.forEach((ch, idx) => {
        const mastery = AppState.masteryStats[ch.id] || { total: ch.questions.length, correct: 0 };
        const percent = ch.questions.length > 0 ? Math.round((mastery.correct / ch.questions.length) * 100) : 0;

        html += `
          <div class="chapter-item" data-action="open-gk-chapter" data-subcat="${currentGkSubcategory}" data-chapter-id="${ch.id}">
            <div class="chapter-info">
              <h3>${ch.title}</h3>
              <p>${ch.questions.length} प्रश्न उपलब्ध • अध्याय-वार अभ्यास</p>
            </div>
            <div class="mastery-meter-container">
              <div class="meter-bar-bg">
                <div class="meter-bar-fill" style="width: ${percent}%;"></div>
              </div>
              <span class="meter-text">${percent}%</span>
            </div>
          </div>
        `;
      });
      listContainer.innerHTML = html;
    }
  }

  // ================= TAB 3: LSA VETERINARY SUBJECTS =================
  function renderLsaTab() {
    const container = document.getElementById('lsa-subjects-container');
    if (!container) return;

    const subjects = AppState.db.lsa_subjects || {};
    let html = '';

    Object.values(subjects).forEach(subj => {
      const isLinked = subj.linked && subj.chapters && subj.chapters.length > 0;
      let totalQ = 0;
      if (isLinked) {
        subj.chapters.forEach(c => totalQ += c.questions.length);
      }

      html += `
        <div class="glass-card subject-card" data-action="open-lsa-subject" data-subject-id="${subj.id}">
          <div class="glass-card-header">
            <h3 class="card-title">${subj.title}</h3>
            ${isLinked 
              ? `<span class="badge-count">${totalQ} प्रश्न उपलब्ध</span>` 
              : `<span class="badge-unlinked">0 प्रश्न • डॉक्यूमेंट लिंक नहीं है</span>`
            }
          </div>
          <div class="subject-card-meta">
            ${isLinked 
              ? `<span>अध्याय संख्या: ${subj.chapters.length}</span> • <span>मास्टरी मीटर सक्रिय</span>`
              : `<span>डॉक्यूमेंट लिंक करने पर तुरंत अध्याय व MCQ तैयार होंगे</span>`
            }
          </div>
        </div>
      `;
    });

    container.innerHTML = html;
  }

  // ================= TAB 4: SETTINGS =================
  function renderSettingsTab() {
    updateVaultBadge();
    updateBookmarksBadge();
    updateStorageStatsUI();
    renderLinkedDocsList();
  }

  function updateVaultBadge() {
    const badge = document.getElementById('vault-count-badge');
    if (badge) {
      const count = Object.keys(AppState.wrongVault).length;
      badge.textContent = `${count} प्रश्न`;
    }
  }

  function updateBookmarksBadge() {
    const badge = document.getElementById('bookmarks-count-badge');
    if (badge) {
      const count = Object.keys(AppState.bookmarks).length;
      badge.textContent = `${count} प्रश्न`;
    }
  }

  function updateStorageStatsUI() {
    const qCountEl = document.getElementById('stat-total-mcqs');
    const storageSizeEl = document.getElementById('stat-storage-size');

    // Count all MCQs
    let total = 0;
    if (AppState.db.national_ca && AppState.db.national_ca.dates) {
      Object.values(AppState.db.national_ca.dates).forEach(d => total += d.questions.length);
    }
    if (AppState.db.rajasthan_ca && AppState.db.rajasthan_ca.dates) {
      Object.values(AppState.db.rajasthan_ca.dates).forEach(d => total += d.questions.length);
    }
    ['geography', 'art_culture', 'history'].forEach(k => {
      const cat = AppState.db.rajasthan_gk[k];
      if (cat && cat.chapters) cat.chapters.forEach(c => total += c.questions.length);
    });
    if (AppState.db.lsa_subjects) {
      Object.values(AppState.db.lsa_subjects).forEach(s => {
        if (s.chapters) s.chapters.forEach(c => total += c.questions.length);
      });
    }

    if (qCountEl) qCountEl.textContent = `${total} MCQs`;

    // Estimate localStorage usage
    let bytes = 0;
    for (let key in localStorage) {
      if (localStorage.hasOwnProperty(key)) {
        bytes += (localStorage[key].length + key.length) * 2;
      }
    }
    const mb = (bytes / (1024 * 1024)).toFixed(2);
    if (storageSizeEl) storageSizeEl.textContent = `${mb} MB / 100% ऑफलाइन कैश`;
  }

  function renderLinkedDocsList() {
    const listEl = document.getElementById('linked-docs-tbody');
    if (!listEl) return;

    const rows = [];

    // National CA
    const nat = AppState.db.national_ca;
    let natQ = 0;
    if (nat.dates) Object.values(nat.dates).forEach(d => natQ += d.questions.length);
    rows.push({
      target: 'राष्ट्रीय अंतरराष्ट्रीय करंट अफेयर',
      url: nat.doc_url || 'डॉक्यूमेंट लिंक है',
      questions: `${natQ} MCQs`,
      status: 'सक्रिय (Pre-linked)',
      key: 'national_ca'
    });

    // Rajasthan CA
    const raj = AppState.db.rajasthan_ca;
    if (raj && raj.linked) {
      let rajQ = 0;
      if (raj.dates) Object.values(raj.dates).forEach(d => rajQ += d.questions.length);
      rows.push({
        target: 'राजस्थान करंट अफेयर',
        url: raj.doc_url || 'लिंक्ड',
        questions: `${rajQ} MCQs`,
        status: 'सक्रिय',
        key: 'rajasthan_ca'
      });
    }

    // GK
    ['geography', 'art_culture', 'history'].forEach(k => {
      const g = AppState.db.rajasthan_gk[k];
      if (g && g.linked) {
        let q = 0;
        g.chapters.forEach(c => q += c.questions.length);
        rows.push({
          target: g.title,
          url: g.doc_url || 'लिंक्ड',
          questions: `${q} MCQs`,
          status: 'सक्रिय',
          key: `gk_${k}`
        });
      }
    });

    // LSA
    if (AppState.db.lsa_subjects) {
      Object.values(AppState.db.lsa_subjects).forEach(s => {
        if (s.linked) {
          let q = 0;
          s.chapters.forEach(c => q += c.questions.length);
          rows.push({
            target: s.title,
            url: s.doc_url || 'लिंक्ड',
            questions: `${q} MCQs`,
            status: 'सक्रिय',
            key: `lsa_${s.id}`
          });
        }
      });
    }

    let html = '';
    rows.forEach(r => {
      html += `
        <tr>
          <td style="padding: 10px 8px; border-bottom: 1px solid var(--glass-border-subtle); font-weight: 600;">${r.target}</td>
          <td style="padding: 10px 8px; border-bottom: 1px solid var(--glass-border-subtle); font-size: 12px; color: var(--text-muted);">${r.questions}</td>
          <td style="padding: 10px 8px; border-bottom: 1px solid var(--glass-border-subtle); font-size: 12px; color: var(--success);">${r.status}</td>
        </tr>
      `;
    });

    listEl.innerHTML = html;
  }

  // ================= QUIZ WORKSPACE CONTROLLER =================
  function openQuizWorkspace(context, pushHistory = true) {
    AppState.activeContext = context;
    AppState.practiceAnswers = {};
    AppState.examAnswers = {};
    clearInterval(AppState.examTimerId);
    if (pushHistory) {
      try { history.pushState({ screen: 'workspace' }, ''); } catch(e) {}
    }

    // Hide other views and show workspace
    DOM.tabViews.forEach(v => v.classList.remove('active'));
    DOM.viewWorkspace.classList.add('active');
    window.scrollTo({ top: 0, behavior: 'smooth' });

    // Update Workspace Headers
    document.getElementById('workspace-title').textContent = context.title;
    document.getElementById('workspace-subtitle').textContent = `${context.questions.length} प्रश्न उपलब्ध • RPSC / RSSB एग्जामिनर स्तर`;

    // Reset controls
    setQuizView('mcq');
    setQuizMode('practice');

    renderQuizContent();
  }

  function setQuizView(view) {
    AppState.quizView = view;
    document.querySelectorAll('[data-action="switch-quiz-view"]').forEach(btn => {
      btn.classList.toggle('active', btn.getAttribute('data-view') === view);
    });
    renderQuizContent();
  }

  function setQuizMode(mode) {
    AppState.quizMode = mode;
    document.querySelectorAll('[data-action="switch-quiz-mode"]').forEach(btn => {
      btn.classList.toggle('active', btn.getAttribute('data-mode') === mode);
    });

    const timerBar = document.getElementById('exam-timer-bar');
    const examPalette = document.getElementById('exam-palette-container');
    const examSubmitBtn = document.getElementById('btn-submit-exam');

    if (mode === 'exam') {
      timerBar.style.display = 'flex';
      examPalette.style.display = 'block';
      examSubmitBtn.style.display = 'flex';
      startExamTimer();
    } else {
      timerBar.style.display = 'none';
      examPalette.style.display = 'none';
      examSubmitBtn.style.display = 'none';
      clearInterval(AppState.examTimerId);
    }

    renderQuizContent();
  }

  function startExamTimer() {
    clearInterval(AppState.examTimerId);
    const totalQ = AppState.activeContext.questions.length;
    // 60 seconds per question
    AppState.examTimeRemaining = totalQ * 60;
    updateTimerDisplay();

    AppState.examTimerId = setInterval(() => {
      AppState.examTimeRemaining--;
      updateTimerDisplay();
      if (AppState.examTimeRemaining <= 0) {
        clearInterval(AppState.examTimerId);
        submitExam();
      }
    }, 1000);
  }

  function updateTimerDisplay() {
    const timerEl = document.getElementById('exam-timer-text');
    if (!timerEl) return;
    const mins = Math.floor(AppState.examTimeRemaining / 60);
    const secs = AppState.examTimeRemaining % 60;
    timerEl.textContent = `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
  }

  function renderQuizContent() {
    const mcqContainer = document.getElementById('workspace-mcq-list');
    const onelinerContainer = document.getElementById('workspace-oneliner-list');

    if (AppState.quizView === 'oneliner') {
      mcqContainer.style.display = 'none';
      onelinerContainer.style.display = 'block';
      renderOneLiners(onelinerContainer);
    } else {
      onelinerContainer.style.display = 'none';
      mcqContainer.style.display = 'block';
      renderMcqs(mcqContainer);
    }

    if (AppState.quizMode === 'exam') {
      renderExamPalette();
    }
  }

  function cleanNoteText(text) {
    if (!text) return '';
    let cleaned = String(text);
    cleaned = cleaned.replace(/✅\s*\*?सही उत्तर:\*?[^\n]*\n*/gi, '');
    cleaned = cleaned.replace(/📌\s*\*?परीक्षा संदर्भ:\*?[^\n]*\n*/gi, '');
    cleaned = cleaned.replace(/📖\s*\*?(?:विस्तृत\s*)?एग्जामिनर व्याख्या(?:\s*\([^)]*\))?:\*?[^\n]*\n*/gi, '');
    cleaned = cleaned.replace(/💡\s*\*?याद रखने की ट्रिक:[^\n]*\n*/gi, '');
    cleaned = cleaned.replace(/✨\s*\*?💡[^\n]*\n*/gi, '');
    cleaned = cleaned.replace(/•\s*यह प्रश्न RPSC\s*\/\s*RSSB[^\n]*\n*/gi, '');
    cleaned = cleaned.replace(/^नोट:\s*/gi, '');
    cleaned = cleaned.trim();
    return cleaned;
  }

  function renderMcqs(container) {
    const questions = AppState.activeContext.questions;
    if (!questions || questions.length === 0) {
      container.innerHTML = `
        <div class="empty-state-box">
          <span class="empty-icon">📝</span>
          <h4>कोई प्रश्न नहीं मिला</h4>
          <p>इस श्रेणी या तारीख के लिए अभी प्रश्न उपलब्ध नहीं हैं।</p>
        </div>
      `;
      return;
    }

    let html = '';
    const optionLabels = ['(A)', '(B)', '(C)', '(D)'];

    questions.forEach((q, idx) => {
      const qNum = idx + 1;
      const isBookmarked = !!AppState.bookmarks[q.id];
      const isPractice = (AppState.quizMode === 'practice');
      const selectedIdx = isPractice ? AppState.practiceAnswers[q.id] : AppState.examAnswers[q.id];
      const hasAnswered = (selectedIdx !== undefined);

      html += `
        <div class="mcq-card" id="card-${q.id}">
          <div class="mcq-q-header">
            <span class="mcq-num-badge">प्रश्न ${qNum} / ${questions.length}</span>
            <button class="mcq-bookmark-btn ${isBookmarked ? 'bookmarked' : ''}" 
                    data-action="toggle-bookmark" 
                    data-qid="${q.id}" 
                    title="बुकमार्क करें">
              ${isBookmarked ? '★' : '☆'}
            </button>
          </div>

          <div class="mcq-question-text">${q.question}</div>

          <div class="mcq-options-list">
      `;

      q.options.forEach((opt, optIdx) => {
        let optClass = 'option-item';

        if (isPractice && hasAnswered) {
          if (optIdx === q.correct_index) {
            optClass += ' correct';
          } else if (optIdx === selectedIdx) {
            optClass += ' incorrect';
          }
        } else if (!isPractice && selectedIdx === optIdx) {
          optClass += ' selected-exam';
        }

        html += `
          <div class="${optClass}" 
               data-action="select-option" 
               data-qid="${q.id}" 
               data-opt-idx="${optIdx}" 
               data-q-idx="${idx}">
            <div class="option-label-circle">${optionLabels[optIdx]}</div>
            <div class="option-text">${opt}</div>
          </div>
        `;
      });

      html += `</div>`; // .mcq-options-list

      // In practice mode, reveal note once answered
      if (isPractice && hasAnswered) {
        const noteText = cleanNoteText(q.note || q.explanation);
        if (noteText) {
          html += `
            <div class="note-box">
              <strong>नोट:</strong> ${formatMarkdown(noteText)}
            </div>
          `;
        }
      }

      html += `</div>`; // .mcq-card
    });

    container.innerHTML = html;
  }

  function renderOneLiners(container) {
    const questions = AppState.activeContext.questions;
    let html = '';
    questions.forEach((q, idx) => {
      const noteText = cleanNoteText(q.note || q.explanation);
      html += `
        <div class="oneliner-card">
          <span class="oneliner-badge">रिवीज़न बिंदु #${idx + 1}</span>
          <div class="oneliner-text">${formatMarkdown(q.one_liner || q.question)}</div>
          ${noteText ? `
            <div class="note-box" style="margin-top: 8px; font-size: 12.5px; padding: 8px 12px;">
              <strong>नोट:</strong> ${formatMarkdown(noteText)}
            </div>
          ` : ''}
        </div>
      `;
    });
    container.innerHTML = html;
  }

  function renderExamPalette() {
    const paletteEl = document.getElementById('exam-palette-grid');
    if (!paletteEl) return;
    const questions = AppState.activeContext.questions;
    let html = '';

    questions.forEach((q, idx) => {
      const isAnswered = (AppState.examAnswers[q.id] !== undefined);
      html += `
        <div class="palette-item ${isAnswered ? 'answered' : ''}" 
             data-action="scroll-to-question" 
             data-qid="${q.id}">
          ${idx + 1}
        </div>
      `;
    });

    paletteEl.innerHTML = html;
  }

  function updateCardUI(q, qId, optIdx, isPractice) {
    const cards = document.querySelectorAll(`[id="card-${qId}"]`);
    cards.forEach(card => {
      const optionEls = card.querySelectorAll('.option-item');
      optionEls.forEach((optEl, idx) => {
        if (isPractice) {
          if (idx === q.correct_index) {
            optEl.classList.add('correct');
          } else if (idx === optIdx) {
            optEl.classList.add('incorrect');
          }
        } else {
          optEl.classList.toggle('selected-exam', idx === optIdx);
        }
      });

      if (isPractice) {
        let noteBox = card.querySelector('.note-box');
        if (!noteBox) {
          const noteText = cleanNoteText(q.note || q.explanation);
          if (noteText) {
            noteBox = document.createElement('div');
            noteBox.className = 'note-box';
            noteBox.innerHTML = `<strong>नोट:</strong> ${formatMarkdown(noteText)}`;
            card.appendChild(noteBox);
          }
        }
      }
    });
  }

  function handleOptionSelection(qId, optIdx, qIdx) {
    let q = AppState.activeContext && AppState.activeContext.questions && AppState.activeContext.questions.find(item => item.id === qId);
    if (!q && AppState.activeCaDateKey) {
      const catKey = AppState.currentCaCategory || 'national_ca';
      const targetObj = AppState.db[catKey] || {};
      const datesMap = targetObj.dates || {};
      const dayData = datesMap[AppState.activeCaDateKey];
      if (dayData && dayData.questions) {
        q = dayData.questions.find(item => item.id === qId);
      }
    }
    if (!q) return;

    markStreakActivity();

    if (AppState.quizMode === 'practice') {
      // In practice mode, allow clicking once or changing
      if (AppState.practiceAnswers[qId] !== undefined) return; // locked after first answer
      AppState.practiceAnswers[qId] = optIdx;

      const isCorrect = (optIdx === q.correct_index);

      // Wrong Vault logic
      if (!isCorrect) {
        AppState.wrongVault[q.id] = {
          questionObj: q,
          userWrongIdx: optIdx,
          timestamp: Date.now()
        };
        saveVault();
      } else {
        // If answered correctly and was in wrong vault (retest), remove it!
        if (AppState.wrongVault[q.id]) {
          delete AppState.wrongVault[q.id];
          saveVault();
        }
      }

      // Update Mastery stats
      const masterKey = (AppState.activeContext && AppState.activeContext.dateKey) || AppState.activeCaDateKey || 'general';
      if (!AppState.masteryStats[masterKey]) {
        AppState.masteryStats[masterKey] = { total: 0, correct: 0 };
      }
      AppState.masteryStats[masterKey].total++;
      if (isCorrect) AppState.masteryStats[masterKey].correct++;
      saveMastery();

      // Instant visual feedback on the card
      updateCardUI(q, qId, optIdx, true);

      if (DOM.viewWorkspace && DOM.viewWorkspace.classList.contains('active')) {
        renderQuizContent();
      }
    } else {
      // Exam mode
      AppState.examAnswers[qId] = optIdx;
      updateCardUI(q, qId, optIdx, false);
      if (DOM.viewWorkspace && DOM.viewWorkspace.classList.contains('active')) {
        renderExamPalette();
      }
    }
  }

  function submitExam() {
    clearInterval(AppState.examTimerId);
    const questions = AppState.activeContext.questions;
    let correctCount = 0;
    let incorrectCount = 0;
    let unattemptedCount = 0;

    questions.forEach(q => {
      const ans = AppState.examAnswers[q.id];
      if (ans === undefined) {
        unattemptedCount++;
      } else if (ans === q.correct_index) {
        correctCount++;
        // If in wrong vault and answered correctly in exam, remove from vault!
        if (AppState.wrongVault[q.id]) {
          delete AppState.wrongVault[q.id];
        }
      } else {
        incorrectCount++;
        // Save to wrong answer vault
        AppState.wrongVault[q.id] = {
          questionObj: q,
          userWrongIdx: ans,
          timestamp: Date.now()
        };
      }
    });

    saveVault();

    // RPSC / RSSB Standard Marking: +2 for correct, -0.67 for incorrect (1/3 negative)
    const rawScore = (correctCount * 2.0) - (incorrectCount * 0.67);
    const maxScore = questions.length * 2.0;
    const accuracy = (correctCount + incorrectCount > 0)
      ? Math.round((correctCount / (correctCount + incorrectCount)) * 100)
      : 0;

    // Show Scorecard Modal
    document.getElementById('score-total-val').textContent = `${rawScore.toFixed(2)} / ${maxScore}`;
    document.getElementById('score-correct-val').textContent = correctCount;
    document.getElementById('score-wrong-val').textContent = incorrectCount;
    document.getElementById('score-unattempted-val').textContent = unattemptedCount;
    document.getElementById('score-accuracy-val').textContent = `${accuracy}%`;

    DOM.scorecardModal.classList.add('active');

    // Switch to practice view so user can review every answer with AI explanations
    setQuizMode('practice');
    AppState.practiceAnswers = Object.assign({}, AppState.examAnswers);
    renderQuizContent();
  }

  // ================= ACTION HANDLER =================
  function handleAction(action, el, e) {
    switch (action) {
      case 'open-ca-category': {
        const cat = el.getAttribute('data-category');
        openCaCategory(cat);
        break;
      }
      case 'back-to-ca-hub': {
        backToCaHub();
        break;
      }
      case 'select-calendar-date': {
        const dateKey = el.getAttribute('data-date');
        handleCalendarDateTap(dateKey);
        break;
      }
      case 'switch-date-view': {
        const view = el.getAttribute('data-view');
        AppState.quizView = view;
        if (AppState.activeCaDateKey) handleCalendarDateTap(AppState.activeCaDateKey);
        break;
      }
      case 'switch-date-mode': {
        const mode = el.getAttribute('data-mode');
        AppState.quizMode = mode;
        if (AppState.activeCaDateKey) handleCalendarDateTap(AppState.activeCaDateKey);
        break;
      }
      case 'open-full-workspace': {
        if (AppState.activeContext && AppState.activeContext.questions) {
          openQuizWorkspace(AppState.activeContext);
        }
        break;
      }
      case 'open-today-class': {
        handleOpenTodayClass();
        break;
      }
      case 'sync-today-class': {
        handleIncrementalSync('national_ca');
        break;
      }
      case 'sync-current-affairs': {
        handleIncrementalSync(AppState.currentCaCategory || 'national_ca');
        break;
      }
      case 'open-national-ca-calendar': {
        // Scroll down to interactive calendar
        document.getElementById('calendar-section').scrollIntoView({ behavior: 'smooth' });
        break;
      }
      case 'open-raj-ca': {
        const raj = AppState.db.rajasthan_ca;
        if (raj && raj.linked && raj.dates && Object.keys(raj.dates).length > 0) {
          // Open Rajasthan CA
          alert('राजस्थान करंट अफेयर सक्रिय है।');
        } else {
          // Prompt to link in Settings
          promptLinkDocument('rajasthan_ca');
        }
        break;
      }
      case 'select-cal-month': {
        selectedCaMonth = el.value;
        renderInteractiveCalendar();
        break;
      }
      case 'cal-prev-month': {
        navigateCalMonth(-1);
        break;
      }
      case 'cal-next-month': {
        navigateCalMonth(1);
        break;
      }
      case 'launch-mega-test': {
        const type = el.getAttribute('data-type');
        launchMegaRevisionTest(type);
        break;
      }
      case 'switch-gk-subtab': {
        document.querySelectorAll('[data-action="switch-gk-subtab"]').forEach(b => b.classList.remove('active'));
        el.classList.add('active');
        currentGkSubcategory = el.getAttribute('data-subcat');
        renderRajasthanGkTab();
        break;
      }
      case 'open-gk-chapter': {
        const subcat = el.getAttribute('data-subcat');
        const chId = el.getAttribute('data-chapter-id');
        openGkChapterWorkspace(subcat, chId);
        break;
      }
      case 'open-lsa-subject': {
        const subjId = el.getAttribute('data-subject-id');
        openLsaSubjectWorkspace(subjId);
        break;
      }
      case 'prompt-add-doc': {
        const target = el.getAttribute('data-target') || 'geography';
        promptLinkDocument(target);
        break;
      }
      case 'close-workspace': {
        DOM.viewWorkspace.classList.remove('active');
        switchTab(AppState.currentTab);
        break;
      }
      case 'switch-quiz-view': {
        const view = el.getAttribute('data-view');
        setQuizView(view);
        break;
      }
      case 'switch-quiz-mode': {
        const mode = el.getAttribute('data-mode');
        setQuizMode(mode);
        break;
      }
      case 'select-option': {
        const qId = el.getAttribute('data-qid');
        const optIdx = parseInt(el.getAttribute('data-opt-idx'), 10);
        const qIdx = parseInt(el.getAttribute('data-q-idx'), 10);
        handleOptionSelection(qId, optIdx, qIdx);
        break;
      }
      case 'toggle-bookmark': {
        const qId = el.getAttribute('data-qid');
        toggleBookmark(qId);
        break;
      }
      case 'scroll-to-question': {
        const qId = el.getAttribute('data-qid');
        const targetCard = document.getElementById(`card-${qId}`);
        if (targetCard) targetCard.scrollIntoView({ behavior: 'smooth', block: 'center' });
        break;
      }
      case 'submit-exam': {
        if (confirm('क्या आप परीक्षा सबमिट करके स्कोरकार्ड देखना चाहते हैं?')) {
          submitExam();
        }
        break;
      }
      case 'close-scorecard-modal': {
        DOM.scorecardModal.classList.remove('active');
        break;
      }
      case 'open-print-modal': {
        DOM.printModal.classList.add('active');
        break;
      }
      case 'close-print-modal': {
        DOM.printModal.classList.remove('active');
        break;
      }
      case 'trigger-print': {
        const layout = el.getAttribute('data-layout'); // '1-col' or '2-col'
        triggerPrint(layout);
        break;
      }
      case 'open-wrong-vault': {
        openVaultWorkspace();
        break;
      }
      case 'open-bookmarks': {
        openBookmarksWorkspace();
        break;
      }
      case 'check-in-app-update': {
        runInAppUpdateSimulation();
        break;
      }
      case 'export-backup-json': {
        exportBackupJson();
        break;
      }
      case 'import-backup-json': {
        document.getElementById('import-file-input').click();
        break;
      }
      case 'clear-cache': {
        if (confirm('क्या आप स्थानीय कैश और मास्टरी डेटा रीसेट करना चाहते हैं?')) {
          localStorage.clear();
          location.reload();
        }
        break;
      }
      case 'open-streak-info': {
        DOM.streakModal.classList.add('active');
        break;
      }
      case 'close-streak-modal': {
        DOM.streakModal.classList.remove('active');
        break;
      }
    }
  }

  function handleCalendarDateTap(dateKey) {
    AppState.activeCaDateKey = dateKey;
    renderInteractiveCalendar(); // refresh highlight on calendar cell

    const container = document.getElementById('ca-date-content-container');
    if (!container) return;

    const catKey = AppState.currentCaCategory || 'national_ca';
    const targetObj = AppState.db[catKey] || {};
    const datesMap = targetObj.dates || {};
    const dayData = datesMap[dateKey];
    const isLinked = targetObj.linked;

    if (!dayData || !dayData.questions || dayData.questions.length === 0) {
      container.innerHTML = `
        <div class="glass-card empty-state-box" style="margin-top: 14px; animation: fadeInView 0.25s ease-out;">
          <span class="empty-icon">📅</span>
          <h4>तारीख ${dateKey} के लिए अभी कोई प्रश्न नहीं मिला</h4>
          <p style="font-size: 13px; color: var(--text-secondary); margin-bottom: 14px;">
            ${isLinked 
              ? 'इस तारीख के नोट्स गूगल डॉक्स में जोड़े जाने पर "🔄 सिंक करें" बटन से तुरंत आ जाएंगे।' 
              : 'इस विषय के लिए अभी गूगल डॉक लिंक नहीं है। सेटिंग्स में जाकर लिंक जोड़ें।'}
          </p>
          ${isLinked 
            ? `<button class="btn btn-secondary" data-action="sync-current-affairs">🔄 सिंक करें</button>` 
            : `<button class="btn btn-primary" data-action="prompt-add-doc" data-target="${catKey}">सेटिंग्स में डॉक्यूमेंट जोड़ें →</button>`}
        </div>
      `;
      return;
    }

    // Set activeContext so options selection, bookmarks, and vault work seamlessly
    AppState.activeContext = {
      type: 'ca',
      subCategory: catKey,
      dateKey: dateKey,
      title: `📅 ${dayData.display_date} • ${targetObj.title || 'करंट अफेयर'}`,
      questions: dayData.questions
    };

    renderBelowCalendarQuiz(container, dayData);
  }

  function renderBelowCalendarQuiz(container, dayData) {
    const questions = dayData.questions;
    const isOneLiner = (AppState.quizView === 'oneliner');
    const isExam = (AppState.quizMode === 'exam');

    let html = `
      <div class="glass-card" style="margin-top: 14px; animation: fadeInView 0.25s ease-out;">
        <div class="glass-card-header" style="flex-wrap: wrap; gap: 8px;">
          <div>
            <h3 style="font-size: 16px; font-weight: 800; color: var(--text-main);">
              📅 ${dayData.display_date} के समाचार एवं प्रश्न
            </h3>
            <p style="font-size: 12px; color: var(--text-muted); margin-top: 2px;">
              कुल ${questions.length} प्रश्न एवं रिवीज़न बिंदु • RPSC / RSSB एग्जामिनर स्तर
            </p>
          </div>
          <button class="btn btn-secondary btn-sm" data-action="open-full-workspace">
            🖨️ A4 PDF एक्सपोर्ट / फुल स्क्रीन
          </button>
        </div>

        <!-- View & Mode Toggles -->
        <div class="view-mode-toggles" style="margin: 14px 0 16px 0;">
          <div class="segmented-control">
            <button class="segment-btn ${!isOneLiner ? 'active' : ''}" data-action="switch-date-view" data-view="mcq">
              📝 MCQ अभ्यास
            </button>
            <button class="segment-btn ${isOneLiner ? 'active' : ''}" data-action="switch-date-view" data-view="oneliner">
              📖 दैनिक समाचार व नोट्स
            </button>
          </div>

          <div class="segmented-control">
            <button class="segment-btn ${!isExam ? 'active' : ''}" data-action="switch-date-mode" data-mode="practice">
              ⚡ प्रैक्टिस मोड
            </button>
            <button class="segment-btn ${isExam ? 'active' : ''}" data-action="switch-date-mode" data-mode="exam">
              ⏱️ एग्जाम मोड (-0.67)
            </button>
          </div>
        </div>
    `;

    if (isExam) {
      html += `
        <div class="exam-timer-bar" style="margin-bottom: 14px;">
          <div class="timer-display">
            <span>⏳</span>
            <span id="exam-timer-text">00:00</span>
          </div>
          <div class="marking-info-tag">
            +2 सही | -0.67 निगेटिव (1/3)
          </div>
        </div>
      `;
    }

    html += `<div id="ca-date-items-wrapper">`;

    if (isOneLiner) {
      // One-liner / Daily News view
      questions.forEach((q, idx) => {
        const noteText = cleanNoteText(q.note || q.explanation);
        html += `
          <div class="oneliner-card">
            <span class="oneliner-badge">समाचार व रिवीज़न बिंदु #${idx + 1}</span>
            <div class="oneliner-text">${formatMarkdown(q.one_liner || q.question)}</div>
            ${noteText ? `
              <div class="note-box" style="margin-top: 8px; font-size: 12.5px; padding: 8px 12px;">
                <strong>नोट:</strong> ${formatMarkdown(noteText)}
              </div>
            ` : ''}
          </div>
        `;
      });
    } else {
      // MCQ Quiz view
      const optionLabels = ['(A)', '(B)', '(C)', '(D)'];
      questions.forEach((q, idx) => {
        const qNum = idx + 1;
        const isBookmarked = !!AppState.bookmarks[q.id];
        const isPractice = !isExam;
        const selectedIdx = isPractice ? AppState.practiceAnswers[q.id] : AppState.examAnswers[q.id];
        const hasAnswered = (selectedIdx !== undefined);

        html += `
          <div class="mcq-card" id="card-${q.id}" style="margin-bottom: 14px;">
            <div class="mcq-q-header">
              <span class="mcq-num-badge">प्रश्न ${qNum} / ${questions.length}</span>
              <button class="mcq-bookmark-btn ${isBookmarked ? 'bookmarked' : ''}" 
                      data-action="toggle-bookmark" 
                      data-qid="${q.id}" 
                      title="बुकमार्क करें">
                ${isBookmarked ? '★' : '☆'}
              </button>
            </div>

            <div class="mcq-question-text">${q.question}</div>

            <div class="mcq-options-list">
        `;

        q.options.forEach((opt, optIdx) => {
          let optClass = 'option-item';
          if (isPractice && hasAnswered) {
            if (optIdx === q.correct_index) {
              optClass += ' correct';
            } else if (optIdx === selectedIdx) {
              optClass += ' incorrect';
            }
          } else if (!isPractice && selectedIdx === optIdx) {
            optClass += ' selected-exam';
          }

          html += `
            <div class="${optClass}" 
                 data-action="select-option" 
                 data-qid="${q.id}" 
                 data-opt-idx="${optIdx}" 
                 data-q-idx="${idx}">
              <div class="option-label-circle">${optionLabels[optIdx]}</div>
              <div class="option-text">${opt}</div>
            </div>
          `;
        });

        html += `</div>`; // .mcq-options-list

        if (isPractice && hasAnswered) {
          const noteText = cleanNoteText(q.note || q.explanation);
          if (noteText) {
            html += `
              <div class="note-box">
                <strong>नोट:</strong> ${formatMarkdown(noteText)}
              </div>
            `;
          }
        }

        html += `</div>`; // .mcq-card
      });

      if (isExam) {
        html += `
          <button class="btn btn-primary btn-full" data-action="submit-exam" style="margin-top: 14px; padding: 14px; font-size: 15px;">
            🏁 परीक्षा सबमिट करें व स्कोरकार्ड देखें
          </button>
        `;
      }
    }

    html += `</div></div>`; // #ca-date-items-wrapper and .glass-card
    container.innerHTML = html;
  }

  function handleOpenTodayClass() {
    openCaCategory('national_ca');
    const todayDateKey = '2026-11-20';
    const novDates = (AppState.db.national_ca && AppState.db.national_ca.dates) || {};
    
    if (novDates[todayDateKey] && novDates[todayDateKey].questions && novDates[todayDateKey].questions.length > 0) {
      handleCalendarDateTap(todayDateKey);
    } else {
      const sortedKeys = Object.keys(novDates).sort();
      const latestKey = sortedKeys.length > 0 ? sortedKeys[sortedKeys.length - 1] : todayDateKey;
      handleCalendarDateTap(latestKey);
    }
  }

  function navigateCalMonth(direction) {
    const [y, m] = selectedCaMonth.split('-').map(Number);
    let newM = m + direction;
    let newY = y;
    if (newM < 1) { newM = 12; newY--; }
    if (newM > 12) { newM = 1; newY++; }
    selectedCaMonth = `${newY}-${String(newM).padStart(2, '0')}`;
    renderInteractiveCalendar();
  }

  function launchMegaRevisionTest(rangeType) {
    const allDates = AppState.db.national_ca.dates || {};
    const sortedDateKeys = Object.keys(allDates).sort();
    let candidateKeys = [];

    if (rangeType === 'last_7_days') {
      candidateKeys = sortedDateKeys.slice(-7);
    } else {
      // Whole month
      candidateKeys = sortedDateKeys.filter(k => k.startsWith(selectedCaMonth));
      if (candidateKeys.length === 0) candidateKeys = sortedDateKeys.slice(-20);
    }

    let pooledQuestions = [];
    candidateKeys.forEach(k => {
      pooledQuestions.push(...allDates[k].questions);
    });

    if (pooledQuestions.length === 0) {
      alert('इस रेंज के लिए कोई प्रश्न नहीं मिला।');
      return;
    }

    // Shuffle and pick 30-50 questions
    const shuffled = [...pooledQuestions].sort(() => 0.5 - Math.random());
    const testSet = shuffled.slice(0, Math.min(50, shuffled.length));

    openQuizWorkspace({
      type: 'mega',
      subCategory: 'mega_revision',
      dateKey: null,
      title: rangeType === 'last_7_days' ? '⚡ साप्ताहिक रिवीज़न मेगा टेस्ट (25-50 Q)' : '🏆 पूरा महीना रिवीज़न मेगा टेस्ट (50 Q)',
      questions: testSet
    });
  }

  function promptLinkDocument(targetCategory) {
    switchTab('tab-settings');
    const select = document.getElementById('target-category-select');
    if (select) select.value = targetCategory;
    const formBox = document.getElementById('add-doc-card');
    if (formBox) {
      formBox.scrollIntoView({ behavior: 'smooth' });
      formBox.style.outline = '2px solid var(--primary)';
      setTimeout(() => formBox.style.outline = 'none', 1500);
    }
  }

  function openGkChapterWorkspace(subcat, chId) {
    const cat = AppState.db.rajasthan_gk[subcat];
    const ch = cat.chapters.find(c => c.id === chId);
    if (!ch) return;

    openQuizWorkspace({
      type: 'gk',
      subCategory: subcat,
      chapterId: chId,
      title: `🏛️ ${cat.title} ➔ ${ch.title}`,
      questions: ch.questions
    });
  }

  function openLsaSubjectWorkspace(subjId) {
    const subj = AppState.db.lsa_subjects[subjId];
    if (!subj.linked || !subj.chapters || subj.chapters.length === 0) {
      promptLinkDocument(`lsa_${subjId}`);
      return;
    }

    let pooledQuestions = [];
    subj.chapters.forEach(c => pooledQuestions.push(...c.questions));

    openQuizWorkspace({
      type: 'lsa',
      subCategory: subjId,
      chapterId: null,
      title: `🐾 ${subj.title} • सभी अध्याय`,
      questions: pooledQuestions
    });
  }

  function toggleBookmark(qId) {
    const q = AppState.activeContext.questions.find(item => item.id === qId);
    if (!q) return;

    if (AppState.bookmarks[qId]) {
      delete AppState.bookmarks[qId];
    } else {
      AppState.bookmarks[qId] = q;
    }
    saveBookmarks();
    renderQuizContent();
  }

  function openVaultWorkspace() {
    const vaultItems = Object.values(AppState.wrongVault);
    if (vaultItems.length === 0) {
      alert('गलत सवालों की तिजोरी खाली है! बहुत बढ़िया!');
      return;
    }

    openQuizWorkspace({
      type: 'vault',
      subCategory: 'wrong_vault',
      dateKey: null,
      title: '🚨 गलत सवाल तिजोरी (Wrong Answer Vault) • री-टेस्ट',
      questions: vaultItems.map(v => v.questionObj)
    });
  }

  function openBookmarksWorkspace() {
    const bookmarkItems = Object.values(AppState.bookmarks);
    if (bookmarkItems.length === 0) {
      alert('कोई बुकमार्क सवाल सहेजा नहीं गया है।');
      return;
    }

    openQuizWorkspace({
      type: 'bookmarks',
      subCategory: 'saved_bookmarks',
      dateKey: null,
      title: '★ बुकमार्क सवाल (Saved Bookmarks)',
      questions: bookmarkItems
    });
  }

  // ================= ADD / SYNC DOCUMENT CONTROLLER =================
  async function handleAddOrSyncDoc() {
    const categorySelect = document.getElementById('target-category-select');
    const docUrlInput = document.getElementById('doc-url-input');
    const chapterTitleInput = document.getElementById('chapter-title-input');
    const rawTextInput = document.getElementById('raw-text-input');
    const syncStatusEl = document.getElementById('doc-sync-status-msg');

    const targetCat = categorySelect.value;
    const docUrl = docUrlInput.value.trim();
    const rawText = rawTextInput.value.trim();
    const chTitle = chapterTitleInput.value.trim() || 'अध्याय 1';

    if (!docUrl && !rawText) {
      alert('कृपया गूगल डॉक्स URL या टेक्स्ट नोट्स दर्ज करें।');
      return;
    }

    syncStatusEl.style.display = 'block';
    syncStatusEl.innerHTML = `🔄 सामग्री लोड और प्रोसेस की जा रही है...`;

    try {
      let content = rawText;
      if (!content && docUrl) {
        content = await window.TaiyariParser.fetchGoogleDocText(docUrl);
      }

      if (targetCat === 'national_ca' || targetCat === 'rajasthan_ca') {
        // Collect existing question IDs for incremental re-sync
        const existingMap = {};
        const targetObj = AppState.db[targetCat];
        if (targetObj && targetObj.dates) {
          Object.values(targetObj.dates).forEach(d => {
            (d.questions || []).forEach(q => existingMap[q.id] = q);
          });
        }

        const parseResult = window.TaiyariParser.parseCurrentAffairsText(content, existingMap);
        
        // Merge into target
        if (!AppState.db[targetCat]) {
          AppState.db[targetCat] = { linked: true, doc_url: docUrl, dates: {} };
        }
        AppState.db[targetCat].linked = true;
        AppState.db[targetCat].doc_url = docUrl || AppState.db[targetCat].doc_url;
        AppState.db[targetCat].last_synced = new Date().toISOString();

        // Merge dates incrementally
        for (let dk in parseResult.parsedDates) {
          if (!AppState.db[targetCat].dates[dk]) {
            AppState.db[targetCat].dates[dk] = parseResult.parsedDates[dk];
          } else {
            // Merge newly added questions without duplicates
            const currentQ = AppState.db[targetCat].dates[dk].questions;
            parseResult.parsedDates[dk].questions.forEach(newQ => {
              if (!currentQ.some(eq => eq.id === newQ.id)) {
                currentQ.push(newQ);
              }
            });
          }
        }

        saveDatabase();
        syncStatusEl.innerHTML = `✅ इंक्रीमेंटल री-सिंक सफल! ${parseResult.newlyAddedCount} नए प्रश्न जोड़े गए (${parseResult.totalDates} तारीखें)।`;
      } else if (targetCat.startsWith('gk_') || ['geography', 'art_culture', 'history'].includes(targetCat)) {
        const gkKey = targetCat.replace('gk_', '');
        const parseRes = window.TaiyariParser.parseChapterOrTextbookNotes(content, chTitle);
        
        const catObj = AppState.db.rajasthan_gk[gkKey];
        catObj.linked = true;
        catObj.doc_url = docUrl || catObj.doc_url;
        catObj.last_synced = new Date().toISOString();

        if (parseRes.isMultiChapter) {
          catObj.chapters = parseRes.chapters;
          let totalQ = 0;
          catObj.chapters.forEach(c => totalQ += c.questions.length);
          syncStatusEl.innerHTML = `✅ ${catObj.title} के सभी ${parseRes.chapters.length} अध्याय और ${totalQ} MCQ सफलतापूर्वक तैयार हुए!`;
        } else {
          if (!catObj.chapters) catObj.chapters = [];
          catObj.chapters.push(parseRes.chapters[0]);
          syncStatusEl.innerHTML = `✅ अध्याय '${chTitle}' में ${parseRes.chapters[0].questions.length} प्रश्न जोड़े गए!`;
        }

        saveDatabase();
      } else if (targetCat.startsWith('lsa_')) {
        const subjId = targetCat.replace('lsa_', '');
        const parseRes = window.TaiyariParser.parseChapterOrTextbookNotes(content, chTitle);
        const subjObj = AppState.db.lsa_subjects[subjId];
        subjObj.linked = true;
        subjObj.doc_url = docUrl || subjObj.doc_url;
        subjObj.last_synced = new Date().toISOString();

        if (parseRes.isMultiChapter) {
          subjObj.chapters = parseRes.chapters;
          let totalQ = 0;
          subjObj.chapters.forEach(c => totalQ += c.questions.length);
          syncStatusEl.innerHTML = `✅ ${subjObj.title} के सभी ${parseRes.chapters.length} अध्याय और ${totalQ} प्रश्न तैयार!`;
        } else {
          if (!subjObj.chapters) subjObj.chapters = [];
          subjObj.chapters.push(parseRes.chapters[0]);
          syncStatusEl.innerHTML = `✅ ${subjObj.title} में अध्याय '${chTitle}' (${parseRes.chapters[0].questions.length} प्रश्न) जोड़ा गया!`;
        }

        saveDatabase();
      }

      renderSettingsTab();
      renderCurrentAffairsTab();
    } catch (err) {
      console.error(err);
      syncStatusEl.innerHTML = `❌ त्रुटि: ${err.message}`;
    }
  }

  async function handleIncrementalSync(targetCat) {
    const docUrl = AppState.db[targetCat]?.doc_url;
    if (!docUrl) {
      promptLinkDocument(targetCat);
      return;
    }

    const btn = document.querySelector('[data-action="sync-current-affairs"]');
    if (btn) btn.innerHTML = `🔄 सिंक हो रहा है...`;

    try {
      const text = await window.TaiyariParser.fetchGoogleDocText(docUrl);
      
      const existingMap = {};
      const targetObj = AppState.db[targetCat];
      if (targetObj && targetObj.dates) {
        Object.values(targetObj.dates).forEach(d => {
          (d.questions || []).forEach(q => existingMap[q.id] = q);
        });
      }

      const res = window.TaiyariParser.parseCurrentAffairsText(text, existingMap);
      
      for (let dk in res.parsedDates) {
        if (!AppState.db[targetCat].dates[dk]) {
          AppState.db[targetCat].dates[dk] = res.parsedDates[dk];
        } else {
          const cur = AppState.db[targetCat].dates[dk].questions;
          res.parsedDates[dk].questions.forEach(nq => {
            if (!cur.some(eq => eq.id === nq.id)) cur.push(nq);
          });
        }
      }

      AppState.db[targetCat].last_synced = new Date().toISOString();
      saveDatabase();
      renderCurrentAffairsTab();
      alert(`सिंक सफल! ${res.newlyAddedCount} नए प्रश्न प्राप्त हुए। कुल ${res.totalDates} तारीखें उपलब्ध हैं।`);
    } catch (e) {
      alert(`सिंक त्रुटि: ${e.message}\n(ऑफ़लाइन डेटा सुरक्षित है)`);
    } finally {
      if (btn) btn.innerHTML = `🔄 सिंक करें`;
    }
  }

  // ================= IN-APP LIVE UPDATE =================
  function runInAppUpdateSimulation() {
    const container = document.getElementById('update-progress-box');
    const fill = document.getElementById('update-progress-fill');
    const msg = document.getElementById('update-status-text');
    const btn = document.getElementById('btn-check-update');

    container.style.display = 'block';
    btn.disabled = true;

    const steps = [
      { p: 15, text: 'नया वर्जन v2.1.0 चेक हो रहा है...' },
      { p: 35, text: 'करंट अफेयर्स एवं परीक्षा पैच डाउनलोड हो रहा है...' },
      { p: 65, text: 'ऑफलाइन डेटाबेस सत्यापित किया जा रहा है...' },
      { p: 85, text: 'एग्जामिनर प्रश्न बैंक अपडेट हो रहा है...' },
      { p: 100, text: 'अपडेट पूर्ण हुआ! ऐप नवीनतम RPSC/RSSB मानकों के साथ तैयार है।' }
    ];

    let i = 0;
    function nextStep() {
      if (i < steps.length) {
        fill.style.width = `${steps[i].p}%`;
        msg.textContent = `${steps[i].p}% - ${steps[i].text}`;
        i++;
        setTimeout(nextStep, 500);
      } else {
        btn.disabled = false;
        btn.textContent = '✅ ऐप अप-टू-डेट है';
      }
    }
    nextStep();
  }

  // ================= PRINT & PDF EXPORT =================
  function triggerPrint(layout) {
    const printArea = document.getElementById('print-area-content');
    const questions = AppState.activeContext.questions;

    let html = `
      <div class="print-header">
        <h2>मेरी तैयारी • RPSC / RSSB परीक्षा नोट्स</h2>
        <p>${AppState.activeContext.title} | कुल प्रश्न: ${questions.length} | तिथि: 20-नवंबर-2026</p>
      </div>
      <div class="${layout === '2-col' ? 'print-2-col' : ''}">
    `;

    const optionLabels = ['(A)', '(B)', '(C)', '(D)'];

    questions.forEach((q, idx) => {
      html += `
        <div style="margin-bottom: 14px; page-break-inside: avoid; border-bottom: 1px dashed #ccc; padding-bottom: 8px;">
          <div style="font-weight: 700; font-size: 13px;">Q${idx + 1}. ${q.question}</div>
          <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 4px; margin: 6px 0; font-size: 12px;">
            ${q.options.map((opt, oi) => `<div>${optionLabels[oi]} ${opt}</div>`).join('')}
          </div>
          <div style="font-size: 11px; color: #222; margin-top: 4px; background: #f8f8f8; padding: 4px 6px;">
            <strong>सही उत्तर:</strong> ${optionLabels[q.correct_index]} ${q.options[q.correct_index]}<br>
            <strong>व्याख्या:</strong> ${q.explanation.replace(/[*#]/g, '')}
          </div>
        </div>
      `;
    });

    html += `</div>`;
    printArea.innerHTML = html;

    DOM.printModal.classList.remove('active');
    setTimeout(() => {
      window.print();
    }, 200);
  }

  // ================= BACKUP & RESTORE =================
  function exportBackupJson() {
    const fullBackup = {
      db: AppState.db,
      vault: AppState.wrongVault,
      bookmarks: AppState.bookmarks,
      mastery: AppState.masteryStats,
      exportedAt: new Date().toISOString()
    };

    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(fullBackup, null, 2));
    const dlAnchor = document.createElement('a');
    dlAnchor.setAttribute("href", dataStr);
    dlAnchor.setAttribute("download", `meri_taiyari_backup_${new Date().toISOString().split('T')[0]}.json`);
    dlAnchor.click();
  }

  // Utility Markdown formatter
  function formatMarkdown(str) {
    if (!str) return "";
    return str
      .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.+?)\*/g, '<em>$1</em>')
      .replace(/\n/g, '<br>');
  }

  // ================= NATIVE BACK GESTURE & HARDWARE BACK NAVIGATION =================
  window.handleNativeBackPressed = function() {
    // 1. If Exam Result Modal is open, close it
    const resultModal = document.getElementById('exam-result-modal');
    if (resultModal && (resultModal.style.display === 'flex' || resultModal.classList.contains('active'))) {
      resultModal.style.display = 'none';
      resultModal.classList.remove('active');
      return true;
    }

    // 2. If Workspace view is active, close workspace back to current tab
    if (DOM.viewWorkspace && DOM.viewWorkspace.classList.contains('active')) {
      DOM.viewWorkspace.classList.remove('active');
      clearInterval(AppState.examTimerId);
      switchTab(AppState.currentTab, false);
      return true;
    }

    // 3. If inside Current Affairs calendar detail screen, return to CA Hub
    if (AppState.isInsideCaDetail) {
      backToCaHub();
      return true;
    }

    // 4. If on another tab (GK, Subject, Settings), return to home tab ('tab-ca')
    if (AppState.currentTab !== 'tab-ca') {
      switchTab('tab-ca', false);
      return true;
    }

    // 5. Already at Root Home (CA Hub with nothing open) -> return false so Android shows double-back-to-exit!
    return false;
  };

  // Support HTML5 popstate event (for edge-swipe back gestures in Android WebView)
  window.addEventListener('popstate', function(e) {
    window.handleNativeBackPressed();
  });

  // Start app on DOMContentLoaded
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

})();
