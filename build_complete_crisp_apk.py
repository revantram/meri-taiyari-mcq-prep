import re
import json
import random
import os

print("==> 🚀 Starting Full Crisp APK Dataset Builder...")

# -------------------------------------------------------------
# 1. RAJASTHAN GEOGRAPHY - 23 CHAPTERS (CRISP EXAMINER QUESTIONS)
# -------------------------------------------------------------
with open('/data/user/0/com.termux/files/home/.gemini/antigravity-cli/scratch/meri-taiyari-app/raw_raj_geography.txt', 'r', encoding='utf-8') as f:
    geo_text = f.read().replace('\u200b', '').replace('\ufeff', '')

DISTRACTORS = {
    "km": ["1070 कि.मी.", "4850 कि.मी.", "5920 कि.मी.", "826 कि.मी.", "869 कि.मी.", "692 कि.मी.", "550 कि.मी.", "168 कि.मी.", "464 कि.मी.", "228 कि.मी.", "210 कि.मी."],
    "area": ["3,42,239 वर्ग कि.मी.", "1,32,139 वर्ग मील", "10.41%", "61.11%", "9.60%", "23.03%", "40%"],
    "cm": ["हीरालाल शास्त्री", "मोहनलाल सुखाड़िया", "हरिदेव जोशी", "भैरोंसिंह शेखावत", "जयनारायण व्यास", "टीकाराम पालीवाल", "शिवचरण माथुर", "भजनलाल शर्मा"],
    "committee": ["परमेश चन्द्र समिति", "रामलुभाया समिति", "ललित के. पंवार समिति", "पी. सत्यनारायण राव समिति", "हरिश्चंद्र माथुर समिति"],
    "district": ["जैसलमेर", "बाड़मेर", "बीकानेर", "जोधपुर", "जयपुर", "उदयपुर", "कोटा", "अजमेर", "भीलवाड़ा", "चित्तौड़गढ़", "डूंगरपुर", "बांसवाड़ा", "झालावाड़", "चूरू", "सीकर", "नागौर", "अलवर", "भरतपुर", "धौलपुर", "करौली", "सवाई माधोपुर", "टोंक", "पाली", "सिरोही", "जालौर", "प्रतापगढ़", "राजसमंद", "बूंदी", "बारां", "दौसा", "अनूपगढ़", "फलोदी", "बालोतरा", "सांचौर", "डीग", "सलूंबर"],
    "division": ["जयपुर संभाग", "अजमेर संभाग", "जोधपुर संभाग", "बीकानेर संभाग", "उदयपुर संभाग", "भरतपुर संभाग", "कोटा संभाग"],
    "peak": ["गुरुशिखर (1722 मी.)", "सेर (1597 मी.)", "दिलवाड़ा (1442 मी.)", "जरगा (1431 मी.)", "अचलगढ़ (1380 मी.)", "कुंभलगढ़ (1224 मी.)", "रघुनाथगढ़ (1055 मी.)", "ऋषिकेश (1017 मी.)", "कमलनाथ (1001 मी.)", "तारागढ़ (873 मी.)"],
    "river": ["चंबल नदी", "बनास नदी", "लूणी नदी", "माही नदी", "साबरमती नदी", "कालीसिंध नदी", "बाणगंगा नदी", "पार्वती नदी", "घग्घर नदी", "कांतली नदी", "सोम नदी", "जाखम नदी", "कोठारी नदी"],
    "dam": ["राणा प्रताप सागर बांध", "गांधी सागर बांध", "जवाहर सागर बांध", "कोटा बैराज", "बीसलपुर बांध", "जाखम बांध", "मेजा बांध", "पांचना बांध", "जवाई बांध"],
    "lake": ["सांभर झील", "पचपदरा झील", "डीडवाना झील", "लूणकरणसर झील", "जयसमंद झील", "राजसमंद झील", "पिछोला झील", "फतेहसागर झील", "आनासागर झील", "नक्की झील"],
    "soil": ["काली मृदा (वर्टिसोल)", "लाल-पीली मृदा", "जलोढ़ मृदा (एल्फीसोल)", "रेतीली शुष्क मृदा (एंटीसोल)", "भूरी रेतीली मृदा", "लवणीय मृदा"],
    "climate": ["शुष्क कटिबंधीय (BWhw)", "अर्ध-शुष्क स्टेपी (BShw)", "उप-आद्र मानसूनी (Cwa)", "अति-आद्र (Aw)"],
    "mineral": ["रॉक फॉस्फेट", "सीसा-जस्ता", "तांबा", "लोहा अयस्क", "टंगस्टन", "सफेद संगमरमर", "जिप्सम", "पन्ना"]
}

def pick_distractors(ans, cat):
    pool = DISTRACTORS.get(cat, DISTRACTORS["district"])
    ans_clean = str(ans).strip()
    cands = [d for d in pool if d.strip() != ans_clean]
    rng = random.Random(abs(hash(ans_clean)) % 1000)
    rng.shuffle(cands)
    return cands[:3]

# Split chapters
chapter_matches = list(re.finditer(r'(?m)^[ \t]*(अध्याय\s*[-–]?\s*\d+)[ \t]*\n[ \t]*[❀\*\-–•\s]*(.+?)[❀\*\-–•\s]*$', geo_text))

geo_chapters = []
geo_mcq_counter = 0

for i in range(len(chapter_matches)):
    ch_label = chapter_matches[i].group(1).strip()
    ch_title = chapter_matches[i].group(2).strip()
    start_pos = chapter_matches[i].end()
    end_pos = chapter_matches[i+1].start() if i+1 < len(chapter_matches) else len(geo_text)
    ch_text = geo_text[start_pos:end_pos].strip()

    lines = [l.strip('*•\t-– ') for l in ch_text.splitlines() if l.strip()]
    ch_questions = []

    # Extra for Chapter 23: Parse Nicknames Table
    if 'अध्याय-23' in ch_label or 'जिले और संभाग' in ch_title:
        # Table of nicknames
        nicknames_data = [
            ("जयपुर", "गुलाबी नगरी, पूर्व का पेरिस तथा रत्न नगरी", ["जोधपुर", "उदयपुर", "कोटा"]),
            ("जोधपुर", "सूर्य नगरी (Sun City) तथा नीला शहर (Blue City)", ["जयपुर", "बीकानेर", "जैसलमेर"]),
            ("उदयपुर", "झीलों की नगरी, पूर्व का वेनिस तथा व्हाइट सिटी", ["जयपुर", "अजमेर", "माउंट आबू"]),
            ("चित्तौड़गढ़", "राजस्थान का गौरव तथा शक्ति व भक्ति का नगर", ["उदयपुर", "कुंभलगढ़", "रणथंभौर"]),
            ("जैसलमेर", "स्वर्ण नगरी, झरोखों की नगरी तथा रेगिस्तान का गुलाब", ["बाड़मेर", "जोधपुर", "बीकानेर"]),
            ("अजमेर", "राजस्थान का हृदय, भारत का मक्का तथा अंडों की टोकरी", ["जयपुर", "पुष्कर", "टोंक"]),
            ("भीलवाड़ा", "राजस्थान का मैनचेस्टर, वस्त्र नगरी तथा अभ्रक नगरी", ["कोटा", "जयपुर", "पाली"]),
            ("कोटा", "राजस्थान का कानपुर, शिक्षा का तीर्थ तथा उद्यानों का नगर", ["जयपुर", "भीलवाड़ा", "जोधपुर"]),
            ("भरतपुर", "राजस्थान का प्रवेश द्वार तथा लोहागढ़", ["धौलपुर", "अलवर", "करौली"]),
            ("धौलपुर", "रेड डायमंड सिटी (Red Diamond)", ["करौली", "भरतपुर", "सवाई माधोपुर"]),
            ("अलवर", "राजस्थान का सिंह द्वार तथा स्कॉटलैंड ऑफ राजस्थान", ["भरतपुर", "जयपुर", "सीकर"]),
            ("बांसवाड़ा", "सौ द्वीपों का शहर तथा मानसून का प्रवेश द्वार", ["डूंगरपुर", "झालावाड़", "उदयपुर"]),
            ("डूंगरपुर", "पहाड़ों की नगरी", ["बांसवाड़ा", "सिरोही", "उदयपुर"]),
            ("झालावाड़", "राजस्थान का नागपुर (संतरा उत्पादन हेतु) तथा विरासत का शहर", ["कोटा", "बांसवाड़ा", "बारां"]),
            ("झालरापाटन", "घंटियों का शहर (City of Bells)", ["झालावाड़", "बूंदी", "पुष्कर"]),
            ("बूंदी", "बावड़ियों का शहर (City of Stepwells) तथा छोटी काशी", ["टोंक", "कोटा", "झालरापाटन"]),
            ("गंगानगर", "राजस्थान का अन्नागार तथा धान का कटोरा", ["हनुमानगढ़", "अनूपगढ़", "बीकानेर"]),
            ("जालौर", "राजस्थान की ग्रेनाइट सिटी तथा सुवर्णगिरि", ["सिरोही", "बाड़मेर", "पाली"]),
            ("बाड़मेर", "राजस्थान का दुबई तथा थार का खजुराहो (किराडू हेतु)", ["जैसलमेर", "बीकानेर", "जालौर"]),
            ("टोंक", "नवाबों का शहर तथा प्राचीन भारत का टाटानगर", ["अजमेर", "सवाई माधोपुर", "जयपुर"]),
            ("माउंट आबू", "राजस्थान का शिमला", ["सिरोही", "उदयपुर", "कुंभलगढ़"]),
            ("करौली", "डांग की रानी", ["धौलपुर", "सवाई माधोपुर", "दौसा"]),
            ("किराडू (बाड़मेर)", "राजस्थान का खजुराहो", ["जगत (उदयपुर)", "भंडदेवरा (बारां)", "ओसियां"]),
            ("जगत (उदयपुर)", "मेवाड़ का खजुराहो", ["किराडू (बाड़मेर)", "भंडदेवरा (बारां)", "रणकपुर"]),
            ("भंडदेवरा (बारां)", "राजस्थान का मिनी खजुराहो / हाड़ौती का खजुराहो", ["किराडू (बाड़मेर)", "जगत (उदयपुर)", "बाडोली"]),
            ("चांदन नलकूप (जैसलमेर)", "थार का घड़ा", ["बटाडू का कुआं", "नक्की झील", "पोकरण"]),
            ("भैंसरोडगढ़", "राजस्थान का वेल्लोर", ["चित्तौड़गढ़", "कुंभलगढ़", "मेहरानगढ़"])
        ]
        for place, nick, dists in nicknames_data:
            geo_mcq_counter += 1
            opts = [place] + dists
            rng = random.Random(abs(hash(place)) % 999)
            rng.shuffle(opts)
            c_idx = opts.index(place)
            ch_questions.append({
                "id": f"CRISP_Q_{geo_mcq_counter}",
                "chapter_id": f"geo_ch_{i+1}",
                "topic": f"{ch_label}: {ch_title}",
                "question": f"राजस्थान में '{nick}' के उपनाम से किसे जाना जाता है?",
                "options": opts,
                "correct_index": c_idx,
                "explanation": f"✅ **सही उत्तर:** {place}\n\n📌 **परीक्षा संदर्भ:** {ch_label} - {ch_title}\n\n📖 **एग्जामिनर व्याख्या:** {place} को '{nick}' कहा जाता है। यह राजस्थान प्रतियोगी परीक्षाओं (RPSC/RSSB) का अत्यंत महत्वपूर्ण तथ्य है।",
                "mnemonic": f"💡 **याद रखने की ट्रिक:** '{nick}' ➔ {place}",
                "one_liner": f"राजस्थान में '{nick}' किसे कहा जाता है? ➔ **{place}**"
            })

    # Line by line processing for crisp questions
    for line in lines:
        if line.startswith('❀') or len(line) < 10 or line.endswith(':'):
            continue

        q_obj = None

        # 1. Chief Minister
        for cm in DISTRACTORS["cm"]:
            if cm in line:
                if 'शुरुआत' in line or '1949' in line:
                    q = "राजस्थान में संभागीय व्यवस्था की शुरुआत (1949) किस मुख्यमंत्री के कार्यकाल में हुई थी?"
                elif 'समाप्ति' in line or '1962' in line:
                    q = "अप्रैल 1962 में राजस्थान की संभागीय व्यवस्था को किस मुख्यमंत्री ने समाप्त कर दिया था?"
                elif 'पुनः' in line or '1987' in line or 'दोबारा' in line:
                    q = "15 जनवरी 1987 को राजस्थान में संभागीय व्यवस्था को पुनः किस मुख्यमंत्री ने शुरू किया था?"
                else:
                    q = f"राजस्थान में '{line.split(':')[0].strip()}' का संबंध किस मुख्यमंत्री से है?"
                ans = cm
                dists = pick_distractors(ans, "cm")
                q_obj = (q, ans, dists, "cm")
                break

        # 2. Committee
        if not q_obj:
            for comm in DISTRACTORS["committee"]:
                if comm in line:
                    if 'प्रतापगढ़' in line or '33' in line:
                        q = "राजस्थान का 33वां जिला 'प्रतापगढ़' (2008) किस समिति की सिफारिश पर गठित किया गया था?"
                    elif 'मार्च 2022' in line or '17 नए' in line:
                        q = "राजस्थान में नए जिलों के गठन हेतु मार्च 2022 में किस समिति का गठन किया गया था?"
                    elif 'जून 2024' in line or 'समीक्षा' in line:
                        q = "जून 2024 में नए जिलों के पुनर्गठन एवं समीक्षा हेतु किस समिति का गठन किया गया?"
                    else:
                        q = f"राजस्थान में '{line.split(':')[0].strip()}' के लिए किस समिति की सिफारिश प्रभावी रही?"
                    ans = comm
                    dists = pick_distractors(ans, "committee")
                    q_obj = (q, ans, dists, "committee")
                    break

        # 3. Divisions
        if not q_obj:
            if 'छठा संभाग' in line or ('अजमेर' in line and '1987' in line and 'संभाग' in line):
                q = "वर्ष 1987 में जयपुर से अलग कर राजस्थान का 6ठा संभाग किसे बनाया गया था?"
                ans = "अजमेर संभाग"
                dists = ["कोटा संभाग", "भरतपुर संभाग", "बीकानेर संभाग"]
                q_obj = (q, ans, dists, "division")
            elif '7वां संभाग' in line or ('भरतपुर' in line and '2005' in line and 'संभाग' in line):
                q = "4 जून 2005 को राजस्थान का 7वां संभाग कौन-सा घोषित किया गया था?"
                ans = "भरतपुर संभाग"
                dists = ["अजमेर संभाग", "कोटा संभाग", "उदयपुर संभाग"]
                q_obj = (q, ans, dists, "division")

        # 4. District Formations
        if not q_obj:
            if '26 वां जिला' in line or '1 नवंबर 1956' in line:
                q = "1 नवंबर 1956 को राजस्थान के पुनर्गठन के समय राज्य का 26वां जिला कौन-सा बना था?"
                ans = "अजमेर"
                dists = ["धौलपुर", "सिरोही", "जयपुर"]
                q_obj = (q, ans, dists, "district")
            elif '27 वां जिला' in line or ('धौलपुर' in line and '1982' in line):
                q = "15 अप्रैल 1982 को राजस्थान का 27वां जिला 'धौलपुर' किस जिले से अलग करके बनाया गया था?"
                ans = "भरतपुर"
                dists = ["सवाई माधोपुर", "करौली", "अलवर"]
                q_obj = (q, ans, dists, "district")
            elif '28वां जिला' in line or ('बारां' in line and '1991' in line):
                q = "10 अप्रैल 1991 को कोटा से अलग कर राजस्थान का 28वां जिला कौन-सा बनाया गया?"
                ans = "बारां"
                dists = ["दौसा", "राजसमंद", "झालावाड़"]
                q_obj = (q, ans, dists, "district")
            elif '29 वां जिला' in line or ('दौसा' in line and '1991' in line):
                q = "10 अप्रैल 1991 को जयपुर से अलग कर राजस्थान का 29वां जिला कौन-सा बना था?"
                ans = "दौसा"
                dists = ["बारां", "अलवर", "टोंक"]
                q_obj = (q, ans, dists, "district")
            elif '30वां जिला' in line or ('राजसमंद' in line and '1991' in line):
                q = "10 अप्रैल 1991 को उदयपुर से अलग कर राजस्थान का 30वां जिला कौन-सा बना?"
                ans = "राजसमंद"
                dists = ["भीलवाड़ा", "पाली", "सलूंबर"]
                q_obj = (q, ans, dists, "district")
            elif '31 वां जिला' in line or ('हनुमानगढ़' in line and '1994' in line):
                q = "12 जुलाई 1994 को श्रीगंगानगर से अलग कर राजस्थान का 31वां जिला कौन-सा बनाया गया?"
                ans = "हनुमानगढ़"
                dists = ["अनूपगढ़", "चूरू", "बीकानेर"]
                q_obj = (q, ans, dists, "district")
            elif '32 वां जिला' in line or ('करौली' in line and '1997' in line):
                q = "19 जुलाई 1997 को सवाई माधोपुर से अलग करके राजस्थान का 32वां जिला कौन-सा बना था?"
                ans = "करौली"
                dists = ["धौलपुर", "दौसा", "टोंक"]
                q_obj = (q, ans, dists, "district")
            elif '33 वां जिला' in line or ('प्रतापगढ़' in line and '2008' in line):
                q = "26 जनवरी 2008 को राजस्थान का 33वां जिला कौन-सा गठित किया गया था?"
                ans = "प्रतापगढ़"
                dists = ["डूंगरपुर", "बांसवाड़ा", "सलूंबर"]
                q_obj = (q, ans, dists, "district")

        # 5. Geography Boundaries & Dimensions
        if not q_obj:
            if 'उत्तर से दक्षिण की लंबाई' in line or '826' in line:
                q = "राजस्थान की उत्तर से दक्षिण तक कुल लंबाई कितनी है?"
                ans = "826 कि.मी."
                dists = ["869 कि.मी.", "1070 कि.मी.", "692 कि.मी."]
                q_obj = (q, ans, dists, "km")
            elif 'पूर्व से पश्चिम की चौड़ाई' in line or '869' in line:
                q = "राजस्थान की पूर्व से पश्चिम तक कुल चौड़ाई कितनी है?"
                ans = "869 कि.मी."
                dists = ["826 कि.मी.", "1070 कि.मी.", "550 कि.मी."]
                q_obj = (q, ans, dists, "km")
            elif 'कुल क्षेत्रफल' in line or '3,42,239' in line:
                q = "राजस्थान का कुल भौगोलिक क्षेत्रफल कितना है?"
                ans = "3,42,239 वर्ग कि.मी."
                dists = ["2,42,239 वर्ग कि.मी.", "3,82,239 वर्ग कि.मी.", "4,42,239 वर्ग कि.मी."]
                q_obj = (q, ans, dists, "area")
            elif '10.41%' in line or 'भारत के कुल क्षेत्रफल का' in line:
                q = "राजस्थान का क्षेत्रफल भारत के कुल क्षेत्रफल का कितना प्रतिशत है?"
                ans = "10.41%"
                dists = ["9.60%", "11.20%", "12.45%"]
                q_obj = (q, ans, dists, "area")
            elif 'अंतर्राष्ट्रीय सीमा' in line or '1070' in line:
                q = "राजस्थान की पाकिस्तान के साथ अंतरराष्ट्रीय सीमा (रेडक्लिफ रेखा) की कुल लंबाई कितनी है?"
                ans = "1070 कि.मी."
                dists = ["4850 कि.मी.", "5920 कि.मी.", "1020 कि.मी."]
                q_obj = (q, ans, dists, "km")
            elif 'कुल स्थलीय सीमा' in line or '5920' in line:
                q = "राजस्थान की कुल स्थलीय सीमा की लंबाई कितनी है?"
                ans = "5920 कि.मी."
                dists = ["4850 कि.मी.", "1070 कि.मी.", "6200 कि.मी."]
                q_obj = (q, ans, dists, "km")
            elif 'अंतरराज्यीय सीमा' in line or '4850' in line:
                q = "राजस्थान की कुल अंतरराज्यीय सीमा (5 पड़ोसी राज्यों के साथ) कितनी है?"
                ans = "4850 कि.मी."
                dists = ["5920 कि.मी.", "1070 कि.मी.", "4250 कि.मी."]
                q_obj = (q, ans, dists, "km")
            elif 'कर्क रेखा' in line and ('बांसवाड़ा' in line or 'डूंगरपुर' in line):
                q = "कर्क रेखा (23½° उत्तरी अक्षांश) राजस्थान के किन दक्षिणी जिलों से होकर गुजरती है?"
                ans = "बांसवाड़ा और डूंगरपुर"
                dists = ["उदयपुर और प्रतापगढ़", "झालावाड़ और कोटा", "जालौर और सिरोही"]
                q_obj = (q, ans, dists, "district")

        # 6. Mountain Peaks
        if not q_obj:
            for pk in DISTRACTORS["peak"]:
                pk_clean = pk.split('(')[0].strip()
                if pk_clean in line and ('ऊंचाई' in line or 'चोटी' in line or 'अरावली' in line or 'मी.' in line):
                    if pk_clean == "गुरुशिखर":
                        q = "अरावली पर्वतमाला तथा राजस्थान की सर्वोच्च पर्वत चोटी 'गुरुशिखर' (1722 मीटर) किस जिले में है?"
                        ans = "सिरोही"
                        dists = ["उदयपुर", "राजसमंद", "जयपुर"]
                        q_obj = (q, ans, dists, "district")
                    elif pk_clean == "रघुनाथगढ़":
                        q = "उत्तरी अरावली की सबसे ऊंची चोटी 'रघुनाथगढ़' (1055 मीटर) किस जिले में स्थित है?"
                        ans = "सीकर"
                        dists = ["झुंझुनूं", "अलवर", "जयपुर"]
                        q_obj = (q, ans, dists, "district")
                    elif pk_clean == "जरगा":
                        q = "भोराट के पठार पर स्थित अरावली की प्रमुख चोटी 'जरगा' (1431 मीटर) किस जिले में है?"
                        ans = "उदयपुर"
                        dists = ["सिरोही", "राजसमंद", "पाली"]
                        q_obj = (q, ans, dists, "district")
                    else:
                        q = f"अरावली पर्वतमाला की प्रमुख चोटी '{pk_clean}' की प्रामाणिक ऊंचाई कितनी है?"
                        ans = pk
                        dists = pick_distractors(ans, "peak")
                        q_obj = (q, ans, dists, "peak")
                    break

        # 7. Dams & Rivers
        if not q_obj:
            if 'पांचना बांध' in line:
                q = "एशिया का सबसे बड़ा मिट्टी का बांध 'पांचना बांध' किस जिले में स्थित है?"
                ans = "करौली"
                dists = ["सवाई माधोपुर", "धौलपुर", "दौसा"]
                q_obj = (q, ans, dists, "district")
            elif 'बीसलपुर' in line:
                q = "राजस्थान की सबसे बड़ी पेयजल परियोजना 'बीसलपुर बांध' किस नदी पर स्थित है?"
                ans = "बनास नदी"
                dists = ["चंबल नदी", "लूणी नदी", "माही नदी"]
                q_obj = (q, ans, dists, "river")
            elif 'राणा प्रताप सागर' in line:
                q = "राजस्थान में भराव क्षमता की दृष्टि से सबसे बड़ा बांध 'राणा प्रताप सागर' कहाँ स्थित है?"
                ans = "चित्तौड़गढ़ (रावतभाटा)"
                dists = ["कोटा", "बूंदी", "झालावाड़"]
                q_obj = (q, ans, dists, "district")
            elif 'जाखम बांध' in line:
                q = "राजस्थान का सबसे ऊंचा बांध (81 मीटर) 'जाखम बांध' किस जिले में स्थित है?"
                ans = "प्रतापगढ़"
                dists = ["बांसवाड़ा", "डूंगरपुर", "उदयपुर"]
                q_obj = (q, ans, dists, "district")
            elif 'माही बजाज सागर' in line:
                q = "राजस्थान का सबसे लंबा बांध (3109 मीटर) 'माही बजाज सागर बांध' किस जिले में स्थित है?"
                ans = "बांसवाड़ा (बोरखेड़ा)"
                dists = ["डूंगरपुर", "प्रतापगढ़", "उदयपुर"]
                q_obj = (q, ans, dists, "district")

        # 8. Lakes
        if not q_obj:
            if 'सांभर झील' in line:
                q = "भारत के कुल नमक उत्पादन का लगभग 8.7% नमक किस झील से उत्पादित होता है?"
                ans = "सांभर झील"
                dists = ["पचपदरा झील", "डीडवाना झील", "लूणकरणसर झील"]
                q_obj = (q, ans, dists, "lake")
            elif 'पचपदरा' in line:
                q = "राजस्थान की किस झील के नमक में 98% सोडियम क्लोराइड (NaCl) पाया जाता है?"
                ans = "पचपदरा झील (बालोतरा)"
                dists = ["सांभर झील", "डीडवाना झील", "कावोध झील"]
                q_obj = (q, ans, dists, "lake")
            elif 'जयसमंद' in line or 'ढेबर' in line:
                q = "राजस्थान की सबसे बड़ी मीठे पानी की कृत्रिम झील (ढेबर झील) कौन-सी है?"
                ans = "जयसमंद झील (सलूंबर)"
                dists = ["राजसमंद झील", "पिछोला झील", "फतेहसागर झील"]
                q_obj = (q, ans, dists, "lake")
            elif 'नक्की झील' in line:
                q = "राजस्थान की सर्वाधिक ऊंचाई (1200 मीटर) पर स्थित सबसे गहरी प्राकृतिक झील कौन-सी है?"
                ans = "नक्की झील (माउंट आबू)"
                dists = ["सिलीसेढ़ झील", "आनासागर झील", "फायसागर झील"]
                q_obj = (q, ans, dists, "lake")

        # 9. Minerals
        if not q_obj:
            if 'झामर-कोटड़ा' in line or 'रॉक फॉस्फेट' in line:
                q = "राजस्थान में प्रसिद्ध 'झामर-कोटड़ा' खान किस खनिज के उत्पादन हेतु प्रसिद्ध है?"
                ans = "रॉक फॉस्फेट"
                dists = ["सीसा-जस्ता", "तांबा", "टंगस्टन"]
                q_obj = (q, ans, dists, "mineral")
            elif 'जावर' in line and ('सीसा' in line or 'जस्ता' in line):
                q = "राजस्थान में महाराणा लाखा के काल से प्रसिद्ध 'जावर' की खानें किस खनिज के लिए जानी जाती हैं?"
                ans = "सीसा-जस्ता एवं चांदी"
                dists = ["तांबा", "लोहा अयस्क", "रॉक फॉस्फेट"]
                q_obj = (q, ans, dists, "mineral")
            elif 'डेगाना' in line or 'टंगस्टन' in line:
                q = "राजस्थान में 'टंगस्टन' की प्रसिद्ध रेवंत पहाड़ी 'डेगाना' किस जिले में स्थित है?"
                ans = "नागौर"
                dists = ["बीकानेर", "जोधपुर", "पाली"]
                q_obj = (q, ans, dists, "district")
            elif 'खेतड़ी' in line or 'ताम्र' in line:
                q = "राजस्थान की प्रसिद्ध 'ताम्र नगरी' खेतड़ी-सिंघाना किस जिले में स्थित है?"
                ans = "नीम का थाना (झुंझुनूं)"
                dists = ["अलवर", "सीकर", "चूरू"]
                q_obj = (q, ans, dists, "district")
            elif 'मकराना' in line or 'संगमरमर' in line:
                q = "विश्व प्रसिद्ध कैल्साइट सफेद संगमरमर (ताजमहल हेतु) राजस्थान के किस स्थान से प्राप्त हुआ था?"
                ans = "मकराना (डीडवाना-कुचामन)"
                dists = ["राजसमंद", "उदयपुर", "किशनगढ़"]
                q_obj = (q, ans, dists, "district")

        # 10. Research Institutes
        if not q_obj:
            if 'काजरी' in line or 'CAZRI' in line:
                q = "केन्द्रीय शुष्क क्षेत्र अनुसंधान संस्थान (काजरी / CAZRI) कहाँ स्थित है?"
                ans = "जोधपुर"
                dists = ["बीकानेर", "जयपुर", "अजमेर"]
                q_obj = (q, ans, dists, "district")
            elif 'आफरी' in line or 'AFRI' in line:
                q = "शुष्क वन अनुसंधान संस्थान (आफरी / AFRI) का मुख्यालय कहाँ स्थित है?"
                ans = "जोधपुर"
                dists = ["उदयपुर", "कोटा", "पाली"]
                q_obj = (q, ans, dists, "district")
            elif 'सरसों' in line or 'सेवर' in line:
                q = "राष्ट्रीय सरसों अनुसंधान निदेशालय (DRMR) राजस्थान के किस स्थान पर स्थित है?"
                ans = "सेवर (भरतपुर)"
                dists = ["तबीजी (अजमेर)", "बोरखेड़ा (कोटा)", "सूरतगढ़ (श्रीगंगानगर)"]
                q_obj = (q, ans, dists, "district")
            elif 'मसाला' in line or 'तबीजी' in line:
                q = "राष्ट्रीय बीजीय मसाला अनुसंधान केंद्र (NRCSS) कहाँ स्थित है?"
                ans = "तबीजी (अजमेर)"
                dists = ["सेवर (भरतपुर)", "अविकानगर (टोंक)", "मंडोर (जोधपुर)"]
                q_obj = (q, ans, dists, "district")
            elif 'अविकानगर' in line or 'भेड़' in line:
                q = "केन्द्रीय भेड़ एवं ऊन अनुसंधान संस्थान (CSWRI) कहाँ स्थित है?"
                ans = "अविकानगर (टोंक)"
                dists = ["जोहड़बीड़ (बीकानेर)", "बिलाड़ा (जोधपुर)", "फतेहपुर (सीकर)"]
                q_obj = (q, ans, dists, "district")

        # 11. General Key : Value line
        if not q_obj and ':' in line:
            parts = line.split(':', 1)
            k = parts[0].strip()
            v = parts[1].strip()
            if 3 < len(k) < 30 and 2 < len(v) < 40 and not any(ch in v for ch in ['{', '}', '[', ']']):
                clean_ans = v.split('(')[0].split('।')[0].strip()
                if len(clean_ans) > 2:
                    if 'जिला' in k:
                        q = f"राजस्थान में '{k}' के रूप में किस जिले को जाना जाता है?"
                        ans = clean_ans
                        dists = pick_distractors(ans, "district")
                    elif 'संभाग' in k:
                        q = f"राजस्थान प्रशासनिक व्यवस्था के अनुसार '{k}' के अंतर्गत प्रमुख स्थिति क्या है?"
                        ans = clean_ans
                        dists = pick_distractors(ans, "division")
                    else:
                        q = f"राजस्थान सामान्य ज्ञान ({ch_title}) के अनुसार, '{k}' का सही मान / विवरण क्या है?"
                        ans = clean_ans
                        dists = pick_distractors(ans, "district")
                    q_obj = (q, ans, dists, "general")

        if q_obj:
            q_text, ans, dists, cat = q_obj
            opts = [ans] + dists[:3]
            rng = random.Random(abs(hash(q_text)) % 9999)
            rng.shuffle(opts)
            c_idx = opts.index(ans)

            geo_mcq_counter += 1
            ch_questions.append({
                "id": f"CRISP_Q_{geo_mcq_counter}",
                "chapter_id": f"geo_ch_{i+1}",
                "topic": f"{ch_label}: {ch_title}",
                "question": q_text,
                "options": opts,
                "correct_index": c_idx,
                "explanation": f"✅ **सही उत्तर:** {ans}\n\n📌 **परीक्षा संदर्भ:** {ch_label} - {ch_title}\n\n📖 **एग्जामिनर व्याख्या:** {line}",
                "mnemonic": f"💡 **याद रखने की ट्रिक:** मुख्य बिंदु '{ans}' को ध्यान में रखें।",
                "one_liner": f"{q_text} ➔ **{ans}**"
            })

    # Deduplicate
    seen_q = set()
    unique_list = []
    for q in ch_questions:
        if q["question"] not in seen_q:
            seen_q.add(q["question"])
            unique_list.append(q)

    geo_chapters.append({
        "id": f"geo_ch_{i+1}",
        "number": i + 1,
        "title": f"{ch_label}: {ch_title}",
        "raw_title": ch_title,
        "questions": unique_list
    })

print(f"==> Rajasthan Geography Processed: 23 Chapters, {sum(len(c['questions']) for c in geo_chapters)} Crisp MCQs.")


# -------------------------------------------------------------
# 2. NATIONAL CURRENT AFFAIRS - DOMAIN-TYPED CRISP MCQS
# -------------------------------------------------------------
with open('/data/user/0/com.termux/files/home/.gemini/antigravity-cli/scratch/meri-taiyari-app/raw_national_ca.txt', 'r', encoding='utf-8') as f:
    nca_text = f.read().replace('\u200b', '').replace('\ufeff', '')

NCA_DOMAINS = {
    "intl_city": ["बीजिंग (चीन)", "टोक्यो (जापान)", "सिंगापुर", "शेंजेन (चीन)", "रियाद (सऊदी अरब)", "बैंकॉक (थाईलैंड)", "जिनेवा (स्विट्जरलैंड)", "पेरिस (फ्रांस)", "वाशिंगटन (यूएसए)", "दुबई (यूएई)", "लंदन (यूके)"],
    "university": ["लुंड यूनिवर्सिटी (स्वीडन)", "हार्वर्ड यूनिवर्सिटी (यूएसए)", "ऑक्सफोर्ड यूनिवर्सिटी (यूके)", "मैसाचुसेट्स इंस्टीट्यूट ऑफ टेक्नोलॉजी (MIT)", "कैम्ब्रिज यूनिवर्सिटी", "टोक्यो यूनिवर्सिटी", "IIT बॉम्बे", "IIT दिल्ली", "IISc बेंगलुरु"],
    "country": ["फिजी", "रूस", "मॉरीशस", "बांग्लादेश", "श्रीलंका", "जापान", "अमेरिका", "फ्रांस", "जर्मनी", "ऑस्ट्रेलिया", "नेपाल", "भूटान"],
    "person_group": ["क्रिकेट से वैभव सूर्यवंशी, विज्ञान से शुभांशु शुक्ला", "भाला फेंक से नीरज चोपड़ा, निशानेबाजी से मनु भाकर", "कुश्ती से अमन सहरावत, मुक्केबाजी से लवलीना", "बैडमिंटन से लक्ष्य सेन, शतरंज से डी. गुकेश"],
    "rocket": ["PSLV-C58", "GSLV-F18", "LVM3-M4", "SSLV-D3", "Falcon-9", "Ariane-6"],
    "satellite": ["NVS-03", "EOS-08", "Aditya-L1", "XPoSat", "INSAT-3DS", "GSAT-20"],
    "actor": ["रणवीर सिंह", "शाहरुख खान", "अल्लू अर्जुन", "विक्की कौशल", "ऋतिक रोशन", "रणबीर कपूर"],
    "actress": ["दीपिका पादुकोण", "आलिया भट्ट", "कृति सेनन", "कियारा आडवाणी", "रानी मुखर्जी"],
    "film": ["धुरंधर", "जवान", "पुष्पा 2", "12th Fail", "कल्कि 2898 AD", "एनिमल"],
    "director": ["आदित्य धर", "संदीप रेड्डी वांगा", "एटली", "प्रशांत नील", "एस. एस. राजामौली"],
    "city": ["श्री विजयापुरम", "विशाखापट्टनम", "कोच्चि", "मुंबई", "चेन्नई", "कोलकाता", "नई दिल्ली", "अहमदाबाद", "जयपुर", "बेंगलुरु"],
    "state": ["गुजरात", "महाराष्ट्र", "उत्तर प्रदेश", "मध्य प्रदेश", "राजस्थान", "कर्नाटक", "तमिलनाडु", "असम", "ओडिशा", "केरल"],
    "planet": ["मंगल ग्रह", "चंद्रमा", "शुक्र ग्रह", "बुध ग्रह", "बृहस्पति"],
    "person": ["प्रशांत चौधरी", "अशोक गाडगिल", "दीनानाथ राजपूत", "डॉ. सौम्या स्वामीनाथन", "के. राधाकृष्णन", "एस. सोमनाथ", "अनिल चौहान"],
    "sports": ["भारत", "ईरान", "पाकिस्तान", "केन्या", "इंग्लैंड", "ऑस्ट्रेलिया"],
    "rank": ["प्रथम (1st)", "द्वितीय (2nd)", "तृतीय (3rd)", "चौथा (4th)", "पाँचवाँ (5th)"],
    "month_day": ["1 नवंबर", "24 अक्टूबर", "15 अगस्त", "2 अक्टूबर", "26 जनवरी", "5 जून"],
    "number": ["8 राज्य एवं 5 केंद्र शासित प्रदेश", "7 राज्य एवं 4 केंद्र शासित प्रदेश", "9 राज्य एवं 6 केंद्र शासित प्रदेश", "10 राज्य एवं 3 केंद्र शासित प्रदेश"],
    "defense": ["पहला बिम्सटेक अभ्यास", "वरुण अभ्यास 2026", "इंद्र अभ्यास 2026", "मालाबार 2026", "सूर्य किरण", "युद्ध अभ्यास"],
    "corridor": ["उत्तरी बुलेट ट्रेन कॉरिडोर", "पूर्वी बुलेट ट्रेन कॉरिडोर", "पश्चिमी बुलेट ट्रेन कॉरिडोर", "दक्षिणी बुलेट ट्रेन कॉरिडोर"]
}

def detect_nca_domain(q_text, ans_text):
    combo = (q_text + " " + ans_text).lower()
    if any(k in combo for k in ["किस देश", "देश के", "देश द्वारा", "नामकरण किस देश"]):
        return "country"
    if any(k in combo for k in ["विश्वविद्यालय", "यूनिवर्सिटी", "रैंकिंग", "संस्थान", "iit", "qs"]):
        return "university"
    if any(k in combo for k in ["खिलाड़ी", "वैज्ञानिक", "time 100", "शामिल किया", "सूची"]):
        return "person_group"
    if any(k in combo for k in ["कहाँ आयोजित", "मीटिंग", "सम्मेलन", "शिखर", "apec", "g20", "ब्रिक्स"]):
        return "intl_city"
    if any(k in combo for k in ["रॉकेट", "gslv", "pslv", "lv"]):
        return "rocket"
    if any(k in combo for k in ["उपग्रह", "satellite", "nvs"]):
        return "satellite"
    if any(k in combo for k in ["अभिनेता", "actor"]):
        return "actor"
    if any(k in combo for k in ["अभिनेत्री", "actress"]):
        return "actress"
    if any(k in combo for k in ["सर्वश्रेष्ठ फिल्म", "मूवी", "धुरंधर"]):
        return "film"
    if any(k in combo for k in ["निर्देशक", "director"]):
        return "director"
    if any(k in combo for k in ["ग्रह", "उल्कापिंड", "मंगल", "चंद्रमा"]):
        return "planet"
    if any(k in combo for k in ["बुलेट ट्रेन", "कॉरिडोर"]):
        return "corridor"
    if any(k in combo for k in ["अभ्यास", "नौसैनिक अभ्यास", "सैन्य अभ्यास"]):
        return "defense"
    if any(k in combo for k in ["कितने राज्य", "केंद्र शासित"]):
        return "number"
    if any(k in combo for k in ["राज्य में", "किस राज्य"]):
        return "state"
    if any(k in combo for k in ["कबड्डी", "क्रिकेट", "विजेता", "चैंपियन"]):
        return "sports"
    if any(k in combo for k in ["पुरस्कार", "किसे प्रदान", "अध्यक्ष", "महानिदेशक", "संस्थापक", "चौधरी"]):
        return "person"
    return "city"

date_pattern = r'(?m)^[ \t]*([0-9]{1,2})\s*[-–]?\s*(नवंबर|अक्टूबर|सितंबर|अगस्त|जुलाई|जून|मई|अप्रैल|मार्च|फरवरी|जनवरी)[ \t]*$'
date_matches = list(re.finditer(date_pattern, nca_text))

month_num_map = {
    'जनवरी': '01', 'फरवरी': '02', 'मार्च': '03', 'अप्रैल': '04',
    'मई': '05', 'जून': '06', 'जुलाई': '07', 'अगस्त': '08',
    'सितंबर': '09', 'अक्टूबर': '10', 'नवंबर': '11', 'दिसंबर': '12'
}

nca_dates_dict = {}
nca_q_counter = 0

for idx in range(len(date_matches)):
    day_num = int(date_matches[idx].group(1))
    month_name = date_matches[idx].group(2)
    month_num = month_num_map[month_name]
    iso_date = f"2026-{month_num}-{day_num:02d}"

    start_pos = date_matches[idx].end()
    end_pos = date_matches[idx+1].start() if idx+1 < len(date_matches) else len(nca_text)
    day_text = nca_text[start_pos:end_pos].strip()

    qa_blocks = re.split(r'(?m)^\s*(?:[0-9]+\.|\*)\s*प्रश्न:', day_text)
    day_questions = []

    for blk in qa_blocks[1:]:
        blk_lines = [l.strip() for l in blk.strip().splitlines() if l.strip()]
        if not blk_lines:
            continue
        q_line = blk_lines[0].strip()

        # Find answer line
        ans_raw = ""
        ans_idx = -1
        for l_idx, l in enumerate(blk_lines[1:], start=1):
            if "उत्तर:" in l or l.startswith("उत्तर:") or l.startswith("* उत्तर:"):
                ans_raw = l.replace("*", "").replace("उत्तर:", "").strip()
                ans_idx = l_idx
                # If answer was just empty header "उत्तर:", look for next sub-bullet
                if not ans_raw and l_idx < len(blk_lines) - 1:
                    sub_line = blk_lines[l_idx + 1].strip('*•\t ')
                    if ':' in sub_line:
                        sub_parts = sub_line.split(':', 1)
                        ans_raw = sub_parts[1].strip()
                    else:
                        ans_raw = sub_line
                break

        if not ans_raw and len(blk_lines) > 1:
            ans_raw = blk_lines[1].strip('*•\t ')

        if not ans_raw:
            continue

        # Extract core answer
        core_ans = ans_raw.split('(')[0].split('।')[0].strip()
        if ':' in core_ans:
            core_ans = core_ans.split(':', 1)[1].strip()
        core_ans = core_ans.strip(" '\"*•")

        if not core_ans or len(core_ans) < 2 or core_ans in ["उत्तर", "उत्तर:", "निम्न", "निम्नलिखित"]:
            continue

        domain = detect_nca_domain(q_line, core_ans)
        pool = NCA_DOMAINS.get(domain, NCA_DOMAINS["city"])
        dists = [d for d in pool if d.strip() != core_ans]
        rng = random.Random(abs(hash(q_line)) % 1000)
        rng.shuffle(dists)
        chosen_dists = dists[:3]

        opts = [core_ans] + chosen_dists
        rng.shuffle(opts)
        c_idx = opts.index(core_ans)

        nca_q_counter += 1
        explanation_body = "\n".join(blk_lines[ans_idx:]) if ans_idx != -1 else ans_raw

        day_questions.append({
            "id": f"NCA_Q_{nca_q_counter}",
            "date": iso_date,
            "topic": f"करंट अफेयर ({day_num} {month_name} 2026)",
            "question": q_line,
            "options": opts,
            "correct_index": c_idx,
            "explanation": f"✅ **सही उत्तर:** {core_ans}\n\n📌 **परीक्षा संदर्भ:** समसामयिकी {day_num} {month_name} 2026\n\n📖 **एग्जामिनर व्याख्या:** {ans_raw}",
            "mnemonic": f"💡 **याद रखने की ट्रिक:** मुख्य बिंदु '{core_ans}' को परीक्षा संदर्भ से जोड़ें।",
            "one_liner": f"{q_line} ➔ **{core_ans}**"
        })

    if day_questions:
        nca_dates_dict[iso_date] = {
            "date": iso_date,
            "display_date": f"{day_num} {month_name} 2026",
            "questions": day_questions,
            "total_questions": len(day_questions)
        }

print(f"==> National Current Affairs Processed: {len(nca_dates_dict)} Dates, {nca_q_counter} Crisp MCQs.")


# -------------------------------------------------------------
# 2B. RAJASTHAN CURRENT AFFAIRS - CRISP MCQS
# -------------------------------------------------------------
with open('/data/user/0/com.termux/files/home/.gemini/antigravity-cli/scratch/meri-taiyari-app/raw_rajasthan_ca.txt', 'r', encoding='utf-8') as f:
    raj_ca_text = f.read().replace('\u200b', '').replace('\ufeff', '')

DISTRACTORS_RAJ = {
    'district': ['जयपुर', 'जोधपुर', 'उदयपुर', 'बीकानेर', 'कोटा', 'अजमेर', 'भीलवाड़ा', 'फलौदी', 'जैसलमेर', 'बाड़मेर', 'डूंगरपुर', 'बांसवाड़ा', 'सीकर', 'झुंझुनूं', 'अलवर', 'भरतपुर', 'धौलपुर', 'करौली', 'सवाई माधोपुर', 'टोंक', 'पाली', 'सिरोही', 'जालौर', 'प्रतापगढ़', 'राजसमंद', 'बूंदी', 'बारां', 'दौसा', 'अनूपगढ़', 'बालोतरा', 'सांचौर', 'डीग', 'सलूंबर'],
    'park': ['भड़ला सोलर पार्क (फलौदी)', 'नोख सोलर पार्क (जैसलमेर)', 'पूगल सोलर पार्क (बीकानेर)', 'फतेहगढ़ सोलर पार्क (जैसलमेर)', 'फलौदी-पोकरण सोलर पार्क'],
    'person': ['भजनलाल शर्मा', 'दीया कुमारी', 'प्रेमचंद बैरवा', 'वासुदेव देवनानी', 'कलराज मिश्र', 'हरिभाऊ बागड़े', 'अशोक गहलोत'],
    'tiger': ['रणथंभौर टाइगर रिज़र्व', 'सरिस्का टाइगर रिज़र्व', 'मुकुंदरा हिल्स टाइगर रिज़र्व', 'रामगढ़ विषधारी टाइगर रिज़र्व', 'कुंभलगढ़ अभयारण्य'],
    'scheme': ['ऑपरेशन क्लीन स्वीप 2.0', 'मिशन दृष्टि', 'मिशन बुनियाद', 'इंदिरा रसोई योजना', 'चिरंजीवी योजना']
}

def detect_raj_ca_domain(q, a):
    combo = (q + ' ' + a).lower()
    if 'सोलर' in combo or 'पार्क' in combo: return 'park'
    if 'टाइगर' in combo or 'भेड़िय' in combo or 'अभयारण्य' in combo or 'संरक्षित' in combo: return 'tiger'
    if 'मुख्यमंत्री' in combo or 'मंत्री' in combo or 'राज्यपाल' in combo or 'अध्यक्ष' in combo or 'पुरस्कार' in combo: return 'person'
    if 'ऑपरेशन' in combo or 'मिशन' in combo or 'अभियान' in combo or 'योजना' in combo: return 'scheme'
    return 'district'

raj_ca_matches = list(re.finditer(date_pattern, raj_ca_text))
raj_ca_dates_dict = {}
raj_ca_q_counter = 0

for idx in range(len(raj_ca_matches)):
    day_num = int(raj_ca_matches[idx].group(1))
    month_name = raj_ca_matches[idx].group(2)
    month_num = month_num_map[month_name]
    iso_date = f'2026-{month_num}-{day_num:02d}'

    start_pos = raj_ca_matches[idx].end()
    end_pos = raj_ca_matches[idx+1].start() if idx+1 < len(raj_ca_matches) else len(raj_ca_text)
    day_text = raj_ca_text[start_pos:end_pos].strip()

    qa_blocks = re.split(r'(?m)^\s*(?:[0-9]+\.|\*)\s*प्रश्न:', day_text)
    day_questions = []

    for blk in qa_blocks[1:]:
        blk_lines = [l.strip() for l in blk.strip().splitlines() if l.strip()]
        if not blk_lines: continue
        q_line = blk_lines[0].strip()

        ans_raw = ''
        for l in blk_lines[1:]:
            if 'उत्तर:' in l:
                ans_raw = l.replace('*', '').replace('उत्तर:', '').strip()
                break

        if not ans_raw: continue

        core_ans = ans_raw.split('(')[0].split('।')[0].strip()
        if ':' in core_ans: core_ans = core_ans.split(':')[1].strip()
        core_ans = core_ans.strip(' \'\"*•')
        if not core_ans or len(core_ans) < 2 or core_ans in ['उत्तर', 'निम्न']: continue

        dom = detect_raj_ca_domain(q_line, core_ans)
        pool = DISTRACTORS_RAJ.get(dom, DISTRACTORS_RAJ['district'])
        dists = [d for d in pool if d.strip() != core_ans]
        rng = random.Random(abs(hash(q_line)) % 1000)
        rng.shuffle(dists)
        chosen = dists[:3]

        opts = [core_ans] + chosen
        rng.shuffle(opts)
        c_idx = opts.index(core_ans)

        raj_ca_q_counter += 1
        day_questions.append({
            'id': f'RAJ_CA_Q_{raj_ca_q_counter}',
            'date': iso_date,
            'topic': f'राजस्थान करंट अफेयर ({day_num} {month_name} 2026)',
            'question': q_line,
            'options': opts,
            'correct_index': c_idx,
            'explanation': f'✅ **सही उत्तर:** {core_ans}\n\n📌 **परीक्षा संदर्भ:** राजस्थान समसामयिकी {day_num} {month_name} 2026\n\n📖 **एग्जामिनर व्याख्या:** {ans_raw}',
            'mnemonic': f'💡 **याद रखने की ट्रिक:** मुख्य बिंदु \'{core_ans}\' को ध्यान में रखें।',
            'one_liner': f'{q_line} ➔ **{core_ans}**'
        })

    if day_questions:
        raj_ca_dates_dict[iso_date] = {
            'date': iso_date,
            'display_date': f'{day_num} {month_name} 2026',
            'questions': day_questions,
            'total_questions': len(day_questions)
        }

print(f"==> Rajasthan Current Affairs Processed: {len(raj_ca_dates_dict)} Dates, {raj_ca_q_counter} Crisp MCQs.")


# -------------------------------------------------------------
# 3. RAJASTHAN GK - ART & CULTURE AND HISTORY CRISP DATASET
# -------------------------------------------------------------
art_culture_chapters = [
    {
        "id": "art_ch_1", "number": 1, "title": "अध्याय-1: राजस्थान के प्रमुख दुर्ग एवं किले", "raw_title": "प्रमुख दुर्ग एवं किले",
        "questions": [
            {
                "id": "ART_Q_1", "question": "यूनेस्को (UNESCO) की विश्व धरोहर सूची में राजस्थान के कितने पहाड़ी किलों को शामिल किया गया है?",
                "options": ["6 किले (चीकू, गाजर, आम)", "7 किले", "5 किले", "8 किले"], "correct_index": 0,
                "explanation": "✅ सही उत्तर: 6 पहाड़ी किले (चित्तौड़गढ़, कुंभलगढ़, रणथंभौर, गागरोन, आमेर, जैसलमेर) 2013 में शामिल किए गए।",
                "mnemonic": "ट्रिक: चीकू गाजर आम", "one_liner": "यूनेस्को में राजस्थान के कितने पहाड़ी किले शामिल हैं? ➔ **6 किले**"
            },
            {
                "id": "ART_Q_2", "question": "राजस्थान का प्रसिद्ध जल दुर्ग (ओदक दुर्ग) 'गागरोन का किला' किन दो नदियों के संगम पर स्थित है?",
                "options": ["आहू और कालीसिंध नदी", "चंबल और बामनी नदी", "बनास और बेड़च नदी", "सोम और जाखम नदी"], "correct_index": 0,
                "explanation": "✅ सही उत्तर: आहू और कालीसिंध नदी के संगम पर झालावाड़ में गागरोन दुर्ग स्थित है।",
                "mnemonic": "ट्रिक: गागरोन = आहू + कालीसिंध", "one_liner": "गागरोन का किला किन नदियों के संगम पर है? ➔ **आहू और कालीसिंध**"
            },
            {
                "id": "ART_Q_3", "question": "'गढ़ तो चित्तौड़गढ़ बाकी सब गढ़ैया' — चित्तौड़गढ़ दुर्ग किस पठार पर निर्मित है?",
                "options": ["मेसा का पठार", "भोराट का पठार", "उड़िया का पठार", "लसाड़िया का पठार"], "correct_index": 0,
                "explanation": "✅ सही उत्तर: चित्तौड़गढ़ दुर्ग 616 मीटर ऊंचे मेसा के पठार पर चित्रांगद मौर्य द्वारा बनवाया गया था।",
                "mnemonic": "ट्रिक: चित्तौड़ = मेसा का पठार", "one_liner": "चित्तौड़गढ़ दुर्ग किस पठार पर स्थित है? ➔ **मेसा का पठार**"
            },
            {
                "id": "ART_Q_4", "question": "अबुल फजल ने किस दुर्ग के लिए कहा था कि 'अन्य सब दुर्ग नंगे हैं, जबकि यह बख्तरबंद है'?",
                "options": ["रणथंभौर दुर्ग", "चित्तौड़गढ़ दुर्ग", "कुंभलगढ़ दुर्ग", "तारागढ़ दुर्ग"], "correct_index": 0,
                "explanation": "✅ सही उत्तर: रणथंभौर दुर्ग (सवाई माधोपुर) सात पहाड़ियों से घिरा होने के कारण बख्तरबंद कहलाता है।",
                "mnemonic": "ट्रिक: बख्तरबंद = रणथंभौर", "one_liner": "बख्तरबंद दुर्ग किसे कहा गया है? ➔ **रणथंभौर दुर्ग**"
            },
            {
                "id": "ART_Q_5", "question": "कुंभलगढ़ दुर्ग की प्रसिद्ध प्राचीर (दीवार) की कुल लंबाई कितनी है, जिसे भारत की महान दीवार कहा जाता है?",
                "options": ["36 कि.मी.", "24 कि.मी.", "48 कि.मी.", "18 कि.मी."], "correct_index": 0,
                "explanation": "✅ सही उत्तर: कुंभलगढ़ की दीवार 36 किमी लंबी तथा इतनी चौड़ी है कि 4 घुड़सवार एक साथ चल सकते हैं।",
                "mnemonic": "ट्रिक: कुंभलगढ़ प्राचीर = 36 किमी", "one_liner": "कुंभलगढ़ दुर्ग की दीवार की लंबाई कितनी है? ➔ **36 कि.मी.**"
            }
        ]
    },
    {
        "id": "art_ch_2", "number": 2, "title": "अध्याय-2: राजस्थान के प्रमुख लोक देवता एवं लोक देवियां", "raw_title": "लोक देवता एवं लोक देवियां",
        "questions": [
            {
                "id": "ART_Q_6", "question": "राजस्थान के पंचपीरों में कौन-से लोक देवता शामिल नहीं हैं?",
                "options": ["तेजाजी", "पाबूजी", "रामदेवजी", "गोगाजी"], "correct_index": 0,
                "explanation": "✅ सही उत्तर: तेजाजी पंचपीरों में शामिल नहीं हैं। पंचपीर हैं: पाबूजी, हड़बूजी, रामदेवजी, मांगलिया मेहाजी, गोगाजी।",
                "mnemonic": "ट्रिक: पाबू, हड़बू, रामदे, मांगलिया मेहा, पांचों पीर पधारज्ये गोगाजी जेहा।", "one_liner": "पंचपीरों में कौन शामिल नहीं हैं? ➔ **तेजाजी**"
            },
            {
                "id": "ART_Q_7", "question": "ऊंटों के देवता तथा प्लेग रक्षक लोक देवता के रूप में राजस्थान में किनकी पूजा की जाती है?",
                "options": ["पाबूजी", "गोगाजी", "हड़बूजी", "मल्लीनाथजी"], "correct_index": 0,
                "explanation": "✅ सही उत्तर: पाबूजी को ऊंटों का देवता तथा प्लेग रक्षक देवता माना जाता है। राइका/रेबारी जाति इनकी मुख्य भक्त है।",
                "mnemonic": "ट्रिक: ऊंट बीमार = पाबूजी की फड़", "one_liner": "ऊंटों के लोक देवता कौन हैं? ➔ **पाबूजी**"
            },
            {
                "id": "ART_Q_8", "question": "चूहों वाली देवी के नाम से विश्व विख्यात 'करणी माता' का मुख्य मंदिर कहाँ स्थित है?",
                "options": ["देशनोक (बीकानेर)", "ओसियां (जोधपुर)", "चाकसू (जयपुर)", "आमेर (जयपुर)"], "correct_index": 0,
                "explanation": "✅ सही उत्तर: देशनोक (बीकानेर) में करणी माता का मंदिर है जहां सफेद चूहों को 'काबा' कहा जाता है।",
                "mnemonic": "ट्रिक: सफेद चूहे = देशनोक करणी माता", "one_liner": "करणी माता का मंदिर कहाँ है? ➔ **देशनोक (बीकानेर)**"
            }
        ]
    }
]

history_chapters = [
    {
        "id": "hist_ch_1", "number": 1, "title": "अध्याय-1: राजस्थान की प्राचीन सभ्यताएं (कालीबंगा, आहड़, गणेश्वर)", "raw_title": "प्राचीन सभ्यताएं",
        "questions": [
            {
                "id": "HIST_Q_1", "question": "कांस्य युगीन सभ्यता 'कालीबंगा' राजस्थान के किस जिले में घग्घर (सरस्वती) नदी के तट पर स्थित है?",
                "options": ["हनुमानगढ़", "श्रीगंगानगर", "अनूपगढ़", "बीकानेर"], "correct_index": 0,
                "explanation": "✅ सही उत्तर: कालीबंगा (काले रंग की चूड़ियां) हनुमानगढ़ जिले में घग्घर नदी के किनारे स्थित है। खोज: अमलानंद घोष (1952)।",
                "mnemonic": "ट्रिक: कालीबंगा = हनुमानगढ़ + घग्घर", "one_liner": "कालीबंगा किस जिले में स्थित है? ➔ **हनुमानगढ़**"
            },
            {
                "id": "HIST_Q_2", "question": "विश्व में जूते हुए खेत के प्राचीनतम साक्ष्य राजस्थान के किस पुरातात्विक स्थल से प्राप्त हुए हैं?",
                "options": ["कालीबंगा", "आहड़", "गणेश्वर", "बैराठ"], "correct_index": 0,
                "explanation": "✅ सही उत्तर: कालीबंगा से दोहरी फसल (चना + सरसों) तथा जूते हुए खेत के साक्ष्य मिले हैं।",
                "mnemonic": "ट्रिक: जुता हुआ खेत = कालीबंगा", "one_liner": "जुते हुए खेत के साक्ष्य कहाँ से मिले? ➔ **कालीबंगा**"
            },
            {
                "id": "HIST_Q_3", "question": "ताम्र युगीन सभ्यताओं की जननी कही जाने वाली 'गणेश्वर सभ्यता' किस नदी के मुहाने पर स्थित है?",
                "options": ["कांतली नदी (नीम का थाना)", "बनास नदी (उदयपुर)", "बाणगंगा नदी (कोटपूतली)", "घग्घर नदी"], "correct_index": 0,
                "explanation": "✅ सही उत्तर: गणेश्वर सभ्यता कांतली नदी के तट पर नीम का थाना (पूर्व में सीकर) में स्थित है।",
                "mnemonic": "ट्रिक: ताम्र जननी = गणेश्वर (कांतली)", "one_liner": "गणेश्वर सभ्यता किस नदी तट पर है? ➔ **कांतली नदी**"
            }
        ]
    },
    {
        "id": "hist_ch_2", "number": 2, "title": "अध्याय-2: राजस्थान का एकीकरण (7 चरण)", "raw_title": "राजस्थान का एकीकरण",
        "questions": [
            {
                "id": "HIST_Q_4", "question": "राजस्थान के एकीकरण के प्रथम चरण 'मत्स्य संघ' का गठन कब हुआ था?",
                "options": ["18 मार्च 1948", "25 मार्च 1948", "18 अप्रैल 1948", "30 मार्च 1949"], "correct_index": 0,
                "explanation": "✅ सही उत्तर: 18 मार्च 1948 को मत्स्य संघ (अलवर, भरतपुर, धौलपुर, करौली) बना। नामकरण के.एम. मुंशी ने किया।",
                "mnemonic": "ट्रिक: मत्स्य संघ = 18 मार्च 1948 (ABCD रियासतें)", "one_liner": "मत्स्य संघ का गठन कब हुआ? ➔ **18 मार्च 1948**"
            },
            {
                "id": "HIST_Q_5", "question": "राजस्थान दिवस प्रतिवर्ष किस तिथि को मनाया जाता है?",
                "options": ["30 मार्च (वृहत राजस्थान गठन)", "1 नवंबर", "18 मार्च", "26 जनवरी"], "correct_index": 0,
                "explanation": "✅ सही उत्तर: 30 मार्च 1949 को वृहत राजस्थान (जयपुर, जोधपुर, जैसलमेर, बीकानेर का विलय) बनने पर प्रतिवर्ष राजस्थान दिवस मनाया जाता है।",
                "mnemonic": "ट्रिक: 30 मार्च = राजस्थान दिवस", "one_liner": "राजस्थान दिवस कब मनाया जाता है? ➔ **30 मार्च**"
            }
        ]
    }
]


# -------------------------------------------------------------
# 4. LSA VETERINARY DIPLOMA SUBJECTS - CRISP EXAMINER DATASET
# -------------------------------------------------------------
lsa_dict = {
    "anatomy": {
        "id": "anatomy", "title": "1. वेटरनरी एनाटॉमी (Veterinary Anatomy)", "linked": True,
        "chapters": [{
            "id": "anat_ch_1", "number": 1, "title": "अध्याय-1: अस्थि विज्ञान (Osteology) एवं कंकाल तंत्र",
            "questions": [
                {
                    "id": "LSA_ANAT_1", "question": "गाय / बैल के शरीर में पसलियों (Ribs) की कुल कितनी जोड़ियां पाई जाती हैं?",
                    "options": ["13 जोड़ी", "18 जोड़ी (घोड़ा)", "14-15 जोड़ी (सूअर)", "12 जोड़ी"], "correct_index": 0,
                    "explanation": "✅ सही उत्तर: गोवंश (Cattle) और भेड़-बकरी में 13 जोड़ी पसलियां होती हैं। घोड़े में 18 जोड़ी होती हैं।",
                    "mnemonic": "ट्रिक: मवेशी = 13 जोड़ी रिब्स", "one_liner": "गाय/बैल में पसलियों की कितनी जोड़ियां होती हैं? ➔ **13 जोड़ी**"
                },
                {
                    "id": "LSA_ANAT_2", "question": "पशु शरीर की सबसे लंबी और मजबूत अस्थि (Longest & Strongest Bone) कौन-सी होती है?",
                    "options": ["फीमर (Femur - जांघ की अस्थि)", "ह्यूमरस (Humerus)", "टिबिया (Tibia)", "रेडियस (Radius)"], "correct_index": 0,
                    "explanation": "✅ सही उत्तर: फीमर (Femur) शरीर की सबसे लंबी एवं मजबूत अस्थि है।",
                    "mnemonic": "ट्रिक: सबसे लंबी = फीमर", "one_liner": "शरीर की सबसे लंबी अस्थि कौन-सी है? ➔ **फीमर (Femur)**"
                }
            ]
        }]
    },
    "physiology": {
        "id": "physiology", "title": "2. वेटरनरी फिजियोलॉजी (Veterinary Physiology)", "linked": True,
        "chapters": [{
            "id": "phys_ch_1", "number": 1, "title": "अध्याय-1: रक्त परिसंचरण एवं शारीरिक क्रियाएं",
            "questions": [
                {
                    "id": "LSA_PHYS_1", "question": "गाय / भैंस का सामान्य शारीरिक तापमान (Normal Body Temperature) कितना होता है?",
                    "options": ["101.5° F (38.5° C)", "103.5° F (बकरी)", "107° F (मुर्गी)", "98.6° F (मानव)"], "correct_index": 0,
                    "explanation": "✅ सही उत्तर: गाय-भैंस का सामान्य तापमान 101.5°F (38.5°C) होता है। बकरी का 103.5°F तथा मुर्गी का 107°F होता है।",
                    "mnemonic": "ट्रिक: गोवंश तापमान = 101.5°F", "one_liner": "गाय का सामान्य शारीरिक तापमान कितना होता है? ➔ **101.5° F**"
                },
                {
                    "id": "LSA_PHYS_2", "question": "रोमंथी (Ruminant) पशुओं में आमाशय का सबसे बड़ा भाग कौन-सा होता है जो किण्वन (Fermentation Vat) का कार्य करता है?",
                    "options": ["रूमेन (Rumen - 80% भाग)", "रेटिकुलम (Reticulum)", "ओमेसम (Omasum)", "एबोमेसम (Abomasum - सत्य आमाशय)"], "correct_index": 0,
                    "explanation": "✅ सही उत्तर: रूमेन कुल आमाशय का 80% भाग होता है और इसमें सूक्ष्मजीवों द्वारा किण्वन होता है।",
                    "mnemonic": "ट्रिक: सबसे बड़ा पेट = रूमेन (80%)", "one_liner": "रोमंथी पशुओं के आमाशय का सबसे बड़ा भाग कौन-सा है? ➔ **रूमेन (Rumen)**"
                }
            ]
        }]
    },
    "nutrition": {
        "id": "nutrition", "title": "3. पशु पोषण (Animal Nutrition)", "linked": True,
        "chapters": [{
            "id": "nutr_ch_1", "number": 1, "title": "अध्याय-1: चारा एवं आहार प्रबंधन (Silage, Hay & DCP)",
            "questions": [
                {
                    "id": "LSA_NUTR_1", "question": "सर्वोत्तम साइलेज (Silage) बनाने के लिए किस फसल को सर्वाधिक उपयुक्त माना जाता है?",
                    "options": ["मक्का (Maize)", "बरसीम (Berseem)", "रिजका (Lucerne)", "जई (Oat)"], "correct_index": 0,
                    "explanation": "✅ सही उत्तर: मक्का (कार्बोहाइड्रेट प्रचुर) साइलेज बनाने हेतु सर्वश्रेष्ठ है। बरसीम/रिजका हे (Hay) बनाने हेतु सर्वश्रेष्ठ है।",
                    "mnemonic": "ट्रिक: साइलेज = मक्का, हे = बरसीम/रिजका", "one_liner": "सर्वोत्तम साइलेज किस फसल से बनती है? ➔ **मक्का (Maize)**"
                }
            ]
        }]
    },
    "lpm": {
        "id": "lpm", "title": "4. पशुधन उत्पादन एवं प्रबंधन (LPM)", "linked": True,
        "chapters": [{
            "id": "lpm_ch_1", "number": 1, "title": "अध्याय-1: पशु नस्लें एवं दुग्ध उत्पादन",
            "questions": [
                {
                    "id": "LSA_LPM_1", "question": "भैंस की किस नस्ल के दूध में सर्वाधिक वसा (Fat 12-14%) पाई जाती है तथा शरीर तांबे जैसा (Copper coloured) होता है?",
                    "options": ["भदावरी (Bhadawari)", "मुर्रा (Murrah - जलेबी सींग)", "जाफराबादी (मिनी हाथी)", "मेहसाना"], "correct_index": 0,
                    "explanation": "✅ सही उत्तर: भदावरी नस्ल में सर्वाधिक वसा प्रतिशत (12-14%) होता है।",
                    "mnemonic": "ट्रिक: सर्वाधिक घी/फैट = भदावरी", "one_liner": "सर्वाधिक वसा प्रतिशत वाली भैंस की नस्ल कौन-सी है? ➔ **भदावरी**"
                }
            ]
        }]
    },
    "pharmacology": {
        "id": "pharmacology", "title": "5. वेटरनरी फार्माकोलॉजी एवं टॉक्सिकोलॉजी", "linked": True,
        "chapters": [{
            "id": "pharm_ch_1", "number": 1, "title": "अध्याय-1: औषधियां एवं उनका वर्गीकरण",
            "questions": [
                {
                    "id": "LSA_PHARM_1", "question": "पशुओं में बुखार (ज्वर) कम करने वाली औषधियों को क्या कहा जाता है?",
                    "options": ["एंटीपायरेटिक (Antipyretic - जैसे पैरासिटामोल)", "एनाल्जेसिक (Analgesic - दर्द निवारक)", "एंटीसेप्टिक (Antiseptic)", "एंटीबायोटिक (Antibiotic)"], "correct_index": 0,
                    "explanation": "✅ सही उत्तर: एंटीपायरेटिक औषधियां तापमान कम करती हैं। एनाल्जेसिक दर्द निवारक होती हैं।",
                    "mnemonic": "ट्रिक: पायरेटिक = ताप/बुखार", "one_liner": "बुखार कम करने वाली औषधि क्या कहलाती है? ➔ **एंटीपायरेटिक**"
                }
            ]
        }]
    },
    "medicine": {
        "id": "medicine", "title": "6. वेटरनरी मेडिसिन (Clinical Medicine)", "linked": True,
        "chapters": [{
            "id": "med_ch_1", "number": 1, "title": "अध्याय-1: संक्रामक रोग (खुरपका-मुंहपका, गलघोंटू, लंगड़ा बुखार)",
            "questions": [
                {
                    "id": "LSA_MED_1", "question": "पशुओं में गलघोंटू (HS - Haemorrhagic Septicaemia) रोग का प्रमुख जीवाणु कारक कौन-सा है?",
                    "options": ["पाश्चुरेला बोविसेप्टिका (Pasteurella multocida)", "क्लॉस्ट्रिडियम चौवोई (BQ)", "बैसिलस एन्थ्रेसिस (Anthrax)", "ब्रूसेला एबॉोर्टस"], "correct_index": 0,
                    "explanation": "✅ सही उत्तर: गलघोंटू (HS) पाश्चुरेला मल्टीसिडा/बोविसेप्टिका जीवाणु से होता है जिसमें गले में सूजन व घर्र-घर्र की आवाज आती है।",
                    "mnemonic": "ट्रिक: HS = पाश्चुरेला", "one_liner": "गलघोंटू (HS) का रोगजनक कौन है? ➔ **पाश्चुरेला बोविसेप्टिका**"
                }
            ]
        }]
    },
    "surgery": {
        "id": "surgery", "title": "7. वेटरनरी सर्जरी एवं रेडियोलॉजी", "linked": True,
        "chapters": [{
            "id": "surg_ch_1", "number": 1, "title": "अध्याय-1: शल्य चिकित्सा एवं एनेस्थीसिया",
            "questions": [
                {
                    "id": "LSA_SURG_1", "question": "पशुओं में आमाशय के रूमेन में अत्यधिक गैस भरने (ब्लोट/अफारा) पर किस उपकरण द्वारा गैस निकाली जाती है?",
                    "options": ["ट्रोकार एवं कैनुला (Trocar & Cannula)", "थर्मामीटर", "बीपी उपकरण", "स्यूचर नीडल"], "correct_index": 0,
                    "explanation": "✅ सही उत्तर: बाएं कोख (Left paralumbar fossa) में ट्रोकार एवं कैनुला छिद्रित कर गैस बाहर निकाली जाती है।",
                    "mnemonic": "ट्रिक: अफारा गैस = ट्रोकार एवं कैनुला", "one_liner": "अफारे में गैस निकालने वाला उपकरण कौन-सा है? ➔ **ट्रोकार एवं कैनुला**"
                }
            ]
        }]
    },
    "gynecology": {
        "id": "gynecology", "title": "8. पशु प्रजनन एवं स्त्री रोग विज्ञान", "linked": True,
        "chapters": [{
            "id": "gyn_ch_1", "number": 1, "title": "अध्याय-1: मद चक्र एवं कृत्रिम गर्भाधान (AI)",
            "questions": [
                {
                    "id": "LSA_GYN_1", "question": "वीर्य (Semen) को लंबे समय तक सुरक्षित रखने हेतु तरल नाइट्रोजन (Liquid Nitrogen) का तापमान कितना होता है?",
                    "options": ["-196° C", "-79° C (ड्राई आइस)", "-20° C", "0° C"], "correct_index": 0,
                    "explanation": "✅ सही उत्तर: तरल नाइट्रोजन (LN2) का तापमान -196°C होता है जिसमें वीर्य सीमन स्ट्रॉ क्रायोप्रिजर्व रहते हैं।",
                    "mnemonic": "ट्रिक: LN2 = -196 डिग्री सेल्सियस", "one_liner": "तरल नाइट्रोजन का तापमान कितना होता है? ➔ **-196° C**"
                }
            ]
        }]
    },
    "genetics": {
        "id": "genetics", "title": "9. पशु आनुवंशिकी एवं प्रजनन", "linked": True,
        "chapters": [{
            "id": "gen_ch_1", "number": 1, "title": "अध्याय-1: आनुवंशिकी के नियम एवं गुणसूत्र",
            "questions": [
                {
                    "id": "LSA_GEN_1", "question": "गाय (Cattle) में द्विगुणित गुणसूत्रों (Chromosome 2n) की संख्या कितनी होती है?",
                    "options": ["60 गुणसूत्र", "54 गुणसूत्र (भेड़)", "50 गुणसूत्र (भैंस - रिवर)", "48 गुणसूत्र (भैंस - स्वैम्प)"], "correct_index": 0,
                    "explanation": "✅ सही उत्तर: गाय और बकरी में 2n = 60 गुणसूत्र होते हैं। भेड़ में 54, रिवर बफैलो में 50 होते हैं।",
                    "mnemonic": "ट्रिक: गाय/बकरी = 60 गुणसूत्र", "one_liner": "गाय में गुणसूत्रों की संख्या कितनी होती है? ➔ **60 गुणसूत्र**"
                }
            ]
        }]
    },
    "extension": {
        "id": "extension", "title": "10. प्रसार शिक्षा एवं पशुपालन अर्थशास्त्र", "linked": True,
        "chapters": [{
            "id": "ext_ch_1", "number": 1, "title": "अध्याय-1: पशुपालन प्रसार विधियां एवं योजनाएं",
            "questions": [
                {
                    "id": "LSA_EXT_1", "question": "भारत में श्वेत क्रांति (White Revolution / Operation Flood) के जनक किन्हें कहा जाता है?",
                    "options": ["डॉ. वर्गीज कुरियन (Dr. Verghese Kurien)", "डॉ. एम. एस. स्वामीनाथन (हरित क्रांति)", "डॉ. नॉर्मन बोरलॉग", "डॉ. अमृता पटेल"], "correct_index": 0,
                    "explanation": "✅ सही उत्तर: डॉ. वर्गीज कुरियन को भारत में श्वेत क्रांति (ऑपरेशन फ्लड 1970) का जनक माना जाता है।",
                    "mnemonic": "ट्रिक: दूध/श्वेत क्रांति = वर्गीज कुरियन", "one_liner": "श्वेत क्रांति के जनक कौन हैं? ➔ **डॉ. वर्गीज कुरियन**"
                }
            ]
        }]
    }
}


# -------------------------------------------------------------
# 5. ASSEMBLE FULL DATABASE INTO INITIAL_DATA.JS
# -------------------------------------------------------------
initial_data_obj = {
    "config": {
        "app_name": "मेरी तैयारी • MCQ Prep",
        "version": "2.4.0",
        "build_date": "2026-11-20",
        "marking_scheme": {
            "correct": 2.0,
            "negative": 0.67,
            "time_per_q_sec": 60
        }
    },
    "national_ca": {
        "id": "national_ca",
        "title": "राष्ट्रीय एवं अंतरराष्ट्रीय करंट अफेयर",
        "linked": True,
        "doc_url": "https://docs.google.com/document/d/1EEDq2GZn4d9UucwlEifT6KF37IN1bK3a4A_Ch8a5JOg/edit?usp=drivesdk",
        "last_synced": "2026-11-20T23:00:00Z",
        "dates": nca_dates_dict
    },
    "rajasthan_ca": {
        "id": "rajasthan_ca",
        "title": "राजस्थान करंट अफेयर",
        "linked": True,
        "doc_url": "https://docs.google.com/document/d/1gEJesr7k_8B8wTkuvsmnm6Wo1m9CQZwpL-x50aBLrMY/edit?usp=drivesdk",
        "last_synced": "2026-11-20T23:00:00Z",
        "dates": raj_ca_dates_dict
    },
    "rajasthan_gk": {
        "geography": {
            "id": "geography",
            "title": "राजस्थान भूगोल (Rajasthan Geography)",
            "linked": True,
            "doc_url": "https://docs.google.com/document/d/1Qoh9heJ75cwdYFKWA2wfl8Q7LWaFJdobVEwxxug1BKc/edit?usp=drivesdk",
            "last_synced": "2026-11-20T21:00:00Z",
            "total_chapters": len(geo_chapters),
            "total_questions": sum(len(c["questions"]) for c in geo_chapters),
            "chapters": geo_chapters
        },
        "art_culture": {
            "id": "art_culture",
            "title": "कला एवं संस्कृति (Art & Culture)",
            "linked": True,
            "doc_url": "",
            "last_synced": "2026-11-20T21:00:00Z",
            "total_chapters": len(art_culture_chapters),
            "total_questions": sum(len(c["questions"]) for c in art_culture_chapters),
            "chapters": art_culture_chapters
        },
        "history": {
            "id": "history",
            "title": "राजस्थान इतिहास (Rajasthan History)",
            "linked": True,
            "doc_url": "",
            "last_synced": "2026-11-20T21:00:00Z",
            "total_chapters": len(history_chapters),
            "total_questions": sum(len(c["questions"]) for c in history_chapters),
            "chapters": history_chapters
        }
    },
    "lsa_subjects": lsa_dict
}

js_content = "window.INITIAL_DATA = " + json.dumps(initial_data_obj, ensure_ascii=False) + ";\n"

# Write to root initial_data.js and assets/initial_data.js
root_path = "/data/user/0/com.termux/files/home/.gemini/antigravity-cli/scratch/meri-taiyari-app/initial_data.js"
assets_path = "/data/user/0/com.termux/files/home/.gemini/antigravity-cli/scratch/meri-taiyari-app/assets/initial_data.js"

with open(root_path, "w", encoding="utf-8") as f:
    f.write(js_content)

with open(assets_path, "w", encoding="utf-8") as f:
    f.write(js_content)

print(f"==> ✅ Successfully generated and saved initial_data.js ({len(js_content)} bytes)")
print("==> Geography total questions:", sum(len(c["questions"]) for c in geo_chapters))
print("==> National CA total dates:", len(nca_dates_dict), "questions:", nca_q_counter)
print("==> Art & Culture total questions:", sum(len(c["questions"]) for c in art_culture_chapters))
print("==> History total questions:", sum(len(c["questions"]) for c in history_chapters))
print("==> LSA Subjects ready: 10 subjects.")
