/**
 * parser.js - Meri Taiyari Clean Examiner Parser
 * Generates concise, 1-2 line direct examiner-grade questions with homogeneous 1-3 word options.
 * No raw line quoting, no mismatched options.
 */

window.TaiyariParser = window.DocParser = (function() {
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
    state: ["गुजरात", "महाराष्ट्र", "उत्तर प्रदेश", "मध्य प्रदेश", "राजस्थान", "कर्नाटक", "तमिलनाडु", "असम", "ओडिशा"],
    intl_city: ["बीजिंग (चीन)", "टोक्यो (जापान)", "सिंगापुर", "शेंजेन (चीन)", "रियाद (सऊदी अरब)", "बैंकॉक (थाईलैंड)", "जिनेवा (स्विट्जरलैंड)", "पेरिस (फ्रांस)", "वाशिंगटन (यूएसए)", "दुबई (यूएई)", "लंदन (यूके)"],
    university: ["लुंड यूनिवर्सिटी (स्वीडन)", "हार्वर्ड यूनिवर्सिटी (यूएसए)", "ऑक्सफोर्ड यूनिवर्सिटी (यूके)", "मैसाचुसेट्स इंस्टीट्यूट ऑफ टेक्नोलॉजी (MIT)", "कैम्ब्रिज यूनिवर्सिटी", "टोक्यो यूनिवर्सिटी", "IIT बॉम्बे", "IIT दिल्ली", "IISc बेंगलुरु"],
    country: ["फिजी", "रूस", "मॉरीशस", "बांग्लादेश", "श्रीलंका", "जापान", "अमेरिका", "फ्रांस", "जर्मनी", "ऑस्ट्रेलिया", "नेपाल", "भूटान"],
    person_group: ["क्रिकेट से वैभव सूर्यवंशी, विज्ञान से शुभांशु शुक्ला", "भाला फेंक से नीरज चोपड़ा, निशानेबाजी से मनु भाकर", "कुश्ती से अमन सहरावत, मुक्केबाजी से लवलीना", "बैडमिंटन से लक्ष्य सेन, शतरंज से डी. गुकेश"],
    indian_city: ["नई दिल्ली", "मुंबई", "बेंगलुरु", "अहमदाबाद", "हैदराबाद", "कोलकाता", "चेन्नई", "जयपुर", "पुणे", "लखनऊ"],
    sports: ["भारत", "ईरान", "ऑस्ट्रेलिया", "इंग्लैंड", "दक्षिण अफ्रीका", "पाकिस्तान"],
    defense: ["पहला बिम्सटेक अभ्यास", "वरुण अभ्यास 2026", "इंद्र अभ्यास 2026", "मालाबार 2026", "सूर्य किरण", "युद्ध अभ्यास"],
    park: ["भड़ला सोलर पार्क (फलौदी)", "नोख सोलर पार्क (जैसलमेर)", "पूगल सोलर पार्क (बीकानेर)", "फतेहगढ़ सोलर पार्क (जैसलमेर)", "फलौदी-पोकरण सोलर पार्क"],
    tiger: ["रणथंभौर टाइगर रिज़र्व", "सरिस्का टाइगर रिज़र्व", "मुकुंदरा हिल्स टाइगर रिज़र्व", "रामगढ़ विषधारी टाइगर रिज़र्व", "कुंभलगढ़ अभयारण्य"]
  };

  function pickDistractors(ans, cat) {
    let pool = DISTRACTORS[cat];
    const ansClean = String(ans).trim();
    if (!pool) {
      for (const [k, arr] of Object.entries(DISTRACTORS)) {
        if (arr.some(item => item.includes(ansClean) || ansClean.includes(item.split('(')[0].trim()))) {
          pool = arr;
          break;
        }
      }
    }
    if (!pool) pool = DISTRACTORS.indian_city;
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
    const exportUrl = getExportUrl(docId);

    // 1. Android WebView Native Bridge (Async callback)
    if (window.AndroidInterface && typeof window.AndroidInterface.fetchGoogleDocNative === 'function') {
      try {
        const text = await new Promise((resolve, reject) => {
          const callbackId = 'doc_cb_' + Date.now() + '_' + Math.floor(Math.random() * 1000);
          const timeoutId = setTimeout(() => {
            if (window._nativeDocCallbacks && window._nativeDocCallbacks[callbackId]) {
              delete window._nativeDocCallbacks[callbackId];
            }
            reject(new Error("Native fetch timeout"));
          }, 35000);

          if (!window._nativeDocCallbacks) {
            window._nativeDocCallbacks = {};
            window.onNativeDocFetched = function(cbId, success, base64OrErr) {
              const cb = window._nativeDocCallbacks && window._nativeDocCallbacks[cbId];
              if (cb) {
                delete window._nativeDocCallbacks[cbId];
                if (success) {
                  try {
                    const binary = window.atob(base64OrErr);
                    const bytes = new Uint8Array(binary.length);
                    for (let i = 0; i < binary.length; i++) bytes[i] = binary.charCodeAt(i);
                    const decoded = new TextDecoder('utf-8').decode(bytes);
                    cb.resolve(decoded);
                  } catch(e) {
                    cb.resolve(window.atob(base64OrErr));
                  }
                } else {
                  cb.reject(new Error(base64OrErr));
                }
              }
            };
          }

          window._nativeDocCallbacks[callbackId] = {
            resolve: (val) => { clearTimeout(timeoutId); resolve(val); },
            reject: (err) => { clearTimeout(timeoutId); reject(err); }
          };

          window.AndroidInterface.fetchGoogleDocNative(exportUrl, callbackId);
        });

        if (text && text.length > 50) return text;
      } catch (nativeErr) {
        console.warn("Native bridge fetch failed, falling back to proxies:", nativeErr);
      }
    }

    // 2. Direct fetch & CORS proxies fallback
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
        let domain = "indian_city";
        const qLower = (qText + " " + coreAns).toLowerCase();

        if (qLower.includes("किस देश") || qLower.includes("देश के") || qLower.includes("देश द्वारा") || qLower.includes("नामकरण किस देश")) {
          domain = "country";
        } else if (qLower.includes("विश्वविद्यालय") || qLower.includes("यूनिवर्सिटी") || qLower.includes("संस्थान") || qLower.includes("रैंकिंग") || qLower.includes("iit") || qLower.includes("qs")) {
          domain = "university";
        } else if (qLower.includes("खिलाड़ी") || qLower.includes("वैज्ञानिक") || qLower.includes("time 100") || qLower.includes("शामिल किया") || qLower.includes("सूची")) {
          domain = "person_group";
        } else if (qLower.includes("कहाँ आयोजित") || qLower.includes("मीटिंग") || qLower.includes("सम्मेलन") || qLower.includes("शिखर") || qLower.includes("apec") || qLower.includes("g20") || qLower.includes("ब्रिक्स")) {
          domain = "intl_city";
        } else if (qLower.includes("रॉकेट") || qLower.includes("gslv") || qLower.includes("pslv")) {
          domain = "rocket";
        } else if (qLower.includes("उपग्रह") || qLower.includes("satellite") || qLower.includes("nvs")) {
          domain = "satellite";
        } else if (qLower.includes("अभ्यास") || qLower.includes("नौसैनिक") || qLower.includes("सैन्य")) {
          domain = "defense";
        } else if (qLower.includes("सोलर") || qLower.includes("पार्क")) {
          domain = "park";
        } else if (qLower.includes("टाइगर") || qLower.includes("भेड़िय") || qLower.includes("अभयारण्य")) {
          domain = "tiger";
        } else if (qLower.includes("अभिनेता") || qLower.includes("अभिनेत्री")) {
          domain = "actor";
        } else if (qLower.includes("फिल्म") || qLower.includes("मूवी")) {
          domain = "film";
        } else if (qLower.includes("राज्य")) {
          domain = "state";
        } else if (qLower.includes("राजस्थान") || qLower.includes("जिला")) {
          domain = "district";
        }

        const dists = pickDistractors(coreAns, domain);
        const options = [coreAns, ...dists].sort(() => 0.5 - Math.random());
        const correctIdx = options.indexOf(coreAns);

        const qHash = Math.abs(qText.split('').reduce((a, b) => ((a << 5) - a) + b.charCodeAt(0), 0)).toString(36);
        const qId = `CA_${dateKey}_${qHash}`;

        parsedQuestions.push({
          id: qId,
          date: dateKey,
          display_date: displayDate,
          category: "current_affairs",
          topic: `करंट अफेयर (${displayDate})`,
          question: qText,
          options: options,
          correct_index: correctIdx,
          note: rawAns || coreAns,
          explanation: rawAns || coreAns,
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
          qObj = { q: "10 अप्रैल 1991 को जयपुर से अलग कर राजस्थान का 29वां जिला कौन-सा बना था?", ans: "दौसा", cat: "district" };
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

      // 5. Intelligent Topic Key-Value lines (Never generate generic header questions)
      const genericHeaders = ["विशेषता", "विवरण", "स्थान", "उद्देश्य", "परिचय", "महत्वपूर्ण तथ्य", "नोट", "प्रकार", "संदर्भ", "नाम", "उपाय", "कारण"];
      if (!qObj && line.includes(':')) {
        const parts = line.split(':');
        const k = parts[0].trim();
        const v = parts[1].trim();
        if (k.length > 2 && k.length < 35 && v.length > 2 && v.length < 50) {
          const isGeneric = genericHeaders.some(gh => k.toLowerCase() === gh || k.toLowerCase().startsWith(gh));
          if (!isGeneric) {
            const cleanV = v.split('(')[0].split('।')[0].trim();
            if (cleanV.length >= 2 && !cleanV.includes('\n')) {
              let cat = "district";
              let q = `राजस्थान के संदर्भ में, '${k}' किससे संबंधित है?`;
              if (DISTRACTORS.dam.some(d => line.includes(d.split(' ')[0]))) {
                cat = "dam";
                q = `'${k}' का संबंध राजस्थान के किस बांध या परियोजना से है?`;
              } else if (DISTRACTORS.river.some(r => line.includes(r.split(' ')[0]))) {
                cat = "river";
                q = `'${k}' का संबंध राजस्थान की किस नदी से है?`;
              } else if (DISTRACTORS.lake.some(l => line.includes(l.split(' ')[0]))) {
                cat = "lake";
                q = `'${k}' का संबंध किस झील से है?`;
              } else if (DISTRACTORS.cm.some(cm => line.includes(cm))) {
                cat = "cm";
                q = `'${k}' का संबंध किस मुख्यमंत्री से है?`;
              }
              qObj = { q, ans: cleanV, cat };
            }
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
          note: line,
          explanation: line,
          one_liner: `${qObj.q} ➔ **${qObj.ans}**`
        });
      }
    }

    return questions;
  }

  const ParserAPI = {
    extractDocId,
    getExportUrl,
    fetchGoogleDocText,
    parseCurrentAffairsText,
    parseChapterOrTextbookNotes,
    parsePureExaminerFactualNotes: parseCrispExaminerQuestions
  };

  window.TaiyariParser = ParserAPI;
  window.DocParser = ParserAPI;
  return ParserAPI;
})();
