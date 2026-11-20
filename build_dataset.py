import re
import json
import random

with open('/data/user/0/com.termux/files/home/.gemini/antigravity-cli/scratch/meri-taiyari-app/raw_national_ca.txt', 'r', encoding='utf-8') as f:
    text = f.read().replace('\u200b', '').replace('\ufeff', '')

# Months mapping
month_map = {
    'जनवरी': ('01', 'January'),
    'फरवरी': ('02', 'February'),
    'मार्च': ('03', 'March'),
    'अप्रैल': ('04', 'April'),
    'मई': ('05', 'May'),
    'जून': ('06', 'June'),
    'जुलाई': ('07', 'July'),
    'अगस्त': ('08', 'August'),
    'सितंबर': ('09', 'September'),
    'अक्टूबर': ('10', 'October'),
    'नवंबर': ('11', 'November'),
    'दिसंबर': ('12', 'December')
}

date_pattern = r'(?m)^[ \t]*([0-9]{1,2})\s*[-–]?\s*(नवंबर|अक्टूबर|सितंबर|अगस्त|जुलाई|जून|मई|अप्रैल|मार्च|फरवरी|जनवरी)[ \t]*$'
matches = list(re.finditer(date_pattern, text))
print(f"Total date headers found: {len(matches)}")

parsed_by_date = {}

# Pool of realistic examiner distractors by domain
distractor_bank = [
    "भारतीय प्रौद्योगिकी संस्थान (IIT) मद्रास", "भारतीय विज्ञान संस्थान (IISc) बेंगलुरु", "IIT बॉम्बे", "IIT दिल्ली",
    "नासा (NASA)", "यूरोपीय अंतरिक्ष एजेंसी (ESA)", "जाक्सा (JAXA)", "रॉसकॉसमॉस (Roscosmos)",
    "फ्रांस", "जर्मनी", "जापान", "संयुक्त राज्य अमेरिका", "ऑस्ट्रेलिया", "सिंगापुर", "रूस", "चीन",
    "असम", "ओडिशा", "मध्य प्रदेश", "गुजरात", "महाराष्ट्र", "तमिलनाडु", "केरल", "उत्तर प्रदेश",
    "नई दिल्ली", "मुंबई", "अहमदाबाद", "कोलकाता", "चेन्नई", "हैदराबाद", "बेंगलुरु",
    "15 अगस्त 2026", "26 जनवरी 2026", "2 अक्टूबर 2026", "1 नवंबर 2026", "31 अक्टूबर 2026",
    "अनुराग ठाकुर", "धर्मेंद्र प्रधान", "अश्विनी वैष्णव", "मनसुख मंडाविया", "एस. जयशंकर",
    "कथन (I) सही है परंतु (II) असत्य है", "कथन (I) और (II) दोनों सत्य हैं", "कथन (I) और (II) दोनों असत्य हैं",
    "प्रथम स्थान", "द्वितीय स्थान", "तृतीय स्थान", "पंचम स्थान",
    "नीति आयोग (NITI Aayog)", "पर्यावरण एवं वन मंत्रालय", "गृह मंत्रालय", "विदेश मंत्रालय",
    "जी-20 शिखर सम्मेलन", "क्वाड शिखर सम्मेलन", "ब्रिक्स शिखर सम्मेलन", "आसियान सम्मेलन"
]

def generate_distractors(correct_ans, details, all_answers):
    distractors = []
    # 1. Search if details contain bullet points with candidate options
    # e.g. "दूसरा स्थान अमेरिका के एल कैपिटन"
    detail_cands = re.findall(r'[:—\-–]\s*([A-Za-z0-9\u0900-\u097F\s\(\)\'\"]{3,40})', details)
    for c in detail_cands:
        c_clean = c.strip(" *•-\t\n'\"").split('(')[0].strip()
        if len(c_clean) > 3 and c_clean != correct_ans and c_clean not in distractors:
            distractors.append(c_clean)
        if len(distractors) >= 3:
            break

    # 2. Pick from other answers from same date
    if len(distractors) < 3:
        for a in all_answers:
            a_clean = a.split('(')[0].strip()
            if len(a_clean) > 2 and a_clean != correct_ans and a_clean not in distractors:
                distractors.append(a_clean)
            if len(distractors) >= 3:
                break

    # 3. Fallback to realistic bank
    if len(distractors) < 3:
        for d in distractor_bank:
            if d != correct_ans and d not in distractors:
                distractors.append(d)
            if len(distractors) >= 3:
                break

    return distractors[:3]

def make_mnemonic(q_text, ans_text, topic):
    key = ans_text.split('(')[0].strip()
    return f"स्मृति सूत्र (Memory Trick): '{key[:15]}' को मुख्य संदर्भ से जोड़कर याद रखें — परीक्षा में सटीक पहचान के लिए।"

q_counter = 0

for i in range(len(matches)):
    day_num = int(matches[i].group(1))
    month_name = matches[i].group(2)
    month_code, _ = month_map[month_name]
    
    date_key = f"2026-{month_code}-{day_num:02d}"
    display_date = f"{day_num}-{month_name}-2026"
    
    start_pos = matches[i].end()
    end_pos = matches[i+1].start() if i+1 < len(matches) else len(text)
    section_text = text[start_pos:end_pos]
    
    # Split section into item chunks
    # Items usually start with e.g. "1. " or "2. " or "* प्रश्न:"
    items = re.split(r'(?m)^(?=[ \t]*(?:\d+[\.:]|[•*])[ \t]*(?:[^\n]*\n)?[ \t]*\*?[ \t]*प्रश्न:)', section_text)
    
    date_questions = []
    # Collect all answers first for distractor generation
    date_answers = []
    
    raw_blocks = []
    for item in items:
        item = item.strip()
        if 'प्रश्न:' not in item or 'उत्तर:' not in item:
            continue
        
        # Extract question
        q_match = re.search(r'प्रश्न:\s*(.+?)(?=\n[ \t]*\*?[ \t]*उत्तर:|\Z)', item, re.DOTALL)
        a_match = re.search(r'उत्तर:\s*(.+?)(?=\n[ \t]*\*?[ \t]*(?:विवरण|तकनीकी विशेषताएं|महत्वपूर्ण तथ्य|विशेषताएं):|\Z)', item, re.DOTALL)
        d_match = re.search(r'(?:विवरण|तकनीकी विशेषताएं|महत्वपूर्ण तथ्य|विशेषताएं):\s*(.+)', item, re.DOTALL)
        
        if q_match and a_match:
            q_str = q_match.group(1).strip()
            a_str = a_match.group(1).strip()
            # Clean answer if multiple lines
            a_lines = [l.strip(" \t*-•") for l in a_str.split('\n') if l.strip(" \t*-•")]
            a_clean = a_lines[0] if a_lines else a_str
            d_str = d_match.group(1).strip() if d_match else ""
            
            # Find topic title if present before प्रश्न:
            top_part = item[:q_match.start()].strip()
            top_lines = [l.strip(" \t*-•1234567890.") for l in top_part.split('\n') if l.strip()]
            topic_str = top_lines[0] if top_lines else f"करंट अफेयर्स बिंदु"
            
            date_answers.append(a_clean)
            raw_blocks.append({
                'topic': topic_str,
                'question': q_str,
                'answer': a_clean,
                'details': d_str
            })
            
    for b in raw_blocks:
        q_counter += 1
        q_id = f"CA_{date_key}_{q_counter}"
        correct_ans = b['answer']
        
        distractors = generate_distractors(correct_ans, b['details'], date_answers)
        
        # Create 4 options and shuffle deterministically
        options = [correct_ans] + distractors
        # Keep deterministic order based on question hash so it stays stable
        rng = random.Random(q_counter * 31)
        rng.shuffle(options)
        correct_idx = options.index(correct_ans)
        
        # Formulate rich examiner explanation
        explanation_lines = [
            f"✅ **सही उत्तर:** {correct_ans}",
            f"📌 **परीक्षा संदर्भ:** {b['topic']}"
        ]
        if b['details']:
            clean_det = "\n".join([f"• {l.strip(' *•\t')}" for l in b['details'].split('\n') if l.strip(' *•\t')])
            explanation_lines.append(f"📖 **विस्तृत एग्जामिनर व्याख्या (Facts from Notes):**\n{clean_det}")
        else:
            explanation_lines.append(f"📖 **व्याख्या:** {b['question']} का सही उत्तर '{correct_ans}' है।")

        # Memory mnemonic
        mnemonic = f"💡 **याद रखने की ट्रिक:** {b['topic'][:25]} ➔ मुख्य कुंजी '{correct_ans.split('(')[0].strip()}' को ध्यान में रखें।"
        
        # One-liner
        one_liner = f"**{b['topic']}**: {b['question'].replace('किस ', '').replace('कहाँ ', '')} ➔ **{correct_ans}**"
        
        date_questions.append({
            "id": q_id,
            "date": date_key,
            "display_date": display_date,
            "category": "national_international",
            "topic": b['topic'],
            "question": b['question'],
            "options": options,
            "correct_index": correct_idx,
            "explanation": "\n\n".join(explanation_lines),
            "mnemonic": mnemonic,
            "one_liner": one_liner
        })
        
    if date_questions:
        if date_key not in parsed_by_date:
            parsed_by_date[date_key] = {
                "date": date_key,
                "display_date": display_date,
                "month": month_name,
                "questions": []
            }
        parsed_by_date[date_key]["questions"].extend(date_questions)

print(f"Total dates parsed with questions: {len(parsed_by_date)}")
total_q = sum(len(d["questions"]) for d in parsed_by_date.values())
print(f"Total MCQs generated: {total_q}")

# Sort dates chronologically
sorted_dates = sorted(parsed_by_date.keys())
print("Sample parsed dates:", sorted_dates[:10], "...", sorted_dates[-5:])

with open('/data/user/0/com.termux/files/home/.gemini/antigravity-cli/scratch/meri-taiyari-app/parsed_national_ca.json', 'w', encoding='utf-8') as f:
    json.dump({
        "metadata": {
            "title": "राष्ट्रीय एवं अंतरराष्ट्रीय करंट अफेयर",
            "source_doc": "https://docs.google.com/document/d/1EEDq2GZn4d9UucwlEifT6KF37IN1bK3a4A_Ch8a5JOg/edit?usp=drivesdk",
            "last_synced": "2026-11-20T17:50:00+05:30",
            "total_questions": total_q,
            "total_dates": len(parsed_by_date)
        },
        "dates": parsed_by_date
    }, f, ensure_ascii=False, indent=2)

print("Saved to parsed_national_ca.json successfully!")
