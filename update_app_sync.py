with open('/data/user/0/com.termux/files/home/.gemini/antigravity-cli/scratch/meri-taiyari-app/assets/app.js', 'r', encoding='utf-8') as f:
    text = f.read()

# Replace parseChapterNotes with parseChapterOrTextbookNotes
target_old = """      } else if (targetCat.startsWith('gk_') || ['geography', 'art_culture', 'history'].includes(targetCat)) {
        const gkKey = targetCat.replace('gk_', '');
        const questions = window.TaiyariParser.parseChapterNotes(content, chTitle);
        
        const catObj = AppState.db.rajasthan_gk[gkKey];
        catObj.linked = true;
        catObj.doc_url = docUrl || catObj.doc_url;

        // Check if chapter already exists
        const chId = `ch_${Date.now()}`;
        catObj.chapters.push({
          id: chId,
          title: chTitle,
          questions: questions
        });

        saveDatabase();
        syncStatusEl.innerHTML = `✅ अध्याय '${chTitle}' में ${questions.length} प्रश्न जोड़े गए!`;
      } else if (targetCat.startsWith('lsa_')) {
        const subjId = targetCat.replace('lsa_', '');
        const questions = window.TaiyariParser.parseChapterNotes(content, chTitle);
        const subjObj = AppState.db.lsa_subjects[subjId];
        subjObj.linked = true;
        subjObj.doc_url = docUrl || subjObj.doc_url;

        if (!subjObj.chapters) subjObj.chapters = [];
        subjObj.chapters.push({
          id: `lsa_ch_${Date.now()}`,
          title: chTitle,
          questions: questions
        });

        saveDatabase();
        syncStatusEl.innerHTML = `✅ ${subjObj.title} में अध्याय '${chTitle}' (${questions.length} प्रश्न) जोड़ा गया!`;
      }"""

replacement_new = """      } else if (targetCat.startsWith('gk_') || ['geography', 'art_culture', 'history'].includes(targetCat)) {
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
      }"""

if target_old in text:
    text = text.replace(target_old, replacement_new)
    with open('/data/user/0/com.termux/files/home/.gemini/antigravity-cli/scratch/meri-taiyari-app/assets/app.js', 'w', encoding='utf-8') as f:
        f.write(text)
    print("app.js updated successfully!")
else:
    print("Target block not found, check matching!")
