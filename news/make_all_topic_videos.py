"""Batch-generate 16 NeonMan-style Hindi Cricket News videos with real images & natural Female Host voice.

Outputs:
  - news/videos/topic_01.mp4 .. news/videos/topic_16.mp4
"""
from __future__ import annotations

import asyncio
import json
import re
import sys
from pathlib import Path
from typing import Any
from urllib.parse import quote

import httpx
from dotenv import load_dotenv
from playwright.async_api import async_playwright

ROOT_DIR = Path(__file__).resolve().parent.parent
SRC_DIR = ROOT_DIR / "src"
NEWS_DIR = Path(__file__).resolve().parent
BUILD_ROOT = NEWS_DIR / "build_batch"
VIDEOS_DIR = NEWS_DIR / "videos"

for d in (BUILD_ROOT, VIDEOS_DIR):
    d.mkdir(parents=True, exist_ok=True)

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))
if str(NEWS_DIR) not in sys.path:
    sys.path.insert(0, str(NEWS_DIR))

from cricket_live.commentary import get_mp3_duration_sec, synthesize_fish_audio  # noqa: E402
from make_single_story_video import (  # noqa: E402
    FPS,
    PAUSE_BETWEEN_BEATS_SEC,
    TRANSITION_SEC,
    _build_zoompan_expr,
    _normalize_to_1280x720,
    _probe_duration,
    _probe_image,
    _run,
)

load_dotenv(ROOT_DIR / ".env", override=True)
# Use verified Fish Audio Female Hindi Host voice (Girl hindi) for all news videos
import os
os.environ["FISH_REFERENCE_ID"] = os.getenv("FISH_HOST_FEMALE_REFERENCE_ID", "94fc4065e6e04b9baf1aea2107e91d66")

MOTIONS = ["zoom_in_top", "zoom_out_center", "pan_left_to_right", "zoom_in_center", "pan_right_to_left"]
XFADES = ["slideleft", "smoothleft", "slideright", "wipeleft", "smoothright"]

TOPICS: list[dict[str, Any]] = [
    {
        "id": "topic_01",
        "title": "Harbhajan Singh SLAMS India-Pakistan Players?! 😡 ICC & BCCI Step In? 🚨 Asia Cup Heated LAFDA 😱 Cricket News",
        "keywords": ["harbhajan", "india-pakistan", "behaviour", "icc"],
        "wiki": ["Harbhajan Singh", "India national cricket team", "Pakistan national cricket team", "Cricket pitch"],
        "beats": [
            ("excited", "नमस्ते दोस्तों! अभी-अभी इंडिया और पाकिस्तान के बीच एशिया कप राइजिंग स्टार्स मुकाबले से जुड़ी एक बहुत बड़ी खबर सामने आ रही है, जो मैं आपको विस्तार से बता रही हूँ।"),
            ("conversational", "दोहा में खेले गए इस हाई-वोल्टेज मुकाबले में दोनों टीमों के खिलाड़ियों के बीच मैदान पर काफी गरमा-गरमी देखने को मिली। मैच के दौरान कुछ खिलाड़ियों के बीच तीखी नोकझोंक भी हुई, जिसका वीडियो सोशल मीडिया पर तेज़ी से वायरल हो रहा है।"),
            ("conversational", "इसी घटना पर अब पूर्व भारतीय दिग्गज स्पिनर हरभजन सिंह ने कड़ा ऐतराज जताया है। हरभजन ने साफ शब्दों में कहा है कि इंडिया और पाकिस्तान के बीच मुकाबला हमेशा रोमांचक होता है, लेकिन खेल की भावना और मर्यादा सबसे ऊपर होनी चाहिए।"),
            ("conversational", "उन्होंने आईसीसी, बीसीसीआई और पीसीबी से भी इस मामले में तुरंत दखल देने की मांग की है ताकि भविष्य में ऐसी घटनाएं दोबारा न हों और युवा खिलाड़ी सिर्फ अपने खेल पर ध्यान दें।"),
            ("excited", "अब देखना दिलचस्प होगा कि आईसीसी और दोनों क्रिकेट बोर्ड इस पर क्या कदम उठाते हैं! आप इस पूरे विवाद पर क्या सोचते हैं, कमेंट में अपनी राय ज़रूर बताइए।"),
        ],
    },
    {
        "id": "topic_02",
        "title": "India vs Pakistan 3 TIMES in 2027 World Cup?! 🤯🔥 Schedule & Scenarios REVEALED 😱 IND vs PAK Cricket News",
        "keywords": ["three times", "2027 cricket world cup", "india vs pakistan"],
        "wiki": ["India national cricket team", "Pakistan national cricket team", "Cricket World Cup", "Cricket stadium"],
        "beats": [
            ("excited", "नमस्ते दोस्तों! क्रिकेट फैंस के लिए एक बेहद रोमांचक खबर सामने आ रही है — दो हज़ार सत्ताईस के वनडे वर्ल्ड कप में भारत और पाकिस्तान एक नहीं, बल्कि तीन बार आमने-सामने आ सकते हैं!"),
            ("conversational", "जी हाँ, मैं आपको बता रही हूँ कि टूर्नामेंट के फॉर्मेट और ग्रुप स्टेज के हिसाब से ऐसे समीकरण बन रहे हैं जहाँ दोनों चिर-प्रतिद्वंद्वियों की तीन महा-टक्कर देखने को मिल सकती है।"),
            ("conversational", "पहली भिड़ंत ग्रुप स्टेज में तय मानी जा रही है। इसके बाद अगर दोनों टीमें सुपर सिक्स चरण में पहुँचती हैं, तो वहाँ दूसरी बार आमना-सामना हो सकता है।"),
            ("conversational", "और अगर भारत और पाकिस्तान दोनों सेमीफ़ाइनल या फ़ाइनल में जगह बना लेते हैं, तो क्रिकेट इतिहास में पहली बार एक ही वर्ल्ड कप में तीन बार इंडिया बनाम पाकिस्तान मुकाबला देखने को मिलेगा!"),
            ("excited", "अगर ऐसा होता है, तो वर्ल्ड कप का रोमांच और व्यूअरशिप सारे रिकॉर्ड तोड़ देगी। आपको क्या लगता है, क्या यह तीन बार की भिड़ंत देखने को मिलेगी? कमेंट में ज़रूर बताइए!"),
        ],
    },
    {
        "id": "topic_03",
        "title": "Babar Azam SNUBS Pakistani Media, Talks to INDIAN Media! 😳🔥 ILT20 Debut HUGE Controversy 😱 PAK Cricket News",
        "keywords": ["babar azam", "pakistani journalists", "indian media", "ilt20"],
        "wiki": ["Babar Azam", "Dubai International Cricket Stadium", "Pakistan national cricket team", "Cricket press conference"],
        "beats": [
            ("excited", "नमस्ते दोस्तों! पाकिस्तान के स्टार बल्लेबाज़ बाबर आज़म इस वक्त अपने आईएलटी ट्वेंटी डेब्यू के बाद एक बड़ी चर्चा और विवाद में घिर गए हैं!"),
            ("conversational", "रिपोर्ट्स के मुताबिक, दुबई में मैच खत्म होने के बाद बाबर आज़म जब मैदान से बाहर निकले तो वहाँ कई पाकिस्तानी पत्रकार उनसे बात करने के लिए इंतज़ार कर रहे थे।"),
            ("conversational", "लेकिन चौंकाने वाली बात यह रही कि बाबर आज़म ने पाकिस्तानी पत्रकारों के सवालों को पूरी तरह नज़रअंदाज़ कर दिया और बिना रुके आगे बढ़ गए, जबकि दूसरी तरफ उन्होंने भारतीय मीडिया के साथ बड़े आराम से बातचीत की।"),
            ("conversational", "उनके इस कदम के बाद सोशल मीडिया और पाकिस्तानी क्रिकेट हलकों में काफी बहस छिड़ गई है। कई फैंस और पत्रकारों ने इस पर हैरानी जताई है।"),
            ("conversational", "मैं आपको बता रही हूँ कि बाबर का यह अंदाज़ इस समय हर तरफ सुर्खियों में बना हुआ है। इस पर आपकी क्या राय है, हमें कमेंट बॉक्स में ज़रूर लिखें।"),
        ],
    },
    {
        "id": "topic_04",
        "title": "\"Badla Lenge Pakistan Se\" — India A TROLLED BADLY! 😂💔 Loss vs SL A Leaves Fans SHOCKED 😱 Asia Cup 2026 News",
        "keywords": ["badla lenge", "memes", "india a", "sri lanka a"],
        "wiki": ["Sri Lanka national cricket team", "India national cricket team", "West End Park International Cricket Stadium", "Cricket celebration"],
        "beats": [
            ("conversational", "नमस्ते दोस्तों! एशिया कप राइजिंग स्टार्स दो हज़ार छब्बीस के पहले सेमीफ़ाइनल में श्रीलंका ए के हाथों इंडिया ए की हार के बाद सोशल मीडिया पर मीम्स और ट्रोलिंग की बाढ़ आ गई है।"),
            ("conversational", "दरअसल, मुकाबले से पहले कई भारतीय फैंस यह उम्मीद लगा रहे थे कि इंडिया ए सेमीफ़ाइनल जीतकर फ़ाइनल में पाकिस्तान से हिसाब बराबर करेगी।"),
            ("conversational", "लेकिन दोहा के मैदान पर श्रीलंका ए ने शानदार गेंदबाज़ी और बल्लेबाज़ी का प्रदर्शन करते हुए इंडिया ए को बड़ा झटका दिया और फ़ाइनल की उम्मीदें तोड़ दीं।"),
            ("conversational", "हार के तुरंत बाद इंटरनेट पर तुम तो बोल रहे थे फ़ाइनल में बदला लेंगे पाकिस्तान से जैसे मज़ेदार मीम्स वायरल होने लगे।"),
            ("conversational", "हालांकि हार-जीत खेल का हिस्सा है, और युवा भारतीय खिलाड़ियों के लिए यह टूर्नामेंट दबाव में खेलने और सीखने का एक बड़ा मंच ज़रूर साबित हुआ है।"),
        ],
    },
    {
        "id": "topic_05",
        "title": "India-Pakistan Bilateral Cricket RESUMING?! 🚨 Navjot Singh Sidhu BIG Statement 😳 Govt Decision? 🔥 IND vs PAK News",
        "keywords": ["bilateral", "navjot singh sidhu", "government decides"],
        "wiki": ["Navjot Singh Sidhu", "BCCI", "Pakistan Cricket Board", "India vs Pakistan cricket"],
        "beats": [
            ("excited", "नमस्ते दोस्तों! इंडिया और पाकिस्तान के बीच द्विपक्षीय क्रिकेट सीरीज़ को लेकर एक बार फिर बड़ी चर्चा शुरू हो गई है, जिसके बारे में मैं आपको बता रही हूँ।"),
            ("conversational", "दोनों देशों के बीच कई सालों से कोई द्विपक्षीय टेस्ट या वनडे सीरीज़ नहीं खेली गई है, और फैंस लगातार इस महा-मुकाबले की वापसी का इंतज़ार कर रहे हैं।"),
            ("conversational", "इसी बीच पूर्व भारतीय बल्लेबाज़ नवजोत सिंह सिद्धू ने एक बड़ा बयान देते हुए साफ कहा है कि दोनों देशों के बीच क्रिकेट रिश्ते फिर से शुरू करने का फैसला पूरी तरह सरकार के हाथ में है।"),
            ("conversational", "रिपोर्ट्स में भी यही कहा गया है कि जब तक भारत सरकार की तरफ से कोई हरी झंडी नहीं मिलती, तब तक बीसीसीआई इस पर कोई कदम नहीं उठा सकता।"),
            ("conversational", "यानी फिलहाल दोनों टीमें सिर्फ आईसीसी टूर्नामेंट और एशिया कप जैसे मल्टी-नेशन इवेंट्स में ही आमने-सामने खेलती नज़र आएंगी।"),
        ],
    },
    {
        "id": "topic_06",
        "title": "Pakistan Star PRAISES Vaibhav Sooryavanshi! 🔥👏 \"May Never Do That Again\" — Kiwi Legend SHOCKED 😱 Asia Cup News",
        "keywords": ["sooryavanshi", "chris cairns", "204", "star pakistan"],
        "wiki": ["Chris Cairns", "Cricket bat ball", "Young cricketer batting", "Cricket boundary six"],
        "beats": [
            ("excited", "नमस्ते दोस्तों! भारत के युवा बल्लेबाज़ वैभव सूर्यवंशी की तूफानी बल्लेबाज़ी ने सिर्फ भारत ही नहीं, बल्कि पाकिस्तान और न्यूज़ीलैंड के दिग्गजों को भी हैरान कर दिया है!"),
            ("conversational", "एशिया कप राइजिंग स्टार्स में वैभव सूर्यवंशी की विस्फोटक बल्लेबाज़ी देखकर एक स्टार पाकिस्तानी क्रिकेटर ने भी उनकी जमकर तारीफ की है।"),
            ("conversational", "वहीं न्यूज़ीलैंड के पूर्व दिग्गज ऑलराउंडर क्रिस केर्न्स ने उनके तिरेपन गेंदों में बनाए गए दो सौ चार रन के ऐतिहासिक दोहरे शतक पर बड़ा बयान दिया है।"),
            ("conversational", "क्रिस केर्न्स ने कहा कि ऐसी अविश्वसनीय पारी क्रिकेट में बार-बार देखने को नहीं मिलती और यह युवा खिलाड़ी आने वाले समय में बड़े रिकॉर्ड तोड़ सकता है।"),
            ("excited", "वाकई इतनी कम उम्र में वैभव सूर्यवंशी का यह निडर अंदाज़ भारतीय क्रिकेट के उज्ज्वल भविष्य की साफ झलक दिखाता है!"),
        ],
    },
    {
        "id": "topic_07",
        "title": "PAKISTAN in HUGE TROUBLE vs Bangladesh A! 🚨 233-Run Chase Thriller in Doha 😱 Asia Cup Semi-Final News",
        "keywords": ["pakistan vs bangladesh", "233", "semi-final", "doha"],
        "wiki": ["Bangladesh national cricket team", "Pakistan national cricket team", "West End Park International Cricket Stadium", "Cricket fielding"],
        "beats": [
            ("excited", "नमस्ते दोस्तों! दोहा में खेले गए एशिया कप राइजिंग स्टार्स दो हज़ार छब्बीस के दूसरे सेमीफ़ाइनल में पाकिस्तान ए और बांग्लादेश ए के बीच ज़बरदस्त रोमांच देखने को मिला!"),
            ("conversational", "दो सौ तैंतीस रन के लक्ष्य का पीछा करते हुए पाकिस्तान ए की शुरुआत काफी मुश्किल रही और शुरुआती विकेट गिरने से पूरी टीम भारी दबाव में आ गई।"),
            ("conversational", "बांग्लादेश ए के गेंदबाज़ों ने शानदार लाइन और लेंथ के साथ शुरुआती ओवरों में रन गति पर पूरी तरह लगाम लगाकर रखी।"),
            ("conversational", "हालांकि इसके बाद मिडल ऑर्डर में हसन नवाज़ और शाहज़ैब खान ने सूझबूझ भरी साझेदारी कर पारी को संभाला और टीम को मुकाबले में वापस ला खड़ा किया।"),
            ("conversational", "इस तरह के नॉकआउट मुकाबले सच में फैंस की धड़कनें बढ़ा देते हैं, जहाँ हर एक ओवर मैच का पासा पलट सकता है।"),
        ],
    },
    {
        "id": "topic_08",
        "title": "India A's BIG MISTAKE Exposed! 😡 Tilak Varma Captaincy Under Fire After Loss 🚨 Third Pacer Missing? 😳 Cricket News",
        "keywords": ["tilak varma", "third pacer", "rising stars asia cup"],
        "wiki": ["Tilak Varma", "India national cricket team", "Fast bowler cricket", "Cricket captain"],
        "beats": [
            ("conversational", "नमस्ते दोस्तों! एशिया कप राइजिंग स्टार्स के सेमीफ़ाइनल में श्रीलंका ए के खिलाफ इंडिया ए की हार के बाद टीम की रणनीति और कप्तानी पर बड़े सवाल उठ रहे हैं।"),
            ("conversational", "क्रिकेट जानकारों का साफ मानना है कि इस अहम नॉकआउट मुकाबले की प्लेइंग इलेवन में एक मज़बूत तीसरे तेज़ गेंदबाज़ की कमी टीम को बहुत भारी पड़ी।"),
            ("conversational", "इसके साथ ही कप्तान तिलक वर्मा की कप्तानी भी इस मैच में खास असर नहीं छोड़ पाई और अहम मौकों पर गेंदबाज़ी बदलावों को लेकर सवाल खड़े हुए।"),
            ("conversational", "तीन सौ से ज़्यादा रन बनाने के बावजूद गेंदबाज़ी आक्रमण में धार न होने के कारण विपक्षी बल्लेबाज़ों ने आसानी से लक्ष्य का पीछा कर लिया।"),
            ("conversational", "उम्मीद है कि टीम मैनेजमेंट और युवा खिलाड़ी इस हार से ज़रूरी सबक लेकर आने वाले टूर्नामेंट्स में और मज़बूत वापसी करेंगे।"),
        ],
    },
    {
        "id": "topic_09",
        "title": "Jasprit Bumrah REJECTS MI Vice-Captaincy?! 😱 Rohit Sharma RETURNS as MI CAPTAIN 🚨💙 IPL 2027 BIG News",
        "keywords": ["bumrah", "vice-captain", "mumbai indians", "ipl 2027"],
        "wiki": ["Jasprit Bumrah", "Rohit Sharma", "Wankhede Stadium", "Mumbai Indians"],
        "beats": [
            ("excited", "नमस्ते दोस्तों! आईपीएल दो हज़ार सत्ताईस से पहले मुंबई इंडियंस खेमे से एक बेहद चौंकाने वाली खबर सामने आ रही है, जो मैं आपको बता रही हूँ!"),
            ("conversational", "रिपोर्ट्स के मुताबिक, मुंबई इंडियंस फ्रेंचाइज़ी ने स्टार तेज़ गेंदबाज़ जसप्रीत बुमराह को रोहित शर्मा की कप्तानी में उप-कप्तान बनने का बड़ा ऑफर दिया था।"),
            ("conversational", "लेकिन सबसे हैरान करने वाली बात यह है कि जसप्रीत बुमराह ने इस जिम्मेदारी को लेने से साफ इनकार कर दिया है।"),
            ("conversational", "खबरों के अनुसार बुमराह अपने वर्कलोड और गेंदबाज़ी पर पूरा ध्यान केंद्रित करना चाहते हैं, इसी वजह से उन्होंने उप-कप्तानी ठुकराई।"),
            ("excited", "अब देखना बेहद दिलचस्प होगा कि रोहित शर्मा के साथ मुंबई इंडियंस उप-कप्तान की जिम्मेदारी किस खिलाड़ी को सौंपती है!"),
        ],
    },
    {
        "id": "topic_10",
        "title": "Rohit Sharma's FIRST STATEMENT After Returning As MI Captain! 💙🔥 Hardik Pandya TRADED to PBKS 😱 IPL 2027 News",
        "keywords": ["rohit sharma", "first statement", "hardik pandya", "punjab kings"],
        "wiki": ["Rohit Sharma", "Hardik Pandya", "Wankhede Stadium", "IPL trophy"],
        "beats": [
            ("excited", "नमस्ते दोस्तों! मुंबई इंडियंस के करोड़ों फैंस के लिए जश्न का माहौल है — पांच बार के चैंपियन कप्तान रोहित शर्मा आईपीएल दो हज़ार सत्ताईस में फिर से एमआई की कमान संभालने जा रहे हैं!"),
            ("conversational", "हार्दिक पांड्या के पंजाब किंग्स में ट्रेड होने के बाद मुंबई इंडियंस फ्रेंचाइज़ी ने एक बार फिर अपने सबसे सफल कप्तान हिटमैन पर भरोसा जताया है।"),
            ("conversational", "कप्तानी वापस मिलने के बाद रोहित शर्मा ने अपना पहला आधिकारिक बयान देते हुए कहा कि वे आने वाली चुनौतियों के लिए पूरी तरह तैयार हैं।"),
            ("conversational", "रोहित आखिरी बार दो हज़ार तेईस में मुंबई के कप्तान थे, और अब उनके लौटते ही टीम में एक नया जोश और आत्मविश्वास देखने को मिल रहा है।"),
            ("excited", "फैंस एक बार फिर रोहित शर्मा को नीली जर्सी में कप्तानी करते देखने के लिए बेहद उत्साहित हैं!"),
        ],
    },
    {
        "id": "topic_11",
        "title": "IPL 2027 vs PSL 12 CLASH! 🚨 PCB Announces March–May Dates 😳 BCCI BIG Scheduling Move? 🔥 Cricket News",
        "keywords": ["psl", "2027", "march", "bcci", "scheduling"],
        "wiki": ["BCCI", "Pakistan Cricket Board", "Cricket stadium night", "T20 cricket match"],
        "beats": [
            ("excited", "नमस्ते दोस्तों! दो हज़ार सत्ताईस के क्रिकेट कैलेंडर में एक बार फिर आईपीएल और पीएसएल के बीच सीधी टक्कर देखने को मिलने वाली है!"),
            ("conversational", "पाकिस्तान क्रिकेट बोर्ड ने आधिकारिक तौर पर पुष्टि की है कि पीएसएल सीज़न बारह अठारह मार्च से दो मई दो हज़ार सत्ताईस तक आयोजित किया जाएगा।"),
            ("conversational", "दूसरी तरफ बीसीसीआई भी प्लेऑफ के दौरान होने वाली भारी गर्मी और बारिश से बचने के लिए आईपीएल दो हज़ार सत्ताईस को मार्च के मध्य से मई के मध्य तक कराने की योजना बना रहा है।"),
            ("conversational", "ऐसे में दोनों बड़ी टी-ट्वेंटी लीग्स की तारीखें एक बार फिर आपस में टकराती हुई नज़र आ रही हैं।"),
            ("conversational", "अब देखने वाली बात होगी कि विदेशी स्टार खिलाड़ी किस लीग को प्राथमिकता देते हैं और ब्रॉडकास्टर्स के लिए यह क्लैश कितना बड़ा साबित होता है।"),
        ],
    },
    {
        "id": "topic_12",
        "title": "BCCI REJECTS 12-Team IPL Expansion?! 🚨 Pune & Vadodara Fans HEARTBROKEN 💔😱 IPL 2028 HUGE Update",
        "keywords": ["expansion", "12 teams", "pune", "vadodara"],
        "wiki": ["BCCI", "Narendra Modi Stadium", "Pune cricket stadium", "Indian Premier League"],
        "beats": [
            ("conversational", "नमस्ते दोस्तों! आईपीएल में दो नई टीमों के जुड़ने की अटकलों के बीच बीसीसीआई की तरफ से एक बहुत बड़ा स्पष्टीकरण सामने आया है।"),
            ("conversational", "पिछले कुछ दिनों से ऐसी खबरें तेज़ी से फैल रही थीं कि दो हज़ार अट्ठाईस तक पुणे और वडोदरा के रूप में आईपीएल को बारह टीमों का टूर्नामेंट बनाया जा सकता है।"),
            ("conversational", "लेकिन अब शीर्ष बीसीसीआई अधिकारियों ने इन सभी खबरों को खारिज करते हुए साफ कर दिया है कि फिलहाल टीमों की संख्या बढ़ाने की कोई योजना नहीं है।"),
            ("conversational", "बोर्ड का मानना है कि मौजूदा दस टीमों का फॉर्मेट और शेड्यूल अभी सबसे संतुलित है और इसमें तुरंत बदलाव करने की ज़रूरत नहीं है।"),
            ("conversational", "इस खबर से पुणे और वडोदरा के फैंस को थोड़ी निराशा ज़रूर हुई है, लेकिन आने वाले सीज़न में भी दस टीमों के बीच ही रोमांचक जंग जारी रहेगी।"),
        ],
    },
    {
        "id": "topic_13",
        "title": "Gautam Gambhir & Shubman Gill SLAMMED for Siraj Snub! 😡 \"Not Everyone Has Courage\" — BIG Verdict 😳 IND vs NZ News",
        "keywords": ["gautam gambhir", "shubman gill", "siraj", "snub"],
        "wiki": ["Mohammed Siraj", "Shubman Gill", "Gautam Gambhir", "Test cricket match"],
        "beats": [
            ("excited", "नमस्ते दोस्तों! न्यूज़ीलैंड के खिलाफ दूसरे टेस्ट मैच की प्लेइंग इलेवन से तेज़ गेंदबाज़ मोहम्मद सिराज को बाहर रखने पर भारतीय टीम मैनेजमेंट की जमकर आलोचना हो रही है!"),
            ("conversational", "हेड कोच गौतम गंभीर और कप्तान शुभमन गिल के इस बड़े फैसले पर कई पूर्व क्रिकेटरों और क्रिकेट विशेषज्ञों ने खुलकर हैरानी जताई है।"),
            ("conversational", "जानकारों का कहना है कि विदेशी पिचों पर सिराज जैसे आक्रामक और अनुभवी तेज़ गेंदबाज़ को बाहर बैठाना टीम के लिए नुकसानदायक साबित हो सकता है।"),
            ("conversational", "सोशल मीडिया पर भी फैंस इस फैसले को लेकर दो गुटों में बंटे हुए नज़र आ रहे हैं और लगातार अपनी नाराज़गी ज़ाहिर कर रहे हैं।"),
            ("conversational", "मैं आपको बता रही हूँ कि अब सभी की निगाहें मैच के नतीजे पर टिकी हैं, जो यह तय करेगा कि मैनेजमेंट का यह दांव सही था या गलत।"),
        ],
    },
    {
        "id": "topic_14",
        "title": "Shubman Gill's BOLD Demand BACKED by Ex-Chief Selector! 🔥 Lift Ban on Saliva? 😳🚨 IND vs NZ Test News",
        "keywords": ["saliva", "shubman gill", "msk prasad", "wellington"],
        "wiki": ["Shubman Gill", "Cricket ball shine", "Basin Reserve Wellington", "Fast bowling cricket"],
        "beats": [
            ("conversational", "नमस्ते दोस्तों! भारतीय टेस्ट कप्तान शुभमन गिल की एक बड़ी मांग को अब पूर्व मुख्य चयनकर्ता एमएसके प्रसाद का भी खुला समर्थन मिल गया है।"),
            ("conversational", "वेलिंग्टन टेस्ट के समापन के बाद शुभमन गिल ने गेंद को चमकाने के लिए सलाइवा यानी थूक के इस्तेमाल से बैन हटाने की वकालत की थी।"),
            ("conversational", "अब एमएसके प्रसाद ने भी इस बात का समर्थन करते हुए कहा है कि लाल गेंद से होने वाले टेस्ट क्रिकेट में गेंदबाज़ों को मदद मिलनी बहुत ज़रूरी है।"),
            ("conversational", "उनका मानना है कि सलाइवा के बिना गेंदबाज़ों को रिवर्स स्विंग हासिल करने में काफी मुश्किलों का सामना करना पड़ता है।"),
            ("conversational", "अब देखना होगा कि क्या आईसीसी इस बड़े सुझाव पर दोबारा विचार करता है और टेस्ट क्रिकेट में इस नियम की वापसी होती है या नहीं।"),
        ],
    },
    {
        "id": "topic_15",
        "title": "Kiwi Legend's STUNNING Verdict on Jasprit Bumrah! 😱🔥 \"India Become Favourites Because of Him\" 😳 IND vs NZ News",
        "keywords": ["bumrah", "favourites", "chris cairns", "kiwi"],
        "wiki": ["Jasprit Bumrah", "New Zealand national cricket team", "Cricket bowling action", "India cricket team"],
        "beats": [
            ("excited", "नमस्ते दोस्तों! भारतीय तेज़ गेंदबाज़ जसप्रीत बुमराह की घातक गेंदबाज़ी का लोहा एक बार फिर न्यूज़ीलैंड के पूर्व दिग्गज खिलाड़ी ने माना है!"),
            ("conversational", "न्यूज़ीलैंड के पूर्व ऑलराउंडर क्रिस केर्न्स ने साफ शब्दों में कहा है कि जसप्रीत बुमराह की मौजूदगी ही टीम इंडिया को किसी भी परिस्थिति में जीत का सबसे बड़ा दावेदार बनाती है।"),
            ("conversational", "उन्होंने कहा कि दोनों टीमों के बीच असली अंतर जसप्रीत बुमराह ही पैदा करते हैं, क्योंकि उनके पास हर चरण में विकेट निकालने की अद्भुत क्षमता है।"),
            ("conversational", "बुमराह का अनोखा एक्शन, तेज़ रफ़्तार और सटीक यॉर्कर उन्हें दुनिया के बाकी सभी गेंदबाज़ों से बिल्कुल अलग स्तर पर खड़ा करते हैं।"),
            ("excited", "भारतीय क्रिकेट फैंस के लिए विपक्षी देश के दिग्गज से यह तारीफ सुनना वाकई बहुत गर्व की बात है!"),
        ],
    },
    {
        "id": "topic_16",
        "title": "BCCI vs PCB Pay Scale & Contract SHAKE-UP! 🚨 Big Names DROPPED by PCB 😱 Sourav Ganguly & Yuvraj DC Plan 🔥",
        "keywords": ["ganguly", "yuvraj", "delhi capitals", "pcb", "contract"],
        "wiki": ["Sourav Ganguly", "Yuvraj Singh", "Delhi Capitals", "BCCI headquarters"],
        "beats": [
            ("conversational", "नमस्ते दोस्तों! आज दो बड़ी खबरें क्रिकेट प्रशासन और आईपीएल फ्रेंचाइज़ी रणनीति से जुड़ी हुई हैं, जो मैं आपको बता रही हूँ।"),
            ("conversational", "पहली खबर में पीसीबी ने अपने सेंट्रल कॉन्ट्रैक्ट लिस्ट में बड़ा फेरबदल करते हुए कई बड़े नामों को बाहर का रास्ता दिखा दिया है, जिसकी तुलना अब बीसीसीआई के मज़बूत ग्रेड ए, बी और सी सिस्टम से हो रही है।"),
            ("conversational", "जहाँ बीसीसीआई अपने शीर्ष खिलाड़ियों जैसे बुमराह, गिल और जडेजा को स्थिर अनुबंध देता है, वहीं पीसीबी में लगातार बदलाव देखने को मिल रहे हैं।"),
            ("conversational", "दूसरी तरफ आईपीएल में पूर्व भारतीय दिग्गज सौरव गांगुली और युवराज सिंह मिलकर दिल्ली कैपिटल्स की नई रणनीति और रिटेंशन प्लान को आकार देने में अहम भूमिका निभा रहे हैं।"),
            ("conversational", "देखने वाली बात होगी कि इन दोनों दिग्गजों के अनुभव से दिल्ली कैपिटल्स को आने वाले सीज़न में कितना बड़ा फायदा मिलता है!"),
        ],
    },
]


def _is_valid_image(path: Path) -> bool:
    if not path.exists() or path.stat().st_size < 12000:
        return False
    try:
        w, h, _ = _probe_image(path)
        return w >= 320 and h >= 180
    except Exception:
        return False


async def _fetch_topic_images(topic: dict[str, Any], news_items: list[dict[str, Any]], img_dir: Path) -> list[Path]:
    img_dir.mkdir(parents=True, exist_ok=True)
    existing = sorted([p for p in img_dir.glob("*") if _is_valid_image(p)])
    if len(existing) >= 4:
        return existing[:4]

    candidate_urls: list[str] = []
    kws = [k.lower() for k in topic["keywords"]]
    matching_articles = [
        it for it in news_items
        if any(k in f"{it.get('title','')} {it.get('summary','')}".lower() for k in kws)
    ]
    for it in matching_articles[:6]:
        if it.get("image_url"):
            candidate_urls.append(it["image_url"])

    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/131.0.0.0 Safari/537.36"}

    # Scrape article og:image / main photos via Playwright for matching articles
    article_urls = [it["source_url"] for it in matching_articles if it.get("source_url")][:3]
    if article_urls:
        try:
            async with async_playwright() as pw:
                b = await pw.chromium.launch(headless=True)
                page = await b.new_page(viewport={"width": 1280, "height": 800})
                for u in article_urls:
                    try:
                        await page.goto(u, wait_until="domcontentloaded", timeout=15000)
                        await asyncio.sleep(1.5)
                        imgs = await page.evaluate("""() => {
                            const out = [];
                            const og = document.querySelector('meta[property="og:image"]')?.content;
                            if (og) out.push(og);
                            for (const im of document.querySelectorAll('img')) {
                                const s = im.currentSrc || im.src || im.getAttribute('data-src') || '';
                                if (!s.startsWith('http')) continue;
                                if (/logo|icon|avatar|svg|gif|pixel|ads|doubleclick|badge/i.test(s)) continue;
                                const r = im.getBoundingClientRect();
                                if ((im.naturalWidth >= 400 || r.width >= 350) && (im.naturalHeight >= 220 || r.height >= 200)) out.push(s);
                            }
                            return out.slice(0, 5);
                        }""")
                        candidate_urls.extend(imgs)
                    except Exception:
                        pass
                await b.close()
        except Exception:
            pass

    # Wikimedia Commons real photos for topic subjects
    async with httpx.AsyncClient(headers={"User-Agent": "CricketLiveBot/1.0"}, follow_redirects=True, timeout=15) as c:
        for q in topic["wiki"]:
            try:
                wu = f"https://commons.wikimedia.org/w/api.php?action=query&generator=search&gsrnamespace=6&gsrsearch={quote(q)}&gsrlimit=3&prop=imageinfo&iiprop=url&iiurlwidth=1280&format=json"
                r = await c.get(wu)
                if r.status_code == 200 and r.text.strip().startswith("{"):
                    for v in (r.json().get("query", {}).get("pages") or {}).values():
                        ii = (v.get("imageinfo") or [{}])[0]
                        u2 = ii.get("thumburl") or ii.get("url")
                        if u2 and any(e in u2.lower() for e in (".jpg", ".jpeg", ".png")):
                            candidate_urls.append(u2)
            except Exception:
                pass

        saved = list(existing)
        seen: set[str] = set()
        idx = len(saved)
        for u in candidate_urls:
            if len(saved) >= 4:
                break
            if not u or u in seen or not u.startswith("http"):
                continue
            seen.add(u)
            try:
                resp = await c.get(u, headers=headers)
                if resp.status_code == 200 and len(resp.content) > 15000:
                    ext = ".png" if ".png" in u.lower().split("?")[0] else ".jpg"
                    p = img_dir / f"img_{idx:02d}{ext}"
                    p.write_bytes(resp.content)
                    if _is_valid_image(p):
                        saved.append(p)
                        idx += 1
                    else:
                        p.unlink(missing_ok=True)
            except Exception:
                pass

    # Fallback pool from verified real images in news/build_01 or news/build_02 if < 4
    if len(saved) < 4:
        fallback_pool = list((NEWS_DIR / "build_01" / "raw_imgs").glob("*.jpg")) + list((NEWS_DIR / "build_02" / "candidates").glob("*.jpg"))
        for fp in fallback_pool:
            if len(saved) >= 4:
                break
            if _is_valid_image(fp) and fp not in saved:
                saved.append(fp)

    return saved[:4]


async def _render_topic_video(topic: dict[str, Any], news_items: list[dict[str, Any]], force: bool = False) -> Path:
    tid = topic["id"]
    out_mp4 = VIDEOS_DIR / f"{tid}.mp4"
    if out_mp4.exists() and out_mp4.stat().st_size > 100_000 and not force:
        print(f"[{tid}] Already exists ({out_mp4.name}), skipping.")
        return out_mp4

    tdir = BUILD_ROOT / tid
    img_dir = tdir / "imgs"
    norm_dir = tdir / "norm"
    clip_dir = tdir / "clips"
    audio_dir = tdir / "audio"
    for d in (tdir, img_dir, norm_dir, clip_dir, audio_dir):
        d.mkdir(parents=True, exist_ok=True)

    print(f"\n=== [{tid}] {topic['title']} ===")
    imgs = await _fetch_topic_images(topic, news_items, img_dir)
    if len(imgs) < 3:
        raise RuntimeError(f"[{tid}] Not enough valid images ({len(imgs)})")
    print(f"  Images ready: {[p.name for p in imgs]}")

    # 1. Synthesize natural Female Host voice beats (speaker="host")
    beat_paths: list[Path] = []
    beat_durs: list[float] = []
    for idx, (mood, text) in enumerate(topic["beats"]):
        mp3_p = audio_dir / f"beat_{idx:02d}.mp3"
        audio_bytes = await synthesize_fish_audio(text, speaker="host", mood=mood)
        if not audio_bytes:
            raise RuntimeError(f"[{tid}] Empty TTS for beat {idx}")
        mp3_p.write_bytes(audio_bytes)
        dur = _probe_duration(mp3_p)
        if dur <= 0.3:
            dur = await get_mp3_duration_sec(audio_bytes)
        beat_paths.append(mp3_p)
        beat_durs.append(dur)
        print(f"  beat_{idx:02d}.mp3 -> {dur:.2f}s ({mood})")

    # Concat beats with clean 0.28s pauses + loudnorm
    voice_full = tdir / "voice_full.mp3"
    audio_cmd: list[str] = ["ffmpeg", "-y", "-v", "error"]
    for p in beat_paths:
        audio_cmd.extend(["-i", str(p)])
    n_beats = len(beat_paths)
    af_parts: list[str] = []
    concat_inputs: list[str] = []
    for idx in range(n_beats):
        af_parts.append(f"[{idx}:a]aresample=48000,aformat=sample_fmts=fltp:sample_rates=48000:channel_layouts=stereo[a{idx}]")
        concat_inputs.append(f"[a{idx}]")
        if idx < n_beats - 1:
            af_parts.append(f"anullsrc=r=48000:cl=stereo:d={PAUSE_BETWEEN_BEATS_SEC:.3f}[s{idx}]")
            concat_inputs.append(f"[s{idx}]")
    af_parts.append(f"{''.join(concat_inputs)}concat=n={2*n_beats-1}:v=0:a=1,loudnorm=I=-16:TP=-1.5:LRA=9[aout]")
    af_script = audio_dir / "audio_concat.ffscript"
    af_script.write_text(";\n".join(af_parts), encoding="utf-8")
    audio_cmd.extend(["-filter_complex_script", str(af_script), "-map", "[aout]", "-ac", "2", "-c:a", "libmp3lame", "-b:a", "192k", str(voice_full)])
    _run(audio_cmd, f"{tid} concat audio")
    total_audio_dur = _probe_duration(voice_full)
    if total_audio_dur < 60.0:
        # Pad slightly with gentle end pause or verify beats are >= 60s
        print(f"  WARNING: {tid} audio is {total_audio_dur:.2f}s (<60s), extending target video to 62s")
    target_dur = max(62.0, min(116.0, total_audio_dur + 0.35))
    n_shots = len(imgs)
    slot_dur = target_dur / n_shots
    clip_paths: list[Path] = []
    clip_durs: list[float] = []
    xfades: list[str] = []

    for idx, src_img in enumerate(imgs):
        norm_p = norm_dir / f"frame_{idx:02d}.jpg"
        _normalize_to_1280x720(src_img, norm_p)
        has_next = idx < n_shots - 1
        clip_target = slot_dur + (TRANSITION_SEC if has_next else 0.0)
        n_frames = max(30, round(clip_target * FPS))
        actual_sec = n_frames / FPS
        clip_p = clip_dir / f"clip_{idx:02d}.mp4"
        motion = MOTIONS[idx % len(MOTIONS)]
        xfades.append(XFADES[idx % len(XFADES)])
        vf = _build_zoompan_expr(motion, n_frames)
        _run(
            ["ffmpeg", "-y", "-v", "error", "-i", str(norm_p), "-vf", vf, "-frames:v", str(n_frames), "-r", str(FPS),
             "-c:v", "libx264", "-preset", "fast", "-crf", "18", "-pix_fmt", "yuv420p", str(clip_p)],
            f"{tid} clip_{idx:02d}",
        )
        clip_paths.append(clip_p)
        clip_durs.append(actual_sec)

    # 3. Chain with xfade transitions + mux audio
    filter_parts: list[str] = []
    prev_label = "[0:v]"
    running_dur = clip_durs[0]
    for idx in range(len(clip_paths) - 1):
        offset = max(0.2, running_dur - TRANSITION_SEC)
        out_label = f"[v{idx:02d}]" if idx < len(clip_paths) - 2 else "[vjoined]"
        filter_parts.append(f"{prev_label}[{idx+1}:v]xfade=transition={xfades[idx]}:duration={TRANSITION_SEC:.3f}:offset={offset:.3f}{out_label}")
        prev_label = out_label
        running_dur = offset + clip_durs[idx + 1]
    fade_out_start = max(1.0, running_dur - 0.45)
    filter_parts.append(f"[vjoined]fade=t=in:st=0:d=0.25,fade=t=out:st={fade_out_start:.3f}:d=0.45,format=yuv420p[vfinal]")

    ffscript = tdir / "xfade.ffscript"
    ffscript.write_text(";\n".join(filter_parts), encoding="utf-8")
    cmd: list[str] = ["ffmpeg", "-y", "-v", "error"]
    for cp in clip_paths:
        cmd.extend(["-i", str(cp)])
    cmd.extend(["-i", str(voice_full), "-filter_complex_script", str(ffscript), "-map", "[vfinal]", "-map", f"{len(clip_paths)}:a",
                "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-c:a", "aac", "-ac", "2", "-b:a", "192k", "-movflags", "+faststart", str(out_mp4)])
    _run(cmd, f"{tid} stitch final")
    final_dur = _probe_duration(out_mp4)
    print(f"  DONE -> {out_mp4.name} ({final_dur:.2f}s, {out_mp4.stat().st_size/(1024*1024):.2f} MB)")
    return out_mp4


async def main() -> None:
    force = "--force" in sys.argv
    news_items = []
    latest_p = NEWS_DIR / "latest_news.json"
    if latest_p.exists():
        news_items = json.loads(latest_p.read_text(encoding="utf-8")).get("items", [])

    results: list[tuple[str, str]] = []
    for topic in TOPICS:
        try:
            mp4 = await _render_topic_video(topic, news_items, force=force)
            results.append((topic["id"], str(mp4)))
        except Exception as exc:
            print(f"[{topic['id']}] ERROR: {exc}")
            results.append((topic["id"], f"ERROR: {exc}"))

    print("\n=== SUMMARY ===")
    for tid, res in results:
        print(f"  {tid}: {res}")


if __name__ == "__main__":
    asyncio.run(main())
