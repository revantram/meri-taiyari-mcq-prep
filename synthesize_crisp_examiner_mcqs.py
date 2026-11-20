import re
import json
import random

print("==> 🚀 Starting Crisp, Short, Examiner-Grade Question Generation...")

with open('/data/user/0/com.termux/files/home/.gemini/antigravity-cli/scratch/meri-taiyari-app/raw_raj_geography.txt', 'r', encoding='utf-8') as f:
    text = f.read().replace('\u200b', '').replace('\ufeff', '')

# Banks of homogeneous distractors for various entities
DISTRACTOR_BANKS = {
    "cm": ["हीरालाल शास्त्री", "मोहनलाल सुखाड़िया", "हरिदेव जोशी", "भैरोंसिंह शेखावत", "जयनारायण व्यास", "टीकाराम पालीवाल", "शिवचरण माथुर", "भजनलाल शर्मा"],
    "committee": ["परमेश चन्द्र समिति", "रामलुभाया समिति", "ललित के. पंवार समिति", "पी. सत्यनारायण राव समिति", "हरिश्चंद्र माथुर समिति"],
    "peak": ["गुरुशिखर (1722 मी.)", "सेर (1597 मी.)", "दिलवाड़ा (1442 मी.)", "जरगा (1431 मी.)", "अचलगढ़ (1380 मी.)", "कुंभलगढ़ (1224 मी.)", "रघुनाथगढ़ (1055 मी.)", "ऋषिकेश (1017 मी.)", "कमलनाथ (1001 मी.)", "तारागढ़ (873 मी.)"],
    "river": ["चंबल नदी", "बनास नदी", "लूणी नदी", "माही नदी", "साबरमती नदी", "कालीसिंध नदी", "बाणगंगा नदी", "पार्वती नदी", "घग्घर नदी", "कांतली नदी", "सोम नदी", "जाखम नदी"],
    "dam": ["राणा प्रताप सागर बांध", "गांधी सागर बांध", "जवाहर सागर बांध", "कोटा बैराज", "बीसलपुर बांध", "जाखम बांध", "मेजा बांध", "पांचना बांध", "जवाई बांध", "सोम-कमला-अंबा बांध"],
    "lake": ["सांभर झील", "पचपदरा झील", "डीडवाना झील", "लूणकरणसर झील", "जयसमंद झील", "राजसमंद झील", "पिछोला झील", "फतेहसागर झील", "आनासागर झील", "नक्की झील"],
    "mineral": ["रॉक फॉस्फेट", "सीसा-जस्ता", "तांबा", "लोहा अयस्क", "टंगस्टन", "सफेद संगमरमर", "जिप्सम", "पन्ना", "लिग्नाइट कोयला"],
    "mine": ["झामर-कोटड़ा (उदयपुर)", "जावर (उदयपुर)", "खेतड़ी (झुंझुनूं)", "डेगाना (नागौर)", "मकराना (नागौर)", "जामसर (बीकानेर)", "राजपुरा-दरीबा (राजसमंद)", "मोरीजा-बानोला (जयपुर)"],
    "sanctuary": ["रणथंभौर राष्ट्रीय उद्यान", "केवलादेव घना राष्ट्रीय उद्यान", "मुकुंदरा हिल्स राष्ट्रीय उद्यान", "सरिस्का वन्यजीव अभयारण्य", "तालछापर अभयारण्य", "राष्ट्रीय मरु उद्यान", "कुंभलगढ़ अभयारण्य", "सीतामाता अभयारण्य"],
    "soil": ["काली मृदा (वर्टिसोल)", "लाल-पीली मृदा", "जलोढ़ मृदा (एल्फीसोल)", "रेतीली शुष्क मृदा (एंटीसोल/एरिडिसोल)", "भूरी रेतीली मृदा", "लवणीय मृदा"],
    "climate": ["शुष्क कटिबंधीय जलवायु (BWhw)", "अर्ध-शुष्क स्टेपी जलवायु (BShw)", "उप-आद्र जलवायु (Cwa)", "अति-आद्र जलवायु (Aw)"],
    "district": ["जैसलमेर", "बाड़मेर", "बीकानेर", "जोधपुर", "जयपुर", "उदयपुर", "कोटा", "अजमेर", "भीलवाड़ा", "चित्तौड़गढ़", "डूंगरपुर", "बांसवाड़ा", "झालावाड़", "चूरू", "सीकर", "नागौर", "अलवर", "भरतपुर", "धौलपुर", "करौली", "सवाई माधोपुर", "टोंक", "पाली", "सिरोही", "जालौर", "प्रतापगढ़", "राजसमंद", "बूंदी", "बारां", "दौसा", "अनूपगढ़", "फलोदी", "बालोतरा", "सांचौर", "डीग", "सलूंबर"],
    "division": ["जयपुर संभाग", "अजमेर संभाग", "जोधपुर संभाग", "बीकानेर संभाग", "उदयपुर संभाग", "भरतपुर संभाग", "कोटा संभाग"],
    "year": ["1949", "1952", "1956", "1962", "1982", "1987", "1991", "1994", "1997", "2005", "2008", "2022", "2024"],
    "institute": ["काजरी (CAZRI - जोधपुर)", "आफरी (AFRI - जोधपुर)", "CSWRI (अविकानगर - टोंक)", "राष्ट्रीय ऊंट अनुसंधान केंद्र (बीकानेर)", "राष्ट्रीय सरसों अनुसंधान केंद्र (सेवर, भरतपुर)", "राष्ट्रीय बीजीय मसाला अनुसंधान केंद्र (तबीजी, अजमेर)"],
    "distance": ["1070 कि.मी.", "4850 कि.मी.", "5920 कि.मी.", "826 कि.मी.", "869 कि.मी.", "692 कि.मी.", "550 कि.मी."],
    "area": ["3,42,239 वर्ग कि.मी.", "1,32,139 वर्ग मील", "10.41%", "61.11%", "9.60%", "23.03%"]
}

def get_distractors(correct_val, category):
    bank = DISTRACTOR_BANKS.get(category, DISTRACTOR_BANKS["district"])
    clean_c = correct_val.strip()
    candidates = [b for b in bank if b != clean_c and b.split('(')[0].strip() != clean_c.split('(')[0].strip()]
    rng = random.Random(abs(hash(clean_c)) % 10000)
    rng.shuffle(candidates)
    return candidates[:3]

# Split text into chapters
chapter_matches = list(re.finditer(r'(?m)^[ \t]*(अध्याय\s*[-–]?\s*\d+)[ \t]*\n[ \t]*[❀\*\-–•\s]*(.+?)[❀\*\-–•\s]*$', text))
print(f"Total Chapters matched: {len(chapter_matches)}")

all_chapters = []
total_q = 0

for idx in range(len(chapter_matches)):
    ch_label = chapter_matches[idx].group(1).strip()
    ch_title = chapter_matches[idx].group(2).strip()
    start_pos = chapter_matches[idx].end()
    end_pos = chapter_matches[idx+1].start() if idx+1 < len(chapter_matches) else len(text)
    ch_text = text[start_pos:end_pos].strip()

    ch_q_list = []

    # Custom high-precision rule parser per chapter
    # Let's extract clean factual points from ch_text
    lines = [l.strip() for l in ch_text.splitlines() if l.strip()]

    for line in lines:
        if line.startswith('❀') or len(line) < 8 or line.endswith(':'):
            continue
        clean_line = line.strip('*•\t-– ')

        # Pattern: CM
        for cm in DISTRACTOR_BANKS["cm"]:
            if cm in clean_line:
                # e.g. "राजस्थान में संभागीय व्यवस्था की शुरुआत 1949 में हीरालाल शास्त्री सरकार द्वारा की गई थी।"
                # Determine action
                if 'शुरुआत' in clean_line or 'शुरू' in clean_line:
                    q_text = f"राजस्थान में संभागीय व्यवस्था की शुरुआत (1949) किस मुख्यमंत्री की सरकार द्वारा की गई थी?"
                elif 'समाप्ति' in clean_line or 'समाप्त' in clean_line:
                    q_text = f"अप्रैल 1962 में राजस्थान की संभागीय व्यवस्था को किस मुख्यमंत्री ने समाप्त कर दिया था?"
                elif 'दोबारा' in clean_line or 'पुनः' in clean_line or 'बहाल' in clean_line:
                    q_text = f"जनवरी 1987 में राजस्थान में संभागीय व्यवस्था को पुनः किस मुख्यमंत्री के कार्यकाल में बहाल किया गया?"
                else:
                    q_text = f"राजस्थान प्रशासनिक व्यवस्था में '{clean_line.split(':')[0].strip()}' का संबंध किस मुख्यमंत्री से है?"
                
                correct_ans = cm
                dists = get_distractors(correct_ans, "cm")
                options = [correct_ans] + dists
                random.shuffle(options)
                total_q += 1
                ch_q_list.append({
                    "id": f"CRISP_GEO_Q{total_q}",
                    "chapter_id": f"geo_ch_{idx+1}",
                    "topic": f"{ch_label}: {ch_title}",
                    "question": q_text,
                    "options": options,
                    "correct_index": options.index(correct_ans),
                    "explanation": f"✅ **सही उत्तर:** {correct_ans}\n\n📖 **एग्जामिनर व्याख्या:** {clean_line}",
                    "mnemonic": f"💡 **याद रखने की ट्रिक:** मुख्य नाम '{correct_ans}' को ध्यान में रखें।",
                    "one_liner": f"{q_text.replace('किस मुख्यमंत्री', correct_ans)}"
                })
                break

        # Pattern: Committee
        for comm in DISTRACTOR_BANKS["committee"]:
            if comm in clean_line:
                if 'प्रतापगढ़' in clean_line:
                    q_text = "26 जनवरी 2008 को राजस्थान का 33वां जिला 'प्रतापगढ़' किस समिति की सिफारिश पर बना था?"
                elif 'नए जिले' in clean_line or '2022' in clean_line:
                    q_text = "राजस्थान में नए जिलों के गठन हेतु मार्च 2022 में किस उच्चस्तरीय समिति का गठन किया गया था?"
                elif 'समीक्षा' in clean_line or '2024' in clean_line:
                    q_text = "जून 2024 में नए जिलों के पुनर्गठन एवं समीक्षा हेतु किस समिति का गठन किया गया था?"
                else:
                    q_text = f"राजस्थान में '{clean_line.split(':')[0].strip()}' के संदर्भ में किस समिति की सिफारिश प्रभावी रही?"
                
                correct_ans = comm
                dists = get_distractors(correct_ans, "committee")
                options = [correct_ans] + dists
                random.shuffle(options)
                total_q += 1
                ch_q_list.append({
                    "id": f"CRISP_GEO_Q{total_q}",
                    "chapter_id": f"geo_ch_{idx+1}",
                    "topic": f"{ch_label}: {ch_title}",
                    "question": q_text,
                    "options": options,
                    "correct_index": options.index(correct_ans),
                    "explanation": f"✅ **सही उत्तर:** {correct_ans}\n\n📖 **एग्जामिनर व्याख्या:** {clean_line}",
                    "mnemonic": f"💡 **याद रखने की ट्रिक:** समिति '{correct_ans}' को सीधे विषय से जोड़कर याद रखें।",
                    "one_liner": f"{q_text.replace('किस समिति', correct_ans)}"
                })
                break

        # Pattern: Peak
        for pk in DISTRACTOR_BANKS["peak"]:
            pk_name = pk.split('(')[0].strip()
            if pk_name in clean_line and ('ऊंचाई' in clean_line or 'चोटी' in clean_line or 'मीटर' in clean_line or 'मी.' in clean_line):
                # District or height
                if 'सिरोही' in clean_line:
                    q_text = f"अरावली पर्वतमाला की प्रमुख चोटी '{pk_name}' किस जिले में स्थित है?"
                    correct_ans = "सिरोही"
                    dists = get_distractors(correct_ans, "district")
                else:
                    q_text = f"अरावली पर्वतमाला की प्रमुख चोटी '{pk_name}' की कुल प्रामाणिक ऊंचाई कितनी है?"
                    correct_ans = pk
                    dists = get_distractors(correct_ans, "peak")
                options = [correct_ans] + dists
                random.shuffle(options)
                total_q += 1
                ch_q_list.append({
                    "id": f"CRISP_GEO_Q{total_q}",
                    "chapter_id": f"geo_ch_{idx+1}",
                    "topic": f"{ch_label}: {ch_title}",
                    "question": q_text,
                    "options": options,
                    "correct_index": options.index(correct_ans),
                    "explanation": f"✅ **सही उत्तर:** {correct_ans}\n\n📖 **एग्जामिनर व्याख्या:** {clean_line}",
                    "mnemonic": f"💡 **याद रखने की ट्रिक:** '{pk_name}' ➔ '{correct_ans}'",
                    "one_liner": f"{pk_name}: {correct_ans}"
                })
                break

        # Pattern: Dam / River
        for dm in DISTRACTOR_BANKS["dam"]:
            dm_name = dm.replace(' बांध', '').replace(' बैराज', '').strip()
            if dm_name in clean_line and ('बांध' in clean_line or 'नदी' in clean_line or 'परियोजना' in clean_line):
                if 'चंबल' in clean_line:
                    q_text = f"राजस्थान में प्रसिद्ध '{dm}' किस नदी पर निर्मित है?"
                    correct_ans = "चंबल नदी"
                    dists = get_distractors(correct_ans, "river")
                elif 'मिट्टी का बांध' in clean_line or 'पांचना' in clean_line:
                    q_text = "एशिया का सबसे बड़ा मिट्टी का बांध 'पांचना बांध' किस जिले में स्थित है?"
                    correct_ans = "करौली"
                    dists = ["सवाई माधोपुर", "धौलपुर", "दौसा"]
                elif 'बीसलपुर' in clean_line:
                    q_text = "राजस्थान की सबसे बड़ी पेयजल परियोजना 'बीसलपुर बांध' किस नदी पर स्थित है?"
                    correct_ans = "बनास नदी"
                    dists = ["चंबल नदी", "लूणी नदी", "माही नदी"]
                elif 'जाखम' in clean_line:
                    q_text = "राजस्थान का सबसे ऊंचा बांध (81 मीटर) 'जाखम बांध' किस जिले में स्थित है?"
                    correct_ans = "प्रतापगढ़"
                    dists = ["बांसवाड़ा", "डूंगरपुर", "उदयपुर"]
                else:
                    q_text = f"राजस्थान में प्रसिद्ध '{dm}' का संबंध किस नदी अथवा जिले से है?"
                    correct_ans = dm
                    dists = get_distractors(correct_ans, "dam")
                options = [correct_ans] + dists
                random.shuffle(options)
                total_q += 1
                ch_q_list.append({
                    "id": f"CRISP_GEO_Q{total_q}",
                    "chapter_id": f"geo_ch_{idx+1}",
                    "topic": f"{ch_label}: {ch_title}",
                    "question": q_text,
                    "options": options,
                    "correct_index": options.index(correct_ans),
                    "explanation": f"✅ **सही उत्तर:** {correct_ans}\n\n📖 **एग्जामिनर व्याख्या:** {clean_line}",
                    "mnemonic": f"💡 **याद रखने की ट्रिक:** '{dm}' ➔ '{correct_ans}'",
                    "one_liner": f"{dm}: {correct_ans}"
                })
                break

        # Pattern: Mineral / Mine
        for mn in DISTRACTOR_BANKS["mineral"]:
            if mn in clean_line and ('खान' in clean_line or 'खनन' in clean_line or 'उत्पादन' in clean_line or 'पाया' in clean_line):
                if 'झामर-कोटड़ा' in clean_line or 'रॉक फॉस्फेट' in clean_line:
                    q_text = "राजस्थान में देश का सर्वाधिक 'रॉक फॉस्फेट' उत्पादक क्षेत्र 'झामर-कोटड़ा' किस जिले में है?"
                    correct_ans = "उदयपुर"
                    dists = ["भीलवाड़ा", "चित्तौड़गढ़", "राजसमंद"]
                elif 'जावर' in clean_line or 'सीसा-जस्ता' in clean_line:
                    q_text = "राजस्थान में प्रसिद्ध सीसा-जस्ता खनन क्षेत्र 'जावर' किस जिले में स्थित है?"
                    correct_ans = "उदयपुर"
                    dists = ["अजमेर", "राजसमंद", "भीलवाड़ा"]
                elif 'खेतड़ी' in clean_line or 'तांबा' in clean_line:
                    q_text = "राजस्थान की 'ताम्र नगरी' के रूप में प्रसिद्ध 'खेतड़ी-सिंघाना' किस जिले के अंतर्गत आता है?"
                    correct_ans = "नीम का थाना (झुंझुनूं)"
                    dists = ["अलवर", "सीकर", "चूरू"]
                elif 'मकराना' in clean_line or 'संगमरमर' in clean_line:
                    q_text = "विश्व प्रसिद्ध कैल्साइट किस्म का सफेद संगमरमर राजस्थान के किस क्षेत्र से निकलता है?"
                    correct_ans = "मकराना (डीडवाना-कुचामन)"
                    dists = ["राजसमंद", "उदयपुर", "किशनगढ़"]
                elif 'डेगाना' in clean_line or 'टंगस्टन' in clean_line:
                    q_text = "राजस्थान में 'टंगस्टन' उत्पादन के लिए प्रसिद्ध रेवंत पहाड़ी 'डेगाना' किस जिले में स्थित है?"
                    correct_ans = "नागौर"
                    dists = ["बीकानेर", "जोधपुर", "पाली"]
                else:
                    q_text = f"राजस्थान में प्रसिद्ध '{mn}' का प्रमुख उत्पादक क्षेत्र कौन-सा है?"
                    correct_ans = mn
                    dists = get_distractors(correct_ans, "mineral")
                options = [correct_ans] + dists
                random.shuffle(options)
                total_q += 1
                ch_q_list.append({
                    "id": f"CRISP_GEO_Q{total_q}",
                    "chapter_id": f"geo_ch_{idx+1}",
                    "topic": f"{ch_label}: {ch_title}",
                    "question": q_text,
                    "options": options,
                    "correct_index": options.index(correct_ans),
                    "explanation": f"✅ **सही उत्तर:** {correct_ans}\n\n📖 **एग्जामिनर व्याख्या:** {clean_line}",
                    "mnemonic": f"💡 **याद रखने की ट्रिक:** '{mn}' ➔ '{correct_ans}'",
                    "one_liner": f"{mn}: {correct_ans}"
                })
                break

        # Pattern: Lake
        for lk in DISTRACTOR_BANKS["lake"]:
            clean_lk = lk.replace(' झील', '').strip()
            if clean_lk in clean_line and ('झील' in clean_line or 'नमक' in clean_line or 'मीठे पानी' in clean_line):
                if 'सांभर' in clean_line or '8.7%' in clean_line:
                    q_text = "देश के कुल नमक उत्पादन का लगभग 8.7% नमक किस झील से उत्पादित होता है?"
                    correct_ans = "सांभर झील"
                    dists = ["पचपदरा झील", "डीडवाना झील", "लूणकरणसर झील"]
                elif 'पचपदरा' in clean_line or '98%' in clean_line:
                    q_text = "राजस्थान की किस झील के नमक में 98% सोडियम क्लोराइड (NaCl) पाया जाता है, जो खाने योग्य सर्वश्रेष्ठ है?"
                    correct_ans = "पचपदरा झील (बालोतरा)"
                    dists = ["सांभर झील", "डीडवाना झील", "कावोध झील"]
                elif 'जयसमंद' in clean_line:
                    q_text = "राजस्थान की सबसे बड़ी मीठे पानी की कृत्रिम झील (ढेबर झील) कौन-सी है?"
                    correct_ans = "जयसमंद झील (सलूंबर)"
                    dists = ["राजसमंद झील", "पिछोला झील", "फतेहसागर झील"]
                elif 'नक्की' in clean_line:
                    q_text = "राजस्थान की सर्वाधिक ऊंचाई (1200 मीटर) पर स्थित तथा सबसे गहरी प्राकृतिक झील कौन-सी है?"
                    correct_ans = "नक्की झील (माउंट आबू)"
                    dists = ["सिलीसेढ़ झील", "आनासागर झील", "फायसागर झील"]
                else:
                    q_text = f"राजस्थान में स्थित प्रसिद्ध '{lk}' के संदर्भ में सही तथ्य पहचानिए:"
                    correct_ans = lk
                    dists = get_distractors(correct_ans, "lake")
                options = [correct_ans] + dists
                random.shuffle(options)
                total_q += 1
                ch_q_list.append({
                    "id": f"CRISP_GEO_Q{total_q}",
                    "chapter_id": f"geo_ch_{idx+1}",
                    "topic": f"{ch_label}: {ch_title}",
                    "question": q_text,
                    "options": options,
                    "correct_index": options.index(correct_ans),
                    "explanation": f"✅ **सही उत्तर:** {correct_ans}\n\n📖 **एग्जामिनर व्याख्या:** {clean_line}",
                    "mnemonic": f"💡 **याद रखने की ट्रिक:** '{lk}' ➔ '{correct_ans}'",
                    "one_liner": f"{lk}: {correct_ans}"
                })
                break

        # Pattern: Institute
        for inst in DISTRACTOR_BANKS["institute"]:
            clean_i = inst.split('(')[0].strip()
            if clean_i in clean_line or ('काजरी' in clean_line) or ('आफरी' in clean_line) or ('सेवर' in clean_line):
                if 'काजरी' in clean_line or 'CAZRI' in clean_line:
                    q_text = "केन्द्रीय शुष्क क्षेत्र अनुसंधान संस्थान (काजरी / CAZRI) की स्थापना 1959 में कहाँ की गई थी?"
                    correct_ans = "जोधपुर"
                    dists = ["बीकानेर", "जयपुर", "अजमेर"]
                elif 'आफरी' in clean_line or 'AFRI' in clean_line:
                    q_text = "शुष्क वन अनुसंधान संस्थान (आफरी / AFRI) का मुख्यालय कहाँ स्थित है?"
                    correct_ans = "जोधपुर"
                    dists = ["उदयपुर", "कोटा", "पाली"]
                elif 'सरसों' in clean_line or 'सेवर' in clean_line:
                    q_text = "राष्ट्रीय सरसों अनुसंधान निदेशालय (DRMR) राजस्थान के किस स्थान पर स्थित है?"
                    correct_ans = "सेवर (भरतपुर)"
                    dists = ["तबीजी (अजमेर)", "बोरखेड़ा (कोटा)", "सूरतगढ़ (श्रीगंगानगर)"]
                elif 'मसाला' in clean_line or 'तबीजी' in clean_line:
                    q_text = "राष्ट्रीय बीजीय मसाला अनुसंधान केंद्र (NRCSS) कहाँ स्थित है?"
                    correct_ans = "तबीजी (अजमेर)"
                    dists = ["सेवर (भरतपुर)", "अविकानगर (टोंक)", "मंडोर (जोधपुर)"]
                elif 'अविकानगर' in clean_line or 'भेड़' in clean_line:
                    q_text = "केन्द्रीय भेड़ एवं ऊन अनुसंधान संस्थान (CSWRI) राजस्थान में कहाँ स्थित है?"
                    correct_ans = "अविकानगर (टोंक)"
                    dists = ["जोहड़बीड़ (बीकानेर)", "बिलाड़ा (जोधपुर)", "फतेहपुर (सीकर)"]
                else:
                    q_text = f"राजस्थान में प्रसिद्ध अनुसंधान संस्थान '{inst}' कहाँ स्थित है?"
                    correct_ans = inst
                    dists = get_distractors(correct_ans, "institute")
                options = [correct_ans] + dists
                random.shuffle(options)
                total_q += 1
                ch_q_list.append({
                    "id": f"CRISP_GEO_Q{total_q}",
                    "chapter_id": f"geo_ch_{idx+1}",
                    "topic": f"{ch_label}: {ch_title}",
                    "question": q_text,
                    "options": options,
                    "correct_index": options.index(correct_ans),
                    "explanation": f"✅ **सही उत्तर:** {correct_ans}\n\n📖 **एग्जामिनर व्याख्या:** {clean_line}",
                    "mnemonic": f"💡 **याद रखने की ट्रिक:** '{inst}' ➔ '{correct_ans}'",
                    "one_liner": f"{inst}: {correct_ans}"
                })
                break

    # If chapter questions < 10, synthesize from key facts
    if len(ch_q_list) < 10:
        # Generate essential core questions from chapter title & facts
        for l in lines[:15]:
            if ':' in l:
                k, v = l.split(':', 1)
                k = k.strip('*•\t-– ')
                v = v.strip('*•\t-– ')
                if 2 < len(k) < 30 and 2 < len(v) < 35:
                    q_text = f"राजस्थान {ch_title} के अनुसार, '{k}' का सही मान अथवा विवरण क्या है?"
                    correct_ans = v
                    dists = ["अनिश्चित", "परिवर्तनीय", "उपलब्ध नहीं"]
                    # find better dists from other lines
                    other_v = [ol.split(':', 1)[1].strip() for ol in lines if ':' in ol and ol != l]
                    if len(other_v) >= 3:
                        dists = other_v[:3]
                    options = [correct_ans] + dists[:3]
                    random.shuffle(options)
                    total_q += 1
                    ch_q_list.append({
                        "id": f"CRISP_GEO_Q{total_q}",
                        "chapter_id": f"geo_ch_{idx+1}",
                        "topic": f"{ch_label}: {ch_title}",
                        "question": q_text,
                        "options": options,
                        "correct_index": options.index(correct_ans),
                        "explanation": f"✅ **सही उत्तर:** {correct_ans}\n\n📖 **एग्जामिनर व्याख्या:** {l}",
                        "mnemonic": f"💡 **याद रखने की ट्रिक:** '{k}' ➔ '{correct_ans}'",
                        "one_liner": f"{k}: {correct_ans}"
                    })

    # Deduplicate questions by question text
    seen_q = set()
    unique_q_list = []
    for q in ch_q_list:
        if q["question"] not in seen_q:
            seen_q.add(q["question"])
            unique_q_list.append(q)

    all_chapters.append({
        "id": f"geo_ch_{idx+1}",
        "number": idx + 1,
        "title": f"{ch_label}: {ch_title}",
        "raw_title": ch_title,
        "questions": unique_q_list
    })
    print(f"✅ {ch_label}: {ch_title} ➔ {len(unique_q_list)} Crisp Examiner MCQs")

print(f"\nTotal Chapters: {len(all_chapters)}")
total_crisp = sum(len(c["questions"]) for c in all_chapters)
print(f"Grand Total Crisp Examiner MCQs: {total_crisp}")

with open('/data/user/0/com.termux/files/home/.gemini/antigravity-cli/scratch/meri-taiyari-app/crisp_raj_geography.json', 'w', encoding='utf-8') as f:
    json.dump({
        "doc_url": "https://docs.google.com/document/d/1Qoh9heJ75cwdYFKWA2wfl8Q7LWaFJdobVEwxxug1BKc/edit?usp=drivesdk",
        "title": "राजस्थान भूगोल (Rajasthan Geography)",
        "total_chapters": len(all_chapters),
        "total_questions": total_crisp,
        "chapters": all_chapters
    }, f, ensure_ascii=False, indent=2)

print("Saved to crisp_raj_geography.json successfully!")
