import re
import json
import random

with open('/data/user/0/com.termux/files/home/.gemini/antigravity-cli/scratch/meri-taiyari-app/raw_raj_geography.txt', 'r', encoding='utf-8') as f:
    text = f.read().replace('\u200b', '').replace('\ufeff', '')

# Match all chapters
chapter_matches = list(re.finditer(r'(?m)^[ \t]*(अध्याय\s*[-–]?\s*\d+)[ \t]*\n[ \t]*[❀\*\-–•\s]*(.+?)[❀\*\-–•\s]*$', text))
print(f"Total chapters matched: {len(chapter_matches)}")

distractor_bank_raj = [
    "जैसलमेर", "बाड़मेर", "बीकानेर", "जोधपुर", "जयपुर", "उदयपुर", "कोटा", "अजमेर", "भीलवाड़ा", "चित्तौड़गढ़", "डूंगरपुर", "बांसवाड़ा", "झालावाड़", "चूरू", "सीकर", "नागौर",
    "अरावली पर्वतमाला", "थार का मरुस्थल", "पूर्वी मैदान", "हाड़ौती का पठार", "लूणी बेसिन", "शेखावाटी बेसिन", "चंबल बेसिन", "बनास बेसिन",
    "चंबल नदी", "बनास नदी", "लूणी नदी", "माही नदी", "साबरमती नदी", "कालीसिंध नदी", "बाणगंगा नदी",
    "काली मृदा (वर्टिसोल)", "लाल-पीली मृदा", "जलोढ़ मृदा (इन्सेप्टिसोल)", "रेतीली शुष्क मृदा (एंटीसोल)",
    "उपोष्ण कटिबंधीय", "शुष्क जलवायु", "अर्ध-शुष्क जलवायु", "अति-आद्र जलवायु", "आद्र जलवायु",
    "5920 कि.मी.", "1070 कि.मी.", "4850 कि.मी.", "826 कि.मी.", "869 कि.मी.", "3,42,239 वर्ग कि.मी.",
    "कथन (I) और (II) दोनों सत्य हैं", "कथन (I) सत्य है तथा (II) असत्य है", "कथन (I) असत्य है तथा (II) सत्य है"
]

def make_distractors(correct_ans, sibling_candidates):
    distractors = []
    clean_c = correct_ans.split('(')[0].split('–')[0].split('-')[0].strip()

    # 1. Pick from siblings
    for s in sibling_candidates:
        clean_s = s.split('(')[0].split('–')[0].split('-')[0].strip()
        if len(clean_s) > 2 and clean_s != clean_c and clean_s not in distractors:
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
total_q_count = 0

for i in range(len(chapter_matches)):
    ch_num_label = chapter_matches[i].group(1).strip()
    ch_title = chapter_matches[i].group(2).strip()
    
    start_pos = chapter_matches[i].end()
    end_pos = chapter_matches[i+1].start() if i+1 < len(chapter_matches) else len(text)
    ch_text = text[start_pos:end_pos].strip()
    
    # Split by section headings or bullet points
    lines = [l.strip() for l in ch_text.splitlines() if l.strip()]
    
    # Extract candidate factual points
    fact_points = []
    current_subheading = ch_title
    
    for l in lines:
        if l.startswith('❀') or (len(l) < 35 and not l.startswith('*') and not ':' in l and not '।' in l):
            current_subheading = l.strip('❀ *•\t-–')
            continue
        
        # Line with key: value or bullet
        clean_l = l.strip(' *•\t')
        if ':' in clean_l or '–' in clean_l or '-' in clean_l:
            parts = re.split(r'[:–\-]\s*', clean_l, maxsplit=1)
            if len(parts) == 2 and len(parts[0]) > 2 and len(parts[1]) > 2:
                fact_points.append({
                    'subheading': current_subheading,
                    'key': parts[0].strip(),
                    'val': parts[1].strip(),
                    'full': clean_l
                })
        elif len(clean_l) > 25 and ('है।' in clean_l or 'हैं।' in clean_l or 'कहा जाता है' in clean_l or 'स्थित है' in clean_l):
            fact_points.append({
                'subheading': current_subheading,
                'key': current_subheading,
                'val': clean_l,
                'full': clean_l
            })

    # Generate questions from fact points
    chapter_questions = []
    sibling_vals = [fp['val'] for fp in fact_points]
    
    # Take high-yield points (between 10 to 25 MCQs per chapter)
    selected_facts = fact_points[:min(25, len(fact_points))]
    if len(fact_points) > 25:
        # Step sample across the chapter so the whole chapter is covered
        step = len(fact_points) / 25.0
        selected_facts = [fact_points[int(j * step)] for j in range(25)]

    for idx, fp in enumerate(selected_facts):
        total_q_count += 1
        q_id = f"GEO_CH{i+1}_{total_q_count}"
        
        # Determine question framing
        key = fp['key']
        val = fp['val']
        
        # Clean answer candidate
        ans_cand = val.split('(')[0].split('।')[0].strip()
        if len(ans_cand) > 50:
            ans_cand = ans_cand[:45] + '...'
            
        # Formulate examiner question
        if 'विस्तार' in key or 'लंबाई' in key or 'चौड़ाई' in key or 'क्षेत्रफल' in key or 'सीमा' in key:
            q_text = f"राजस्थान भूगोल के संदर्भ में, '{key}' के संबंध में सही तथ्य कौन-सा है?"
        elif 'प्रकार' in key or 'जलवायु' in key or 'मृदा' in key:
            q_text = f"राजस्थान में {fp['subheading']} के अंतर्गत '{key}' का सही विवरण क्या है?"
        elif 'जिले' in key or 'मुख्यालय' in key or 'स्थान' in key:
            q_text = f"राजस्थान के संदर्भ में, '{key}' से संबंधित सही जिला / क्षेत्र कौन-सा है?"
        else:
            q_text = f"राजस्थान सामान्य ज्ञान (भूगोल) के संदर्भ में, '{key}' के विषय में सत्य कथन पहचानिए:"

        distractors = make_distractors(ans_cand, sibling_vals)
        options = [ans_cand] + distractors
        
        # Shuffle deterministically
        rng = random.Random(total_q_count * 43)
        rng.shuffle(options)
        correct_idx = options.index(ans_cand)
        
        explanation = (
            f"✅ **सही उत्तर:** {ans_cand}\n\n"
            f"📌 **अध्याय संदर्भ:** {ch_num_label} - {ch_title} ({fp['subheading']})\n\n"
            f"📖 **विस्तृत एग्जामिनर व्याख्या (Facts from Notes):**\n"
            f"• {fp['full']}\n"
            f"• यह तथ्य राजस्थान कर्मचारी चयन बोर्ड (RSSB) एवं RPSC परीक्षाओं के लिए अत्यंत महत्वपूर्ण है।"
        )
        
        mnemonic = f"💡 **याद रखने की ट्रिक:** {key[:20]} ➔ मुख्य कुंजी '{ans_cand[:20]}' से जोड़कर याद रखें।"
        one_liner = f"**{ch_title} ({key})**: {ans_cand}"
        
        chapter_questions.append({
            "id": q_id,
            "chapter_id": f"geo_ch_{i+1}",
            "topic": f"{ch_num_label}: {ch_title}",
            "subheading": fp['subheading'],
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
        "title": f"{ch_num_label}: {ch_title}",
        "raw_title": ch_title,
        "questions": chapter_questions
    })
    print(f"Chapter {i+1}: {ch_title} -> {len(chapter_questions)} MCQs generated")

print(f"\nTotal Rajasthan Geography chapters: {len(parsed_chapters)}")
print(f"Total Rajasthan Geography MCQs generated: {total_q_count}")

with open('/data/user/0/com.termux/files/home/.gemini/antigravity-cli/scratch/meri-taiyari-app/parsed_raj_geography.json', 'w', encoding='utf-8') as f:
    json.dump({
        "doc_url": "https://docs.google.com/document/d/1Qoh9heJ75cwdYFKWA2wfl8Q7LWaFJdobVEwxxug1BKc/edit?usp=drivesdk",
        "title": "राजस्थान भूगोल (Rajasthan Geography)",
        "total_chapters": len(parsed_chapters),
        "total_questions": total_q_count,
        "chapters": parsed_chapters
    }, f, ensure_ascii=False, indent=2)

print("Saved to parsed_raj_geography.json successfully!")
