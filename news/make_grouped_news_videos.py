"""Generate NeonMan-style grouped cricket news videos:
- 3 short news in 1 video, 2 medium news in 1 video, or 1 big standalone news.
- Duration: >= 60s and < 120s per video.
- Voice: Female Hindi Host (Fish Audio Girl hindi 4d7609058bd34213b1378b29efbde1f1), stereo 48kHz AAC.
- Visuals: Real topic-specific images with Ken Burns zoom/pan + xfade transitions.
"""
from __future__ import annotations

import asyncio
import hashlib
import html as html_lib
import json
import os
import re
import sys
from pathlib import Path
from typing import Any
from urllib.parse import quote

import httpx
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parent.parent
SRC_DIR = ROOT_DIR / "src"
NEWS_DIR = Path(__file__).resolve().parent
BUILD_ROOT = NEWS_DIR / "build_episodes"
VIDEOS_DIR = NEWS_DIR / "videos"

for d in (BUILD_ROOT, VIDEOS_DIR):
    d.mkdir(parents=True, exist_ok=True)

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))
if str(NEWS_DIR) not in sys.path:
    sys.path.insert(0, str(NEWS_DIR))

load_dotenv(ROOT_DIR / ".env", override=True)
os.environ["FISH_REFERENCE_ID"] = os.getenv("FISH_HOST_FEMALE_REFERENCE_ID", "94fc4065e6e04b9baf1aea2107e91d66")

from cricket_live.commentary import get_mp3_duration_sec, synthesize_fish_audio  # noqa: E402
from make_all_topic_videos import MOTIONS, XFADES, _fetch_topic_images  # noqa: E402
from make_single_story_video import (  # noqa: E402
    FPS,
    PAUSE_BETWEEN_BEATS_SEC,
    TRANSITION_SEC,
    _build_zoompan_expr,
    _normalize_to_1280x720,
    _probe_duration,
    _run,
)

EPISODES: list[dict[str, Any]] = [
    {
        "id": "ep_01_ind_pak_clash",
        "title": "Harbhajan SLAMS India-Pakistan Players! 😡 IND vs PAK 3 TIMES in 2027 World Cup?! 🤯 Cricket News",
        "keywords": ["harbhajan", "three times", "2027 cricket world cup", "india-pakistan"],
        "wiki": ["Harbhajan Singh", "India national cricket team", "Pakistan national cricket team", "Cricket World Cup", "Cricket stadium"],
        "beats": [
            ("excited", "[excited] नमस्ते दोस्तों! आज के क्रिकेट बुलेटिन में दो बहुत बड़ी और चौंकाने वाली खबरें भारत और पाकिस्तान से जुड़ी हुई हैं!", "Namaste dosto! Aaj ke cricket bulletin mein do badi aur chaunkane wali khabrein India aur Pakistan se judi hui hain!"),
            ("excited", "[surprised] पहली बड़ी खबर! एशिया कप राइज़िंग स्टार्स में भारत और पाकिस्तान के खिलाड़ियों के बीच मैदान पर ज़बरदस्त गरमा-गरमी हो गई! दोनों टीमों के कुछ खिलाड़ियों के बीच तीखी नोकझोंक का वीडियो सोशल मीडिया पर तेज़ी से वायरल हो रहा है!", "Pehli badi khabar! Asia Cup Rising Stars mein India aur Pakistan ke players ke beech maidan par zabardast garma-garmi ho gayi! Video social media par tezi se viral ho raha hai!"),
            ("conversational", "[cheerful] इसी घटना पर पूर्व भारतीय दिग्गज हरभजन सिंह ने कड़ा ऐतराज़ जताया है। उन्होंने साफ कहा है कि मुकाबला चाहे जितना बड़ा हो... खेल की भावना और मर्यादा सबसे ऊपर रहनी चाहिए! उन्होंने आई सी सी, बी सी सी आई और पी सी बी से भी तुरंत दखल देने की मांग की है।", "Is par Harbhajan Singh ne kada aitraaz jataya hai! Unhone kaha ki khel ki bhavna aur maryada sabse upar honi chahiye, aur ICC, BCCI, PCB se turant dakhal dene ki maang ki hai."),
            ("excited", "[excited] और दूसरी धमाकेदार खबर सुनिए! दो हज़ार सत्ताईस के वनडे वर्ल्ड कप में भारत और पाकिस्तान एक नहीं... बल्कि तीन बार आमने-सामने आ सकते हैं!", "Aur doosri dhamakedaar khabar! 2027 ODI World Cup mein India aur Pakistan ek nahi, balki 3 baar aamne-saamne aa sakte hain!"),
            ("conversational", "[cheerful] ग्रुप स्टेज, सुपर सिक्स और नॉकआउट के समीकरण ऐसे बन रहे हैं, जहाँ फैंस को एक ही वर्ल्ड कप में तीन बार महा-मुकाबला देखने को मिल सकता है! आपका इस पर क्या कहना है? कमेंट में ज़रूर बताइए!", "Group stage, Super Six aur Knockout ke equations aise ban rahe hain jahan 3 baar IND vs PAK maha-muqabla dekhne ko mil sakta hai! Comment mein zaroor batayein!"),
        ],
    },
    {
        "id": "ep_02_pak_asiacup_3in1",
        "title": "Babar Azam SNUBS Pak Media 😳 India A TROLLED BADLY 😂 Pak vs Ban 233 Thriller 🚨 Asia Cup News",
        "keywords": ["babar azam", "badla lenge", "pakistan vs bangladesh", "ilt20", "233"],
        "wiki": ["Babar Azam", "Sri Lanka national cricket team", "Bangladesh national cricket team", "Pakistan national cricket team", "Dubai International Cricket Stadium"],
        "beats": [
            ("excited", "[excited] नमस्ते दोस्तों! इस वीडियो में तीन ज़बरदस्त खबरें पाकिस्तान और एशिया कप राइज़िंग स्टार्स से जुड़ी हैं!", "Namaste dosto! Is video mein 3 zabardast khabrein Pakistan aur Asia Cup Rising Stars se judi hain!"),
            ("excited", "[surprised] पहली खबर! पाकिस्तान के स्टार बल्लेबाज़ बाबर आज़म ने दुबई में अपने डेब्यू मैच के बाद पाकिस्तानी पत्रकारों के सवालों को पूरी तरह नज़रअंदाज़ कर दिया! लेकिन भारतीय मीडिया से बड़े आराम से बातचीत की, जिस पर सोशल मीडिया में भारी बवाल मच गया है!", "Pehli khabar! Babar Azam ne Dubai mein apne debut match ke baad Pakistani media ko ignore kar diya, lekin Indian media se aaram se baat ki — jis par social media mein bhari bawaal mach gaya hai!"),
            ("conversational", "[cheerful] दूसरी खबर! एशिया कप राइज़िंग स्टार्स के सेमीफ़ाइनल में श्रीलंका ए के हाथों इंडिया ए की हार के बाद... इंटरनेट पर मज़ेदार मीम्स की बाढ़ आ गई है! फैंस फ़ाइनल में पाकिस्तान से भिड़ंत की उम्मीद कर रहे थे, लेकिन श्रीलंका ए ने बाज़ी मार ली!", "Doosri khabar! SL A ke haathon India A ki haar ke baad internet par funny memes ki baadh aa gayi hai! Fans final mein Pakistan se match ki ummeed kar rahe the, par Sri Lanka A ne baazi maar li!"),
            ("excited", "[excited] तीसरी खबर! दूसरे सेमीफ़ाइनल में दो सौ तैंतीस रन के लक्ष्य का पीछा करते हुए पाकिस्तान ए शुरुआती विकेट गिरने से भारी दबाव में आ गई! हालांकि हसन नवाज़ और शाहज़ैब खान ने शानदार साझेदारी कर पारी को संभाला!", "Teesri khabar! Doosre semi-final mein 233 runs chase karte hue Pakistan A shuruati wickets girne se pressure mein aa gayi, par Hasan Nawaz aur Shahzaib Khan ne shandaar partnership ki!"),
            ("conversational", "[cheerful] वाकई एशिया कप में एक के बाद एक बड़े उलटफेर और ड्रामे देखने को मिल रहे हैं! वीडियो को लाइक और सब्सक्राइब ज़रूर करें!", "Waqai Asia Cup mein ek ke baad ek bade ulatpher aur drame dekhne ko mil rahe hain! Video ko like aur subscribe zaroor karein!"),
        ],
    },
    {
        "id": "ep_03_bilateral_tilak_2in1",
        "title": "India-Pakistan Bilateral Cricket RESUMING?! 🚨 Tilak Varma & India A BIG Mistake Exposed 😡 Cricket News",
        "keywords": ["bilateral", "navjot singh sidhu", "tilak varma", "third pacer"],
        "wiki": ["Navjot Singh Sidhu", "Tilak Varma", "BCCI", "India national cricket team", "Pakistan Cricket Board"],
        "beats": [
            ("excited", "[excited] नमस्ते दोस्तों! दो बहुत अहम खबरों के साथ मैं हाज़िर हूँ — एक तरफ भारत और पाकिस्तान की सीरीज़, और दूसरी तरफ इंडिया ए की बड़ी गलती!", "Namaste dosto! Do bahut aham khabron ke saath main haazir hoon — ek taraf IND-PAK series, aur doosri taraf India A ki badi galti!"),
            ("conversational", "[cheerful] पहली खबर में पूर्व भारतीय बल्लेबाज़ नवजोत सिंह सिद्धू ने साफ कहा है कि भारत और पाकिस्तान के बीच द्विपक्षीय क्रिकेट सीरीज़ शुरू करने का फैसला... पूरी तरह सरकार के हाथ में है। जब तक सरकार मंज़ूरी नहीं देती, दोनों टीमें सिर्फ बड़े टूर्नामेंट्स में ही भिड़ेंगी!", "Pehli khabar mein Navjot Singh Sidhu ne kaha hai ki IND vs PAK bilateral series shuru karne ka faisla poori tarah sarkar ke haath mein hai. Tab tak dono teams sirf bade tournaments mein hi bhidengi!"),
            ("excited", "[surprised] दूसरी खबर! एशिया कप सेमीफ़ाइनल में इंडिया ए की हार के बाद टीम की रणनीति पर कड़े सवाल उठ रहे हैं!", "Doosri khabar! Asia Cup semi-final mein India A ki haar ke baad team ki strategy par bade sawaal uth rahe hain!"),
            ("conversational", "[cheerful] क्रिकेट जानकारों का मानना है कि प्लेइंग इलेवन में तीसरे तेज़ गेंदबाज़ की कमी टीम को बहुत भारी पड़ी... और कप्तान तिलक वर्मा भी अहम मौकों पर गेंदबाज़ी बदलाव से असर नहीं छोड़ पाए।", "Experts ka manna hai ki playing XI mein teesre fast bowler ki kami team ko bhaari padi, aur captain Tilak Varma bhi bowling changes se asar nahi chhod paaye."),
            ("conversational", "[cheerful] तीन सौ से ज़्यादा रन बनाने के बावजूद गेंदबाज़ी में धार न होने के कारण मैच हाथ से फिसल गया! उम्मीद है युवा टीम इससे ज़रूर सीखेगी।", "300 se zyada runs banane ke bawajood bowling mein dhaar na hone se match haath se fisal gaya! Ummeed hai young team isse zaroor seekhegi."),
        ],
    },
    {
        "id": "ep_04_vaibhav_standalone",
        "title": "Vaibhav Sooryavanshi 53-Ball 204! 🤯 Pakistan Star PRAISES Him 👏 Chris Cairns SHOCKED 😱 Cricket News",
        "keywords": ["sooryavanshi", "chris cairns", "204", "star pakistan"],
        "wiki": ["Vaibhav Suryavanshi", "Chris Cairns", "India Under 19 cricket", "Rajasthan Royals batting"],
        "beats": [
            ("excited", "[excited] नमस्ते दोस्तों! आज की सबसे बड़ी और ऐतिहासिक खबर भारत के युवा बल्लेबाज़ वैभव सूर्यवंशी से जुड़ी हुई है... जिनकी तूफानी बल्लेबाज़ी ने पूरी दुनिया को हैरान कर दिया है!", "Namaste dosto! Aaj ki sabse badi khabar India ke young batter Vaibhav Sooryavanshi se judi hai, jinki toofani batting ne poori duniya ko hairan kar diya hai!"),
            ("excited", "[surprised] तिरेपन गेंदों में दो सौ चार रन की विस्फोटक पारी खेलने वाले वैभव सूर्यवंशी ने एशिया कप राइज़िंग स्टार्स में भी अपना शानदार फॉर्म जारी रखा! जिसे देखकर एक स्टार पाकिस्तानी क्रिकेटर ने भी उनकी खुलकर तारीफ की है!", "53 balls mein 204 runs ki visphotak innings khelne wale Vaibhav Sooryavanshi ne Asia Cup mein bhi shandaar form jaari rakha — jiski ek Pakistani star cricketer ne bhi tareef ki hai!"),
            ("conversational", "[cheerful] वहीं न्यूज़ीलैंड के पूर्व दिग्गज ऑलराउंडर क्रिस केर्न्स ने वैभव की दोहरे शतक वाली पारी पर बड़ा बयान दिया है! उन्होंने कहा कि ऐसी अविश्वसनीय बल्लेबाज़ी क्रिकेट में बार-बार देखने को नहीं मिलती!", "Wahin New Zealand ke legend Chris Cairns ne Vaibhav ki double century par kaha ki aisi avishwasniya batting cricket mein baar-baar dekhne ko nahi milti!"),
            ("conversational", "[cheerful] क्रिस केर्न्स ने माना कि इतनी कम उम्र में वैभव का शॉट सिलेक्शन और पावर हिटिंग बिल्कुल विश्व स्तरीय है, और वे आने वाले समय में बड़े-बड़े रिकॉर्ड तोड़ सकते हैं!", "Chris Cairns ne maana ki itni kam umar mein Vaibhav ka shot selection aur power hitting world-class hai, aur woh aage bade records tod sakte hain!"),
            ("excited", "[excited] वाकई भारतीय क्रिकेट को एक नया सुपरस्टार मिल चुका है! वैभव सूर्यवंशी की इस पारी को आप दस में से कितने नंबर देंगे? कमेंट में ज़रूर बताइए!", "Waqai Indian cricket ko ek naya superstar mil chuka hai! Vaibhav ki is innings ko aap 10 mein se kitne number denge? Comment mein zaroor batayein!"),
        ],
    },
    {
        "id": "ep_05_mi_rohit_bumrah_2in1",
        "title": "Jasprit Bumrah REJECTS MI Vice-Captaincy?! 😱 Rohit Sharma RETURNS as MI CAPTAIN 🚨💙 IPL 2027 News",
        "keywords": ["bumrah", "vice-captain", "rohit sharma", "hardik pandya", "mumbai indians"],
        "wiki": ["Jasprit Bumrah", "Rohit Sharma", "Hardik Pandya", "Wankhede Stadium", "Mumbai Indians"],
        "beats": [
            ("excited", "[excited] नमस्ते दोस्तों! आई पी एल दो हज़ार सत्ताईस से पहले मुंबई इंडियंस खेमे से दो बहुत बड़ी और चौंकाने वाली खबरें सामने आ रही हैं!", "Namaste dosto! IPL 2027 se pehle Mumbai Indians camp se do bahut badi aur chaunkane wali khabrein saamne aa rahi hain!"),
            ("excited", "[excited] पहली खबर! पांच बार के चैंपियन कप्तान रोहित शर्मा एक बार फिर मुंबई इंडियंस के कप्तान बन गए हैं! हार्दिक पांड्या के पंजाब किंग्स में ट्रेड होने के बाद फ्रेंचाइज़ी ने फिर से हिटमैन पर भरोसा जताया है!", "Pehli khabar! 5-time champion captain Rohit Sharma ek baar phir Mumbai Indians ke captain ban gaye hain! Hardik Pandya ke PBKS trade ke baad Hitman ki wapsi hui hai!"),
            ("conversational", "[cheerful] कप्तानी वापस मिलने के बाद रोहित शर्मा ने अपना पहला बयान देते हुए कहा कि वे आने वाली चुनौतियों के लिए पूरी तरह तैयार हैं!", "Captaincy wapas milne ke baad Rohit Sharma ne apna pehla statement dete hue kaha ki woh aane wali challenges ke liye poori tarah ready hain!"),
            ("excited", "[surprised] लेकिन दूसरी बड़ी खबर ने सबको चौंका दिया है! रिपोर्ट्स के मुताबिक मुंबई इंडियंस ने स्टार तेज़ गेंदबाज़ जसप्रीत बुमराह को रोहित का उप-कप्तान बनने का ऑफर दिया था... जिसे बुमराह ने ठुकरा दिया है!", "Lekin doosri badi khabar ne sabko chaunka diya hai! Reports ke mutabik MI ne Jasprit Bumrah ko vice-captaincy offer ki thi, jise Bumrah ne reject kar diya hai!"),
            ("conversational", "[cheerful] बताया जा रहा है कि बुमराह अपने वर्कलोड और गेंदबाज़ी पर पूरा ध्यान देना चाहते हैं। अब देखना होगा कि मुंबई इंडियंस का नया उप-कप्तान कौन बनता है!", "Bataya ja raha hai ki Bumrah apne workload aur bowling par focus karna chahte hain. Ab dekhna hoga ki MI ka naya vice-captain kaun banta hai!"),
        ],
    },
    {
        "id": "ep_06_ipl_psl_bcci_3in1",
        "title": "IPL 2027 vs PSL 12 CLASH! 🚨 BCCI Rejects 12 Teams ❌ Ganguly & Yuvraj DC Plan 🔥 Cricket News",
        "keywords": ["psl", "expansion", "ganguly", "yuvraj", "pcb", "bcci"],
        "wiki": ["BCCI", "Narendra Modi Stadium", "Sourav Ganguly", "Yuvraj Singh", "Delhi Capitals"],
        "beats": [
            ("excited", "[excited] नमस्ते दोस्तों! आई पी एल, पी एस एल और क्रिकेट बोर्ड्स से जुड़ी तीन बड़ी खबरें एक साथ लेकर मैं आपके सामने हाज़िर हूँ!", "Namaste dosto! IPL, PSL aur cricket boards se judi 3 badi khabrein ek saath lekar main aapke saamne haazir hoon!"),
            ("excited", "[surprised] पहली खबर! पाकिस्तान क्रिकेट बोर्ड ने पी एस एल सीज़न बारह की तारीखें अठारह मार्च से दो मई दो हज़ार सत्ताईस तय कर दी हैं! जिससे एक बार फिर आई पी एल और पी एस एल के बीच सीधी टक्कर तय मानी जा रही है!", "Pehli khabar! PCB ne PSL 12 ki dates 18 March se 2 May 2027 fix kar di hain, jisse ek baar phir IPL 2027 aur PSL ke beech seedha clash tay maana ja raha hai!"),
            ("conversational", "[cheerful] दूसरी खबर! पुणे और वडोदरा के रूप में आई पी एल में बारह टीमों की चर्चाओं पर बी सी सी आई अधिकारियों ने विराम लगा दिया है, और साफ किया है कि फिलहाल दस टीमों का ही फॉर्मेट जारी रहेगा!", "Doosri khabar! Pune aur Vadodara ke roop mein IPL mein 12 teams ki charchaon par BCCI ne viraam laga diya hai — abhi 10 teams ka hi format rahega!"),
            ("conversational", "[cheerful] तीसरी खबर! जहाँ पी सी बी ने अपने सेंट्रल कॉन्ट्रैक्ट से कई बड़े नामों को बाहर किया है... वहीं आई पी एल में सौरव गांगुली और युवराज सिंह मिलकर दिल्ली कैपिटल्स की नई रणनीति तैयार कर रहे हैं!", "Teesri khabar! Jahan PCB ne apne central contracts se bade naamon ko bahar kiya hai, wahin Sourav Ganguly aur Yuvraj Singh milkar Delhi Capitals ki nayi strategy bana rahe hain!"),
            ("excited", "[excited] तो आने वाले सीज़न से पहले फ्रेंचाइज़ी और बोर्ड स्तर पर हलचल काफी तेज़ हो चुकी है!", "Toh aane wale season se pehle franchise aur board level par halchal kaafi tez ho chuki hai!"),
        ],
    },
    {
        "id": "ep_07_ind_nz_bumrah_3in1",
        "title": "Gambhir & Gill SLAMMED for Siraj Snub 😡 Saliva Ban Lift? 😳 Kiwi Legend on Bumrah 🔥 IND vs NZ News",
        "keywords": ["gautam gambhir", "siraj", "saliva", "chris cairns", "bumrah"],
        "wiki": ["Mohammed Siraj", "Shubman Gill", "Gautam Gambhir", "Jasprit Bumrah", "New Zealand national cricket team"],
        "beats": [
            ("excited", "[excited] नमस्ते दोस्तों! इंडिया बनाम न्यूज़ीलैंड टेस्ट सीरीज़ और टीम इंडिया से जुड़ी तीन बड़ी खबरें इस वक्त सुर्खियों में हैं!", "Namaste dosto! India vs New Zealand Test series aur Team India se judi 3 badi khabrein is waqt surkhiyon mein hain!"),
            ("excited", "[surprised] पहली खबर! दूसरे टेस्ट की प्लेइंग इलेवन से मोहम्मद सिराज को बाहर रखने पर हेड कोच गौतम गंभीर और कप्तान शुभमन गिल की जमकर आलोचना हो रही है! कई पूर्व क्रिकेटरों ने इस फैसले पर हैरानी जताई है!", "Pehli khabar! Doosre Test ki playing XI se Mohammed Siraj ko bahar rakhne par Gautam Gambhir aur Shubman Gill ki jamkar aalochana ho rahi hai!"),
            ("conversational", "[cheerful] दूसरी खबर! शुभमन गिल ने वेलिंग्टन टेस्ट के बाद गेंद पर सलाइवा यानी थूक के इस्तेमाल से बैन हटाने की मांग उठाई है... जिसका अब पूर्व मुख्य चयनकर्ता एम एस के प्रसाद ने भी खुला समर्थन किया है!", "Doosri khabar! Shubman Gill ne Wellington Test ke baad ball par saliva ban hatane ki maang ki hai, jiska ab ex-chief selector MSK Prasad ne bhi samarthan kiya hai!"),
            ("excited", "[cheerful] तीसरी खबर! न्यूज़ीलैंड के पूर्व दिग्गज क्रिस केर्न्स ने जसप्रीत बुमराह की तारीफ करते हुए कहा है कि बुमराह की मौजूदगी ही भारत को किसी भी परिस्थिति में जीत का सबसे बड़ा दावेदार बनाती है!", "Teesri khabar! Kiwi legend Chris Cairns ne Jasprit Bumrah ki tareef karte hue kaha hai ki Bumrah ki maujoodgi hi India ko sabse bada favourite banati hai!"),
            ("excited", "[excited] तो दोस्तों, इन तीनों खबरों में से आपको सबसे ज़्यादा क्या पसंद आया? कमेंट में ज़रूर बताइए!", "Toh dosto, in teeno khabron mein se aapko sabse zyada kya pasand aaya? Comment mein zaroor batayein!"),
        ],
    },
]


def _fmt_ass_time(sec: float) -> str:
    sec = max(0.0, sec)
    h = int(sec // 3600)
    m = int((sec % 3600) // 60)
    s = sec % 60
    return f"{h}:{m:02d}:{s:05.2f}"


def _split_subtitle_chunks(text: str, max_words: int = 4, max_chars: int = 30) -> list[list[str]]:
    words = [w for w in text.strip().split() if w]
    chunks: list[list[str]] = []
    cur: list[str] = []
    cur_len = 0
    for w in words:
        if cur and (len(cur) >= max_words or cur_len + len(w) + 1 > max_chars):
            chunks.append(cur)
            cur = [w]
            cur_len = len(w)
        else:
            cur.append(w)
            cur_len += len(w) + (1 if cur_len else 0)
    if cur:
        chunks.append(cur)
    return chunks or [[text.strip()]]


def _write_ass_subtitles(ass_path: Path, beat_timings: list[tuple[float, float, str]]) -> None:
    """Write modern dynamic word-by-word Hinglish ASS subtitles.

    Words appear progressively as they are spoken, with the active word
    highlighted in bright gold and slightly scaled up.
    """
    header = (
        "[Script Info]\n"
        "ScriptType: v4.00+\n"
        "PlayResX: 1280\n"
        "PlayResY: 720\n"
        "WrapStyle: 2\n"
        "\n"
        "[V4+ Styles]\n"
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, "
        "Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, "
        "Alignment, MarginL, MarginR, MarginV, Encoding\n"
        "Style: Hinglish,Segoe UI,38,&H00FFFFFF,&H0000E5FF,&H00120E0A,&H96000000,"
        "-1,0,0,0,100,100,0.6,0,1,3.4,1.8,2,80,80,44,1\n"
        "\n"
        "[Events]\n"
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"
    )
    events: list[str] = []
    for start_t, end_t, hinglish_text in beat_timings:
        chunks = _split_subtitle_chunks(hinglish_text, max_words=4, max_chars=30)
        all_words = [w for ch in chunks for w in ch]
        total_weight = max(1, sum(max(2, len(re.sub(r"[^A-Za-z0-9]", "", w))) for w in all_words))
        dur = max(0.5, end_t - start_t)
        cursor = start_t

        for ch_idx, chunk_words in enumerate(chunks):
            safe_words = [w.replace("\n", " ").replace("{", "(").replace("}", ")") for w in chunk_words]
            for w_idx, w in enumerate(safe_words):
                weight = max(2, len(re.sub(r"[^A-Za-z0-9]", "", w)))
                w_dur = dur * (weight / total_weight)
                is_very_last = (ch_idx == len(chunks) - 1) and (w_idx == len(safe_words) - 1)
                w_end = end_t if is_very_last else min(end_t, cursor + w_dur)

                prev_txt = " ".join(safe_words[:w_idx])
                if prev_txt:
                    line = (
                        r"{\blur0.6\c&H00FFFFFF&\fscx100\fscy100}"
                        + prev_txt
                        + r" {\c&H0000E5FF&\fscx108\fscy108}"
                        + w
                    )
                else:
                    line = r"{\blur0.6\c&H0000E5FF&\fscx108\fscy108}" + w

                events.append(
                    f"Dialogue: 0,{_fmt_ass_time(cursor)},{_fmt_ass_time(w_end)},Hinglish,,0,0,0,,{line}"
                )
                cursor = w_end
    ass_path.write_text(header + "\n".join(events) + "\n", encoding="utf-8")


async def _search_bing_images(client: httpx.AsyncClient, query: str, limit: int = 8) -> list[str]:
    """Fetch high-res image URLs from Bing Image Search for an exact topic query."""
    url = (
        f"https://www.bing.com/images/search?q={quote(query)}"
        "&qft=+filterui:imagesize-large+filterui:aspect-wide&form=IRFLTR"
    )
    try:
        r = await client.get(url, timeout=15)
        if r.status_code != 200:
            return []
        raw_urls = re.findall(r'murl&quot;:&quot;(https?://[^&]+?)&quot;', r.text)
        if not raw_urls:
            raw_urls = re.findall(r'"murl":"(https?://[^"]+?)"', r.text)
        out: list[str] = []
        for u in raw_urls:
            u_clean = html_lib.unescape(u)
            if any(bad in u_clean.lower() for bad in ("logo", "icon", "avatar", "sprite", "svg", "gif", "vector", "shutterstock", "istockphoto", "alamy", "gettyimages", "dreamstime", "123rf")):
                continue
            out.append(u_clean)
            if len(out) >= limit:
                break
        return out
    except Exception:
        return []


async def _gather_many_images(
    ep: dict[str, Any],
    news_items: list[dict[str, Any]],
    img_dir: Path,
    target_count: int = 12,
    force_refresh: bool = False,
) -> list[Path]:
    from make_all_topic_videos import _is_valid_image

    if force_refresh and img_dir.exists():
        for old in img_dir.glob("img_*"):
            old.unlink(missing_ok=True)

    existing = sorted(
        p for p in img_dir.glob("img_*")
        if p.suffix.lower() in (".jpg", ".jpeg", ".png") and _is_valid_image(p)
    )
    if len(existing) >= target_count and not force_refresh:
        return existing[:target_count]

    candidate_urls: list[str] = []
    kws = [k.lower() for k in ep.get("keywords", [])]
    matching_articles = [
        it for it in news_items
        if any(k in f"{it.get('title', '')} {it.get('summary', '')}".lower() for k in kws)
    ]
    for it in matching_articles[:6]:
        if it.get("image_url"):
            candidate_urls.append(it["image_url"])

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
    }

    async with httpx.AsyncClient(headers=headers, follow_redirects=True, timeout=15) as c:
        # 1. Bing Image Search for each specific subject in ep["wiki"]
        bing_queries = [f"{q} cricket" if "cricket" not in q.lower() and "stadium" not in q.lower() and "bcci" not in q.lower() else q for q in ep.get("wiki", [])]
        for bq in bing_queries:
            urls = await _search_bing_images(c, bq, limit=6)
            candidate_urls.extend(urls)

        # 2. Wikimedia Commons fallback queries for real player/stadium photos
        for q in ep.get("wiki", []):
            try:
                wu = (
                    "https://commons.wikimedia.org/w/api.php?action=query&generator=search"
                    f"&gsrnamespace=6&gsrsearch={quote(q)}&gsrlimit=5&prop=imageinfo&iiprop=url&iiurlwidth=1280&format=json"
                )
                r = await c.get(wu, headers={"User-Agent": "CricketLiveBot/1.0"})
                if r.status_code == 200 and r.text.strip().startswith("{"):
                    for v in (r.json().get("query", {}).get("pages") or {}).values():
                        ii = (v.get("imageinfo") or [{}])[0]
                        u2 = ii.get("thumburl") or ii.get("url")
                        if u2 and any(e in u2.lower() for e in (".jpg", ".jpeg", ".png")):
                            candidate_urls.append(u2)
            except Exception:
                pass

        saved: list[Path] = []
        seen_urls: set[str] = set()
        seen_hashes: set[str] = set()
        idx = 0
        for u in candidate_urls:
            if len(saved) >= target_count:
                break
            if not u or u in seen_urls or not u.startswith("http"):
                continue
            seen_urls.add(u)
            try:
                resp = await c.get(u, headers=headers)
                if resp.status_code == 200 and len(resp.content) > 18000:
                    ctype = resp.headers.get("content-type", "").lower()
                    if "image" not in ctype and not any(e in u.lower() for e in (".jpg", ".jpeg", ".png", ".webp")):
                        continue
                    h = hashlib.md5(resp.content).hexdigest()
                    if h in seen_hashes:
                        continue
                    ext = ".png" if ".png" in u.lower().split("?")[0] else ".jpg"
                    p = img_dir / f"img_{idx:02d}{ext}"
                    p.write_bytes(resp.content)
                    if _is_valid_image(p):
                        seen_hashes.add(h)
                        saved.append(p)
                        idx += 1
                    else:
                        p.unlink(missing_ok=True)
            except Exception:
                pass

    return saved[:target_count]


async def _render_episode(ep: dict[str, Any], news_items: list[dict[str, Any]], force: bool = False) -> Path:
    eid = ep["id"]
    out_mp4 = VIDEOS_DIR / f"{eid}.mp4"
    if out_mp4.exists() and out_mp4.stat().st_size > 200_000 and not force:
        print(f"[{eid}] Already exists, skipping.")
        return out_mp4

    edir = BUILD_ROOT / eid
    img_dir = edir / "imgs"
    norm_dir = edir / "norm"
    clip_dir = edir / "clips"
    audio_dir = edir / "audio"
    for d in (edir, img_dir, norm_dir, clip_dir, audio_dir):
        d.mkdir(parents=True, exist_ok=True)

    print(f"\n=== [{eid}] {ep['title']} ===")
    imgs = await _gather_many_images(ep, news_items, img_dir, target_count=12, force_refresh=force)
    if len(imgs) < 4:
        raise RuntimeError(f"[{eid}] Not enough valid images ({len(imgs)})")
    print(f"  Images ({len(imgs)}): {[p.name for p in imgs]}")

    beat_paths: list[Path] = []
    beat_durs: list[float] = []
    for idx, (mood, text, _) in enumerate(ep["beats"]):
        mp3_p = audio_dir / f"beat_{idx:02d}.mp3"
        audio_bytes = await synthesize_fish_audio(text, speaker="host", mood=mood)
        if not audio_bytes:
            raise RuntimeError(f"[{eid}] Empty TTS for beat {idx}")
        mp3_p.write_bytes(audio_bytes)
        dur = _probe_duration(mp3_p) or await get_mp3_duration_sec(audio_bytes)
        beat_paths.append(mp3_p)
        beat_durs.append(dur)
        print(f"  beat_{idx:02d}.mp3 -> {dur:.2f}s ({mood})")

    # Build Hinglish ASS subtitle timeline matching exact beat durations + pauses
    beat_timings: list[tuple[float, float, str]] = []
    t_cur = 0.0
    for idx, (_, _, hinglish_text) in enumerate(ep["beats"]):
        b_dur = beat_durs[idx]
        beat_timings.append((t_cur, t_cur + b_dur, hinglish_text))
        t_cur += b_dur + (PAUSE_BETWEEN_BEATS_SEC if idx < len(ep["beats"]) - 1 else 0.0)
    ass_path = edir / "subs.ass"
    _write_ass_subtitles(ass_path, beat_timings)

    voice_full = edir / "voice_full.wav"
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
    # synthesize_fish_audio already runs single-pass denoise/EQ; only apply gentle mastering
    # without re-running afftdn or treble boost to keep the voice crystal clear and non-fuzzy.
    voice_fx = (
        "highpass=f=85,"
        "lowpass=f=13500,"
        "equalizer=f=350:t=o:w=1.2:g=-1.0,"
        "acompressor=threshold=-18dB:ratio=1.7:attack=18:release=130,"
        "loudnorm=I=-15:TP=-1.5:LRA=7"
    )
    af_parts.append(f"{''.join(concat_inputs)}concat=n={2*n_beats-1}:v=0:a=1,{voice_fx}[aout]")
    af_script = audio_dir / "audio_concat.ffscript"
    af_script.write_text(";\n".join(af_parts), encoding="utf-8")
    audio_cmd.extend(["-filter_complex_script", str(af_script), "-map", "[aout]", "-ac", "2", "-c:a", "pcm_s16le", str(voice_full)])
    _run(audio_cmd, f"{eid} concat audio")
    total_audio_dur = _probe_duration(voice_full)
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
        vf = _build_zoompan_expr(MOTIONS[idx % len(MOTIONS)], n_frames)
        xfades.append(XFADES[idx % len(XFADES)])
        _run(
            ["ffmpeg", "-y", "-v", "error", "-i", str(norm_p), "-vf", vf, "-frames:v", str(n_frames), "-r", str(FPS),
             "-c:v", "libx264", "-preset", "fast", "-crf", "18", "-pix_fmt", "yuv420p", str(clip_p)],
            f"{eid} clip_{idx:02d}",
        )
        clip_paths.append(clip_p)
        clip_durs.append(actual_sec)

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
    rel_ass = ass_path.relative_to(ROOT_DIR).as_posix()
    filter_parts.append(f"[vjoined]fade=t=in:st=0:d=0.25,fade=t=out:st={fade_out_start:.3f}:d=0.45,subtitles={rel_ass},format=yuv420p[vfinal]")

    ffscript = edir / "xfade.ffscript"
    ffscript.write_text(";\n".join(filter_parts), encoding="utf-8")
    cmd: list[str] = ["ffmpeg", "-y", "-v", "error"]
    for cp in clip_paths:
        cmd.extend(["-i", str(cp)])
    cmd.extend(["-i", str(voice_full), "-filter_complex_script", str(ffscript), "-map", "[vfinal]", "-map", f"{len(clip_paths)}:a",
                "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-c:a", "aac", "-ac", "2", "-b:a", "192k", "-movflags", "+faststart", str(out_mp4)])
    _run(cmd, f"{eid} stitch final")
    final_dur = _probe_duration(out_mp4)
    print(f"  DONE -> {out_mp4.name} ({final_dur:.2f}s, {out_mp4.stat().st_size/(1024*1024):.2f} MB)")
    return out_mp4


async def main() -> None:
    force = "--force" in sys.argv
    latest_p = NEWS_DIR / "latest_news.json"
    news_items = json.loads(latest_p.read_text(encoding="utf-8")).get("items", []) if latest_p.exists() else []
    for ep in EPISODES:
        try:
            await _render_episode(ep, news_items, force=force)
        except Exception as exc:
            print(f"[{ep['id']}] ERROR: {exc}")


if __name__ == "__main__":
    asyncio.run(main())
