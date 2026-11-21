import urllib.request
import json
import time
import os
import re

import base64

print("==> 🤖 Starting Gemini AI Generation for all 23 Geography Chapters...")

API_KEY = base64.b64decode("QVEuQWI4Uk42SzZscU9RR3cyTHhyc3NkenphNkRRbTVybVNrcDBFTkZtX3B2OVFyZW03Unc=").decode()
MODEL_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-lite-latest:generateContent?key={API_KEY}"
CACHE_FILE = "/data/user/0/com.termux/files/home/.gemini/antigravity-cli/scratch/meri-taiyari-app/gemini_geo_cache.json"

def clean_base_name(text):
    t = re.sub(r'\(.*?\)', '', str(text))
    t = re.sub(r'\[.*?\]', '', t)
    return t.strip()

# Load cache
cache = {}
if os.path.exists(CACHE_FILE):
    try:
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            cache = json.load(f)
        print(f"==> Loaded existing cache with {len(cache)} chapters.")
    except Exception as e:
        cache = {}

with open("/data/user/0/com.termux/files/home/.gemini/antigravity-cli/scratch/meri-taiyari-app/raw_raj_geography.txt", "r", encoding="utf-8") as f:
    raw_geo_text = f.read().replace('\u200b', '').replace('\ufeff', '')

geo_matches = list(re.finditer(r'(?m)^[ \t]*अध्याय[- ](\d+)[ \t]*\n[ \t]*[❀*•\- ]*([^\n❀*•]+)', raw_geo_text))

for idx in range(len(geo_matches)):
    ch_num = int(geo_matches[idx].group(1))
    ch_name = geo_matches[idx].group(2).strip()
    ch_key = f"ch_{ch_num}"
    
    if ch_key in cache and len(cache[ch_key].get("questions", [])) >= 10:
        print(f"==> [Ch {ch_num:2d}] {ch_name[:30]} already in cache ({len(cache[ch_key]['questions'])} MCQs). Skipping.")
        continue
        
    start = geo_matches[idx].end()
    end = geo_matches[idx+1].start() if idx+1 < len(geo_matches) else len(raw_geo_text)
    ch_text = raw_geo_text[start:end].strip()
    
    # Send up to 7,000 characters to stay within prompt limits
    ch_text_chunk = ch_text[:7000]
    
    prompt = f"""आप RPSC और RSSB परीक्षा विशेषज्ञ हैं। नीचे दिए गए राजस्थान भूगोल (अध्याय-{ch_num}: {ch_name}) के नोट्स से 15 से 25 सबसे महत्वपूर्ण और प्रामाणिक वस्तुनिष्ठ प्रश्न (MCQ) तैयार करें।
प्रत्येक तथ्य से प्रश्न बनाएं (जैसे अक्षांश, देशांतर, लंबाई, चौड़ाई, चोटियां, नदियां, बांध, खनिज, आंकड़े आदि)।

सख्त नियम:
1. प्रश्न स्पष्ट, प्रामाणिक और मानक परीक्षा स्तर की हिंदी में होना चाहिए।
2. प्रत्येक प्रश्न के ठीक 4 सजातीय (Homogeneous) और अद्वितीय विकल्प होने चाहिए (यदि उत्तर प्रतिशत है तो चारों प्रतिशत, यदि जिला है तो चारों जिले, यदि वर्ष है तो चारों वर्ष, यदि दूरी है तो चारों दूरी)।
3. कोई भी बेतुका या असंगत विकल्प (जैसे प्रतिशत वाले सवाल में जिले का नाम) कभी नहीं होना चाहिए।
4. correct_index (0, 1, 2, 3) सही विकल्प का सूचकांक हो।
5. note में संक्षिप्त प्रामाणिक तथ्य लिखें।

नोट्स:
{ch_text_chunk}

आउटपुट केवल शुद्ध JSON array होना चाहिए:
[
  {{
    "question": "...",
    "options": ["A", "B", "C", "D"],
    "correct_index": 0,
    "note": "..."
  }}
]"""

    print(f"==> [Ch {ch_num:2d}] Calling Gemini AI for '{ch_name[:30]}'...")
    success = False
    for attempt in range(3):
        try:
            req = urllib.request.Request(
                MODEL_URL,
                data=json.dumps({
                    'contents': [{'parts': [{'text': prompt}]}],
                    'generationConfig': {'responseMimeType': 'application/json'}
                }).encode('utf-8'),
                headers={'Content-Type': 'application/json'}
            )
            with urllib.request.urlopen(req, timeout=30) as resp:
                res = json.loads(resp.read().decode('utf-8'))
                txt = res['candidates'][0]['content']['parts'][0]['text']
                parsed_qs = json.loads(txt)
                
                # Validate questions
                valid_qs = []
                for q in parsed_qs:
                    opts = q.get("options", [])
                    c_idx = q.get("correct_index", 0)
                    if len(opts) == 4 and len(set(opts)) == 4 and 0 <= c_idx < 4:
                        clean_opts = [clean_base_name(o) for o in opts]
                        if len(set(clean_opts)) == 4:
                            valid_qs.append(q)
                            
                cache[ch_key] = {
                    "number": ch_num,
                    "title": f"अध्याय-{ch_num}: {ch_name}",
                    "questions": valid_qs
                }
                
                with open(CACHE_FILE, "w", encoding="utf-8") as f:
                    json.dump(cache, f, ensure_ascii=False, indent=2)
                    
                print(f"    ✅ Success: {len(valid_qs)} valid AI questions saved for Ch {ch_num}!")
                success = True
                break
        except Exception as e:
            print(f"    ⚠️ Attempt {attempt+1} error: {e}. Retrying in 5 seconds...")
            time.sleep(5)
            
    # Sleep 4 seconds to respect API rate limits
    time.sleep(4)

print("==> 🏁 Gemini AI generation completed for all chapters in cache.")
