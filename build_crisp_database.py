import re
import json
import random

with open('/data/user/0/com.termux/files/home/.gemini/antigravity-cli/scratch/meri-taiyari-app/raw_raj_geography.txt', 'r', encoding='utf-8') as f:
    text = f.read().replace('\u200b', '').replace('\ufeff', '')

# Domain distractors
DISTRACTORS = {
    "km": ["1070 कि.मी.", "4850 कि.मी.", "5920 कि.मी.", "826 कि.मी.", "869 कि.मी.", "692 कि.मी.", "550 कि.मी.", "168 कि.मी.", "464 कि.मी.", "228 कि.मी.", "210 कि.मी."],
    "area": ["3,42,239 वर्ग कि.मी.", "1,32,139 वर्ग मील", "10.41%", "61.11%", "9.60%", "23.03%", "40%"],
    "cm": ["हीरालाल शास्त्री", "मोहनलाल सुखाड़िया", "हरिदेव जोशी", "भैरोंसिंह शेखावत", "जयनारायण व्यास", "टीकाराम पालीवाल", "शिवचरण माथुर", "भजनलाल शर्मा"],
    "committee": ["परमेश चन्द्र समिति", "रामलुभाया समिति", "ललित के. पंवार समिति", "पी. सत्यनारायण राव समिति", "हरिश्चंद्र माथुर समिति"],
    "district": ["जैसलमेर", "बाड़मेर", "बीकानेर", "जोधपुर", "जयपुर", "उदयपुर", "कोटा", "अजमेर", "भीलवाड़ा", "चित्तौड़गढ़", "डूंगरपुर", "बांसवाड़ा", "झालावाड़", "चूरू", "सीकर", "नागौर", "अलवर", "भरतपुर", "धौलपुर", "करौली", "सवाई माधोपुर", "टोंक", "पाली", "सिरोही", "जालौर", "प्रतापगढ़", "राजसमंद", "बूंदी", "बारां", "दौसा", "अनूपगढ़", "फलोदी", "बालोतरा", "सांचौर", "डीग", "सलूंबर"],
    "division": ["जयपुर संभाग", "अजमेर संभाग", "जोधपुर संभाग", "बीकानेर संभाग", "उदयपुर संभाग", "भरतपुर संभाग", "कोटा संभाग"],
    "peak": ["गुरुशिखर (1722 मी.)", "सेर (1597 मी.)", "दिलवाड़ा (1442 मी.)", "जरगा (1431 मी.)", "अचलगढ़ (1380 मी.)", "कुंभलगढ़ (1224 मी.)", "रघुनाथगढ़ (1055 मी.)", "ऋषिकेश (1017 मी.)", "कमलनाथ (1001 मी.)", "तारागढ़ (873 मी.)"],
    "river": ["चंबल नदी", "बनास नदी", "लूणी नदी", "माही नदी", "साबरमती नदी", "कालीसिंध नदी", "बाणगंगा नदी", "पार्वती नदी", "घग्घर नदी", "कांतली नदी", "सोम नदी", "जाखम नदी"],
    "dam": ["राणा प्रताप सागर बांध", "गांधी सागर बांध", "जवाहर सागर बांध", "कोटा बैराज", "बीसलपुर बांध", "जाखम बांध", "मेजा बांध", "पांचना बांध", "जवाई बांध"],
    "lake": ["सांभर झील", "पचपदरा झील", "डीडवाना झील", "लूणकरणसर झील", "जयसमंद झील", "राजसमंद झील", "पिछोला झील", "फतेहसागर झील", "आनासागर झील", "नक्की झील"],
    "soil": ["काली मृदा (वर्टिसोल)", "लाल-पीली मृदा", "जलोढ़ मृदा (एल्फीसोल)", "रेतीली शुष्क मृदा (एंटीसोल)", "भूरी रेतीली मृदा", "लवणीय मृदा"],
    "climate": ["शुष्क कटिबंधीय (BWhw)", "अर्ध-शुष्क स्टेपी (BShw)", "उप-आद्र मानसूनी (Cwa)", "अति-आद्र (Aw)"],
    "mineral": ["रॉक फॉस्फेट", "सीसा-जस्ता", "तांबा", "लोहा अयस्क", "टंगस्टन", "सफेद संगमरमर", "जिप्सम", "पन्ना"],
    "institute": ["काजरी (CAZRI - जोधपुर)", "आफरी (AFRI - जोधपुर)", "CSWRI (अविकानगर - टोंक)", "राष्ट्रीय ऊंट अनुसंधान केंद्र (बीकानेर)", "राष्ट्रीय सरसों अनुसंधान केंद्र (सेवर, भरतपुर)", "राष्ट्रीय बीजीय मसाला अनुसंधान केंद्र (तबीजी, अजमेर)"],
    "year": ["1949", "1952", "1956", "1962", "1982", "1987", "1991", "1994", "1997", "2005", "2008", "2022", "2024"]
}

def pick_distractors(ans, cat):
    bank = DISTRACTORS.get(cat, DISTRACTORS["district"])
    ans_clean = ans.strip()
    cands = [b for b in bank if b != ans_clean and b.split('(')[0].strip() != ans_clean.split('(')[0].strip()]
    rng = random.Random(abs(hash(ans_clean)) % 1000)
    rng.shuffle(cands)
    return cands[:3]

chapter_matches = list(re.finditer(r'(?m)^[ \t]*(अध्याय\s*[-–]?\s*\d+)[ \t]*\n[ \t]*[❀\*\-–•\s]*(.+?)[❀\*\-–•\s]*$', text))

all_chapters = []
total_mcqs = 0

for i in range(len(chapter_matches)):
    ch_label = chapter_matches[i].group(1).strip()
    ch_title = chapter_matches[i].group(2).strip()
    start_pos = chapter_matches[i].end()
    end_pos = chapter_matches[i+1].start() if i+1 < len(chapter_matches) else len(text)
    ch_text = text[start_pos:end_pos].strip()
    
    lines = [l.strip('*•\t-– ') for l in ch_text.splitlines() if l.strip()]
    ch_questions = []

    for line in lines:
        if line.startswith('❀') or len(line) < 10 or line.endswith(':'):
            continue

        q_obj = None

        # 1. Chief Minister Rule
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

        # 2. Committee Rule
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

        # 3. Division Formation Rule
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

        # 4. District Formation Rule
        if not q_obj:
            if '27 वां जिला' in line or 'धौलपुर' in line and '1982' in line:
                q = "15 अप्रैल 1982 को राजस्थान का 27वां जिला 'धौलपुर' किस जिले से अलग करके बनाया गया था?"
                ans = "भरतपुर"
                dists = ["सवाई माधोपुर", "करौली", "अलवर"]
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

        # 5. Lengths, Boundaries & Geography Numbers
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
                q = "राजस्थान की पाकिस्तान के साथ लगने वाली अंतरराष्ट्रीय सीमा (रेडक्लिफ रेखा) की कुल लंबाई कितनी है?"
                ans = "1070 कि.मी."
                dists = ["4850 कि.मी.", "5920 कि.मी.", "1020 कि.मी."]
                q_obj = (q, ans, dists, "km")
            elif 'कुल स्थलीय सीमा' in line or '5920' in line:
                q = "राजस्थान की कुल स्थलीय सीमा की लंबाई कितनी है?"
                ans = "5920 कि.मी."
                dists = ["4850 कि.मी.", "1070 कि.मी.", "6200 कि.मी."]
                q_obj = (q, ans, dists, "km")
            elif 'अंतरराज्यीय सीमा' in line or '4850' in line:
                q = "राजस्थान की कुल अंतरराज्यीय सीमा (5 पड़ोसी राज्यों से) की लंबाई कितनी है?"
                ans = "4850 कि.मी."
                dists = ["5920 कि.मी.", "1070 कि.मी.", "4250 कि.मी."]
                q_obj = (q, ans, dists, "km")
            elif 'आकार' in line and ('पतंगाकार' in line or 'चतुर्भुज' in line):
                q = "राजस्थान का भौगोलिक आकार किस प्रकार का है?"
                ans = "विषमकोण चतुर्भुज (पतंगाकार)"
                dists = ["समकोण त्रिभुजाकार", "गोलाकार", "आयताकार"]
                q_obj = (q, ans, dists, "general")
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
                        q = "अरावली पर्वतमाला तथा राजस्थान की सर्वोच्च पर्वत चोटी 'गुरुशिखर' (1722 मीटर) किस जिले में स्थित है?"
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
                        q = f"अरावली पर्वतमाला की प्रमुख पर्वत चोटी '{pk_clean}' की प्रामाणिक ऊंचाई कितनी है?"
                        ans = pk
                        dists = pick_distractors(ans, "peak")
                        q_obj = (q, ans, dists, "peak")
                    break

        # 7. Dams & Rivers
        if not q_obj:
            if 'पांचना बांध' in line or ('मिट्टी का बांध' in line and 'करौली' in line):
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
                q = "राजस्थान में भराव क्षमता की दृष्टि से सबसे बड़ा बांध 'राणा प्रताप सागर बांध' किस जिले में स्थित है?"
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

        # 8. Lakes & Salt
        if not q_obj:
            if 'सांभर झील' in line or '8.7%' in line:
                q = "भारत के कुल नमक उत्पादन का लगभग 8.7% नमक किस झील से उत्पादित होता है?"
                ans = "सांभर झील"
                dists = ["पचपदरा झील", "डीडवाना झील", "लूणकरणसर झील"]
                q_obj = (q, ans, dists, "lake")
            elif 'पचपदरा' in line or '98%' in line:
                q = "राजस्थान की किस झील के नमक में 98% सोडियम क्लोराइड (NaCl) पाया जाता है, जो खाने के लिए सर्वश्रेष्ठ है?"
                ans = "पचपदरा झील (बालोतरा)"
                dists = ["सांभर झील", "डीडवाना झील", "कावोध झील"]
                q_obj = (q, ans, dists, "lake")
            elif 'जयसमंद' in line or 'ढेबर' in line:
                q = "राजस्थान की सबसे बड़ी मीठे पानी की कृत्रिम झील (ढेबर झील) कौन-सी है?"
                ans = "जयसमंद झील (सलूंबर)"
                dists = ["राजसमंद झील", "पिछोला झील", "फतेहसागर झील"]
                q_obj = (q, ans, dists, "lake")
            elif 'नक्की झील' in line:
                q = "राजस्थान की सर्वाधिक ऊंचाई (1200 मीटर) पर स्थित तथा सबसे गहरी प्राकृतिक झील कौन-सी है?"
                ans = "नक्की झील (माउंट आबू)"
                dists = ["सिलीसेढ़ झील", "आनासागर झील", "फायसागर झील"]
                q_obj = (q, ans, dists, "lake")

        # 9. Minerals & Mines
        if not q_obj:
            if 'झामर-कोटड़ा' in line or 'रॉक फॉस्फेट' in line:
                q = "राजस्थान में प्रसिद्ध 'झामर-कोटड़ा' खान किस खनिज के उत्पादन हेतु देश भर में प्रसिद्ध है?"
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
                q = "विश्व प्रसिद्ध कैल्साइट सफेद संगमरमर (ताजमहल हेतु प्रयुक्त) राजस्थान के किस स्थान से प्राप्त हुआ था?"
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

        # 11. General Key : Value line (Clean transformation, NEVER quote raw line!)
        if not q_obj and ':' in line:
            parts = line.split(':', 1)
            k = parts[0].strip()
            v = parts[1].strip()
            if 3 < len(k) < 30 and 2 < len(v) < 40 and not any(ch in v for ch in ['{', '}', '[', ']']):
                clean_ans = v.split('(')[0].split('।')[0].strip()
                if len(clean_ans) > 2:
                    q = f"राजस्थान सामान्य ज्ञान ({ch_title}) के अनुसार, '{k}' का सही मान / विवरण क्या है?"
                    ans = clean_ans
                    dists = pick_distractors(ans, "district")
                    q_obj = (q, ans, dists, "general")

        if q_obj:
            q_text, ans, dists, cat = q_obj
            # Clean options
            opts = [ans] + dists[:3]
            rng = random.Random(abs(hash(q_text)) % 9999)
            rng.shuffle(opts)
            c_idx = opts.index(ans)
            
            total_mcqs += 1
            ch_questions.append({
                "id": f"CRISP_Q_{total_mcqs}",
                "chapter_id": f"geo_ch_{i+1}",
                "topic": f"{ch_label}: {ch_title}",
                "question": q_text,
                "options": opts,
                "correct_index": c_idx,
                "explanation": f"✅ **सही उत्तर:** {ans}\n\n📌 **परीक्षा संदर्भ:** {ch_label} - {ch_title}\n\n📖 **एग्जामिनर व्याख्या:** {line}",
                "mnemonic": f"💡 **याद रखने की ट्रिक:** मुख्य बिंदु '{ans}' को ध्यान में रखें।",
                "one_liner": f"{q_text} ➔ **{ans}**"
            })

    # Deduplicate questions
    seen_q = set()
    unique_list = []
    for q in ch_questions:
        if q["question"] not in seen_q:
            seen_q.add(q["question"])
            unique_list.append(q)

    all_chapters.append({
        "id": f"geo_ch_{i+1}",
        "number": i + 1,
        "title": f"{ch_label}: {ch_title}",
        "raw_title": ch_title,
        "questions": unique_list
    })
    print(f"✅ {ch_label}: {ch_title} ➔ {len(unique_list)} Crisp MCQs")

print(f"\n==========================================")
print(f"Total Chapters Processed: {len(all_chapters)}")
grand_total = sum(len(c["questions"]) for c in all_chapters)
print(f"Grand Total Clean & Crisp MCQs: {grand_total}")
print(f"==========================================")

with open('/data/user/0/com.termux/files/home/.gemini/antigravity-cli/scratch/meri-taiyari-app/crisp_raj_geography_v2.json', 'w', encoding='utf-8') as f:
    json.dump({
        "doc_url": "https://docs.google.com/document/d/1Qoh9heJ75cwdYFKWA2wfl8Q7LWaFJdobVEwxxug1BKc/edit?usp=drivesdk",
        "title": "राजस्थान भूगोल (Rajasthan Geography)",
        "total_chapters": len(all_chapters),
        "total_questions": grand_total,
        "chapters": all_chapters
    }, f, ensure_ascii=False, indent=2)

print("Saved to crisp_raj_geography_v2.json!")
