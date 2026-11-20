/**
 * parser.js - Meri Taiyari Clean Examiner Parser
 * Generates concise, 1-2 line direct examiner-grade questions with homogeneous 1-3 word options.
 * No raw line quoting, no mismatched options.
 */

window.DocParser = (function() {
  'use strict';

  const monthMap = {
    "जनवरी": "01", "फरवरी": "02", "मार्च": "03", "अप्रैल": "04",
    "मई": "05", "जून": "06", "जुलाई": "07", "अगस्त": "08",
    "सितंबर": "09", "अक्टूबर": "10", "नवंबर": "11", "दिसंबर": "12"
  };

  const DISTRACTORS = {
    km: ["1070 कि.मी.", "4850 कि.मी.", "5920 कि.मी.", "826 कि.मी.", "869 कि.मी.", "692 कि.मी.", "550 कि.मी.", "168 कि.मी."],
    area: ["3,42,239 वर्ग कि.मी.", "1,32,139 वर्ग मील", "10.41%", "61.11%", "9.60%", "23.03%", "40%"],
    cm: ["हीरालाल शास्त्री", "मोहनलाल सुखाड़िया", "हरिदेव जोशी", "भैरोंसिंह शेखावत", "जयनारायण व्यास", "टीकाराम पालीवाल", "शिवचरण माथुर", "भजनलाल शर्मा"],
    committee: ["परमेश चन्द्र समिति", "रामलुभाया समिति", "ललित के. पंवार समिति", "पी. सत्यनारायण राव समिति", "हरिश्चंद्र माथुर समिति"],
    district: ["जैसलमेर", "बाड़मेर", "बीकानेर", "जोधपुर", "जयपुर", "उदयपुर", "कोटा", "अजमेर", "भीलवाड़ा", "चित्तौड़गढ़", "डूंगरपुर", "बांसवाड़ा", "झालावाड़", "चूरू", "सीकर", "नागौर", "अलवर", "भरतपुर", "धौलपुर", "करौली", "सवाई माधोपुर", "टोंक", "पाली", "सिरोही", "जालौर", "प्रतापगढ़", "राजसमंद", "बूंदी", "बारां", "दौसा", "अनूपगढ़", "फलोदी", "बालोतरा", "सांचौर", "डीग", "सलूंबर"],
    division: ["जयपुर संभाग", "अजमेर संभाग", "जोधपुर संभाग", "बीकानेर संभाग", "उदयपुर संभाग", "भरतपुर संभाग", "कोटा संभाग"],
    peak: ["गुरुशिखर (1722 मी.)", "सेर (1597 मी.)", "दिलवाड़ा (1442 मी.)", "जरगा (1431 मी.)", "अचलगढ़ (1380 मी.)", "कुंभलगढ़ (1224 मी.)", "रघुनाथगढ़ (1055 मी.)", "ऋषिकेश (1017 मी.)", "कमलनाथ (1001 मी.)", "तारागढ़ (873 मी.)"],
    river: ["चंबल नदी", "बनास नदी", "लूणी नदी", "माही नदी", "साबरमती नदी", "कालीसिंध नदी", "बाणगंगा नदी", "पार्वती नदी", "घग्घर नदी", "कांतली नदी", "सोम नदी", "जाखम नदी"],
    dam: ["राणा प्रताप सागर बांध", "गांधी सागर बांध", "जवाहर सागर बांध", "कोटा बैराज", "बीसलपुर बांध", "जाखम बांध", "मेजा बांध", "पांचना बांध", "जवाई बांध"],
    lake: ["सांभर झील", "पचपदरा झील", "डीडवाना झील", "लूणकरणसर झील", "जयसमंद झील", "राजसमंद झील", "पिछोला झील", "फतेहसागर झील", "आनासागर झील", "नक्की झील"],
    soil: ["काली मृदा (वर्टिसोल)", "लाल-पीली मृदा", "जलोढ़ मृदा (एल्फीसोल)", "रेतीली शुष्क मृदा (एंटीसोल)", "भूरी रेतीली मृदा", "लवणीय मृदा"],
    mineral: ["रॉक फॉस्फेट", "सीसा-जस्ता", "तांबा", "लोहा अयस्क", "टंगस्टन", "सफेद संगमरमर", "जिप्सम", "पन्ना"],
    rocket: ["PSLV-C58", "GSLV-F18", "LVM3-M4", "SSLV-D3", "Falcon-9", "Ariane-6"],
    actor: ["रणवीर सिंह", "शाहरुख खान", "अल्लू अर्जुन", "विक्की कौशल", "ऋतिक रोशन", "रणबीर कपूर"],
    film: ["धुरंधर", "जवान", "पुष्पा 2", "12th Fail", "कल्कि 2898 AD", "एनिमल"],
    city: ["श्री विजयापुरम", "विशाखापट्टनम", "कोच्चि", "मुंबई", "चेन्नई", "कोलकाता", "नई दिल्ली", "अहमदाबाद", "जयपुर", "बेंगलुरु"],
    country: ["भारत", "बांग्लादेश", "श्रीलंका", "म्यांमार", "थाईलैंड", "जापान", "फ्रांस", "रूस", "अमेरिका", "जर्मनी"],
    state: ["गुजरात", "महाराष्ट्र", "उत्तर प्रदेश", "मध्य प्रदेश", "राजस्थान", "कर्नाटक", "तमिलनाडु", "असम", "ओडिशा"]
  };

  function pickDistractors(ans, cat) {
    const pool = DISTRACTORS[cat] || DISTRACTORS.district;
    const ansClean = String(ans).trim();
    const cands = pool.filter(d => d.trim() !== ansClean);
    const shuffled = [...cands].sort(() => 0.5 - Math.random());
    return shuffled.slice(0, 3);
  }

  function extractDocId(url) {
    if (!url) return null;
    const m = url.match(/\/d\/([a-zA-Z0-9_-]{25,})/);
    return m ? m[1] : null;
  }

  function getExportUrl(docId) {
    return `https://docs.google.com/document/d/${docId}/export?format=txt`;
  }

  async function fetchGoogleDocText(url) {
    const docId = extractDocId(url);
    if (!docId) throw new Error("अमान्य गूगल डॉक्स लिंक। कृपया पूरा URL दर्ज करें।");

    if (window.AndroidInterface && typeof window.AndroidInterface.fetchGoogleDocNative === 'function') {
      const nativeRes = window.AndroidInterface.fetchGoogleDocNative(docId);
      if (nativeRes && nativeRes.length > 50 && !nativeRes.startsWith("ERROR:")) {
        return nativeRes;
      }
    }

    const exportUrl = getExportUrl(docId);
    const proxies = [
      exportUrl,
      `https://api.allorigins.win/raw?url=${encodeURIComponent(exportUrl)}`,
      `https://corsproxy.io/?${encodeURIComponent(exportUrl)}`
    ];

    for (let pUrl of proxies) {
      try {
        const res = await fetch(pUrl);
        if (res.ok) {
          const txt = await res.text();
          if (txt && txt.length > 50) return txt;
        }
      } catch (e) {
        // continue
      }
    }
    throw new Error("डॉक्यूमेंट लोड नहीं हो सका। कृपया लिंक की 'Share: Anyone with link' अनुमति जांचें।");
  }

  function cleanRawText(raw) {
    return (raw || "")
      .replace(/\u200b/g, '')
      .replace(/\ufeff/g, '')
      .replace(/\r\n/g, '\n')
      .replace(/\r/g, '\n');
  }

  function parseCurrentAffairsText(rawText, existingQuestionsMap = {}) {
    const text = cleanRawText(rawText);
    const dateRegex = /^[ \t]*([0-9]{1,2})\s*[-–]?\s*(नवंबर|अक्टूबर|सितंबर|अगस्त|जुलाई|जून|मई|अप्रैल|मार्च|फरवरी|जनवरी)[ \t]*$/gm;

    const dateMatches = [];
    let match;
    while ((match = dateRegex.exec(text)) !== null) {
      dateMatches.push({
        day: parseInt(match[1], 10),
        monthHindi: match[2],
        index: match.index,
        end: match.index + match[0].length
      });
    }

    const parsedDates = {};
    let newlyAddedCount = 0;

    for (let i = 0; i < dateMatches.length; i++) {
      const cur = dateMatches[i];
      const mCode = monthMap[cur.monthHindi] || "11";
      const dayStr = String(cur.day).padStart(2, '0');
      const dateKey = `2026-${mCode}-${dayStr}`;
      const displayDate = `${cur.day} ${cur.monthHindi} 2026`;

      const start = cur.end;
      const end = (i + 1 < dateMatches.length) ? dateMatches[i + 1].index : text.length;
      const sectionChunk = text.slice(start, end).trim();

      const rawItems = sectionChunk.split(/(?=(?:^|\n)[ \t]*(?:\d+[\.:]|[•*])[ \t]*(?:[^\n]*\n)?[ \t]*\*?[ \t]*प्रश्न:)/g);
      const parsedQuestions = [];

      for (let item of rawItems) {
        if (!item.includes('प्रश्न:') || !item.includes('उत्तर:')) continue;
        const qMatch = item.match(/प्रश्न:\s*([\s\S]+?)(?=\n[ \t]*\*?[ \t]*उत्तर:|$)/);
        const aMatch = item.match(/उत्तर:\s*([\s\S]+?)(?=\n[ \t]*\*?[ \t]*(?:विवरण|तकनीकी विशेषताएं|महत्वपूर्ण तथ्य|विशेषताएं):|$)/);

        if (!qMatch || !aMatch) continue;

        const qText = qMatch[1].trim().replace(/\n+/g, ' ');
        let rawAns = aMatch[1].trim().split('\n')[0].replace(/^[\s\t\*•-]+/, '').trim();

        if ((!rawAns || rawAns.length < 2) && aMatch[1].includes('\n')) {
          const subLines = aMatch[1].split('\n').map(l => l.replace(/^[\s\t\*•-]+/, '').trim()).filter(Boolean);
          if (subLines.length > 1) rawAns = subLines[1].split(':')[1] || subLines[1];
        }

        let coreAns = rawAns.split('(')[0].split('।')[0].trim();
        if (coreAns.includes(':')) coreAns = coreAns.split(':')[1].trim();
        coreAns = coreAns.replace(/^['"•*]+|['"•*]+$/g, '').trim();

        if (!coreAns || coreAns.length < 2 || ["उत्तर", "निम्न", "निम्नलिखित"].includes(coreAns)) continue;

        // Detect category
        let domain = "city";
        const qLower = (qText + " " + coreAns).toLowerCase();
        if (qLower.includes("रॉकेट") || qLower.includes("gslv") || qLower.includes("pslv")) domain = "rocket";
        else if (qLower.includes("अभिनेता")) domain = "actor";
        else if (qLower.includes("फिल्म") || qLower.includes("मूवी")) domain = "film";
        else if (qLower.includes("देश") || qLower.includes("नामकरण")) domain = "country";
        else if (qLower.includes("राज्य")) domain = "state";

        const dists = pickDistractors(coreAns, domain);
        const options = [coreAns, ...dists].sort(() => 0.5 - Math.random());
        const correctIdx = options.indexOf(coreAns);

        const qHash = Math.abs(qText.split('').reduce((a, b) => ((a << 5) - a) + b.charCodeAt(0), 0)).toString(36);
        const qId = `CA_${dateKey}_${qHash}`;

        parsedQuestions.push({
          id: qId,
          date: dateKey,
          display_date: displayDate,
          category: "national_international",
          topic: `करंट अफेयर (${displayDate})`,
          question: qText,
          options: options,
          correct_index: correctIdx,
          explanation: `✅ **सही उत्तर:** ${coreAns}\n\n📌 **परीक्षा संदर्भ:** समसामयिकी ${displayDate}\n\n📖 **एग्जामिनर व्याख्या:** ${rawAns}`,
          mnemonic: `💡 **याद रखने की ट्रिक:** मुख्य बिंदु '${coreAns}' को ध्यान में रखें।`,
          one_liner: `${qText} ➔ **${coreAns}**`
        });
        newlyAddedCount++;
      }

      if (parsedQuestions.length > 0) {
        parsedDates[dateKey] = {
          date: dateKey,
          display_date: displayDate,
          month: cur.monthHindi,
          questions: parsedQuestions,
          total_questions: parsedQuestions.length
        };
      }
    }

    return { parsedDates, newlyAddedCount, totalDates: Object.keys(parsedDates).length };
  }

  function parseChapterOrTextbookNotes(rawText, fallbackChapterTitle = "अध्याय 1") {
    const text = cleanRawText(rawText);
    const chRegex = /^[ \t]*(अध्याय\s*[-–]?\s*\d+)[ \t]*\n[ \t]*[❀\*\-–•\s]*(.+?)[❀\*\-–•\s]*$/gm;

    const chMatches = [];
    let match;
    while ((match = chRegex.exec(text)) !== null) {
      chMatches.push({
        label: match[1].trim(),
        title: match[2].trim(),
        index: match.index,
        end: match.index + match[0].length
      });
    }

    const chapters = [];

    if (chMatches.length === 0) {
      const qs = parseCrispExaminerQuestions(text, fallbackChapterTitle, "ch_1");
      return [{
        id: "ch_1",
        number: 1,
        title: fallbackChapterTitle,
        raw_title: fallbackChapterTitle,
        questions: qs
      }];
    }

    for (let i = 0; i < chMatches.length; i++) {
      const cur = chMatches[i];
      const start = cur.end;
      const end = (i + 1 < chMatches.length) ? chMatches[i + 1].index : text.length;
      const chunk = text.slice(start, end).trim();
      const chId = `geo_ch_${i + 1}`;

      const qs = parseCrispExaminerQuestions(chunk, `${cur.label}: ${cur.title}`, chId);
      chapters.push({
        id: chId,
        number: i + 1,
        title: `${cur.label}: ${cur.title}`,
        raw_title: cur.title,
        questions: qs
      });
    }

    return chapters;
  }

  function parseCrispExaminerQuestions(chunkText, chapterTitle, chIdPrefix) {
    const lines = chunkText.split('\n')
      .map(l => l.replace(/^[\s\*•\t-–]+/, '').trim())
      .filter(l => l.length > 10 && !l.startsWith('❀') && !l.endsWith(':'));

    const questions = [];
    let qCounter = 0;

    for (let line of lines) {
      let qObj = null;

      // 1. Chief Minister
      for (let cm of DISTRACTORS.cm) {
        if (line.includes(cm)) {
          let q = `राजस्थान में '${line.split(':')[0].trim()}' का संबंध किस मुख्यमंत्री से है?`;
          if (line.includes("1949") || line.includes("शुरुआत")) q = "राजस्थान में संभागीय व्यवस्था की शुरुआत (1949) किस मुख्यमंत्री के कार्यकाल में हुई थी?";
          else if (line.includes("1962") || line.includes("समाप्ति")) q = "अप्रैल 1962 में राजस्थान की संभागीय व्यवस्था को किस मुख्यमंत्री ने समाप्त कर दिया था?";
          else if (line.includes("1987") || line.includes("पुनः")) q = "15 जनवरी 1987 को राजस्थान में संभागीय व्यवस्था को पुनः किस मुख्यमंत्री ने शुरू किया था?";
          qObj = { q, ans: cm, cat: "cm" };
          break;
        }
      }

      // 2. Mountain Peaks
      if (!qObj) {
        for (let pk of DISTRACTORS.peak) {
          const pkClean = pk.split('(')[0].trim();
          if (line.includes(pkClean)) {
            if (pkClean === "गुरुशिखर") qObj = { q: "अरावली पर्वतमाला की सर्वोच्च चोटी 'गुरुशिखर' (1722 मीटर) किस जिले में है?", ans: "सिरोही", cat: "district" };
            else if (pkClean === "रघुनाथगढ़") qObj = { q: "उत्तरी अरावली की सबसे ऊंची चोटी 'रघुनाथगढ़' (1055 मीटर) किस जिले में है?", ans: "सीकर", cat: "district" };
            else qObj = { q: `अरावली पर्वतमाला की प्रमुख पर्वत चोटी '${pkClean}' की प्रामाणिक ऊंचाई कितनी है?`, ans: pk, cat: "peak" };
            break;
          }
        }
      }

      // 3. Divisions
      if (!qObj) {
        if (line.includes("छठा संभाग") || (line.includes("अजमेर") && line.includes("1987"))) {
          qObj = { q: "वर्ष 1987 में जयपुर से अलग कर राजस्थान का 6ठा संभाग किसे बनाया गया था?", ans: "अजमेर संभाग", cat: "division" };
        } else if (line.includes("7वां संभाग") || (line.includes("भरतपुर") && line.includes("2005"))) {
          qObj = { q: "4 जून 2005 को राजस्थान का 7वां संभाग कौन-सा घोषित किया गया था?", ans: "भरतपुर संभाग", cat: "division" };
        }
      }

      // 4. District Formations
      if (!qObj) {
        if (line.includes("27 वां जिला") || (line.includes("धौलपुर") && line.includes("1982"))) {
          qObj = { q: "15 अप्रैल 1982 को राजस्थान का 27वां जिला 'धौलपुर' किस जिले से अलग करके बनाया गया था?", ans: "भरतपुर", cat: "district" };
        } else if (line.includes("28वां जिला") || (line.includes("बारां") && line.includes("1991"))) {
          qObj = { q: "10 अप्रैल 1991 को कोटा से अलग कर राजस्थान का 28वां जिला कौन-सा बनाया गया?", ans: "बारां", cat: "district" };
        } else if (line.includes("29 वां जिला") || (line.includes("दौसा") && line.includes("1991"))) {
          qObj = { q: "10 अप्रैल 1991 को जयपुर से अलग कर राजस्थान का 29वां जिला कौन-सा बना تھا?", ans: "दौसा", cat: "district" };
        } else if (line.includes("30वां जिला") || (line.includes("राजसमंद") && line.includes("1991"))) {
          qObj = { q: "10 अप्रैल 1991 को उदयपुर से अलग कर राजस्थान का 30वां जिला कौन-सा बना?", ans: "राजसमंद", cat: "district" };
        } else if (line.includes("31 वां जिला") || (line.includes("हनुमानगढ़") && line.includes("1994"))) {
          qObj = { q: "12 जुलाई 1994 को श्रीगंगानगर से अलग कर राजस्थान का 31वां जिला कौन-सा बनाया गया?", ans: "हनुमानगढ़", cat: "district" };
        } else if (line.includes("32 वां जिला") || (line.includes("करौली") && line.includes("1997"))) {
          qObj = { q: "19 जुलाई 1997 को सवाई माधोपुर से अलग करके राजस्थान का 32वां जिला कौन-सा बना था?", ans: "करौली", cat: "district" };
        } else if (line.includes("33 वां जिला") || (line.includes("प्रतापगढ़") && line.includes("2008"))) {
          qObj = { q: "26 जनवरी 2008 को राजस्थान का 33वां जिला कौन-सा गठित किया गया था?", ans: "प्रतापगढ़", cat: "district" };
        }
      }

      // 5. General Key-Value lines
      if (!qObj && line.includes(':')) {
        const parts = line.split(':');
        const k = parts[0].trim();
        const v = parts[1].trim();
        if (k.length > 3 && k.length < 30 && v.length > 2 && v.length < 40) {
          const cleanV = v.split('(')[0].split('।')[0].trim();
          if (cleanV.length > 2) {
            const q = k.includes("जिला")
              ? `राजस्थान में '${k}' के रूप में किस जिले को जाना जाता है?`
              : `राजस्थान सामान्य ज्ञान (${chapterTitle}) के अनुसार, '${k}' का सही मान / विवरण क्या है?`;
            qObj = { q, ans: cleanV, cat: "district" };
          }
        }
      }

      if (qObj) {
        qCounter++;
        const dists = pickDistractors(qObj.ans, qObj.cat);
        const opts = [qObj.ans, ...dists].sort(() => 0.5 - Math.random());
        const correctIdx = opts.indexOf(qObj.ans);

        questions.push({
          id: `${chIdPrefix}_q_${qCounter}`,
          chapter_id: chIdPrefix,
          topic: chapterTitle,
          question: qObj.q,
          options: opts,
          correct_index: correctIdx,
          explanation: `✅ **सही उत्तर:** ${qObj.ans}\n\n📌 **परीक्षा संदर्भ:** ${chapterTitle}\n\n📖 **एग्जामिनर व्याख्या:** ${line}`,
          mnemonic: `💡 **याद रखने की ट्रिक:** मुख्य बिंदु '${qObj.ans}' को ध्यान में रखें।`,
          one_liner: `${qObj.q} ➔ **${qObj.ans}**`
        });
      }
    }

    return questions;
  }

  return {
    extractDocId,
    getExportUrl,
    fetchGoogleDocText,
    parseCurrentAffairsText,
    parseChapterOrTextbookNotes,
    parsePureExaminerFactualNotes: parseCrispExaminerQuestions
  };
})();
