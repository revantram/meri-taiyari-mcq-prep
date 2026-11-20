import re
import json
import random

with open('/data/user/0/com.termux/files/home/.gemini/antigravity-cli/scratch/meri-taiyari-app/raw_raj_geography.txt', 'r', encoding='utf-8') as f:
    text = f.read().replace('\u200b', '').replace('\ufeff', '')

chapter_matches = list(re.finditer(r'(?m)^[ \t]*(अध्याय\s*[-–]?\s*\d+)[ \t]*\n[ \t]*[❀\*\-–•\s]*(.+?)[❀\*\-–•\s]*$', text))
print(f"Processing {len(chapter_matches)} chapters exhaustively...")

# Extensive distractor bank for Rajasthan GK
distractor_bank_raj = [
    "जैसलमेर", "बाड़मेर", "बीकानेर", "जोधपुर", "जयपुर", "उदयपुर", "कोटा", "अजमेर", "भीलवाड़ा", "चित्तौड़गढ़",
    "डूंगरपुर", "बांसवाड़ा", "झालावाड़", "चूरू", "सीकर", "नागौर", "अलवर", "भरतपुर", "धौलपुर", "करौली",
    "सवाई माधोपुर", "टोंक", "पाली", "सिरोही", "जालौर", "प्रतापगढ़", "राजसमंद", "बूंदी", "बारां", "दौसा",
    "अनूपगढ़", "फलोदी", "बालोतरा", "सांचौर", "कोटपूतली-बहरोड़", "खैरथल-तिजारा", "नीम का थाना", "डीडवाना-कुचामन",
    "अरावली पर्वतमाला", "थार का मरुस्थल", "पूर्वी मैदान", "हाड़ौती का पठार", "लूणी बेसिन", "शेखावाटी बेसिन", "चंबल बेसिन", "बनास बेसिन",
    "चंबल नदी", "बनास नदी", "लूणी नदी", "माही नदी", "साबरमती नदी", "कालीसिंध नदी", "बाणगंगा नदी", "पार्वती नदी", "सोम नदी", "जाखम नदी",
    "काली मृदा (वर्टिसोल)", "लाल-पीली मृदा", "जलोढ़ मृदा (इन्सेप्टिसोल)", "रेतीली शुष्क मृदा (एंटीसोल)", "भूरी रेतीली मृदा",
    "उपोष्ण कटिबंधीय", "शुष्क जलवायु", "अर्ध-शुष्क जलवायु", "अति-आद्र जलवायु", "आद्र जलवायु", "उप-आद्र जलवायु",
    "5920 कि.मी.", "1070 कि.मी.", "4850 कि.मी.", "826 कि.मी.", "869 कि.मी.", "3,42,239 वर्ग कि.मी.",
    "कथन (I) और (II) दोनों सत्य हैं", "कथन (I) सत्य है तथा (II) असत्य है", "कथन (I) असत्य है तथा (II) सत्य है"
]

def make_distractors(correct_ans, siblings):
    distractors = []
    clean_c = correct_ans.split('(')[0].split('–')[0].split('-')[0].strip()

    # 1. Pick from siblings
    for s in siblings:
        clean_s = s.split('(')[0].split('–')[0].split('-')[0].strip()
        if 2 < len(clean_s) < 45 and clean_s != clean_c and clean_s not in distractors:
            distractors.append(clean_s)
        if len(distractors) >= 3:
            break

    # 2. Pick from general bank
    if len(distractors) < 3:
        for db in distractor_bank_raj:
            if db != clean_c and db not in distractors:
                distractors.append(db)
            if len(distractors) >= 3:
                break

    return distractors[:3]

parsed_chapters = []
grand_total_mcqs = 0

for i in range(len(chapter_matches)):
    ch_label = chapter_matches[i].group(1).strip()
    ch_title = chapter_matches[i].group(2).strip()
    
    start_pos = chapter_matches[i].end()
    end_pos = chapter_matches[i+1].start() if i+1 < len(chapter_matches) else len(text)
    ch_text = text[start_pos:end_pos].strip()
    
    lines = [l.strip() for l in ch_text.splitlines() if l.strip()]
    
    facts = []
    current_sub = ch_title
    seen_lines = set()

    for l in lines:
        if l.startswith('❀') or (len(l) < 40 and not l.startswith('*') and not ':' in l and not '।' in l and not '-' in l):
            clean_sub = l.strip('❀ *•\t-–')
            if clean_sub:
                current_sub = clean_sub
            continue
            
        clean_l = l.strip(' *•\t')
        if len(clean_l) < 6 or clean_l in seen_lines:
            continue
        seen_lines.add(clean_l)
        
        # Key: Value or delimiter
        if ':' in clean_l or '–' in clean_l or ('-' in clean_l and not clean_l.startswith('-')):
            parts = re.split(r'[:–\-]\s*', clean_l, maxsplit=1)
            if len(parts) == 2 and len(parts[0].strip()) >= 2 and len(parts[1].strip()) >= 2:
                facts.append({
                    'sub': current_sub,
                    'key': parts[0].strip(),
                    'val': parts[1].strip(),
                    'full': clean_l
                })
        elif len(clean_l) > 20 and ('है।' in clean_l or 'हैं।' in clean_l or 'स्थित है' in clean_l or 'कहा जाता है' in clean_l or 'पाया जाता है' in clean_l):
            # Factual sentence
            facts.append({
                'sub': current_sub,
                'key': current_sub,
                'val': clean_l,
                'full': clean_l
            })

    # Deduplicate candidate values
    sibling_vals = [f['val'] for f in facts]
    
    chapter_questions = []
    for idx, fp in enumerate(facts):
        grand_total_mcqs += 1
        q_id = f"RAJ_GEO_CH{i+1}_{grand_total_mcqs}"
        
        key = fp['key']
        val = fp['val']
        
        # Clean answer candidate
        ans_cand = val.split('(')[0].split('।')[0].strip()
        if len(ans_cand) > 55:
            ans_cand = ans_cand[:50] + '...'
            
        # Realistic examiner question framing
        if any(w in key for w in ['विस्तार', 'लंबाई', 'चौड़ाई', 'क्षेत्रफल', 'सीमा', 'ऊंचाई', 'गहराई', 'अनुपात']):
            q_text = f"राजस्थान भूगोल के संदर्भ में, '{key}' के संबंध में सही मान / तथ्य कौन-सा है?"
        elif any(w in key for w in ['प्रकार', 'जलवायु', 'मृदा', 'वन', 'वर्गीकरण', 'श्रेणी']):
            q_text = f"राजस्थान में {fp['sub']} के अंतर्गत '{key}' का सही विवरण पहचानिए:"
        elif any(w in key for w in ['जिला', 'मुख्यालय', 'स्थान', 'उद्गम', 'संगम', 'अभयारण्य', 'बांध', 'परियोजना', 'खदान', 'क्षेत्र']):
            q_text = f"राजस्थान सामान्य ज्ञान के अनुसार, '{key}' से संबंधित सही स्थान / जिला अथवा विवरण क्या है?"
        elif any(w in key for w in ['सर्वाधिक', 'न्यूनतम', 'प्रथम', 'द्वितीय', 'प्रमुख']):
            q_text = f"राजस्थान में {fp['sub']} के संबंध में '{key}' का सही विकल्प कौन-सा है?"
        else:
            q_text = f"राजस्थान सामान्य ज्ञान ({ch_title}) के संदर्भ में, '{key}' के विषय में सत्य कथन पहचानिए:"

        distractors = make_distractors(ans_cand, sibling_vals)
        options = [ans_cand] + distractors
        
        rng = random.Random(grand_total_mcqs * 53)
        rng.shuffle(options)
        correct_idx = options.index(ans_cand)
        
        explanation = (
            f"✅ **सही उत्तर:** {ans_cand}\n\n"
            f"📌 **अध्याय संदर्भ:** {ch_label} - {ch_title} ({fp['sub']})\n\n"
            f"📖 **विस्तृत एग्जामिनर व्याख्या (Facts from Notes):**\n"
            f"• {fp['full']}\n"
            f"• RPSC / RSSB परीक्षा के नवीनतम पाठ्यक्रम पर आधारित महत्वपूर्ण तथ्य।"
        )
        
        mnemonic = f"💡 **याद रखने की ट्रिक:** '{key[:20]}' ➔ मुख्य बिंदु '{ans_cand[:22]}' को ध्यान में रखें।"
        one_liner = f"**{ch_title} ({key})**: {ans_cand}"
        
        chapter_questions.append({
            "id": q_id,
            "chapter_id": f"geo_ch_{i+1}",
            "topic": f"{ch_label}: {ch_title}",
            "subheading": fp['sub'],
            "question": q_text,
            "options": options,
            "correct_index": correct_idx,
            "explanation": explanation,
            "mnemonic": mnemonic,
            "one_liner": one_liner
        })

    ch_id = f"geo_ch_{i+1}"
    parsed_chapters.append({
        "id": ch_id,
        "number": i + 1,
        "title": f"{ch_label}: {ch_title}",
        "raw_title": ch_title,
        "questions": chapter_questions
    })
    print(f"{ch_label}: {ch_title} -> {len(chapter_questions)} MCQs")

print(f"\n==========================================")
print(f"Total Chapters: {len(parsed_chapters)}")
print(f"Grand Total Rajasthan Geography MCQs Generated: {grand_total_mcqs}")
print(f"==========================================")

with open('/data/user/0/com.termux/files/home/.gemini/antigravity-cli/scratch/meri-taiyari-app/parsed_raj_geography_exhaustive.json', 'w', encoding='utf-8') as f:
    json.dump({
        "doc_url": "https://docs.google.com/document/d/1Qoh9heJ75cwdYFKWA2wfl8Q7LWaFJdobVEwxxug1BKc/edit?usp=drivesdk",
        "title": "राजस्थान भूगोल (Rajasthan Geography)",
        "total_chapters": len(parsed_chapters),
        "total_questions": grand_total_mcqs,
        "chapters": parsed_chapters
    }, f, ensure_ascii=False, indent=2)

print("Saved exhaustive data to parsed_raj_geography_exhaustive.json!")
