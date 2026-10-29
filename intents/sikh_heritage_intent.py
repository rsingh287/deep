"""
ੴ Local Sikh Heritage & Gurbani Modular Intent
Part of Antigravity Local AI PC Cockpit (100% Offline)
"""

import re
from .base_intent import BaseIntent
import sikh_heritage_engine

class SikhHeritageIntent(BaseIntent):
    BAANI_TRIGGERS = [
        "japji", "japu", "jaap sahib", "chaupai", "anand sahib", "rehras",
        "rehraas", "kirtan sohila", "sohila", "sukhmani", "asa di var", "asa ki var",
        "dukh bhanjani", "ardas", "ardaas", "nitnem", "gurbani", "baani"
    ]

    HERITAGE_TRIGGERS = [
        "mool mantar", "mool mantra", "ik onkar", "ikonkar", "ek onkar",
        "sahibzade", "sahibzada", "chaar sahibzade", "panj pyare", "five beloved",
        "five takhts", "panj takht", "akal takht", "five ks", "kakars", "kakkars",
        "three pillars", "naam japna", "kirat karo", "vand chhako",
        "guru nanak", "guru angad", "guru amar das", "guru ram das", "guru arjan",
        "guru hargobind", "guru har rai", "guru har krishan", "guru tegh bahadur",
        "guru gobind singh", "guru granth sahib", "sikh heritage", "sikh history",
        "sikhism"
    ]

    PLAY_KEYWORDS = ["play", "listen", "start", "recite", "chant", "stream", "hear"]

    @classmethod
    def can_handle(cls, norm_prompt: str) -> bool:
        # Check if query matches any Baani
        has_baani = any(b in norm_prompt for b in cls.BAANI_TRIGGERS)
        if has_baani:
            return True

        # Check if query matches heritage keywords
        has_heritage = any(h in norm_prompt for h in cls.HERITAGE_TRIGGERS)
        if has_heritage:
            return True

        return False

    @classmethod
    def execute(cls, user_prompt: str, norm_prompt: str):
        try:
            # 1. Check if user wants audio playback (e.g., "play japji sahib", "listen to rehras", "play nitnem")
            is_play = any(w in norm_prompt for w in cls.PLAY_KEYWORDS) or any(
                norm_prompt.strip() == b or norm_prompt.strip() == f"{b} sahib"
                for b in ["japji", "jaap", "chaupai", "rehras", "sohila", "sukhmani", "nitnem"]
            )

            if is_play and any(b in norm_prompt for b in cls.BAANI_TRIGGERS):
                res = sikh_heritage_engine.play_gurbani_audio(user_prompt)
                if res.get("status") == "success":
                    baani = res["baani"]
                    msg = (
                        f"ੴ **{baani['title']} ({baani['gurmukhi']})**\n\n"
                        f"{res['message']}\n\n"
                        f"**Sacred Details:**\n"
                        f"- **Author:** {baani['author']}\n"
                        f"- **Timing:** {baani['timing']}\n"
                        f"- **Theme:** {baani['theme']}\n\n"
                        f"*{res.get('details', '')}*"
                    )
                    return (
                        msg,
                        "autonomous_gurbani_playback",
                        [
                            {
                                "language": "python",
                                "code": f"sikh_heritage_engine.play_gurbani_audio('{baani['title']}')",
                                "output": f"Playing on PC Speakers: {res.get('filename')}",
                            }
                        ],
                    )
                else:
                    return (
                        f"ੴ Notice: {res.get('message', 'Could not play audio.')}",
                        "autonomous_gurbani_playback",
                        [],
                    )

            # 2. Check offline heritage knowledge
            res = sikh_heritage_engine.search_heritage_knowledge(user_prompt)
            if res:
                return (
                    res["formatted_text"],
                    "autonomous_sikh_heritage_knowledge",
                    [
                        {
                            "language": "markdown",
                            "code": f"lookup_sikh_heritage(category='{res.get('category')}', title='{res.get('title')}')",
                            "output": "100% Offline Local Sikh Heritage Knowledge Retrieved",
                        }
                    ],
                )

            # 3. Fallback to daily contemplation if mentioning Gurbani or Sikh contemplation
            if any(w in norm_prompt for w in ["contemplation", "hukamnama", "verse", "quote"]):
                v = sikh_heritage_engine.get_daily_contemplation()
                txt = (
                    f"### ੴ Daily Gurbani Contemplation\n\n"
                    f"**Gurmukhi:**\n> {v['gurmukhi']}\n\n"
                    f"**Transliteration:**\n*{v['transliteration']}*\n\n"
                    f"**Author:** {v['author']}\n\n"
                    f"**Meaning:**\n{v['meaning']}\n\n"
                    f"**Spiritual Reflection:**\n{v['reflection']}"
                )
                return (
                    txt,
                    "autonomous_sikh_heritage_contemplation",
                    [{"language": "markdown", "code": "daily_contemplation()", "output": "Retrieved"}],
                )
        except Exception as e:
            print(f"[SikhHeritageIntent] Error: {e}")
            return (f"ੴ **Sikh Heritage Error:** {e}", "sikh_heritage_error", [])

        return None
