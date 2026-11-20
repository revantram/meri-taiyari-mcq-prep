with open('/data/user/0/com.termux/files/home/.gemini/antigravity-cli/scratch/meri-taiyari-app/assets/app.js', 'r', encoding='utf-8') as f:
    text = f.read()

old_fn = """  function handleCalendarDateTap(dateKey, hasQ) {
    if (!hasQ) {
      alert(`तारीख ${dateKey} के लिए अभी कोई प्रश्न उपलब्ध नहीं है। गूगल डॉक्स में नए नोट्स जोड़कर '🔄 सिंक करें' दबाएं।`);
      return;
    }

    const dayObj = AppState.db.national_ca.dates[dateKey];
    if (dayObj && dayObj.questions) {
      openQuizWorkspace({
        type: 'ca',
        subCategory: 'national_ca',
        dateKey: dateKey,
        title: `📅 ${dayObj.display_date} • राष्ट्रीय एवं अंतरराष्ट्रीय करंट अफेयर`,
        questions: dayObj.questions
      });
    }
  }"""

new_fn = """  function handleCalendarDateTap(dateKey) {
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
        html += `
          <div class="oneliner-card">
            <span class="oneliner-badge">समाचार व रिवीज़न बिंदु #${idx + 1}</span>
            <div class="oneliner-text">${formatMarkdown(q.one_liner || q.question)}</div>
            <div class="mnemonic-box" style="margin-top: 8px;">
              <span>✨</span>
              <div style="font-size: 12px;">${formatMarkdown(q.mnemonic)}</div>
            </div>
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
          html += `
            <div class="explanation-box">
              ${formatMarkdown(q.explanation)}
            </div>
            <div class="mnemonic-box">
              <span>✨</span>
              <div>${formatMarkdown(q.mnemonic)}</div>
            </div>
          `;
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
  }"""

if old_fn in text:
    text = text.replace(old_fn, new_fn)
    print("handleCalendarDateTap successfully updated.")
else:
    print("Warning: old_fn not found!")

# Now add handleAction cases for new buttons
actions_target = """      case 'select-calendar-date': {
        const dateKey = el.getAttribute('data-date');
        const hasQ = el.getAttribute('data-has-q') === 'true';
        handleCalendarDateTap(dateKey, hasQ);
        break;
      }"""

actions_replacement = """      case 'open-ca-category': {
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
      }"""

if actions_target in text:
    text = text.replace(actions_target, actions_replacement)
    print("handleAction cases successfully added.")
else:
    print("Warning: actions_target not found!")

with open('/data/user/0/com.termux/files/home/.gemini/antigravity-cli/scratch/meri-taiyari-app/assets/app.js', 'w', encoding='utf-8') as f:
    f.write(text)
