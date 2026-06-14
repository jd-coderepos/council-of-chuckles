# utils/banner.py

HERO_HTML = """
<header class="hero">
<div class="wrap hero-grid">
    <div>
    <span class="brand"><span class="brand-mark"></span>Council of Chuckles</span>
    <h1>Small Models. Big Chuckles.</h1>
    <p class="subtitle">Speak a question, assemble a tiny council, and get practical wisdom with a wink.</p>
    <div class="badges">
        <span class="badge">Voice-forward</span>
        <span class="badge">14 spoken languages</span>
        <span class="badge">70+ reply languages</span>
        <span class="badge">Tiny Aya Water</span>
        <span class="badge">Council Engine</span>
    </div>
    </div>
    <div class="hero-art" aria-hidden="true">
    <div class="spark"></div>
    <div class="thinker-sticker socrates">

        <svg viewBox="0 0 120 140" role="img" aria-label="">
        <circle cx="60" cy="60" r="54" fill="#5a3619" stroke="#2f1a08" stroke-width="5"/>
        <circle cx="60" cy="60" r="45" fill="none" stroke="#ffeebd" stroke-width="2" stroke-dasharray="5 6" opacity=".68"/>
        <circle cx="60" cy="64" r="32" fill="#ffd64d" stroke="#9d6616" stroke-width="3"/>
        <circle cx="48" cy="60" r="4" fill="#111"/>
        <circle cx="72" cy="60" r="4" fill="#111"/>

        <path d="M31 43 C38 20, 83 20, 90 43 C78 37, 42 37, 31 43Z" fill="#7b4a21"/>
        <path d="M31 42 C34 35, 39 30, 45 28 M48 27 C52 22, 59 20, 64 25 M68 27 C75 23, 83 30, 87 38" fill="none" stroke="#7b4a21" stroke-width="8" stroke-linecap="round"/>
        <path d="M35 77 C40 103, 80 103, 85 77 C78 90, 43 90, 35 77Z" fill="#8a5727" stroke="#6a3d18" stroke-width="2"/>
        <path d="M45 78 Q60 88 75 78" fill="none" stroke="#111" stroke-width="4" stroke-linecap="round"/>
        <path d="M34 31 Q60 16 86 31" fill="none" stroke="#86a840" stroke-width="5" stroke-linecap="round"/>
        <text x="60" y="22" text-anchor="middle" font-size="10" font-weight="900" fill="#ffeebd">ASK</text>
    
        </svg>
        <span class="thinker-label">Socrates</span>
    </div>
    <div class="thinker-sticker confucius">

        <svg viewBox="0 0 120 140" role="img" aria-label="">
        <circle cx="60" cy="60" r="54" fill="#5a3619" stroke="#2f1a08" stroke-width="5"/>
        <circle cx="60" cy="60" r="45" fill="none" stroke="#ffeebd" stroke-width="2" stroke-dasharray="5 6" opacity=".68"/>
        <circle cx="60" cy="64" r="32" fill="#ffd64d" stroke="#9d6616" stroke-width="3"/>
        <circle cx="48" cy="60" r="4" fill="#111"/>
        <circle cx="72" cy="60" r="4" fill="#111"/>

        <path d="M32 43 C38 24, 82 24, 88 43 L83 50 C71 43, 49 43, 37 50Z" fill="#4a2b19"/>
        <path d="M36 39 Q60 29 84 39" fill="none" stroke="#4a2b19" stroke-width="9" stroke-linecap="round"/>
        <path d="M39 74 C41 102, 79 102, 81 74 C71 88, 49 88, 39 74Z" fill="#f4efe5" stroke="#9d6616" stroke-width="2"/>
        <path d="M41 52 L52 48 M68 48 L79 52" stroke="#4a2b19" stroke-width="4" stroke-linecap="round"/>
        <path d="M48 78 Q60 86 72 78" fill="none" stroke="#111" stroke-width="4" stroke-linecap="round"/>
        <text x="60" y="22" text-anchor="middle" font-size="9" font-weight="900" fill="#ffeebd">ORDER</text>
    
        </svg>
        <span class="thinker-label">Confucius</span>
    </div>
    <div class="thinker-sticker feature">

        <svg viewBox="0 0 120 140" role="img" aria-label="">
        <circle cx="60" cy="60" r="54" fill="#5a3619" stroke="#2f1a08" stroke-width="5"/>
        <circle cx="60" cy="60" r="45" fill="none" stroke="#ffeebd" stroke-width="2" stroke-dasharray="5 6" opacity=".68"/>
        <circle cx="60" cy="64" r="32" fill="#ffd64d" stroke="#9d6616" stroke-width="3"/>
        <circle cx="48" cy="60" r="4" fill="#111"/>
        <circle cx="72" cy="60" r="4" fill="#111"/>

        <path d="M33 43 C39 23, 81 23, 87 43" fill="none" stroke="#fff4d7" stroke-width="13" stroke-linecap="round"/>
        <path d="M40 74 C42 106, 78 106, 80 74 C72 91, 48 91, 40 74Z" fill="#fff4d7" stroke="#9d6616" stroke-width="2"/>
        <path d="M39 51 L52 47 M68 47 L81 51" stroke="#fff4d7" stroke-width="5" stroke-linecap="round"/>
        <path d="M43 72 C50 66, 55 66, 60 72 C65 66, 70 66, 77 72" fill="none" stroke="#fff4d7" stroke-width="7" stroke-linecap="round"/>
        <path d="M48 82 Q60 90 72 82" fill="none" stroke="#111" stroke-width="4" stroke-linecap="round"/>
        <text x="60" y="22" text-anchor="middle" font-size="9" font-weight="900" fill="#ffeebd">FLOW</text>
    
        </svg>
        <span class="thinker-label">Lao Tzu</span>
    </div>
    <div class="thinker-sticker aristotle">

        <svg viewBox="0 0 120 140" role="img" aria-label="">
        <circle cx="60" cy="60" r="54" fill="#5a3619" stroke="#2f1a08" stroke-width="5"/>
        <circle cx="60" cy="60" r="45" fill="none" stroke="#ffeebd" stroke-width="2" stroke-dasharray="5 6" opacity=".68"/>
        <circle cx="60" cy="64" r="32" fill="#ffd64d" stroke="#9d6616" stroke-width="3"/>
        <circle cx="48" cy="60" r="4" fill="#111"/>
        <circle cx="72" cy="60" r="4" fill="#111"/>

        <path d="M35 41 C40 24, 80 24, 85 41 C76 36, 44 36, 35 41Z" fill="#5f3818"/>
        <path d="M39 75 C44 96, 76 96, 81 75 C71 84, 49 84, 39 75Z" fill="#5f3818" stroke="#4a2b19" stroke-width="2"/>
        <path d="M42 51 L53 48 M67 48 L78 51" stroke="#5f3818" stroke-width="4" stroke-linecap="round"/>
        <path d="M48 76 Q60 84 72 76" fill="none" stroke="#111" stroke-width="4" stroke-linecap="round"/>
        <path d="M36 93 Q60 109 84 93" fill="#fff7ea" stroke="#9d6616" stroke-width="2"/>
        <text x="60" y="22" text-anchor="middle" font-size="8.5" font-weight="900" fill="#ffeebd">LOGIC</text>
    
        </svg>
        <span class="thinker-label">Aristotle</span>
    </div>
    <div class="thinker-sticker rumi">

        <svg viewBox="0 0 120 140" role="img" aria-label="">
        <circle cx="60" cy="60" r="54" fill="#5a3619" stroke="#2f1a08" stroke-width="5"/>
        <circle cx="60" cy="60" r="45" fill="none" stroke="#ffeebd" stroke-width="2" stroke-dasharray="5 6" opacity=".68"/>
        <circle cx="60" cy="64" r="32" fill="#ffd64d" stroke="#9d6616" stroke-width="3"/>
        <circle cx="48" cy="60" r="4" fill="#111"/>
        <circle cx="72" cy="60" r="4" fill="#111"/>

        <ellipse cx="60" cy="38" rx="31" ry="16" fill="#fff8ef" stroke="#9d6616" stroke-width="3"/>
        <path d="M35 40 Q60 23 85 40" fill="none" stroke="#fff8ef" stroke-width="12" stroke-linecap="round"/>
        <path d="M39 74 C43 100, 77 100, 81 74 C70 86, 50 86, 39 74Z" fill="#633716" stroke="#4a2b19" stroke-width="2"/>
        <path d="M48 77 Q60 86 72 77" fill="none" stroke="#111" stroke-width="4" stroke-linecap="round"/>
        <path d="M27 83 C39 86, 42 98, 34 106 C24 98, 18 90, 27 83Z" fill="#ffd34b" stroke="#9d6616" stroke-width="2"/>
        <text x="60" y="22" text-anchor="middle" font-size="9" font-weight="900" fill="#ffeebd">POET</text>
    
        </svg>
        <span class="thinker-label">Rumi</span>
    </div>
    <div class="thinker-sticker jung">

        <svg viewBox="0 0 120 140" role="img" aria-label="">
        <circle cx="60" cy="60" r="54" fill="#5a3619" stroke="#2f1a08" stroke-width="5"/>
        <circle cx="60" cy="60" r="45" fill="none" stroke="#ffeebd" stroke-width="2" stroke-dasharray="5 6" opacity=".68"/>
        <circle cx="60" cy="64" r="32" fill="#ffd64d" stroke="#9d6616" stroke-width="3"/>
        <circle cx="48" cy="60" r="4" fill="#111"/>
        <circle cx="72" cy="60" r="4" fill="#111"/>

        <path d="M33 42 C39 23, 81 23, 87 42 C77 37, 43 37, 33 42Z" fill="#715e45"/>
        <circle cx="48" cy="60" r="10" fill="rgba(255,255,255,.16)" stroke="#4e3a25" stroke-width="3"/>
        <circle cx="72" cy="60" r="10" fill="rgba(255,255,255,.16)" stroke="#4e3a25" stroke-width="3"/>
        <line x1="58" y1="60" x2="62" y2="60" stroke="#4e3a25" stroke-width="3"/>
        <path d="M45 75 C51 70, 55 70, 60 74 C65 70, 69 70, 75 75" fill="none" stroke="#715e45" stroke-width="5" stroke-linecap="round"/>
        <path d="M48 84 Q60 90 72 84" fill="none" stroke="#111" stroke-width="4" stroke-linecap="round"/>
        <text x="60" y="22" text-anchor="middle" font-size="9" font-weight="900" fill="#ffeebd">DREAM</text>
    
        </svg>
        <span class="thinker-label">Carl Jung</span>
    </div>
    </div>
</div>
</header>
"""