import json
import re

print("==> 🚀 Assembling Complete Database with Full Rajasthan History (v3.8.0)...")

def clean_base_name(text):
    t = re.sub(r'\(.*?\)', '', str(text))
    t = re.sub(r'\[.*?\]', '', t)
    return t.strip()

# 1. Load Exhaustive Geography (23 chapters, 872 Qs)
with open("gemini_exhaustive_geo_cache.json", "r", encoding="utf-8") as f:
    geo_cache = json.load(f)

geo_chapters = []
total_geo_q = 0
for ch_num in range(1, 24):
    ch_key = f"ch_{ch_num}"
    if ch_key not in geo_cache:
        continue
    c_data = geo_cache[ch_key]
    ch_id = f"geo_ch_{ch_num}"
    ch_title = c_data["title"]
    ch_questions = []
    for q in c_data["questions"]:
        total_geo_q += 1
        opts = q["options"]
        c_idx = q["correct_index"]
        q_text = q["question"]
        note_text = q.get("note", "")
        if not note_text.startswith("नोट:"):
            note_text = f"नोट: {note_text}"
        ch_questions.append({
            "id": f"GEO_Q_{total_geo_q}",
            "chapter_id": ch_id,
            "topic": ch_title,
            "question": q_text,
            "options": opts,
            "correct_index": c_idx,
            "note": note_text,
            "explanation": note_text,
            "one_liner": f"{q_text} ➔ **{opts[c_idx]}**"
        })
    geo_chapters.append({
        "id": ch_id,
        "number": ch_num,
        "title": ch_title,
        "questions": ch_questions
    })

# 2. Load Exhaustive History (23 chapters)
with open("gemini_exhaustive_history_cache.json", "r", encoding="utf-8") as f:
    hist_cache = json.load(f)

hist_chapters = []
total_hist_q = 0
for ch_num in range(1, 24):
    ch_key = f"ch_{ch_num}"
    if ch_key not in hist_cache:
        continue
    c_data = hist_cache[ch_key]
    ch_id = f"hist_ch_{ch_num}"
    ch_title = c_data["title"]
    ch_questions = []
    for q in c_data["questions"]:
        total_hist_q += 1
        opts = q["options"]
        c_idx = q["correct_index"]
        q_text = q["question"]
        note_text = q.get("note", "")
        if not note_text.startswith("नोट:"):
            note_text = f"नोट: {note_text}"
        ch_questions.append({
            "id": f"HIST_Q_{total_hist_q}",
            "chapter_id": ch_id,
            "topic": ch_title,
            "question": q_text,
            "options": opts,
            "correct_index": c_idx,
            "note": note_text,
            "explanation": note_text,
            "one_liner": f"{q_text} ➔ **{opts[c_idx]}**"
        })
    hist_chapters.append({
        "id": ch_id,
        "number": ch_num,
        "title": ch_title,
        "questions": ch_questions
    })

from generate_perfect_database import nca_dates_dict, raj_ca_dates_dict, art_culture_chapters

initial_data_obj = {
    "config": {
        "app_name": "मेरी तैयारी • MCQ Prep",
        "version": "3.8.0",
        "build_date": "2026-11-21",
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
        "last_synced": "2026-11-21T12:00:00Z",
        "dates": nca_dates_dict
    },
    "rajasthan_ca": {
        "id": "rajasthan_ca",
        "title": "राजस्थान समसामयिकी (Rajasthan Current Affairs)",
        "linked": True,
        "doc_url": "https://docs.google.com/document/d/1yN1sXUvsm_3q5a49yvB8W7P3wI4tN9aP8e6k0l9m1sQ/edit?usp=drivesdk",
        "last_synced": "2026-11-21T12:00:00Z",
        "dates": raj_ca_dates_dict
    },
    "rajasthan_gk": {
        "geography": {
            "id": "geography",
            "title": "राजस्थान का भूगोल (Rajasthan Geography)",
            "linked": True,
            "doc_url": "https://docs.google.com/document/d/18rG37nZ7G2F61Z6n2H8rK8x1wQ8b2m6e0k3p4q5s7tU/edit?usp=drivesdk",
            "last_synced": "2026-11-21T12:00:00Z",
            "total_chapters": len(geo_chapters),
            "total_questions": total_geo_q,
            "chapters": geo_chapters
        },
        "history": {
            "id": "history",
            "title": "राजस्थान का इतिहास (Rajasthan History)",
            "linked": True,
            "doc_url": "https://docs.google.com/document/d/13H358iCALp8DmhzHbOXGB3cMcl382TK-dKJzSzN1TRk/edit?usp=drivesdk",
            "last_synced": "2026-11-21T12:00:00Z",
            "total_chapters": len(hist_chapters),
            "total_questions": total_hist_q,
            "chapters": hist_chapters
        },
        "art_culture": {
            "id": "art_culture",
            "title": "राजस्थान कला एवं संस्कृति (Art & Culture)",
            "linked": True,
            "doc_url": "https://docs.google.com/document/d/1artculture_demo_doc/edit",
            "last_synced": "2026-11-21T12:00:00Z",
            "total_chapters": len(art_culture_chapters),
            "total_questions": sum(len(c["questions"]) for c in art_culture_chapters),
            "chapters": art_culture_chapters
        }
    },
    "lsa_subjects": {
        "anatomy": {
            "id": "anatomy", "title": "1. वेटरनरी एनाटॉमी (Veterinary Anatomy)", "linked": True,
            "chapters": [{
                "id": "anat_ch_1", "number": 1, "title": "अध्याय-1: अस्थि विज्ञान (Osteology) एवं कंकाल तंत्र",
                "questions": [
                    {
                        "id": "LSA_ANAT_1", "question": "गाय / बैल के शरीर में पसलियों (Ribs) की कुल कितनी जोड़ियां पाई जाती हैं?",
                        "options": ["13 जोड़ी (Pairs)", "18 जोड़ी", "14 जोड़ी", "12 जोड़ी"], "correct_index": 0,
                        "note": "गाय एवं बैल में कुल 13 जोड़ी पसलियां होती हैं (8 सत्य / स्टर्नल व 5 असत्य / एस्टर्नल)। घोड़े में 18 जोड़ी तथा सूअर में 14-15 जोड़ी पसलियां पाई जाती हैं।",
                        "explanation": "गाय/बैल में 13 जोड़ी पसलियां होती हैं।",
                        "one_liner": "गाय/बैल में पसलियों की कितनी जोड़ियां होती हैं? ➔ **13 जोड़ी**"
                    },
                    {
                        "id": "LSA_ANAT_2", "question": "पशु शरीर की सबसे लंबी और मजबूत अस्थि (Longest & Strongest Bone) कौन-सी होती है?",
                        "options": ["फीमर (जांघ की अस्थि)", "ह्यूमरस", "टिबिया", "रेडियस"], "correct_index": 0,
                        "note": "फीमर (Femur) पशु शरीर की सबसे लंबी एवं सबसे भारी अस्थि है जो पश्च पाद (Hind limb) की जांघ में पाई जाती है।",
                        "explanation": "फीमर पशु शरीर की सबसे लंबी अस्थि है।",
                        "one_liner": "शरीर की सबसे लंबी अस्थि कौन-सी है? ➔ **फीमर (Femur)**"
                    }
                ]
            }]
        }
    }
}

output_js = f"window.INITIAL_DATA = {json.dumps(initial_data_obj, ensure_ascii=False)};"

with open("initial_data.js", "w", encoding="utf-8") as f:
    f.write(output_js)

with open("assets/initial_data.js", "w", encoding="utf-8") as f:
    f.write(output_js)

print(f"==> ✅ Complete Database assembled: Geography ({total_geo_q} Qs), History ({total_hist_q} Qs).")
