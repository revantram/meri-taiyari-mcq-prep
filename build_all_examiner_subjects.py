import re
import json
import random

print("==> 🚀 Starting Pure Examiner-Grade Subject Processing...")

with open('/data/user/0/com.termux/files/home/.gemini/antigravity-cli/scratch/meri-taiyari-app/raw_raj_geography.txt', 'r', encoding='utf-8') as f:
    geo_text = f.read().replace('\u200b', '').replace('\ufeff', '')

BANKS = {
    "cm": [
        "हीरालाल शास्त्री", "मोहनलाल सुखाड़िया", "हरिदेव जोशी", "भैरोंसिंह शेखावत", 
        "जयनारायण व्यास", "टीकाराम पालीवाल", "शिवचरण माथुर", "बरकतुल्लाह खान", "वसुंधरा राजे", "अशोक गहलोत", "भजनलाल शर्मा"
    ],
    "committee": [
        "परमेश चन्द्र समिति", "रामलुभाया समिति", "ललित के. पंवार समिति", "पी. सत्यनारायण राव समिति", "हरिश्चंद्र माथुर समिति", "शिवचरण माथुर समिति"
    ],
    "peak": [
        "गुरुशिखर (1722 मी.)", "सेर (1597 मी.)", "दिलवाड़ा (1442 मी.)", "जरगा (1431 मी.)", 
        "अचलगढ़ (1380 मी.)", "कुंभलगढ़ (1224 मी.)", "रघुनाथगढ़ (1055 मी.)", "ऋषिकेश (1017 मी.)", "कमलनाथ (1001 मी.)", "तारागढ़ (873 मी.)"
    ],
    "river": [
        "चंबल नदी", "बनास नदी", "लूणी नदी", "माही नदी", "साबरमती नदी", "कालीसिंध नदी", 
        "बाणगंगा नदी", "पार्वती नदी", "घग्घर नदी", "कांतली नदी", "सोम नदी", "जाखम नदी", "कोठारी नदी", "खारी नदी"
    ],
    "dam": [
        "राणा प्रताप सागर बांध", "गांधी सागर बांध", "जवाहर सागर बांध", "कोटा बैराज", 
        "बीसलपुर बांध", "जाखम बांध", "मेजा बांध", "सोम-कमला-अंबा बांध", "पांचना बांध", "जवाई बांध"
    ],
    "lake": [
        "सांभर झील", "पचपदरा झील", "डीडवाना झील", "लूणकरणसर झील", "जयसमंद झील", 
        "राजसमंद झील", "पिछोला झील", "फतेहसागर झील", "आनासागर झील", "नक्की झील", "सिलीसेढ़ झील"
    ],
    "sanctuary": [
        "रणथंभौर राष्ट्रीय उद्यान", "केवलादेव घना राष्ट्रीय उद्यान", "मुकुंदरा हिल्स राष्ट्रीय उद्यान", 
        "सरिस्का वन्यजीव अभयारण्य", "तालछापर अभयारण्य", "राष्ट्रीय मरु उद्यान", "कुंभलगढ़ अभयारण्य", "सीतामाता अभयारण्य", "माउंट आबू अभयारण्य"
    ],
    "soil": [
        "काली मृदा (वर्टिसोल)", "लाल-पीली मृदा", "जलोढ़ मृदा (एल्फीसोल / इन्सेप्टिसोल)", 
        "रेतीली शुष्क मृदा (एंटीसोल / एरिडिसोल)", "भूरी रेतीली मृदा", "लवणीय मृदा"
    ],
    "climate": [
        "शुष्क कटिबंधीय जलवायु (BWhw)", "अर्ध-शुष्क स्टेपी जलवायु (BShw)", 
        "उप-आद्र मानसूनी जलवायु (Cwa)", "अति-आद्र जलवायु (Aw)"
    ],
    "mineral": [
        "रॉक फॉस्फेट (झामर-कोटड़ा)", "सीसा-जस्ता (जावर, राजपुरा-दरीबा)", "तांबा (खेतड़ी, खो-दरीबा)", 
        "लोहा (मोरीजा-बानोला)", "टंगस्टन (डेगाना, वाल्दा)", "सफेद संगमरमर (मकराना)", "जिप्सम (जामसर)", "पन्ना (कालागुमान)"
    ],
    "district": [
        "जैसलमेर", "बाड़मेर", "बीकानेर", "जोधपुर", "जयपुर", "उदयपुर", "कोटा", "अजमेर", "भीलवाड़ा", "चित्तौड़गढ़",
        "डूंगरपुर", "बांसवाड़ा", "झालावाड़", "चूरू", "सीकर", "नागौर", "अलवर", "भरतपुर", "धौलपुर", "करौली",
        "सवाई माधोपुर", "टोंक", "पाली", "सिरोही", "जालौर", "प्रतापगढ़", "राजसमंद", "बूंदी", "बारां", "दौसा",
        "अनूपगढ़", "फलोदी", "बालोतरा", "सांचौर", "कोटपूतली-बहरोड़", "खैरथल-तिजारा", "नीम का थाना", "डीडवाना-कुचामन"
    ],
    "division": [
        "जयपुर संभाग", "अजमेर संभाग", "जोधपुर संभाग", "बीकानेर संभाग", "उदयपुर संभाग", "भरतपुर संभाग", "कोटा संभाग"
    ],
    "year": [
        "1949", "1952", "1956", "1962", "1982", "1987", "1991", "1994", "1997", "2005", "2008", "2022", "2024"
    ]
}

def extract_matched_entity(full_text):
    # 1. CM check
    for cm in BANKS["cm"]:
        if cm in full_text:
            return "cm", cm
            
    # 2. Committee check
    for comm in BANKS["committee"]:
        if comm in full_text:
            return "committee", comm
            
    # 3. Peak check
    for pk in BANKS["peak"]:
        clean_pk = pk.split('(')[0].strip()
        if clean_pk in full_text:
            return "peak", pk
            
    # 4. Dam check
    for dm in BANKS["dam"]:
        clean_dm = dm.replace(' बांध', '').replace(' बैराज', '').strip()
        if clean_dm in full_text:
            return "dam", dm

    # 5. Lake check
    for lk in BANKS["lake"]:
        clean_lk = lk.replace(' झील', '').strip()
        if clean_lk in full_text:
            return "lake", lk

    # 6. River check
    for rv in BANKS["river"]:
        clean_rv = rv.replace(' नदी', '').strip()
        if clean_rv in full_text:
            return "river", rv

    # 7. Sanctuary check
    for sn in BANKS["sanctuary"]:
        clean_sn = sn.split()[0].strip()
        if clean_sn in full_text and len(clean_sn) > 3:
            return "sanctuary", sn

    # 8. Soil check
    for sl in BANKS["soil"]:
        clean_sl = sl.split('(')[0].strip()
        if clean_sl in full_text:
            return "soil", sl

    # 9. Climate check
    for cl in BANKS["climate"]:
        clean_cl = cl.split('(')[0].strip()
        if clean_cl in full_text:
            return "climate", cl

    # 10. Mineral check
    for mn in BANKS["mineral"]:
        clean_mn = mn.split('(')[0].strip()
        if clean_mn in full_text:
            return "mineral", mn

    # 11. Division check
    for dv in BANKS["division"]:
        clean_dv = dv.replace(' संभाग', '').strip()
        if clean_dv in full_text and 'संभाग' in full_text:
            return "division", dv

    # 12. District check
    for dt in BANKS["district"]:
        if dt in full_text:
            return "district", dt

    # 13. Year check
    ym = re.search(r'\b(19\d\d|20\d\d)\b', full_text)
    if ym:
        return "year", ym.group(1)

    return "general", None

chapter_matches = list(re.finditer(r'(?m)^[ \t]*(अध्याय\s*[-–]?\s*\d+)[ \t]*\n[ \t]*[❀\*\-–•\s]*(.+?)[❀\*\-–•\s]*$', geo_text))
print(f"Total Chapters to process: {len(chapter_matches)}")

all_processed_chapters = []
total_mcqs = 0

for i in range(len(chapter_matches)):
    ch_label = chapter_matches[i].group(1).strip()
    ch_title = chapter_matches[i].group(2).strip()
    start_pos = chapter_matches[i].end()
    end_pos = chapter_matches[i+1].start() if i+1 < len(chapter_matches) else len(geo_text)
    ch_text = geo_text[start_pos:end_pos].strip()
    
    lines = [l.strip() for l in ch_text.splitlines() if l.strip()]
    
    subsections = []
    cur_sub = ch_title
    cur_points = []
    
    for l in lines:
        if l.startswith('❀') or (len(l) < 40 and not l.startswith('*') and not ':' in l and not '।' in l and not '-' in l):
            clean_sub = l.strip('❀ *•\t-–')
            if clean_sub:
                if cur_points:
                    subsections.append((cur_sub, cur_points))
                    cur_points = []
                cur_sub = clean_sub
            continue
            
        clean_l = l.strip(' *•\t')
        if len(clean_l) >= 8:
            cur_points.append(clean_l)
            
    if cur_points:
        subsections.append((cur_sub, cur_points))

    ch_questions = []

    # 1. Statement-based (कथन I, II, III) evaluation questions
    for sub_title, p_list in subsections:
        # Filter genuine factual sentences (not just labels)
        valid_facts = [p for p in p_list if len(p) > 20 and not p.endswith(':')]
        if len(valid_facts) >= 3:
            f1, f2, f3 = valid_facts[0], valid_facts[1], valid_facts[2]
            
            stmt_q = (
                f"राजस्थान सामान्य ज्ञान ({ch_title} - {sub_title}) के संदर्भ में निम्नलिखित कथनों पर विचार कीजिए:\n"
                f"I. {f1}\n"
                f"II. {f2}\n"
                f"III. {f3}\n\n"
                f"उपर्युक्त में से कौन-सा/से कथन सत्य है/हैं?"
            )
            
            total_mcqs += 1
            stmt_opts = [
                "I, II और III सभी सत्य हैं",
                "केवल I और II सत्य हैं",
                "केवल II और III सत्य हैं",
                "केवल I और III सत्य हैं"
            ]
            
            ch_questions.append({
                "id": f"GEO_STMT_{i+1}_{total_mcqs}",
                "chapter_id": f"geo_ch_{i+1}",
                "topic": f"{ch_label}: {ch_title}",
                "subheading": sub_title,
                "question_type": "statement_multi",
                "question": stmt_q,
                "options": stmt_opts,
                "correct_index": 0,
                "explanation": (
                    f"✅ **सही उत्तर: I, II और III सभी सत्य हैं**\n\n"
                    f"📌 **परीक्षा संदर्भ:** {ch_label} - {ch_title} ({sub_title})\n\n"
                    f"📖 **विस्तृत एग्जामिनर व्याख्या (Facts from Notes):**\n"
                    f"• {f1}\n• {f2}\n• {f3}\n"
                    f"RPSC एवं RSSB परीक्षा के आधिकारिक पाठ्यक्रम के अनुसार ये सभी कथन पूर्णतः सत्य हैं।"
                ),
                "mnemonic": f"💡 **याद रखने की ट्रिक:** '{sub_title[:20]}' ➔ तीनों मुख्य बिंदुओं को एक साथ स्मरण रखें।",
                "one_liner": f"**{sub_title}**: {f1[:60]}... (सभी बिंदु सत्य)"
            })

    # 2. Direct Analytical Questions with strictly Homogeneous Distractors
    for sub_title, p_list in subsections:
        for p in p_list:
            if len(p) < 10: continue
            
            ent_cat, ent_val = extract_matched_entity(p)
            
            if ent_cat != "general" and ent_val:
                correct_ans = ent_val
                # Pick 3 homogeneous distractors from exact same category bank
                bank = BANKS[ent_cat]
                distractors = [b for b in bank if b != correct_ans]
                rng = random.Random(total_mcqs * 37)
                rng.shuffle(distractors)
                options = [correct_ans] + distractors[:3]
                rng.shuffle(options)
                correct_idx = options.index(correct_ans)
                
                # Context-specific examiner questions
                if ent_cat == "cm":
                    q_text = f"राजस्थान में '{sub_title}' के अंतर्गत निम्नलिखित कार्य / घटना किस मुख्यमंत्री अथवा सरकार के कार्यकाल से संबंधित है?\n\"{p}\""
                elif ent_cat == "committee":
                    q_text = f"राजस्थान में '{sub_title}' के संबंध में निम्नलिखित प्रशासनिक निर्णय किस समिति की सिफारिश पर आधारित था?\n\"{p}\""
                elif ent_cat == "peak":
                    q_text = f"अरावली पर्वतमाला की प्रमुख चोटियों के संदर्भ में, निम्नलिखित विवरण किस पर्वत चोटी से संबंधित है?\n\"{p}\""
                elif ent_cat == "river":
                    q_text = f"राजस्थान के अपवाह तंत्र के तहत, निम्नलिखित प्रवाह एवं उद्गम विवरण किस नदी का है?\n\"{p}\""
                elif ent_cat == "dam":
                    q_text = f"राजस्थान की जल संसाधन परियोजनाओं के तहत, निम्नलिखित विवरण किस बांध अथवा परियोजना का है?\n\"{p}\""
                elif ent_cat == "lake":
                    q_text = f"राजस्थान की झीलों के संदर्भ में, निम्नलिखित तथ्य किस झील से संबंधित है?\n\"{p}\""
                elif ent_cat == "mineral":
                    q_text = f"राजस्थान में खनिज संपदा एवं खानों के संदर्भ में, निम्नलिखित प्रमुख खनन विवरण किससे संबंधित है?\n\"{p}\""
                elif ent_cat == "sanctuary":
                    q_text = f"राजस्थान के वन्यजीव संरक्षण के अंतर्गत, निम्नलिखित विवरण किस अभयारण्य अथवा राष्ट्रीय उद्यान का है?\n\"{p}\""
                elif ent_cat == "soil":
                    q_text = f"राजस्थान के मृदा वर्गीकरण (ICAR / वैज्ञानिक वर्गीकरण) के तहत, निम्नलिखित विशेषताएं किस मृदा की हैं?\n\"{p}\""
                elif ent_cat == "climate":
                    q_text = f"राजस्थान के जलवायु प्रदेशों के संबंध में, निम्नलिखित विशिष्ट विवरण किस जलवायु कटिबंध का है?\n\"{p}\""
                elif ent_cat == "district":
                    q_text = f"राजस्थान के भूगोल एवं प्रशासनिक संरचना के संदर्भ में, निम्नलिखित तथ्य किस जिले से संबंधित है?\n\"{p}\""
                elif ent_cat == "division":
                    q_text = f"राजस्थान की प्रशासनिक व्यवस्था के तहत, निम्नलिखित संभाग विवरण किस संभाग से संबंधित है?\n\"{p}\""
                elif ent_cat == "year":
                    q_text = f"राजस्थान के '{sub_title}' के संदर्भ में, निम्नलिखित ऐतिहासिक अथवा प्रशासनिक घटना किस वर्ष घटित हुई थी?\n\"{p}\""
                else:
                    q_text = f"राजस्थान सामान्य ज्ञान ({ch_title}) के तहत निम्नलिखित सत्य तथ्य पहचानिए:\n\"{p}\""

                total_mcqs += 1
                ch_questions.append({
                    "id": f"GEO_EXAM_{i+1}_{total_mcqs}",
                    "chapter_id": f"geo_ch_{i+1}",
                    "topic": f"{ch_label}: {ch_title}",
                    "subheading": sub_title,
                    "question_type": f"homogeneous_{ent_cat}",
                    "question": q_text,
                    "options": options,
                    "correct_index": correct_idx,
                    "explanation": (
                        f"✅ **सही उत्तर: {correct_ans}**\n\n"
                        f"📌 **परीक्षा संदर्भ:** {ch_label} - {ch_title} ({sub_title})\n\n"
                        f"📖 **विस्तृत एग्जामिनर व्याख्या (Facts from Notes):**\n"
                        f"• {p}\n"
                        f"• यह प्रश्न RPSC / RSSB मानक पाठ्यक्रम के अनुसार होमोजिनियस विकल्पों के साथ तैयार किया गया है।"
                    ),
                    "mnemonic": f"💡 **याद रखने की ट्रिक:** '{sub_title[:20]}' ➔ सही उत्तर '{correct_ans}' को मुख्य संदर्भ से जोड़कर याद रखें।",
                    "one_liner": f"**{sub_title}**: {p[:80]}..."
                })

    all_processed_chapters.append({
        "id": f"geo_ch_{i+1}",
        "number": i + 1,
        "title": f"{ch_label}: {ch_title}",
        "raw_title": ch_title,
        "questions": ch_questions
    })
    print(f"✅ {ch_label}: {ch_title} -> {len(ch_questions)} Pure Examiner-Grade MCQs")

print(f"\n==========================================")
print(f"Total Chapters Processed: {len(all_processed_chapters)}")
print(f"Grand Total Pure Examiner MCQs: {total_mcqs}")
print(f"==========================================")

with open('/data/user/0/com.termux/files/home/.gemini/antigravity-cli/scratch/meri-taiyari-app/parsed_raj_geography_pure_examiner.json', 'w', encoding='utf-8') as f:
    json.dump({
        "doc_url": "https://docs.google.com/document/d/1Qoh9heJ75cwdYFKWA2wfl8Q7LWaFJdobVEwxxug1BKc/edit?usp=drivesdk",
        "title": "राजस्थान भूगोल (Rajasthan Geography)",
        "total_chapters": len(all_processed_chapters),
        "total_questions": total_mcqs,
        "chapters": all_processed_chapters
    }, f, ensure_ascii=False, indent=2)

print("Saved to parsed_raj_geography_pure_examiner.json successfully!")
