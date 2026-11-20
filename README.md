# मेरी तैयारी • MCQ Prep (Rajasthan & LSA Exam Prep)

📱 **राजस्थान प्रतियोगी परीक्षाओं (RPSC / RSSB) एवं पशुधन सहायक (LSA) हेतु विशेष रूप से तैयार ऑफलाइन-फर्स्ट एंड्रॉइड एप्लीकेशन।**

---

## 📥 सीधा APK डाउनलोड लिंक (Direct Download)
- **APK रिलीज़ डाउनलोड:** [MeriTaiyari_MCQ_Prep.apk](https://github.com/revantram/meri-taiyari-mcq-prep/releases/latest/download/MeriTaiyari_MCQ_Prep.apk)
- **रिलीज़ पेज:** [GitHub Releases](https://github.com/revantram/meri-taiyari-mcq-prep/releases)

---

## ✨ प्रमुख विशेषताएं (Key Features)

1. **एग्जामिनर-ग्रेड शुद्ध MCQ प्रश्न (Crisp Examiner-Style):**
   - RPSC / RSSB परीक्षा पैटर्न पर आधारित छोटे, प्रत्यक्ष 1-2 लाइन के प्रश्न।
   - 4 सजातीय (Homogeneous) सटीक विकल्प।
   - कोई लंबे अव्यवस्थित उद्धरण या बेमेल विकल्प नहीं।
2. **4-टैब नेविगेशन:**
   - 📅 **करंट अफेयर:** 2-स्टेप नेविगेशन (राष्ट्रीय/अंतरराष्ट्रीय एवं राजस्थान करंट अफेयर), तारीख-वार इंटरैक्टिव कैलेंडर एवं त्वरित री-सिंक।
   - 🏛️ **राजस्थान सामान्य ज्ञान (जीके):** राजस्थान भूगोल (23 अध्याय), कला एवं संस्कृति, तथा राजस्थान इतिहास।
   - 🐾 **सब्जेक्ट (LSA):** पशुधन सहायक डिप्लोमा के सभी 10 वेटनरी विषय अध्याय-वार।
   - ⚙️ **सेटिंग्स:** गूगल डॉक्स सिंक, गलत सवाल तिजोरी (Wrong Answer Vault), बुकमार्क एवं लाइट/डार्क थीम।
3. **Apple iOS 18 Liquid Glass डिज़ाइन:**
   - फ्रॉस्टेड ग्लास लुक, स्मूथ एनिमेशन और हाई-कंट्रास्ट डार्क/लाइट मोड।
4. **100% ऑफलाइन फर्स्ट:**
   - बिना इंटरनेट के सभी 980+ भूगोल प्रश्न, 1300+ करंट अफेयर्स प्रश्न और वेटनरी प्रश्न तुरंत लोड होते हैं।

---

## 🛠️ प्रोजेक्ट संरचना (Architecture)
- **UI:** Single Page Application (HTML5, Vanilla CSS3, JavaScript ES6)
- **Native Android Wrapper:** Java WebView (`MainActivity.java`, AndroidX, Material)
- **Local Storage:** SQLite / JSON-backed fast memory DB with LocalStorage caching
- **Build System:** Termux-ready pure CLI build pipeline (`build_apk.sh`) using `aapt2`, `d8`, `javac`, and `apksigner`.
