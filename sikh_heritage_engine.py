"""
ੴ Local Sikh Heritage & Gurbani Engine (100% Offline)
Antigravity Local AI PC Cockpit

Features:
- Offline Gurbani Audio Dispatcher for Daily Nitnem (Japji, Jaap, Savaiye, Chaupai, Anand, Rehras, Sohila, Sukhmani, Asa Di Var, Ardas).
- Strict adherence to PC Speakers audio routing & zero external cloud dependencies.
- Local library search in C:\\Users\\User\\Music and C:\\Users\\User\\Music\\Nitnem.
- Seamless automatic download fallback via yt-dlp to C:\\Users\\User\\Music if missing.
- Curated offline encyclopedia: The 10 Gurus, Sri Guru Granth Sahib Ji, Chaar Sahibzade, Panj Pyare, 5 Takhts,
  Mool Mantar, 3 Pillars, 5 Ks, Nanakshahi Calendar & Daily Contemplations.
"""

import os
import re
import difflib
import time
from typing import Dict, Any, List, Optional

# Base directories
MUSIC_DIR = os.path.expanduser(r"~\Music")
NITNEM_DIR = os.path.join(MUSIC_DIR, "Nitnem")
os.makedirs(NITNEM_DIR, exist_ok=True)

# =========================================================================
# ੴ SACRED NITNEM & GURBANI AUDIO DIRECTORY
# =========================================================================

NITNEM_BAANIS = {
    "japji_sahib": {
        "id": "japji_sahib",
        "title": "Japji Sahib",
        "gurmukhi": "ਜਪੁਜੀ ਸਾਹਿਬ",
        "author": "Guru Nanak Dev Ji (First Guru)",
        "timing": "Amrit Vela (Early Morning / Dawn)",
        "source": "Sri Guru Granth Sahib Ji, Ang 1 - 8",
        "structure": "Mool Mantar, 38 Pauris, 2 Saloks",
        "theme": "The foundational essence of Sikh spirituality: divine order (Hukam), truthful living, conquering the ego, and realizing the Formless Creator.",
        "search_keys": ["japji", "japu", "japuji", "japu ji", "japji sahib"],
        "download_query": "Japji Sahib Full Path Bhai Manpreet Singh Ji Kanpuri or Bhai Joginder Singh Riar",
        "opening_verse": "ੴ ਸਤਿ ਨਾਮੁ ਕਰਤਾ ਪੁਰਖੁ ਨਿਰਭਉ ਨਿਰਵੈਰੁ ਅਕਾਲ ਮੂਰਤਿ ਅਜੂਨੀ ਸੈਭੰ ਗੁਰ ਪ੍ਰਸਾਦਿ ॥",
    },
    "jaap_sahib": {
        "id": "jaap_sahib",
        "title": "Jaap Sahib",
        "gurmukhi": "ਜਾਪੁ ਸਾਹਿਬ",
        "author": "Guru Gobind Singh Ji (Tenth Guru)",
        "timing": "Amrit Vela (Morning)",
        "source": "Sri Dasam Granth Sahib Ji, Ang 1 - 10",
        "structure": "199 Verses (Chhands)",
        "theme": "A cosmic, martial salutation to Akal Purakh's infinite names, transcendent formlessness, invincibility, and omnipresent grace.",
        "search_keys": ["jaap", "jaapu", "jaap sahib", "jaapu sahib"],
        "download_query": "Jaap Sahib Full Nitnem Path",
        "opening_verse": "ਚਕ੍ਰ ਚਿਹਨ ਅਰੁ ਬਰਨ ਜਾਤਿ ਅਰੁ ਪਾਤਿ ਨਹਿਨ ਜਿਹ ॥",
    },
    "tav_prasad_savaiye": {
        "id": "tav_prasad_savaiye",
        "title": "Tav-Prasad Savaiye",
        "gurmukhi": "ਤ੍ਵ ਪ੍ਰਸਾਦਿ ਸਵੱਯੇ",
        "author": "Guru Gobind Singh Ji (Tenth Guru)",
        "timing": "Amrit Vela (Morning)",
        "source": "Sri Dasam Granth Sahib Ji (Akal Ustat)",
        "structure": "10 Quatrains (Savaiyas)",
        "theme": "Rejecting hollow rituals, asceticism, and pomp; affirms that only those whose hearts are filled with sincere unconditional love attain the Supreme Lord ('Jin Prem Kiyo Tin Hee Prabh Paayo').",
        "search_keys": ["tav prasad", "savaiye", "sawaiye", "swaiye", "tavprasad", "tav prasad savaiye"],
        "download_query": "Tav Prasad Savaiye Full Path Nitnem",
        "opening_verse": "ਸ੍ਰਾਵਗ ਸੁਧ ਸਮੂਹ ਸਿਧਾਨ ਕੇ ਦੇਖਿ ਫਿਰਿਓ ਘਰ ਜੋਗ ਜਤੀ ਕੇ ॥",
    },
    "chaupai_sahib": {
        "id": "chaupai_sahib",
        "title": "Chaupai Sahib (Benti Chaupai)",
        "gurmukhi": "ਬੇਨਤੀ ਚੌਪਈ ਸਾਹਿਬ",
        "author": "Guru Gobind Singh Ji (Tenth Guru)",
        "timing": "Amrit Vela (Morning) & Rehras Sahib (Evening)",
        "source": "Sri Dasam Granth Sahib Ji (Charitropakhyan)",
        "structure": "29 Chaupais, 1 Dohra",
        "theme": "The ultimate shield and supplication for divine spiritual protection, courage in righteous action, and deliverance from fear and adversity.",
        "search_keys": ["chaupai", "chaupai sahib", "benti chaupai", "chopai", "chaupayi"],
        "download_query": "Chaupai Sahib Full Nitnem Path",
        "opening_verse": "ਹਮਰੀ ਕਰੋ ਹਾਥ ਦੈ ਰੱਛਾ ॥ ਪੂਰਨ ਹੋਇ ਚਿਤ ਕੀ ਇੱਛਾ ॥",
    },
    "anand_sahib": {
        "id": "anand_sahib",
        "title": "Anand Sahib",
        "gurmukhi": "ਅਨੰਦੁ ਸਾਹਿਬ",
        "author": "Guru Amar Das Ji (Third Guru)",
        "timing": "Amrit Vela (Morning), Evening, and concluding all congregations",
        "source": "Sri Guru Granth Sahib Ji, Ang 917 - 922 (Raag Ramkali)",
        "structure": "40 Pauris (Complete) / 6 Pauris (Short recitation)",
        "theme": "The Song of Spiritual Bliss; describes the transcendent joy of achieving unison with the Satguru and living in spiritual equanimity.",
        "search_keys": ["anand", "anand sahib", "anandu", "anandu sahib"],
        "download_query": "Anand Sahib Full 40 Pauris Nitnem Path",
        "opening_verse": "ਅਨੰਦੁ ਭਇਆ ਮੇਰੀ ਮਾਏ ਸਤਿਗੁਰੂ ਮੈ ਪਾਇਆ ॥",
    },
    "rehras_sahib": {
        "id": "rehras_sahib",
        "title": "Rehras Sahib",
        "gurmukhi": "ਰਹਰਾਸਿ ਸਾਹਿਬ",
        "author": "Guru Nanak Dev Ji, Guru Amar Das Ji, Guru Ram Das Ji, Guru Arjan Dev Ji, Guru Gobind Singh Ji",
        "timing": "Sandhya Vela (Sunset / Evening)",
        "source": "Sri Guru Granth Sahib Ji (Ang 8 - 12) & Sri Dasam Granth Sahib Ji",
        "structure": "So Dar, So Purakh, Chaupai Sahib, Anand Sahib stanzas, Mundavani, Salok",
        "theme": "Evening meditation reflecting upon divine grace, offering thanks at the conclusion of daily worldly labors, and purifying the soul.",
        "search_keys": ["rehras", "rehraas", "rehras sahib", "evening nitnem", "sandhya"],
        "download_query": "Rehras Sahib Full Path Nitnem",
        "opening_verse": "ਸੋ ਦਰੁ ਤੇਰਾ ਕੇਹਾ ਸੋ ਘਰੁ ਕੇਹਾ ਜਿਤੁ ਬਹਿ ਸਰਬ ਸਮਾਲੇ ॥",
    },
    "kirtan_sohila": {
        "id": "kirtan_sohila",
        "title": "Kirtan Sohila",
        "gurmukhi": "ਕੀਰਤਨ ਸੋਹਿਲਾ",
        "author": "Guru Nanak Dev Ji, Guru Ram Das Ji, Guru Arjan Dev Ji",
        "timing": "Night (Before sleep / Bedside)",
        "source": "Sri Guru Granth Sahib Ji, Ang 12 - 13",
        "structure": "5 Shabads (Raag Gauri Dipaki, Asa, Dhanasri, Gauri Purbi)",
        "theme": "Song of Divine union and soul rest; dispels fears of darkness, mortality, and nightmares, preparing the consciousness for restful contemplation.",
        "search_keys": ["sohila", "kirtan sohila", "sohila sahib", "bedtime prayer"],
        "download_query": "Kirtan Sohila Full Path Nitnem",
        "opening_verse": "ਜੈ ਘਰਿ ਕੀਰਤਿ ਆਖੀਐ ਕਰਤੇ ਕਾ ਹੋਇ ਬੀਚਾਰੋ ॥",
    },
    "sukhmani_sahib": {
        "id": "sukhmani_sahib",
        "title": "Sukhmani Sahib",
        "gurmukhi": "ਸੁਖਮਨੀ ਸਾਹਿਬ",
        "author": "Guru Arjan Dev Ji (Fifth Guru)",
        "timing": "Any time of day / Morning",
        "source": "Sri Guru Granth Sahib Ji, Ang 262 - 296 (Raag Gauri)",
        "structure": "24 Ashtpadis (Each with 1 Salok and 8 Pauris)",
        "theme": "The Jewel of Peace; supreme elixir for mental tranquility, dissolving stress, sorrow, and anxiety through persistent remembrance of the True Name.",
        "search_keys": ["sukhmani", "sukhmani sahib", "peace prayer"],
        "download_query": "Sukhmani Sahib Full Path Bhai Joginder Singh Riar",
        "opening_verse": "ਸਲੋਕੁ ॥ ੴ ਸਤਿਗੁਰ ਪ੍ਰਸਾਦਿ ॥ ਆਦਿ ਗੁਰਏ ਨਮਹ ॥ ਜੁਗਾਦਿ ਗੁਰਏ ਨਮਹ ॥",
    },
    "asa_di_var": {
        "id": "asa_di_var",
        "title": "Asa Di Var",
        "gurmukhi": "ਆਸਾ ਦੀ ਵਾਰ",
        "author": "Guru Nanak Dev Ji (with Saloks by Guru Angad Dev Ji)",
        "timing": "Amrit Vela (Dawn / Morning Kirtan)",
        "source": "Sri Guru Granth Sahib Ji, Ang 462 - 475 (Raag Asa)",
        "structure": "24 Pauris and 59 Saloks",
        "theme": "The Ballad of Hope; fierce denunciation of hypocrisy, caste prejudice, and religious arrogance; exalts humility, selfless service, and truth.",
        "search_keys": ["asa di var", "asa ki var", "aasa di vaar", "asa di vaar"],
        "download_query": "Asa Di Var Full Path Kirtan",
        "opening_verse": "ਸਲੋਕੁ ਮਃ ੧ ॥ ਬਲਿਹਾਰੀ ਗੁਰ ਆਪਣੇ ਦਿਉਹਾੜੀ ਸਦ ਵਾਰ ॥",
    },
    "dukh_bhanjani_sahib": {
        "id": "dukh_bhanjani_sahib",
        "title": "Dukh Bhanjani Sahib",
        "gurmukhi": "ਦੁਖ ਭੰਜਨੀ ਸਾਹਿਬ",
        "author": "Guru Arjan Dev Ji (Fifth Guru)",
        "timing": "Any time for physical, mental, or emotional healing",
        "source": "Sri Guru Granth Sahib Ji (Raag Gauri, Bilawal, Sorath)",
        "structure": "Sacred collection of healing Shabads",
        "theme": "The Destroyer of Suffering; powerful spiritual medicine restoring faith, hope, and physical wellness during illness and distress.",
        "search_keys": ["dukh bhanjani", "dukh bhanjani sahib", "dukhbhanjani"],
        "download_query": "Dukh Bhanjani Sahib Full Path",
        "opening_verse": "ਦੂਖੁ ਤਦੇ ਜਾ ਵਿਸਰੈ ਸੁਖੁ ਤਾ ਕੈ ਹਿਰਦੈ ਹੋਇ ॥",
    },
    "ardas": {
        "id": "ardas",
        "title": "Sri Ardas",
        "gurmukhi": "ਅਰਦਾਸ",
        "author": "Khalsa Tradition (Opening Var Sri Bhagauti Ji by Guru Gobind Singh Ji)",
        "timing": "Conclusion of Nitnem, congregational prayers, and all major endeavors",
        "source": "Sikh Rahit Maryada & Sri Dasam Granth Sahib Ji",
        "structure": "Three parts: Invocation of 10 Gurus, Historical chronicle of sacrifices, Personal supplication & Sarbat Da Bhala",
        "theme": "Solemn collective prayer connecting Sikhs with historical martyrdoms, ending with prayer for the welfare and prosperity of all humanity.",
        "search_keys": ["ardas", "ardaas", "sikh ardas", "supplication"],
        "download_query": "Ardas Full Recitation Audio",
        "opening_verse": "ੴ ਵਾਹਿਗੁਰੂ ਜੀ ਕੀ ਫ਼ਤਹਿ ॥ ਸ੍ਰੀ ਭਗਉਤੀ ਜੀ ਸਹਾਇ ॥",
    },
}

# =========================================================================
# ੴ SIKH HERITAGE KNOWLEDGE BASE (100% OFFLINE)
# =========================================================================

GURU_SAHIBAN = [
    {
        "order": 1,
        "name": "Guru Nanak Dev Ji",
        "gurmukhi": "ਗੁਰੂ ਨਾਨਕ ਦੇਵ ਜੀ",
        "dates": "1469 – 1539",
        "birthplace": "Rai Bhoi Ki Talwandi (Nankana Sahib, Punjab)",
        "gaddi": "1469 – 1539 (Founder)",
        "sacred_cities": ["Kartarpur Sahib", "Sultanpur Lodhi"],
        "major_compositions": ["Japji Sahib", "Asa Di Var", "Sidh Gosht", "Barah Maha", "Dakhni Oankar"],
        "core_pillars": [
            "Naam Japna (Contemplating the Divine Name)",
            "Kirat Karo (Earning by honest, righteous labor)",
            "Vand Chhako (Sharing earnings with those in need)"
        ],
        "key_teachings": "Formulated the foundational Sikh truth: 'There is no Hindu, there is no Muslim' (all are children of One Creator). Undertook 4 epic Udasis (travels) across Asia, Tibet, Middle East (Mecca/Baghdad) preaching oneness, equality of women, and abolition of caste.",
    },
    {
        "order": 2,
        "name": "Guru Angad Dev Ji",
        "gurmukhi": "ਗੁਰੂ ਅੰਗਦ ਦੇਵ ਜੀ",
        "dates": "1504 – 1552",
        "original_name": "Bhai Lehna Ji",
        "gaddi": "1539 – 1552",
        "sacred_cities": ["Khadur Sahib"],
        "contributions": "Standardized and popularized the Gurmukhi script, compiled the first biographical records of Guru Nanak Dev Ji, established Mall Akhara (wrestling grounds for youth physical fitness), and expanded Langar institutional management with Mata Khivi Ji.",
    },
    {
        "order": 3,
        "name": "Guru Amar Das Ji",
        "gurmukhi": "ਗੁਰੂ ਅਮਰਦਾਸ ਜੀ",
        "dates": "1479 – 1574",
        "gaddi": "1552 – 1574",
        "sacred_cities": ["Goindval Sahib"],
        "major_compositions": ["Anand Sahib"],
        "contributions": "Constructed Baoli Sahib at Goindval (84 steps symbolizing freedom from 84 lakh life cycles), established the Manji System (22 administrative preaching centers led by men and women alike), strictly forbade Sati (widow immolation) and Purdah (face veils), institutionalized 'Pehle Pangat, Phir Sangat' (eat together in equality before congregating).",
    },
    {
        "order": 4,
        "name": "Guru Ram Das Ji",
        "gurmukhi": "ਗੁਰੂ ਰਾਮਦਾਸ ਜੀ",
        "dates": "1534 – 1581",
        "original_name": "Bhai Jetha Ji",
        "gaddi": "1574 – 1581",
        "sacred_cities": ["Amritsar (Guru Ka Chakk / Ramdaspur)"],
        "major_compositions": ["Lavan (The four hymns of the Anand Karaj marriage ceremony)", "Gauri Bavan Akhari"],
        "contributions": "Founded the holy city of Amritsar (Ramdaspur), excavated the sacred Sarovar (Pool of Nectar), initiated the architectural plan for Sri Harmandir Sahib, and composed the Lavan hymns uniting souls in spiritual partnership with Akal Purakh.",
    },
    {
        "order": 5,
        "name": "Guru Arjan Dev Ji",
        "gurmukhi": "ਗੁਰੂ ਅਰਜਨ ਦੇਵ ਜੀ",
        "dates": "1563 – 1606",
        "gaddi": "1581 – 1606",
        "sacred_cities": ["Amritsar", "Tarn Taran Sahib", "Kartarpur (Jalandhar)", "Sri Hargobindpur"],
        "major_compositions": ["Sukhmani Sahib", "Bavan Akhari", "Chaubole", "Barah Maha"],
        "contributions": "Compiled the Adi Granth in 1604 and installed it at Sri Harmandir Sahib with Baba Buddha Ji as the first Granthi. Built Sri Harmandir Sahib with 4 doors open to all four castes and all directions. First Sikh Guru to embrace martyrdom (Shaheedi in Lahore under Emperor Jahangir on burning sand and boiling water), standing as an eternal pillar of peaceful defiance against religious tyranny.",
    },
    {
        "order": 6,
        "name": "Guru Hargobind Ji",
        "gurmukhi": "ਗੁਰੂ ਹਰਿਗੋਬਿੰਦ ਜੀ",
        "dates": "1595 – 1644",
        "gaddi": "1606 – 1644",
        "sacred_cities": ["Amritsar", "Kiratpur Sahib"],
        "contributions": "Introduced the revolutionary doctrine of Miri & Piri (two swords representing temporal sovereignty and spiritual authority). Founded Sri Akal Takht Sahib (Throne of the Timeless One) in 1606 opposite Harmandir Sahib. Transformed Sikhs into Saint-Soldiers (Sant-Sipahi), established horse cavalry, and freed 52 Hindu kings from Gwalior Fort (celebrated as Bandi Chhor Divas).",
    },
    {
        "order": 7,
        "name": "Guru Har Rai Ji",
        "gurmukhi": "ਗੁਰੂ ਹਰਿਰਾਇ ਜੀ",
        "dates": "1630 – 1661",
        "gaddi": "1644 – 1661",
        "sacred_cities": ["Kiratpur Sahib"],
        "contributions": "Maintained a disciplined cavalry of 2,200 horsemen without ever initiating an offensive war. Established a renowned hospital and free herbal medicine dispensary at Kiratpur Sahib that healed Prince Dara Shikoh. Embodied deep compassion for all sentient beings, nature, and animals.",
    },
    {
        "order": 8,
        "name": "Guru Har Krishan Ji",
        "gurmukhi": "ਗੁਰੂ ਹਰਿਕ੍ਰਿਸ਼ਨ ਜੀ",
        "dates": "1656 – 1664",
        "gaddi": "1661 – 1664",
        "sacred_cities": ["Kiratpur Sahib", "Delhi (Gurdwara Bangla Sahib)"],
        "contributions": "Known affectionately as 'Bal Guru' (Child Guru, ascending at age 5). Traveled to Delhi during a devastating smallpox and cholera epidemic, personally nursing afflicted citizens regardless of religion at Raja Jai Singh's bungalow (now Gurdwara Bangla Sahib), sanctifying its water and taking on suffering with unbounded love.",
    },
    {
        "order": 9,
        "name": "Guru Tegh Bahadur Ji",
        "gurmukhi": "ਗੁਰੂ ਤੇਗ ਬਹਾਦਰ ਜੀ",
        "dates": "1621 – 1675",
        "gaddi": "1664 – 1675",
        "sacred_cities": ["Anandpur Sahib (Chakk Nanaki)", "Baba Bakala"],
        "major_compositions": ["Salok Mahalla 9 (57 Saloks in SGGS)", "59 Shabads across 15 Ragas"],
        "contributions": "Revered as 'Hind Di Chadar' (Shield of Humanity). Founded Anandpur Sahib. When Kashmiri Pandits led by Pandit Kirpa Ram pleaded for salvation from forced religious conversion under Emperor Aurangzeb, Guru Sahib willingly laid down his life at Chandni Chowk, Delhi (Gurdwara Sis Ganj Sahib) to defend universal freedom of conscience for another faith.",
    },
    {
        "order": 10,
        "name": "Guru Gobind Singh Ji",
        "gurmukhi": "ਗੁਰੂ ਗੋਬਿੰਦ ਸਿੰਘ ਜੀ",
        "dates": "1666 – 1708",
        "birthplace": "Patna Sahib (Bihar)",
        "gaddi": "1675 – 1708",
        "sacred_cities": ["Anandpur Sahib", "Paonta Sahib", "Talwandi Sabo (Damdama Sahib)", "Nanded (Hazur Sahib)"],
        "major_compositions": ["Jaap Sahib", "Tav-Prasad Savaiye", "Chaupai Sahib", "Zafarnama", "Chandi Di Var", "Akal Ustat"],
        "contributions": "Created the Khalsa Panth on Vaisakhi 1699 at Anandpur Sahib through Khande Di Pahul (Amrit Sanchar), bestowing the identity of Panj Kakars and the titles of Singh (Lion) and Kaur (Princess). Authored the historic Persian letter Zafarnama ('Epistle of Victory') to Aurangzeb. Bestowed eternal, Guruship upon Sri Guru Granth Sahib Ji at Nanded in 1708, ending the human lineage.",
    },
    {
        "order": 11,
        "name": "Sri Guru Granth Sahib Ji",
        "gurmukhi": "ਸ੍ਰੀ ਗੁਰੂ ਗ੍ਰੰਥ ਸਾਹਿਬ ਜੀ",
        "dates": "Eternal Living Guru (Consecrated 1708 at Hazur Sahib)",
        "structure": "1,430 Angs (pages), 31 Classical Indian Ragas, 5,894 Shabads",
        "contributors": "Compositions of 6 Sikh Gurus (Guru Nanak, Angad, Amar Das, Ram Das, Arjan, and Tegh Bahadur Ji), 15 Bhagats (including Bhagat Kabir, Ravidas, Farid, Namdev, Trilochan, Jaidev, Ramanand), 11 Bhatts, and 4 Gursikhs.",
        "key_teachings": "The eternal Shabad Guru; embodies universal egalitarianism, rejecting religious boundaries, caste, and dogma; guides all human souls toward inner illumination and oneness with Akal Purakh.",
    }
]

CHAAR_SAHIBZADE = {
    "title": "Chaar Sahibzade (The Four Princely Sons of Guru Gobind Singh Ji)",
    "summary": "Sacrificed their lives during the tragic week of Poh in December 1704 for the protection of righteousness (Dharma) and the freedom of the human spirit.",
    "vadde_sahibzade": [
        {
            "name": "Baba Ajit Singh Ji",
            "age": 18,
            "battle": "Battle of Chamkaur Sahib (December 1704)",
            "details": "Eldest son of Guru Gobind Singh Ji. Led small bands of Sikhs in fierce sorties against massive Mughal and allied hill armies. Fought with superhuman bravery until attaining martyrdom on the battlefield."
        },
        {
            "name": "Baba Jujhar Singh Ji",
            "age": 14,
            "battle": "Battle of Chamkaur Sahib (December 1704)",
            "details": "Second son of Guru Gobind Singh Ji. Witnessing his elder brother's valor, he asked his father's permission to fight. Guru Sahib lovingly armed him. At age 14, he charged fearlessly into battle and attained martyrdom."
        }
    ],
    "chhote_sahibzade": [
        {
            "name": "Baba Zorawar Singh Ji",
            "age": 9,
            "location": "Fatehgarh Sahib, Sirhind (December 1704)",
            "details": "Third son. Separated from the Guru at the River Sarsa with their grandmother Mata Gujri Ji. Betrayed by Gangu, they were imprisoned in the freezing Cold Tower (Thanda Burj). Offered kingdoms and wealth to renounce their faith by Nawab Wazir Khan, he resolutely proclaimed: 'We will die for our faith and dignity, but never bow to tyranny!'"
        },
        {
            "name": "Baba Fateh Singh Ji",
            "age": 7,
            "location": "Fatehgarh Sahib, Sirhind (December 1704)",
            "details": "Youngest son. At merely 7 years of age, stood unshakable alongside Baba Zorawar Singh Ji. Both princes were bricked alive in a masonry wall by order of Wazir Khan. When the wall collapsed, they were martyred on 13 Poh (December 1704). Mata Gujri Ji breathed her last upon hearing the news."
        }
    ]
}

PANJ_PYARE = [
    {
        "name": "Bhai Daya Singh Ji",
        "pre_khalsa_name": "Daya Ram",
        "origin": "Lahore (Punjab)",
        "occupation": "Shopkeeper / Khatri",
        "significance": "First to step forward at Anandpur Sahib when Guru Gobind Singh Ji asked for a head in 1699. Embodying compassion (Daya)."
    },
    {
        "name": "Bhai Dharam Singh Ji",
        "pre_khalsa_name": "Dharam Das",
        "origin": "Hastinapur / Meerut (Uttar Pradesh)",
        "occupation": "Farmer / Jat",
        "significance": "Second to offer his head, embodying righteousness and moral duty (Dharam)."
    },
    {
        "name": "Bhai Himmat Singh Ji",
        "pre_khalsa_name": "Himmat Rai",
        "origin": "Jagannath Puri (Odisha)",
        "occupation": "Water-carrier / Jhiwar",
        "significance": "Third to offer his head, embodying courage and strength (Himmat)."
    },
    {
        "name": "Bhai Mohkam Singh Ji",
        "pre_khalsa_name": "Mohkam Chand",
        "origin": "Dwarka (Gujarat)",
        "occupation": "Tailor / Calico Printer (Chhimba)",
        "significance": "Fourth to offer his head, embodying determination and resilience (Mohkam)."
    },
    {
        "name": "Bhai Sahib Singh Ji",
        "pre_khalsa_name": "Sahib Chand",
        "origin": "Bidar (Karnataka)",
        "occupation": "Barber (Nai)",
        "significance": "Fifth to offer his head, embodying mastery, dignity, and sovereignty (Sahib)."
    }
]

FIVE_TAKHTS = [
    {
        "name": "Sri Akal Takht Sahib",
        "gurmukhi": "ਸ੍ਰੀ ਅਕਾਲ ਤਖ਼ਤ ਸਾਹਿਬ",
        "location": "Amritsar, Punjab",
        "founder": "Guru Hargobind Ji (1606)",
        "significance": "The Throne of the Timeless One; supreme temporal seat of spiritual authority for the worldwide Sikh Panth, facing Sri Harmandir Sahib."
    },
    {
        "name": "Takht Sri Keshgarh Sahib",
        "gurmukhi": "ਤਖ਼ਤ ਸ੍ਰੀ ਕੇਸਗੜ੍ਹ ਸਾਹਿਬ",
        "location": "Anandpur Sahib, Punjab",
        "founder": "Guru Gobind Singh Ji (1699)",
        "significance": "Birthplace of the Khalsa; where Khande Di Pahul (Amrit Sanchar) was first administered to the Panj Pyare on Vaisakhi 1699."
    },
    {
        "name": "Takht Sri Damdama Sahib",
        "gurmukhi": "ਤਖ਼ਤ ਸ੍ਰੀ ਦਮਦਮਾ ਸਾਹਿਬ",
        "location": "Talwandi Sabo, Bathinda, Punjab",
        "founder": "Guru Gobind Singh Ji (1705)",
        "significance": "Guru Ki Kashi; place where Guru Gobind Singh Ji recited and dictated the complete Sri Guru Granth Sahib Ji from memory to Bhai Mani Singh Ji, adding the Saloks of Guru Tegh Bahadur Ji."
    },
    {
        "name": "Takht Sri Patna Sahib",
        "gurmukhi": "ਤਖ਼ਤ ਸ੍ਰੀ ਪਟਨਾ ਸਾਹਿਬ",
        "location": "Patna, Bihar",
        "founder": "Commemorating Birthplace of Guru Gobind Singh Ji (1666)",
        "significance": "Birthplace and childhood home of Guru Gobind Singh Ji on the banks of the Ganges."
    },
    {
        "name": "Takht Sri Hazur Sahib",
        "gurmukhi": "ਤਖ਼ਤ ਸ੍ਰੀ ਹਜ਼ੂਰ ਸਾਹਿਬ",
        "location": "Nanded, Maharashtra",
        "founder": "Guru Gobind Singh Ji (1708)",
        "significance": "Sachkhand; place where Guru Gobind Singh Ji spent his final earthly days on the banks of Godavari, bestowing eternal Guruship upon Sri Guru Granth Sahib Ji."
    }
]

MOOL_MANTAR_DETAILS = {
    "gurmukhi": "ੴ ਸਤਿ ਨਾਮੁ ਕਰਤਾ ਪੁਰਖੁ ਨਿਰਭਉ ਨਿਰਵੈਰੁ ਅਕਾਲ ਮੂਰਤਿ ਅਜੂਨੀ ਸੈਭੰ ਗੁਰ ਪ੍ਰਸਾਦਿ ॥",
    "transliteration": "Ik Oankaar Sat Naam Kartaa Purakh Nirbhau Nirvair Akaal Moorat Ajoonee Saibhang Gur Parsaad.",
    "breakdown": [
        {"word": "ੴ (Ik Oankaar)", "meaning": "One Supreme Reality, indivisible, all-pervading and transcendent."},
        {"word": "ਸਤਿ ਨਾਮੁ (Sat Naam)", "meaning": "Truth is Its eternal identity and existence."},
        {"word": "ਕਰਤਾ ਪੁਰਖੁ (Kartaa Purakh)", "meaning": "The Creative Being, the omnipotent architect of the entire cosmos."},
        {"word": "ਨਿਰਭਉ (Nirbhau)", "meaning": "Without fear; free from anxiety and subjugation."},
        {"word": "ਨਿਰਵੈਰੁ (Nirvair)", "meaning": "Without enmity or hatred; holding universal love for all."},
        {"word": "ਅਕਾਲ ਮੂਰਤਿ (Akaal Moorat)", "meaning": "Timeless, beyond birth, decay, and physical mortality."},
        {"word": "ਅਜੂਨੀ (Ajoonee)", "meaning": "Beyond incarnations, womb, or reincarnation cycles."},
        {"word": "ਸੈਭੰ (Saibhang)", "meaning": "Self-existent, self-illuminated, created by none."},
        {"word": "ਗੁਰ ਪ੍ਰਸਾਦਿ (Gur Parsaad)", "meaning": "Realized and attained through the Grace of the True Guru."}
    ],
    "explanation": "The Mool Mantar is the opening root verse of Sri Guru Granth Sahib Ji, encapsulating the entire theological framework of Sikh monotheism: God is non-dual, truthful, benevolent, fearless, timeless, and accessible via divine grace."
}

FIVE_KS = [
    {"kakar": "Kesh (ਕੇਸ)", "desc": "Uncut hair — accepting the natural gift and form of the Creator, symbolizing spiritual surrender, discipline, and saintliness."},
    {"kakar": "Kangha (ਕੰਘਾ)", "desc": "Wooden comb — worn in the hair, symbolizing cleanliness, order, and disciplined grooming of both mind and body."},
    {"kakar": "Kara (ਕੜਾ)", "desc": "Steel/iron bangle — worn on the dominant wrist, reminding the wearer of eternal connection to Akal Purakh and moral restraint in every deed."},
    {"kakar": "Kachera (ਕਛਹਿਰਾ)", "desc": "Cotton undergarment — symbolizing modesty, self-control, marital fidelity, and readiness for righteous agility."},
    {"kakar": "Kirpan (ਕਿਰਪਾਨ)", "desc": "Ceremonial sword/dagger — emblem of spiritual sovereignty, grace (Kirpa) and honor (Aan); carried solely for defending the weak and upholding justice."}
]

CONTEMPLATION_VERSES = [
    {
        "gurmukhi": "ਜਿਨ੍ਹ੍ਹ ਪ੍ਰੇਮ ਕੀਓ ਤਿਨ੍ਹ੍ਹ ਹੀ ਪ੍ਰਭੁ ਪਾਇਓ ॥",
        "transliteration": "Jin prem kiyo tin hee prabh paayo.",
        "author": "Guru Gobind Singh Ji (Tav-Prasad Savaiye)",
        "meaning": "Only those who are drenched in pure, unconditional love truly realize the Divine Lord.",
        "reflection": "Rituals and scholarly theories hold no weight without genuine compassion in one's heart."
    },
    {
        "gurmukhi": "ਮਨ ਤੂੰ ਜੋਤਿ ਸਰੂਪੁ ਹੈ ਆਪਣਾ ਮੂਲੁ ਪਛਾਣੁ ॥",
        "transliteration": "Man toon jot saroop hai aapna mool pachhaan.",
        "author": "Guru Amar Das Ji (SGGS Ang 441)",
        "meaning": "O my mind, you are the very embodiment of Divine Light; recognize your true origin!",
        "reflection": "You are not limited by anxiety or circumstance; your inner consciousness is eternal light."
    },
    {
        "gurmukhi": "ਸਰਬੱਤ ਦਾ ਭਲਾ ॥",
        "transliteration": "Sarbat Da Bhala.",
        "author": "Daily Ardas Principle",
        "meaning": "May prosperity, peace, and well-being bless all of creation and humanity.",
        "reflection": "Universal benevolence: a Sikh never prays solely for oneself, but asks for upliftment of everyone."
    },
    {
        "gurmukhi": "ਸਚਹੁ ਓਰੈ ਸਭੁ ਕੋ ਉਪਰਿ ਸਚੁ ਆਚਾਰੁ ॥",
        "transliteration": "Sachahu orai sabh ko upar sach aachaar.",
        "author": "Guru Nanak Dev Ji (SGGS Ang 62)",
        "meaning": "Truth is the highest virtue, but higher still is truthful, honest living.",
        "reflection": "Spiritual wisdom is proven not by speech, but by how honorably we treat others in daily action."
    },
    {
        "gurmukhi": "ਨਾਨਕ ਨਾਮ ਚੜ੍ਹਦੀ ਕਲਾ ਤੇਰੇ ਭਾਣੇ ਸਰਬੱਤ ਦਾ ਭਲਾ ॥",
        "transliteration": "Nanak Naam Chardi Kala, Tere Bhaane Sarbat Da Bhala.",
        "author": "Concluding Verse of Ardas",
        "meaning": "Nanak prays for the Divine Name, for ever-rising high spirits (Chardi Kala), and by Your Will, peace and prosperity for all.",
        "reflection": "Chardi Kala is relentless optimism and courage, maintaining joy even amidst tribulations."
    }
]


# =========================================================================
# 🔊 AUDIO DISPATCHER & PLAYBACK IMPLEMENTATION
# =========================================================================

def find_local_baani_audio(baani_key: str, force_rescan: bool = False) -> Optional[Dict[str, Any]]:
    """
    Searches C:\\Users\\User\\Music and C:\\Users\\User\\Music\\Nitnem for an existing
    recording of the requested Baani.
    """
    baani_info = NITNEM_BAANIS.get(baani_key)
    if not baani_info:
        return None

    import local_music_engine
    tracks = local_music_engine.scan_local_music(max_results=2000, force_rescan=force_rescan)
    if not tracks and not force_rescan:
        tracks = local_music_engine.scan_local_music(max_results=2000, force_rescan=True)

    keys = [k.lower() for k in baani_info["search_keys"]]

    # 1. Look specifically in Nitnem subfolder first
    for t in tracks:
        p_low = t["path"].lower()
        if "nitnem" in p_low:
            if any(k in p_low for k in keys):
                return t

    # 2. Exact Baani keyword match across whole music library
    for t in tracks:
        p_low = t["path"].lower()
        t_low = t["title"].lower()
        f_low = t["filename"].lower()
        if any(k in p_low or k in t_low or k in f_low for k in keys):
            return t

    # 3. For morning Nitnem banis (Japji, Jaap, Savaiye, Chaupai, Anand), check if complete Nitnem or Five Bania audio is present
    if baani_key in ("japji_sahib", "jaap_sahib", "tav_prasad_savaiye", "chaupai_sahib", "anand_sahib"):
        for t in tracks:
            combined = (t["path"] + " " + t["title"] + " " + t["filename"]).lower()
            if ("five bania" in combined or "panj bania" in combined or "nitnem full" in combined or "morning nitnem" in combined) and "queen" not in combined:
                return t

    return None


def play_gurbani_audio(query: str) -> Dict[str, Any]:
    """
    Core Gurbani Audio Recitation Dispatcher:
    - Resolves requested Baani.
    - Searches C:\\Users\\User\\Music & C:\\Users\\User\\Music\\Nitnem.
    - If found, launches on PC Speakers immediately.
    - If missing, downloads via yt-dlp to C:\\Users\\User\\Music\\Nitnem and plays on PC Speakers.
    - Zero browser opening, 100% offline-ready.
    """
    import local_music_engine

    q_low = query.lower().strip()
    matched_key = None

    # Detect requested Baani
    for key, info in NITNEM_BAANIS.items():
        for sk in info["search_keys"]:
            if sk in q_low:
                matched_key = key
                break
        if matched_key:
            break

    # Default fallback to Japji Sahib if generic "nitnem" or "gurbani" requested
    if not matched_key:
        if "nitnem" in q_low or "morning prayer" in q_low:
            matched_key = "japji_sahib"
        elif "evening" in q_low:
            matched_key = "rehras_sahib"
        elif "night" in q_low or "bedtime" in q_low or "sleep" in q_low:
            matched_key = "kirtan_sohila"
        else:
            matched_key = "japji_sahib"

    baani = NITNEM_BAANIS[matched_key]

    # 1. Search local audio
    local_track = find_local_baani_audio(matched_key)
    if local_track:
        res = local_music_engine.play_track(local_track["path"])
        return {
            "status": "success",
            "source": "local",
            "baani": baani,
            "filename": local_track["filename"],
            "path": local_track["path"],
            "message": f"ੴ Playing {baani['title']} ({baani['gurmukhi']}) from your local library on PC Speakers.",
            "details": f"**{baani['title']}** by {baani['author']}\n*Time:* {baani['timing']}\n*Theme:* {baani['theme']}"
        }

    # 2. Not found locally: Auto-download via yt-dlp directly to ~/Music/Nitnem
    print(f"[GurbaniEngine] '{baani['title']}' not found in local library. Downloading authentic audio once...")
    download_query = f"{baani['title']} Nitnem Full Path Audio"
    try:
        # We invoke download_and_play_track from local_music_engine
        dl_res = local_music_engine.download_and_play_track(download_query)
        if dl_res.get("status") == "success":
            return {
                "status": "success",
                "source": "downloaded",
                "baani": baani,
                "filename": dl_res.get("filename", baani["title"]),
                "path": dl_res.get("path", ""),
                "message": f"ੴ Downloaded & Playing {baani['title']} ({baani['gurmukhi']}) on PC Speakers.",
                "details": f"**{baani['title']}** by {baani['author']}\n*Time:* {baani['timing']}\n*Theme:* {baani['theme']}\n*Saved permanently to your local Music library.*"
            }
        else:
            return {
                "status": "error",
                "baani": baani,
                "message": f"Could not stream or download {baani['title']}: {dl_res.get('message')}"
            }
    except Exception as e:
        return {
            "status": "error",
            "baani": baani,
            "message": f"Playback dispatch error: {e}"
        }


# =========================================================================
# 📖 SIKH HERITAGE OFFLINE QUERY ENGINE
# =========================================================================

def search_heritage_knowledge(query: str) -> Optional[Dict[str, Any]]:
    """
    Answers questions about Sikh history, the 10 Gurus, Chaar Sahibzade,
    Panj Pyare, 5 Takhts, Mool Mantar, or Baanis using 100% offline local knowledge.
    """
    q_low = query.lower().strip()

    # 1. Check for Mool Mantar request
    if any(k in q_low for k in ["mool mantar", "mool mantra", "ik onkar", "ikonkar", "ek onkar"]):
        return {
            "category": "scripture",
            "title": "ੴ Mool Mantar (The Root Divine Credo)",
            "data": MOOL_MANTAR_DETAILS,
            "formatted_text": (
                f"### ੴ Mool Mantar (ਸ੍ਰੀ ਮੂਲ ਮੰਤਰ)\n\n"
                f"**Gurmukhi:**\n> {MOOL_MANTAR_DETAILS['gurmukhi']}\n\n"
                f"**Roman Transliteration:**\n*{MOOL_MANTAR_DETAILS['transliteration']}*\n\n"
                f"**Core Breakdown:**\n" +
                "\n".join([f"- **{item['word']}**: {item['meaning']}" for item in MOOL_MANTAR_DETAILS['breakdown']]) +
                f"\n\n**Significance:** {MOOL_MANTAR_DETAILS['explanation']}"
            )
        }

    # 2. Check for Chaar Sahibzade request
    if any(k in q_low for k in ["sahibzade", "sahibzada", "chaar sahibzade", "char sahibzade", "ajit singh", "jujhar singh", "zorawar singh", "fateh singh"]):
        return {
            "category": "history",
            "title": "Chaar Sahibzade (Four Sons of Guru Gobind Singh Ji)",
            "data": CHAAR_SAHIBZADE,
            "formatted_text": (
                f"### ⚔️ Chaar Sahibzade (ਸਾਹਿਬਜ਼ਾਦੇ) & Mata Gujri Ji\n\n"
                f"{CHAAR_SAHIBZADE['summary']}\n\n"
                f"#### Vadde Sahibzade (Battle of Chamkaur Sahib - 1704):\n"
                f"- **Baba Ajit Singh Ji (18 yrs)**: Eldest son. Fought valiantly against massive odds, attaining martyrdom defending righteousness.\n"
                f"- **Baba Jujhar Singh Ji (14 yrs)**: Second son. Asked his father for permission to battle, martyred heroically on the Chamkaur plains.\n\n"
                f"#### Chhote Sahibzade (Fatehgarh Sahib, Sirhind - 1704):\n"
                f"- **Baba Zorawar Singh Ji (9 yrs)** & **Baba Fateh Singh Ji (7 yrs)**: Kept steadfast in the Cold Tower (Thanda Burj) with grandmother Mata Gujri Ji. Refused to surrender their conscience or faith to Nawab Wazir Khan, and were bricked alive with divine dignity."
            )
        }

    # 3. Check for Panj Pyare request
    if any(k in q_low for k in ["panj pyare", "five beloved", "panj piaray", "panj pyara"]):
        txt = "### ⚔️ Panj Pyare (The Five Beloved Ones - Vaisakhi 1699)\n\n"
        txt += "Created by Guru Gobind Singh Ji at Anandpur Sahib through Khande Di Pahul:\n\n"
        for p in PANJ_PYARE:
            txt += f"- **{p['name']}** (Formerly *{p['pre_khalsa_name']}* from {p['origin']}, {p['occupation']}) — {p['significance']}\n"
        return {
            "category": "history",
            "title": "Panj Pyare (The Five Beloved Ones)",
            "data": PANJ_PYARE,
            "formatted_text": txt
        }

    # 4. Check for Five Takhts request
    if any(k in q_low for k in ["takht", "takhat", "five takhts", "panj takht", "akal takht"]):
        txt = "### 🏛️ The Five Takhts (Supreme Seats of Sikh Temporal Authority)\n\n"
        for t in FIVE_TAKHTS:
            txt += f"- **{t['name']}** ({t['gurmukhi']}) — *{t['location']}*\n  Founded/Associated: {t['founder']}\n  *{t['significance']}*\n\n"
        return {
            "category": "institutions",
            "title": "The Five Takhts",
            "data": FIVE_TAKHTS,
            "formatted_text": txt.strip()
        }

    # 5. Check for Five Ks (Kakars)
    if any(k in q_low for k in ["five ks", "5 ks", "kakars", "kakkars", "kesh", "kangha", "kara", "kachera", "kirpan"]):
        txt = "### ⚔️ The Five Ks (ਪੰਜ ਕਕਾਰ) — Sacred Uniform of the Khalsa\n\n"
        for k in FIVE_KS:
            txt += f"- **{k['kakar']}**: {k['desc']}\n"
        return {
            "category": "philosophy",
            "title": "The Five Ks of the Khalsa",
            "data": FIVE_KS,
            "formatted_text": txt.strip()
        }

    # 6. Check for Three Pillars request
    if any(k in q_low for k in ["three pillars", "3 pillars", "naam japna", "kirat karo", "vand chhako"]):
        txt = (
            "### ੴ The Three Pillars of Sikhism (Guru Nanak Dev Ji)\n\n"
            "1. **ਨਾਮ ਜਪੋ (Naam Japna)**: Mindful remembrance and meditation upon Akal Purakh's Name, maintaining spiritual purity.\n"
            "2. **ਕਿਰਤ ਕਰੋ (Kirat Karo)**: Earning an honest, truthful living through hard labor without deceit, exploitation, or laziness.\n"
            "3. **ਵੰਡ ਛਕੋ (Vand Chhako)**: Selflessly sharing one's food, wealth, and blessings with the less fortunate and the community."
        )
        return {
            "category": "philosophy",
            "title": "Three Pillars of Sikhism",
            "formatted_text": txt
        }

    # 7. Check for specific Guru Sahiban
    for g in GURU_SAHIBAN:
        g_name_low = g["name"].lower()
        order_str = f"guru {g['order']}"
        if g_name_low in q_low or order_str in q_low or (g.get("original_name") and g["original_name"].lower() in q_low):
            txt = f"### ੴ {g['name']} ({g['gurmukhi']})\n\n"
            txt += f"- **Period:** {g['dates']} | **Guruship:** {g['gaddi']}\n"
            if g.get("birthplace"):
                txt += f"- **Birthplace:** {g['birthplace']}\n"
            if g.get("sacred_cities"):
                txt += f"- **Key Cities:** {', '.join(g['sacred_cities'])}\n"
            if g.get("major_compositions"):
                txt += f"- **Major Compositions:** {', '.join(g['major_compositions'])}\n"
            txt += f"\n**Historical Milestones & Teachings:**\n{g.get('contributions') or g.get('key_teachings', '')}"
            return {
                "category": "gurus",
                "title": g["name"],
                "data": g,
                "formatted_text": txt
            }

    # 8. Check for specific Baani description
    for key, b in NITNEM_BAANIS.items():
        if any(sk in q_low for sk in b["search_keys"]):
            txt = (
                f"### ੴ {b['title']} ({b['gurmukhi']})\n\n"
                f"- **Author:** {b['author']}\n"
                f"- **Recitation Time:** {b['timing']}\n"
                f"- **Source:** {b['source']}\n"
                f"- **Structure:** {b['structure']}\n\n"
                f"**Theme & Significance:**\n{b['theme']}\n\n"
                f"**Opening Verse:**\n> {b['opening_verse']}"
            )
            return {
                "category": "baani",
                "title": b["title"],
                "data": b,
                "formatted_text": txt
            }

    return None


def get_daily_contemplation() -> Dict[str, Any]:
    """Returns today's contemplation verse based on day of year."""
    import datetime
    day_of_year = datetime.datetime.now().timetuple().tm_yday
    verse = CONTEMPLATION_VERSES[day_of_year % len(CONTEMPLATION_VERSES)]
    return verse
