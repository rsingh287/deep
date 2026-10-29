"""
===================================================================
D.E.E.P SOVEREIGN AI COCKPIT: ADVANCED WEB ARCHITECT SKILL
===================================================================
Generates state-of-the-art, visually stunning, multi-section websites
complete with domain-adaptive 3D WebGL scenes, procedural geometries,
contextual particle systems, high-resolution imagery, rich typography,
glassmorphism styling, stereoscopic CSS 3D card tilt physics, and responsive layouts.

Strict Directive:
NEVER output basic text-only sites or a one-size-fits-all 3D scene.
The 3D geometry, lighting, particle physics, color tokens, and copy
MUST dynamically adapt to the requested topic and industry domain.
"""

import os
import re
import json
import time
import socket
import threading
import socketserver
import http.server
from typing import Dict, List, Optional, Any
import requests

# Curated High-Definition Contextual Imagery Palettes (Unsplash CDN)
IMAGE_CATEGORIES = {
    "tech": [
        ("https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&w=1200&q=80", "High-tech circuit microprocessor and neural hardware"),
        ("https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?auto=format&fit=crop&w=800&q=80", "Cyber security matrix code stream"),
        ("https://images.unsplash.com/photo-1550751827-4bd374c3f58b?auto=format&fit=crop&w=800&q=80", "Next-gen cybernetic workstation interface"),
        ("https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?auto=format&fit=crop&w=800&q=80", "Abstract glassmorphism 3D geometry glow"),
    ],
    "automotive": [
        ("https://images.unsplash.com/photo-1617788138017-80ad40651399?auto=format&fit=crop&w=1200&q=80", "Futuristic electric hypercar aerodynamic design"),
        ("https://images.unsplash.com/photo-1503376780353-7e6692767b70?auto=format&fit=crop&w=800&q=80", "Supercar cockpit digital telemetry"),
        ("https://images.unsplash.com/photo-1552519507-da3b142c6e3d?auto=format&fit=crop&w=800&q=80", "High-performance sports vehicle carbon chassis"),
        ("https://images.unsplash.com/photo-1542282088-72c9c27ed0cd?auto=format&fit=crop&w=800&q=80", "Modern automotive night cruise with light trails"),
    ],
    "apple": [
        ("https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?auto=format&fit=crop&w=1200&q=80", "Flagship titanium smartphone precision display"),
        ("https://images.unsplash.com/photo-1592750475338-74b7b21085ab?auto=format&fit=crop&w=800&q=80", "Ultra-thin flagship device with cinematic lens"),
        ("https://images.unsplash.com/photo-1565849904461-04a58ad377e0?auto=format&fit=crop&w=800&q=80", "OLED edge-to-edge retina screen"),
        ("https://images.unsplash.com/photo-1510557880182-3d4d3cba35a5?auto=format&fit=crop&w=800&q=80", "Minimalist acoustic wireless spatial audio"),
    ],
    "business": [
        ("https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?auto=format&fit=crop&w=1200&q=80", "Modern corporate glass skyscraper headquarters"),
        ("https://images.unsplash.com/photo-1551836022-d5d88e9218df?auto=format&fit=crop&w=800&q=80", "Executive boardroom analytics & strategy"),
        ("https://images.unsplash.com/photo-1460925895917-afdab827c52f?auto=format&fit=crop&w=800&q=80", "Financial growth metrics and analytics dashboard"),
        ("https://images.unsplash.com/photo-1507679799987-c73779587ccf?auto=format&fit=crop&w=800&q=80", "Sovereign global enterprise leadership"),
    ],
    "nature": [
        ("https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=1200&q=80", "Pristine mountain alpine lake reflection"),
        ("https://images.unsplash.com/photo-1470071459604-3b5ec3a7fe05?auto=format&fit=crop&w=800&q=80", "Ethereal morning misty forest canopy"),
        ("https://images.unsplash.com/photo-1441974231531-c6227db76b6e?auto=format&fit=crop&w=800&q=80", "Sunlit woodland with vibrant emerald foliage"),
        ("https://images.unsplash.com/photo-1469474968028-56623f02e42e?auto=format&fit=crop&w=800&q=80", "Panoramic wilderness horizon sunset"),
    ],
    "fitness": [
        ("https://images.unsplash.com/photo-1517838277536-f5f99be501cd?auto=format&fit=crop&w=1200&q=80", "High-intensity athletic training in modern gymnasium"),
        ("https://images.unsplash.com/photo-1534438327276-14e5300c3a48?auto=format&fit=crop&w=800&q=80", "Performance weightlifting strength training"),
        ("https://images.unsplash.com/photo-1518611012118-696072aa579a?auto=format&fit=crop&w=800&q=80", "Mindful athletic conditioning and mobility"),
        ("https://images.unsplash.com/photo-1571019614242-c5c5dee9f50b?auto=format&fit=crop&w=800&q=80", "Elite cardio endurance sprint session"),
    ],
    
    "cybersecurity": [
        ("https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?auto=format&fit=crop&w=1200&q=80", "Autonomous cyber defense SOC terminal and matrix streams"),
        ("https://images.unsplash.com/photo-1550751827-4bd374c3f58b?auto=format&fit=crop&w=800&q=80", "Zero-trust cryptographic network architecture"),
        ("https://images.unsplash.com/photo-1563986768609-322da13575f3?auto=format&fit=crop&w=800&q=80", "High-security digital operations and firewall hardware"),
        ("https://images.unsplash.com/photo-1510511459019-5dda7724fd87?auto=format&fit=crop&w=800&q=80", "Deep packet inspection and threat containment"),
    ],
    "luxury_watch": [
        ("https://images.unsplash.com/photo-1523275335684-37898b6baf30?auto=format&fit=crop&w=1200&q=80", "Haute Horlogerie mechanical skeleton tourbillon timepiece"),
        ("https://images.unsplash.com/photo-1547996160-71dfabb1a79f?auto=format&fit=crop&w=800&q=80", "Hand-finished Swiss mechanical movement and anglage"),
        ("https://images.unsplash.com/photo-1522335789203-aabd1fc54bc9?auto=format&fit=crop&w=800&q=80", "Precision chronometer escapement balance wheel"),
        ("https://images.unsplash.com/photo-1508615039623-a25605d2b022?auto=format&fit=crop&w=800&q=80", "Luxury gold atelier watchmaking craftsmanship"),
    ],
    "aerospace": [
        ("https://images.unsplash.com/photo-1451187580459-43490279c0fa?auto=format&fit=crop&w=1200&q=80", "Orbital satellite constellation overlooking planet Earth"),
        ("https://images.unsplash.com/photo-1517976487502-5731c26b6038?auto=format&fit=crop&w=800&q=80", "Rocket propulsion stage firing and telemetry"),
        ("https://images.unsplash.com/photo-1446776811953-b23d57bd21aa?auto=format&fit=crop&w=800&q=80", "Deep space mission control center and trajectory paths"),
        ("https://images.unsplash.com/photo-1541185933-ef5d8ed016c2?auto=format&fit=crop&w=800&q=80", "Aerospace launch vehicle on the launchpad at dusk"),
    ],
    "music_synth": [
        ("https://images.unsplash.com/photo-1598488035139-bdbb2231ce04?auto=format&fit=crop&w=1200&q=80", "Modular analog Eurorack synthesizer studio console"),
        ("https://images.unsplash.com/photo-1511379938547-c1f69419868d?auto=format&fit=crop&w=800&q=80", "Vintage audio mixer and studio acoustic monitoring"),
        ("https://images.unsplash.com/photo-1514525253161-7a46d19cd819?auto=format&fit=crop&w=800&q=80", "Electronic music performance with vibrant neon lighting"),
        ("https://images.unsplash.com/photo-1470225620780-dba8ba36b745?auto=format&fit=crop&w=800&q=80", "Professional sound engineering and master recording"),
    ],
    "biotech": [
        ("https://images.unsplash.com/photo-1532187863486-abf9dbad1b69?auto=format&fit=crop&w=1200&q=80", "Biotechnology laboratory and automated genomics research"),
        ("https://images.unsplash.com/photo-1579154204601-01588f351e67?auto=format&fit=crop&w=800&q=80", "CRISPR molecular gene editing and DNA crystallography"),
        ("https://images.unsplash.com/photo-1530497610245-94d3c16cda28?auto=format&fit=crop&w=800&q=80", "Precision pharmaceutical medicine and cleanroom synthesis"),
        ("https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?auto=format&fit=crop&w=800&q=80", "Cellular biology microscopy and fluorescent proteins"),
    ],
    "architecture": [
        ("https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=1200&q=80", "Modernist cantilever luxury villa and architectural lighting"),
        ("https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?auto=format&fit=crop&w=800&q=80", "Spacious open-plan penthouse architectural interior"),
        ("https://images.unsplash.com/photo-1600607687939-ce8a6c25118c?auto=format&fit=crop&w=800&q=80", "Minimalist concrete pavilion and reflection water court"),
        ("https://images.unsplash.com/photo-1512917774080-9991f1c4c750?auto=format&fit=crop&w=800&q=80", "Contemporary luxury residence framing natural landscape"),
    ],
    "food": [
        ("https://images.unsplash.com/photo-1501339847302-ac426a4a7cbb?auto=format&fit=crop&w=1200&q=80", "Artisanal coffee brewing and roasted beans"),
        ("https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?auto=format&fit=crop&w=800&q=80", "Fresh steaming pour-over coffee bar"),
        ("https://images.unsplash.com/photo-1555396273-367ea4eb4db5?auto=format&fit=crop&w=800&q=80", "Warm ambient bistro dining experience"),
        ("https://images.unsplash.com/photo-1514432324607-a09d9b4aefdd?auto=format&fit=crop&w=800&q=80", "Specialty espresso cup with crema latte art"),
    ]
}


def _detect_thematic_profile(topic: str) -> Dict[str, Any]:
    """
    Selects and parameterizes a rich domain-specific design profile matching the topic.
    Provides bespoke color palettes, 3D geometries, particle behaviors, copy, and metrics.
    """
    t_lower = topic.lower()
    raw_name = re.sub(r'[^a-zA-Z0-9 ]', '', topic).strip().title()
    brand_name = raw_name if raw_name else "Apex Vanguard"

    # 1. Coffee / Hospitality / Dining
    if any(k in t_lower for k in ["coffee", "cafe", "roast", "roastery", "espresso", "latte", "barista", "bakery", "restaurant", "dining", "bistro", "culinary", "chef", "food", "tea", "brew"]):
        return {
            "domain": "coffee",
            "brand_name": brand_name,
            "brand_icon": "☕",
            "images": IMAGE_CATEGORIES["food"],
            "colors": {
                "bg": "#0c0a09",
                "surface": "#1c1917",
                "surface_glass": "rgba(28, 25, 23, 0.78)",
                "surface_border": "rgba(255, 237, 213, 0.10)",
                "surface_border_hover": "rgba(245, 158, 11, 0.55)",
                "primary": "#f59e0b",
                "primary_glow": "rgba(245, 158, 11, 0.38)",
                "accent": "#ea580c",
                "accent_glow": "rgba(234, 88, 12, 0.35)",
                "text": "#fdfaf7",
                "text_muted": "#a8a29e",
            },
            "hero_badge": "Specialty Roastery &bull; Micro-Batch Arabica",
            "headline_prefix": "Experience The Craft Of",
            "hero_desc": "Artisan single-origin beans, fluid-bed convection micro-roasting, and silky pour-over extractions engineered with 3D thermal precision.",
            "btn_primary": "Explore Single Origins →",
            "btn_secondary": "View Cupping Notes",
            "hud_pill": "Barista 3D Studio &bull; 94°C Brew",
            "hud_metric_label": "3D Ceramic Lathe",
            "hud_metric_val": "Glazed Cup &bull; Warm Steam Particles",
            "hud_btn1": "Toggle Steam",
            "hud_btn2": "Roast: Dark",
            "hud_btn3": "🎨 Amber Warmth",
            "stats": [
                ("100%", "Single-Origin Arabica"),
                ("88+", "Specialty Cup Score"),
                ("48h", "Precision Micro-Roast"),
                ("Zero", "Artificial Additives")
            ],
            "features_tag": "Artisanal Integrity",
            "features_title": "Crafted For Discerning Palates",
            "features": [
                ("Farm Direct", "High-Altitude Sourcing", "Direct ethical partnerships with family-run farms in Yirgacheffe, Huila, and Antigua with full fair-trade transparency.", "Discover Terroir ➔"),
                ("Fluid Bed", "Clean Hot-Air Roasting", "Zero-smoke hot-air convection roasters preserve floral jasmine nuances, crisp stone-fruit acidity, and cocoa sweetness.", "Explore Roasting ➔"),
                ("Hand Poured", "Master Barista Extractions", "Meticulously calibrated water mineral profiles, V60 pour-overs, and velvet nitro cold brews pulled on demand.", "View Brew Menu ➔")
            ],
            "showcase_tag": "Cupping Room",
            "showcase_title": "Uncompromised Roast Profiling",
            "showcase_desc": "Every harvest is sample-roasted in small 250g batches, cupped blindly by certified Q-graders, and roasted fresh to order so peak aroma reaches your cup.",
            "showcase_btn": "Order Fresh Roasted Bag ➔",
            "testimonials": [
                ("★★★★★", "The single-origin Ethiopian washed Yirgacheffe roasted here has the cleanest jasmine and bergamot notes I have ever cupped in 15 years as a Q-grader.", "Elena Rostova", "Certified Q-Grader & Coffee Judge", "https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=150&q=80"),
                ("★★★★★", "Their roast profiling is surgical. Every single batch is dialed with zero char and flawless sweetness. Our cafe customers are completely obsessed.", "Mateo Silva", "Head Roaster, Guild of Craft Baristas", "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=150&q=80")
            ],
            "faqs": [
                ("How soon after roasting is my coffee shipped?", "All orders are roasted in micro-batches within 24 hours of dispatch to ensure optimal degas time and peak flavor clarity upon arrival."),
                ("What makes your single-origin beans different?", "We never blend or hide inferior beans. Each lot represents a single farm or washing station, scored at 86+ points on the international SCA scale."),
                ("What water temperature and grind size do you recommend?", "For pour-over brews, we recommend filtered water at 93°C–94°C with a medium-coarse grind and a 1:16 brew ratio.")
            ],
            "three_scene_type": "coffee"
        }

    # 2. Automotive / Supercar / Racing
    if any(k in t_lower for k in ["car", "automotive", "supercar", "hypercar", "tesla", "porsche", "ferrari", "lamborghini", "vehicle", "race", "racing", "motor", "f1", "speed"]):
        return {
            "domain": "automotive",
            "brand_name": brand_name,
            "brand_icon": "🏎️",
            "images": IMAGE_CATEGORIES["automotive"],
            "colors": {
                "bg": "#08090c",
                "surface": "#0f121a",
                "surface_glass": "rgba(15, 18, 26, 0.78)",
                "surface_border": "rgba(255, 255, 255, 0.08)",
                "surface_border_hover": "rgba(0, 240, 255, 0.55)",
                "primary": "#00f0ff",
                "primary_glow": "rgba(0, 240, 255, 0.38)",
                "accent": "#ef4444",
                "accent_glow": "rgba(239, 68, 68, 0.35)",
                "text": "#f8fafc",
                "text_muted": "#94a3b8",
            },
            "hero_badge": "Active Aerodynamics &bull; Tri-Motor AWD",
            "headline_prefix": "Command The Raw Speed Of",
            "hero_desc": "Architected with wind-tunnel aerodynamic chassis geometry, vectoring tri-motor propulsion, and carbon-monocoque torsional rigidity.",
            "btn_primary": "Configure Hypercar →",
            "btn_secondary": "View Track Telemetry",
            "hud_pill": "Aero Telemetry &bull; 60 FPS",
            "hud_metric_label": "Carbon Monocoque",
            "hud_metric_val": "Aerodynamic Chassis &bull; 1,600 Speed Trails",
            "hud_btn1": "Aero Wing",
            "hud_btn2": "Speed: 200 MPH",
            "hud_btn3": "🎨 Racing Livery",
            "stats": [
                ("1.9s", "0-60 MPH Acceleration"),
                ("1,250 HP", "Tri-Motor Powertrain"),
                ("480 Mi", "Aerodynamic Range"),
                ("0.19 Cd", "Ultra-Low Drag")
            ],
            "features_tag": "Aerodynamic Superiority",
            "features_title": "Engineered For The Edge Of Physics",
            "features": [
                ("Active Aero", "Dynamic Hydraulic Downforce", "Active front splitters and rear multi-stage hydraulic wing continuously adjust downforce for cornering stability.", "Inspect Downforce ➔"),
                ("Tri-Motor AWD", "Torque Vectoring Propulsion", "Independent digital wheel motors calculate traction 1,000 times per second to eradicate understeer instantly.", "Explore Powertrain ➔"),
                ("Carbon Tub", "F1 Monocoque Construction", "Aerospace-grade pre-preg carbon fiber composite delivers Formula 1 crash safety with minimal unsprung mass.", "Examine Chassis ➔")
            ],
            "showcase_tag": "Track Testing",
            "showcase_title": "Uncompromising Telemetry & Control",
            "showcase_desc": "Tested on the Nürburgring Nordschleife, every aerodynamic contour, brake cooling duct, and rear diffuser fin is calibrated for lap-record downforce.",
            "showcase_btn": "Book Track Experience ➔",
            "testimonials": [
                ("★★★★★", "The instant cornering exit velocity and tri-motor torque vectoring feel telepathic. It redefines what an electric hypercar can achieve.", "Sebastian Vance", "Endurance Racing Champion", "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=150&q=80"),
                ("★★★★★", "Achieving a 0.19 drag coefficient while maintaining over 650kg of downforce at 180 MPH is an aerodynamic triumph.", "Claire Moreau", "Chief Aerodynamics Director", "https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=150&q=80")
            ],
            "faqs": [
                ("What is the battery recharge duration?", "Using 800V ultra-fast DC architecture, the battery charges from 10% to 80% in just 14 minutes."),
                ("Is this vehicle road legal in all jurisdictions?", "Yes. The vehicle is fully certified and street-legal in North America, Europe, and Asia-Pacific."),
                ("How does the active rear wing react under emergency braking?", "Under severe deceleration, the wing deploys as an aerodynamic airbrake in 120 milliseconds, shaving 25 meters off 100-0 MPH stopping distances.")
            ],
            "three_scene_type": "automotive"
        }

    # 3. Apple / Smartphone / Tech Gadget
    if any(k in t_lower for k in ["iphone", "apple", "phone", "smartphone", "mobile", "ipad", "macbook", "gadget", "apple watch", "smartwatch", "airpods", "titanium"]):
        return {
            "domain": "apple",
            "brand_name": brand_name,
            "brand_icon": "📱",
            "images": IMAGE_CATEGORIES["apple"],
            "colors": {
                "bg": "#090a0f",
                "surface": "#11131c",
                "surface_glass": "rgba(17, 19, 28, 0.78)",
                "surface_border": "rgba(255, 255, 255, 0.10)",
                "surface_border_hover": "rgba(56, 189, 248, 0.55)",
                "primary": "#38bdf8",
                "primary_glow": "rgba(56, 189, 248, 0.38)",
                "accent": "#a855f7",
                "accent_glow": "rgba(168, 85, 247, 0.35)",
                "text": "#f8fafc",
                "text_muted": "#94a3b8",
            },
            "hero_badge": "Grade 5 Titanium &bull; Super Retina XDR",
            "headline_prefix": "Discover The Precision Of",
            "hero_desc": "Forged in aerospace Grade 5 titanium with micro-blasted textures, 3-nanometer silicon, and triple optical camera lenses with sapphire glass.",
            "btn_primary": f"Order {brand_name} →",
            "btn_secondary": "Compare Tech Specs",
            "hud_pill": "Titanium Glass &bull; 120Hz ProMotion",
            "hud_metric_label": "Precision Slab",
            "hud_metric_val": "Triple Lens Array &bull; Optical Refraction",
            "hud_btn1": "Camera: 48MP",
            "hud_btn2": "Finish: Titanium",
            "hud_btn3": "🎨 Finish",
            "stats": [
                ("3,000 Nits", "Super Retina Peak"),
                ("3nm", "Neural Silicon Core"),
                ("Grade 5", "Aerospace Titanium"),
                ("48MP", "Quad-Pixel Optics")
            ],
            "features_tag": "Design Engineering",
            "features_title": "Titanium. So Strong. So Light. So Pro.",
            "features": [
                ("Titanium Enclosure", "Aerospace Grade 5", "Precision contoured edges and the thinnest display borders ever engineered on a flagship handheld device.", "View Materials ➔"),
                ("Photonic Engine", "Triple Optical Zoom", "Next-generation portraits with instant focal-point switching, powered by the custom 48MP main sensor.", "See Camera ➔"),
                ("ProMotion 120Hz", "Spatial Depth Display", "Dynamic refresh rates from 1Hz to 120Hz provide fluid interactions while conserving battery life.", "Explore Display ➔")
            ],
            "showcase_tag": "Studio Optics",
            "showcase_title": "A Pro Studio In Your Palm",
            "showcase_desc": "Shoot 4K 120 fps ProRes log video directly to external storage, capturing extraordinary color depth with industry-standard Academy Color Encoding.",
            "showcase_btn": "Buy Flagship Edition ➔",
            "testimonials": [
                ("★★★★★", "The sculpted titanium contouring and weight balance make it the most refined industrial design ever produced.", "Marcus Sterling", "Industrial Design Director", "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=150&q=80"),
                ("★★★★★", "The optical dynamic range and 4K 120fps ProRes log recording make it an honest cinema camera that fits in your jacket pocket.", "Sophie Lin", "Cinematographer & Photographer", "https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=150&q=80")
            ],
            "faqs": [
                ("What makes Grade 5 Titanium superior?", "Grade 5 titanium has one of the highest strength-to-weight ratios of any metal, making this the lightest and most durable pro flagship yet."),
                ("Does it support satellite emergency connectivity?", "Yes. Built-in directional satellite antenna arrays allow emergency SOS and roadside assistance without cellular reception."),
                ("How long does the all-day battery last?", "Up to 33 hours of continuous video playback on a single charge.")
            ],
            "three_scene_type": "apple"
        }

    # 4. Nature / Eco / Sustainability
    if any(k in t_lower for k in ["nature", "eco", "green", "forest", "outdoor", "garden", "wild", "wildlife", "sustainable", "sustainability", "climate", "solar", "organic", "plant"]):
        return {
            "domain": "nature",
            "brand_name": brand_name,
            "brand_icon": "🌿",
            "images": IMAGE_CATEGORIES["nature"],
            "colors": {
                "bg": "#050f08",
                "surface": "#0a1c10",
                "surface_glass": "rgba(10, 28, 16, 0.78)",
                "surface_border": "rgba(255, 255, 255, 0.08)",
                "surface_border_hover": "rgba(16, 185, 129, 0.55)",
                "primary": "#10b981",
                "primary_glow": "rgba(16, 185, 129, 0.38)",
                "accent": "#facc15",
                "accent_glow": "rgba(250, 204, 21, 0.35)",
                "text": "#f0fdf4",
                "text_muted": "#86efac",
            },
            "hero_badge": "100% Carbon Negative &bull; Living Biosphere",
            "headline_prefix": "Harmonize With The Power Of",
            "hero_desc": "Architected with regenerative ecological principles, bio-diverse reforestation, and clean closed-loop renewable energy.",
            "btn_primary": "Explore Eco Sanctuary →",
            "btn_secondary": "View Carbon Ledger",
            "hud_pill": "Living Biosphere &bull; Net Negative",
            "hud_metric_label": "Undulating Eco-Mesh",
            "hud_metric_val": "Terrain Wave &bull; 1,200 Bio-Spores",
            "hud_btn1": "Terrain Wave",
            "hud_btn2": "Wind: 1x",
            "hud_btn3": "🎨 Foliage",
            "stats": [
                ("-100%", "Carbon Footprint"),
                ("1.8M+", "Native Trees Planted"),
                ("Zero", "Single-Use Plastic"),
                ("100%", "Renewable Solar/Hydro")
            ],
            "features_tag": "Regenerative Earth",
            "features_title": "Restoring Planetary Equilibrium",
            "features": [
                ("Circular Loop", "100% Biodegradable Materials", "Every material breaks down naturally into nutrient-rich organic compost within 90 days with zero microplastics.", "Read Life Cycle ➔"),
                ("Regenerative Soil", "Agroforestry Ecosystems", "Direct stewardship of biodiverse sanctuaries that restore indigenous flora, wild topsoil, and native pollinators.", "See Forest Projects ➔"),
                ("Clean Microgrid", "Surplus Renewable Power", "Our solar and micro-hydro generation produces 140% of operations needs, returning clean power to rural communities.", "Inspect Energy ➔")
            ],
            "showcase_tag": "Living Sanctuary",
            "showcase_title": "Measurable Biodiversity Impact",
            "showcase_desc": "Track real-time wildlife corridor recoveries, soil carbon sequestration metrics, and protected alpine watersheds on our public blockchain ledger.",
            "showcase_btn": "Support Forest Conservation ➔",
            "testimonials": [
                ("★★★★★", "This initiative proves that human enterprise can actively regenerate natural ecosystems rather than merely minimizing damage.", "Dr. Aris Thorne", "Conservation Ecologist", "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=150&q=80"),
                ("★★★★★", "The verified blockchain carbon accounting sets the global gold standard for environmental transparency.", "Amara Patel", "Director, Global Wildlands Trust", "https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=150&q=80")
            ],
            "faqs": [
                ("How is your carbon negativity audited?", "Every ton of sequestered carbon is independently verified via satellite multispectral imagery and third-party soil core sampling."),
                ("Where are the reforestation projects located?", "Our primary sanctuaries are situated in the Pacific Northwest rainforests, the Costa Rican cloud forests, and the Scottish Highlands."),
                ("How can individuals contribute directly?", "You can sponsor dedicated acreage in our living reserves and receive real-time wildlife monitoring updates.")
            ],
            "three_scene_type": "nature"
        }

    # 5. Fitness / Athletics / Health
    if any(k in t_lower for k in ["fitness", "gym", "workout", "health", "train", "training", "crossfit", "athlete", "athletic", "sport", "sports", "conditioning", "muscle", "wellness"]):
        return {
            "domain": "fitness",
            "brand_name": brand_name,
            "brand_icon": "🔥",
            "images": IMAGE_CATEGORIES["fitness"],
            "colors": {
                "bg": "#09090b",
                "surface": "#18181b",
                "surface_glass": "rgba(24, 24, 27, 0.78)",
                "surface_border": "rgba(255, 255, 255, 0.08)",
                "surface_border_hover": "rgba(249, 115, 22, 0.55)",
                "primary": "#f97316",
                "primary_glow": "rgba(249, 115, 22, 0.38)",
                "accent": "#ef4444",
                "accent_glow": "rgba(239, 68, 68, 0.35)",
                "text": "#fafafa",
                "text_muted": "#a1a1aa",
            },
            "hero_badge": "High-Intensity Conditioning &bull; Kinetic Pulse",
            "headline_prefix": "Unleash The Energy Of",
            "hero_desc": "Architected with biometric telemetry, dynamic resistance intervals, and AI-periodized muscle hypertrophy conditioning.",
            "btn_primary": "Start Training Session →",
            "btn_secondary": "View Conditioning Protocols",
            "hud_pill": "Kinetic Engine &bull; Peak Heart Rate",
            "hud_metric_label": "Kinetic Shard Core",
            "hud_metric_val": "Dynamic Barbell &bull; 1,400 Fiery Embers",
            "hud_btn1": "Kinetic Burst",
            "hud_btn2": "Pace: 1x",
            "hud_btn3": "🎨 Blaze Fire",
            "stats": [
                ("850+", "Max Calorie Burn / Session"),
                ("100%", "AI Biometric Adaptation"),
                ("24/7", "Heart Rate Zone Sync"),
                ("98.4%", "Athlete Goal Rate")
            ],
            "features_tag": "High-Performance Training",
            "features_title": "Built To Break Physical Limits",
            "features": [
                ("Kinetic Intervals", "Metabolic Conditioning", "Sequenced high-intensity blocks designed to trigger the EPOC afterburn effect, elevating resting metabolic rate for 36 hours.", "View Workout Splits ➔"),
                ("Live Biometrics", "Real-Time Zone Calibration", "Continuous optical heart-rate monitoring ensures you train in the exact target zone for maximum VO2 max expansion.", "Inspect Tracking ➔"),
                ("Hypertrophy", "Periodized Strength Cycles", "AI-adjusted progressive overload and recovery monitoring to prevent plateaus while safeguarding joint health.", "Explore Strength ➔")
            ],
            "showcase_tag": "Elite Performance",
            "showcase_title": "Science-Backed Athletic Longevity",
            "showcase_desc": "Combines Olympic-level strength training with restorative mobility workflows so you build explosive power and durability without burning out.",
            "showcase_btn": "Claim 7-Day Athletic Pass ➔",
            "testimonials": [
                ("★★★★★", "The metabolic conditioning blocks completely transformed my speed and muscular endurance. The biometrics keep you honest every single rep.", "Kaelen Ross", "Decathlete & Crossfit Competitor", "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=150&q=80"),
                ("★★★★★", "As a performance physical therapist, I appreciate how the programming balances maximum hypertrophy with strict joint resilience.", "Tasha Brooks", "Doctor of Physical Therapy", "https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=150&q=80")
            ],
            "faqs": [
                ("Is this suitable for beginners or only elite athletes?", "Our AI programming auto-scales weights, rest intervals, and movement progressions to match your current baseline fitness."),
                ("What biometric monitors are compatible?", "All Apple Watch, Garmin, Whoop, and Polar optical HR sensors connect seamlessly."),
                ("How many days per week are recommended?", "Most members achieve breakthrough body composition results with 3 to 4 focused sessions per week.")
            ],
            "three_scene_type": "fitness"
        }

    # 6. Business / Finance / Capital
    if any(k in t_lower for k in ["business", "finance", "invest", "investment", "stock", "stocks", "trading", "crypto", "banking", "capital", "venture", "agency", "corporate", "asset", "quantitative", "quant fund", "quant trading", "wealth", "hedge fund", "portfolio", "equity", "equities", "bento"]):
        return {
            "domain": "business",
            "brand_name": brand_name,
            "brand_icon": "📈",
            "images": IMAGE_CATEGORIES["business"],
            "colors": {
                "bg": "#080c14",
                "surface": "#0f172a",
                "surface_glass": "rgba(15, 23, 42, 0.78)",
                "surface_border": "rgba(255, 255, 255, 0.08)",
                "surface_border_hover": "rgba(16, 185, 129, 0.55)",
                "primary": "#10b981",
                "primary_glow": "rgba(16, 185, 129, 0.38)",
                "accent": "#f59e0b",
                "accent_glow": "rgba(245, 158, 11, 0.35)",
                "text": "#f8fafc",
                "text_muted": "#94a3b8",
            },
            "hero_badge": "Institutional Capital &bull; Quantitative Alpha",
            "headline_prefix": "Scale The Growth Of",
            "hero_desc": "Architected with sub-millisecond execution engines, logarithmic growth models, and Tier-1 institutional multi-asset custody.",
            "btn_primary": "Open Institutional Account →",
            "btn_secondary": "Explore Quantitative Yield",
            "hud_pill": "Execution Matrix &bull; 0.02ms Latency",
            "hud_metric_label": "Growth Pillar Grid",
            "hud_metric_val": "Logarithmic Pillars &bull; Golden Capital Flow",
            "hud_btn1": "Pillars: Bull",
            "hud_btn2": "Velocity: 1x",
            "hud_btn3": "🎨 Gold Theme",
            "stats": [
                ("$4.8B", "Assets Under Management"),
                ("99.98%", "Order Fill Rate"),
                ("0.02ms", "Dark Pool Routing"),
                ("Tier-1", "Bank Vault Custody")
            ],
            "features_tag": "Quantitative Precision",
            "features_title": "Institutional Capital Management",
            "features": [
                ("Alpha Engines", "Algorithmic Arbitrage", "Machine-learning models scan global exchange order books to capture micro-inefficiencies with zero emotional bias.", "View Algorithms ➔"),
                ("Cold Vaults", "Multi-Sig Cryptographic Custody", "SOC-2 Type II certified cryptographic vaults with MPC threshold keys and $500M comprehensive insurance.", "Inspect Security ➔"),
                ("Deep Liquidity", "Multi-Asset Smart Routing", "Aggregated liquidity across global equities, sovereign debt, and digital assets with guaranteed sub-millisecond fill rates.", "Explore Markets ➔")
            ],
            "showcase_tag": "Execution Edge",
            "showcase_title": "Unmatched Market Telemetry",
            "showcase_desc": "Direct market access with dedicated dark fiber interconnects, cross-margining efficiency, and comprehensive institutional compliance reporting.",
            "showcase_btn": "Request Prime Brokerage Deck ➔",
            "testimonials": [
                ("★★★★★", "Their execution fill latency and algorithmic dark pool liquidity routing are the most reliable we have deployed across our $2B fund.", "Harrison Drake", "Chief Investment Officer, Drake Global", "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=150&q=80"),
                ("★★★★★", "The institutional risk modeling and automated Sharpe ratio optimization give our portfolio managers an extraordinary analytical edge.", "Vivian Vance", "Head of Quantitative Strategy", "https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=150&q=80")
            ],
            "faqs": [
                ("What is the minimum institutional account requirement?", "Direct prime brokerage accounts require an initial capitalization of $1,000,000 USD."),
                ("How are client assets segregated and safeguarded?", "All client capital is held in bankruptcy-remote segregated accounts at Tier-1 custodian banks."),
                ("What reporting feeds are available for audit?", "We provide real-time FIX 4.4 and 5.0 feeds, daily NAV statements, and automated API audit integration.")
            ],
            "three_scene_type": "business"
        }

    
    # 7. Cybersecurity / DevSecOps SOC / Defense
    if any(k in t_lower for k in ["cyber", "security", "soc", "firewall", "hacker", "hack", "penetration", "pentest", "infosec", "zero-trust", "threat", "vulnerability", "cve"]):
        return {
            "domain": "cybersecurity",
            "brand_name": brand_name,
            "brand_icon": "🛡️",
            "images": IMAGE_CATEGORIES["cybersecurity"],
            "colors": {
                "bg": "#05080f",
                "surface": "#0a101d",
                "surface_glass": "rgba(10, 16, 29, 0.88)",
                "surface_border": "rgba(0, 240, 255, 0.18)",
                "surface_border_hover": "rgba(0, 240, 255, 0.55)",
                "primary": "#00f0ff",
                "primary_glow": "rgba(0, 240, 255, 0.38)",
                "accent": "#ef4444",
                "accent_glow": "rgba(239, 68, 68, 0.35)",
                "text": "#f8fafc",
                "text_muted": "#94a3b8",
            },
            "hero_badge": "Zero-Trust Mesh &bull; eBPF Kernel Sentinel",
            "headline_prefix": "Command Autonomous Defense With",
            "hero_desc": "Architected with sub-millisecond automated threat containment, kernel-level eBPF behavioral telemetry, and quantum-resistant cryptographic shields.",
            "btn_primary": "Deploy Threat Shield →",
            "btn_secondary": "View Threat Telemetry",
            "hud_pill": "Laser Firewall &bull; Active Defenses",
            "hud_metric_label": "Laser Defense Grid",
            "hud_metric_val": "Scanning Beam &bull; 800 Matrix Particles",
            "hud_btn1": "Beam: Scan",
            "hud_btn2": "Speed: 1x",
            "hud_btn3": "🎨 Livery",
            "stats": [
                ("0.04ms", "Mean Containment Time"),
                ("100%", "Zero-Day Exploit Catch"),
                ("2.4 TB/s", "DDoS Scrubbing Capacity"),
                ("Post-Q", "Kyber Lattice Cryptography")
            ],
            "features_tag": "Zero-Trust Architecture",
            "features_title": "Enterprise Defense Command",
            "features": [
                ("Kernel eBPF", "Continuous Syscall Auditing", "Monitors OS kernel events directly with zero overhead, intercepting unprivileged code executions instantaneously.", "Inspect eBPF ➔"),
                ("Lattice Shield", "Post-Quantum Cryptography", "Implements NIST-standardized ML-KEM and Kyber key encapsulation to secure data against future quantum harvesting.", "View Cryptography ➔"),
                ("Autonomous SOC", "Automated Playbook Execution", "Isolates compromised microservice cgroups in 0.038 milliseconds with zero human latency required.", "Test Playbooks ➔")
            ],
            "three_scene_type": "cybersecurity"
        }

    # 8. Luxury Swiss Horlogerie / Watchmaker / Atelier
    if any(k in t_lower for k in ["watch", "horlogerie", "rolex", "patek", "audemars", "timepiece", "chronometer", "tourbillon", "luxury watch"]):
        return {
            "domain": "luxury_watch",
            "brand_name": brand_name,
            "brand_icon": "👑",
            "images": IMAGE_CATEGORIES["luxury_watch"],
            "colors": {
                "bg": "#0a0908",
                "surface": "#141210",
                "surface_glass": "rgba(20, 18, 16, 0.85)",
                "surface_border": "rgba(212, 175, 55, 0.16)",
                "surface_border_hover": "rgba(212, 175, 55, 0.55)",
                "primary": "#d4af37",
                "primary_glow": "rgba(212, 175, 55, 0.38)",
                "accent": "#fef08a",
                "accent_glow": "rgba(254, 240, 138, 0.35)",
                "text": "#fdfbf7",
                "text_muted": "#a8a29e",
            },
            "hero_badge": "Genève Poinçon &bull; Flying Tourbillon",
            "headline_prefix": "The Sovereign Art Of",
            "hero_desc": "Architected with a 0.29g titanium flying tourbillon cage revolving once every 60 seconds, hand-finished anglage, and 21,600 vph chronometer precision.",
            "btn_primary": "Reserve Bespoke Timepiece →",
            "btn_secondary": "Explore Calibre Atelier",
            "hud_pill": "Tourbillon Movement &bull; 60s Rev",
            "hud_metric_label": "Skeleton Calibre",
            "hud_metric_val": "Oscillating Balance Wheel &bull; Jewel Rubies",
            "hud_btn1": "Tourbillon: 60s",
            "hud_btn2": "Finish: Gold",
            "hud_btn3": "🎨 Polish",
            "stats": [
                ("60s", "Flying Tourbillon Rev"),
                ("21,600", "Vibrations Per Hour"),
                ("72h", "Power Reserve"),
                ("COSC", "Chronometer Certified")
            ],
            "features_tag": "Haute Horlogerie",
            "features_title": "Swiss Handcrafted Perfection",
            "features": [
                ("Flying Cage", "Titanium Tourbillon", "0.29-gram titanium cage counteracts gravitational timing variances across all wrist postures.", "Examine Cage ➔"),
                ("Hand Anglage", "Gentian Wood Beveling", "Internal angles hand-beveled to a 45-degree specular mirror polish in our Val-de-Travers atelier.", "View Finishing ➔"),
                ("Free-Sprung", "Variable-Inertia Balance", "Gyromax-style balance wheel with gold adjustment micro-screws for precision chronometer regulation.", "Inspect Calibre ➔")
            ],
            "three_scene_type": "luxury_watch"
        }

    # 9. Aerospace / Space Exploration / Satellite Constellation
    if any(k in t_lower for k in ["space", "aerospace", "orbit", "orbital", "satellite", "rocket", "spacex", "nasa", "constellation", "astronaut"]):
        return {
            "domain": "aerospace",
            "brand_name": brand_name,
            "brand_icon": "🚀",
            "images": IMAGE_CATEGORIES["aerospace"],
            "colors": {
                "bg": "#030712",
                "surface": "#0b1120",
                "surface_glass": "rgba(11, 17, 32, 0.85)",
                "surface_border": "rgba(56, 189, 248, 0.2)",
                "surface_border_hover": "rgba(56, 189, 248, 0.55)",
                "primary": "#38bdf8",
                "primary_glow": "rgba(56, 189, 248, 0.38)",
                "accent": "#6366f1",
                "accent_glow": "rgba(99, 102, 241, 0.35)",
                "text": "#f8fafc",
                "text_muted": "#94a3b8",
            },
            "hero_badge": "Low Earth Orbit &bull; Electric Hall Thrusters",
            "headline_prefix": "Command The Cosmos With",
            "hero_desc": "Architected with precision geostationary insertion, electric Hall-effect krypton thrusters, and satellite constellation bus architectures for 15-year orbital endurance.",
            "btn_primary": "Calculate Orbital Insertion →",
            "btn_secondary": "View Launch Manifest",
            "hud_pill": "Satellite Orbit &bull; 7.78 km/s",
            "hud_metric_label": "Orbital Constellation",
            "hud_metric_val": "Solar Array &bull; 1,200 Starfield Warp",
            "hud_btn1": "Array: Open",
            "hud_btn2": "Speed: 1x",
            "hud_btn3": "🎨 Orbit",
            "stats": [
                ("7.78 km/s", "Orbital Velocity"),
                ("540 km", "Circular Altitude"),
                ("95.4m", "Orbital Period"),
                ("100 Gbps", "Optical Cross-Links")
            ],
            "features_tag": "Orbital Architecture",
            "features_title": "Next-Gen Satellite Constellation",
            "features": [
                ("Krypton Ion", "Electric Hall Thruster", "Ultra-high specific impulse delivers 3,200 seconds of propulsion for autonomous collision avoidance.", "Examine Propulsion ➔"),
                ("Laser Cross-Link", "Coherent Space Mesh", "100 Gbps space-to-space inter-satellite optical laser links route data globally with zero ground relay lag.", "Inspect Optics ➔"),
                ("Synthetic Radar", "Sub-Meter Ground SAR", "High-frequency radar arrays pierce cloud cover and night skies to deliver real-time Earth telemetry.", "View Payloads ➔")
            ],
            "three_scene_type": "aerospace"
        }

    # 10. Modular Music Synthesizer / Audio Studio
    if any(k in t_lower for k in ["music", "synth", "synthesizer", "eurorack", "soundtrack", "recording studio", "audio studio", "music studio", "sound engineering", "beatmaker", "vst", "daw"]) or ("audio" in t_lower and any(w in t_lower for w in ["synth", "sound", "studio", "track", "mix"])):
        return {
            "domain": "music_synth",
            "brand_name": brand_name,
            "brand_icon": "🎹",
            "images": IMAGE_CATEGORIES["music_synth"],
            "colors": {
                "bg": "#100f14",
                "surface": "#191722",
                "surface_glass": "rgba(25, 23, 34, 0.85)",
                "surface_border": "rgba(168, 85, 247, 0.22)",
                "surface_border_hover": "rgba(168, 85, 247, 0.55)",
                "primary": "#a855f7",
                "primary_glow": "rgba(168, 85, 247, 0.38)",
                "accent": "#ec4899",
                "accent_glow": "rgba(236, 72, 153, 0.35)",
                "text": "#f8fafc",
                "text_muted": "#a1a1aa",
            },
            "hero_badge": "Voltage Controlled Oscillator &bull; Eurorack",
            "headline_prefix": "Harmonize Pure Sound With",
            "hero_desc": "Architected with discrete operational amplifiers, state-variable 24dB/oct ladder filters, and real-time zero-latency Web Audio API sound synthesis.",
            "btn_primary": "Launch Web Audio Lab →",
            "btn_secondary": "Explore Patch Library",
            "hud_pill": "Eurorack Console &bull; Oscilloscope",
            "hud_metric_label": "Modular Rack",
            "hud_metric_val": "Rotary Knobs &bull; Oscilloscope Wave",
            "hud_btn1": "Wave: Saw",
            "hud_btn2": "Cutoff: 1.2k",
            "hud_btn3": "🎨 Patch",
            "stats": [
                ("24 dB/oct", "Ladder Resonant Filter"),
                ("0.02ms", "Web Audio API Latency"),
                ("100%", "Pure Analog Circuitry"),
                ("Poly 16", "Voice Polyphony")
            ],
            "features_tag": "Acoustic Engineering",
            "features_title": "Analog Harmonic Precision",
            "features": [
                ("VCO Core", "Discrete Transistor Pairs", "Thermally compensated discrete matched transistors ensure rock-solid pitch stability across octave registers.", "Inspect Core ➔"),
                ("Moog Ladder", "Resonant Low-Pass Filter", "True 4-pole cascaded transconductance architecture yields legendary rich, buttery analog warmth.", "Explore Filter ➔"),
                ("ADSR Matrix", "Exponential Envelope Curve", "Snappy microsecond attack transients for crisp percussive plucks and lush evolving pads.", "View Envelopes ➔")
            ],
            "three_scene_type": "music_synth"
        }

    # 11. Biotech / Genomics / CRISPR Life Sciences
    if any(k in t_lower for k in ["biotech", "genomics", "dna", "crispr", "gene", "biology", "pharma", "clinical", "molecular", "cell", "genetics"]):
        return {
            "domain": "biotech",
            "brand_name": brand_name,
            "brand_icon": "🧬",
            "images": IMAGE_CATEGORIES["biotech"],
            "colors": {
                "bg": "#040d12",
                "surface": "#0a1b24",
                "surface_glass": "rgba(10, 27, 36, 0.85)",
                "surface_border": "rgba(20, 184, 166, 0.22)",
                "surface_border_hover": "rgba(20, 184, 166, 0.55)",
                "primary": "#14b8a6",
                "primary_glow": "rgba(20, 184, 166, 0.38)",
                "accent": "#3b82f6",
                "accent_glow": "rgba(59, 130, 246, 0.35)",
                "text": "#f0fdfa",
                "text_muted": "#99f6e4",
            },
            "hero_badge": "CRISPR Cas-9 &bull; Therapeutic Prime Editing",
            "headline_prefix": "Transform Molecular Medicine With",
            "hero_desc": "Architected with single-nucleotide prime editing, targeted in vivo lipid nanoparticle mRNA delivery, and algorithmic off-target cleavage eradication.",
            "btn_primary": "Analyze Genome Sequence →",
            "btn_secondary": "Review Clinical Pipeline",
            "hud_pill": "Double Helix &bull; 100% Homology",
            "hud_metric_label": "DNA Molecular Strand",
            "hud_metric_val": "Rotating Helix &bull; CRISPR Cleavage",
            "hud_btn1": "Helix: Spin",
            "hud_btn2": "Cas-9: Ready",
            "hud_btn3": "🎨 Nucleotide",
            "stats": [
                ("100%", "Target Homology"),
                ("Zero", "Off-Target Cleavage"),
                ("Phase 3", "Clinical Lead Asset"),
                ("LNP-RNA", "Targeted Delivery")
            ],
            "features_tag": "Genomic Engineering",
            "features_title": "Curative Molecular Medicine",
            "features": [
                ("Prime Editing", "Search-and-Replace Writing", "Directly writes new genetic sequences without double-strand DNA breaks or donor DNA templates.", "Explore Editing ➔"),
                ("Targeted LNP", "Tissue-Specific Delivery", "Ionizable lipid nanoparticles engineered to deliver base-editor cargos specifically to targeted organ tissues.", "Inspect LNPs ➔"),
                ("AI Guide RNA", "High-Fidelity gRNA Design", "Deep-learning predictive models eliminate unintended off-target genome interactions with mathematical rigor.", "View Pipeline ➔")
            ],
            "three_scene_type": "biotech"
        }

    # 12. Modernist Architecture / Luxury Real Estate
    if any(k in t_lower for k in ["architecture", "architect", "villa", "penthouse", "real estate", "interior", "mansion", "residence", "estate"]):
        return {
            "domain": "architecture",
            "brand_name": brand_name,
            "brand_icon": "🏛️",
            "images": IMAGE_CATEGORIES["architecture"],
            "colors": {
                "bg": "#0d0f12",
                "surface": "#15191f",
                "surface_glass": "rgba(21, 25, 31, 0.85)",
                "surface_border": "rgba(202, 138, 4, 0.22)",
                "surface_border_hover": "rgba(202, 138, 4, 0.55)",
                "primary": "#ca8a04",
                "primary_glow": "rgba(202, 138, 4, 0.38)",
                "accent": "#f5f5f4",
                "accent_glow": "rgba(245, 245, 244, 0.35)",
                "text": "#f8fafc",
                "text_muted": "#94a3b8",
            },
            "hero_badge": "Cantilever Concrete &bull; Biophilic Glass",
            "headline_prefix": "Architecting The Horizon With",
            "hero_desc": "Architected with cantilevered reinforced architectural concrete, panoramic acoustic glazing, and biophilic natural light orientation across alpine and coastal terrains.",
            "btn_primary": "Explore Architectural Works →",
            "btn_secondary": "Request Private Commission",
            "hud_pill": "Cantilever Villa &bull; Sun Path",
            "hud_metric_label": "Modernist Pavilion",
            "hud_metric_val": "Cantilever Wireframe &bull; Sun Angle",
            "hud_btn1": "Sun: Midday",
            "hud_btn2": "Elevation: 1x",
            "hud_btn3": "🎨 Travertine",
            "stats": [
                ("12,000", "Square Feet Gross Area"),
                ("32m", "Unsupported Cantilever"),
                ("Net Zero", "Passive Solar Balance"),
                ("LEED", "Platinum Certified")
            ],
            "features_tag": "Modernist Architecture",
            "features_title": "Spatial Form & Natural Light",
            "features": [
                ("Cantilever Form", "Post-Tensioned Concrete", "Dramatic 32-meter unsupported living room cantilever framing unobstructed ocean and mountain horizons.", "Inspect Structure ➔"),
                ("Acoustic Glazing", "Triple Insulated Panes", "Floor-to-ceiling motorized sliding glass curtains with zero-threshold indoor/outdoor transition.", "View Glazing ➔"),
                ("Biophilic Sun", "Passive Thermal Mass", "Oriented to capture low winter solar radiation while shading high summer glare, maintaining ambient equilibrium.", "Explore Solar ➔")
            ],
            "three_scene_type": "architecture"
        }

    # 7. Quantum / AI / High-Tech Sovereign Workstation (Default)
    return {
        "domain": "quantum",
        "brand_name": brand_name,
        "brand_icon": "⚡",
        "images": IMAGE_CATEGORIES["tech"],
        "colors": {
            "bg": "#06080d",
            "surface": "#0e131f",
            "surface_glass": "rgba(14, 19, 31, 0.78)",
            "surface_border": "rgba(255, 255, 255, 0.08)",
            "surface_border_hover": "rgba(0, 240, 255, 0.55)",
            "primary": "#00f0ff",
            "primary_glow": "rgba(0, 240, 255, 0.38)",
            "accent": "#8b5cf6",
            "accent_glow": "rgba(139, 92, 246, 0.35)",
            "text": "#f8fafc",
            "text_muted": "#94a3b8",
        },
        "hero_badge": "128-Qubit Neural Matrix &bull; Sovereign AI",
        "headline_prefix": "Experience The Power Of",
        "hero_desc": "Architected with cutting-edge Three.js WebGL spatial computing, real-time mouse-tracking quaternion physics, and stereoscopic CSS 3D depth geometry.",
        "btn_primary": "Enter 3D Experience →",
        "btn_secondary": "View Spatial Showcase",
        "hud_pill": "WebGL 3D Core &bull; 60 FPS",
        "hud_metric_label": "3D WebGL Matrix",
        "hud_metric_val": "2,000 Particle Orbit &bull; 360° Drag",
        "hud_btn1": "Wireframe",
        "hud_btn2": "Speed: 1x",
        "hud_btn3": "🎨 Color",
        "stats": [
            ("128-Qubit", "Coherence Matrix"),
            ("0.08ms", "Inference Latency"),
            ("99.999%", "Cluster SLA Uptime"),
            ("Zero-Trust", "Cryptographic Shield")
        ],
        "features_tag": "Spatial Precision",
        "features_title": "State-Of-The-Art 3D Capabilities",
        "features": [
            ("Neural Core", "WebGL Three.js Mesh", "Real-time vector vertex geometry with multi-point specular illumination and zero runtime lag.", "Explore Geometry ➔"),
            ("Stereoscopic", "CSS 3D Parallax Tilt", "Cards calculate mouse angles in real time to generate dynamic 3D perspective and glare reflections.", "Test Parallax ➔"),
            ("Glass HUD", "Dynamic Glassmorphic Interface", "Tailored fluid geometry, rich HSL palettes, and adaptive micro-interactions built for human excellence.", "View Interface ➔")
        ],
        "showcase_tag": "Visual Showcase",
        "showcase_title": "Engineered With Pure Craftsmanship",
        "showcase_desc": "Every visual asset, 3D polygon, and typography element is meticulously calibrated to produce an awe-inspiring first impression while preserving instantaneous load times.",
        "showcase_btn": "Initiate Session ➔",
        "testimonials": [
            ("★★★★★", "The interactive 3D WebGL canvas and mouse tilt parallax completely redefined our standard. It feels alive, futuristic, and extraordinarily fast.", "Sarah Chen", "VP of Product Design, Apex Core", "https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=150&q=80"),
            ("★★★★★", "No generic boilerplate or basic text. Every section is meticulously crafted with real 3D WebGL rendering, photography, and typography.", "Marcus Vance", "Chief Architect, Sovereign AI Systems", "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=150&q=80")
        ],
        "faqs": [
            ("How is this system engineered with 3D capabilities?", "It combines modern Three.js WebGL hardware acceleration, dynamic 3D geometry meshes, CSS 3D perspective transforms, and curated high-resolution photography without bloated external runtime dependencies."),
            ("Is the 3D canvas mobile responsive?", "Yes. The WebGL renderer and camera dynamically recalculate aspect ratios and pixel ratios on all screen sizes, from mobile phones to ultra-wide monitors."),
            ("Can this system integrate with local AI backends?", "Absolutely. The application natively links to the D.E.E.P Sovereign Cockpit API, PostgreSQL durable ledger, and Qdrant memory layers.")
        ],
        "three_scene_type": "quantum"
    }


def _generate_threejs_scene_code(profile: Dict[str, Any]) -> str:
    """
    Generates procedural Three.js JavaScript tailored specifically to the selected domain.
    Coffee creates a ceramic cup, saucer, espresso surface, and warm rising steam particles.
    Automotive creates an aerodynamic chassis, glowing wheels, and 1,600 speed light trails.
    Apple creates a titanium slab, triple optical lenses, and an orbital halo ring.
    Nature creates an undulating landscape terrain mesh, living eco-sphere, and bio-spores.
    Fitness creates a dynamic kinetic hexagonal barbell core with fiery embers.
    Business creates logarithmic financial candlestick pillars and golden capital flow.
    Quantum creates a hyper-dimensional torus knot, inner nucleus, and electron nebula.
    """
    scene_type = profile.get("three_scene_type", "quantum")

    if scene_type == "coffee":
        return """
      // --- Domain Scene: Procedural Ceramic Coffee Cup with Warm Rising Steam ---
      const mainGroup = new THREE.Group();

      // Cup body (tapered cylinder)
      const cupGeo = new THREE.CylinderGeometry(0.95, 0.68, 1.25, 36, 1, false);
      const ceramicMat = new THREE.MeshStandardMaterial({
        color: 0x221714,
        roughness: 0.22,
        metalness: 0.18,
        emissive: 0x140d0a,
        wireframe: false
      });
      const cupMesh = new THREE.Mesh(cupGeo, ceramicMat);
      mainGroup.add(cupMesh);

      // Cup rim ring
      const rimGeo = new THREE.TorusGeometry(0.94, 0.05, 16, 36);
      const rimMat = new THREE.MeshStandardMaterial({ color: 0x3d2820, roughness: 0.2 });
      const rimMesh = new THREE.Mesh(rimGeo, rimMat);
      rimMesh.rotation.x = Math.PI / 2;
      rimMesh.position.y = 0.62;
      mainGroup.add(rimMesh);

      // Liquid Surface (Dark roasted espresso)
      const liquidGeo = new THREE.CircleGeometry(0.91, 32);
      const liquidMat = new THREE.MeshStandardMaterial({
        color: 0x120a07,
        roughness: 0.08,
        metalness: 0.85,
        emissive: 0x0a0503
      });
      const liquidMesh = new THREE.Mesh(liquidGeo, liquidMat);
      liquidMesh.rotation.x = -Math.PI / 2;
      liquidMesh.position.y = 0.52;
      mainGroup.add(liquidMesh);

      // Crema / Latte Art swirl
      const cremaGeo = new THREE.TorusGeometry(0.42, 0.07, 12, 28);
      const cremaMat = new THREE.MeshBasicMaterial({ color: 0xf59e0b, transparent: true, opacity: 0.85 });
      const cremaMesh = new THREE.Mesh(cremaGeo, cremaMat);
      cremaMesh.rotation.x = -Math.PI / 2;
      cremaMesh.position.y = 0.53;
      mainGroup.add(cremaMesh);

      // Cup Handle
      const handleGeo = new THREE.TorusGeometry(0.42, 0.08, 16, 32, Math.PI * 1.15);
      const handleMesh = new THREE.Mesh(handleGeo, ceramicMat);
      handleMesh.position.set(0.98, 0.06, 0);
      handleMesh.rotation.z = -Math.PI / 2.3;
      mainGroup.add(handleMesh);

      // Ceramic Saucer underneath
      const saucerGeo = new THREE.CylinderGeometry(1.65, 1.45, 0.12, 36);
      const saucerMesh = new THREE.Mesh(saucerGeo, ceramicMat);
      saucerMesh.position.y = -0.68;
      mainGroup.add(saucerMesh);

      mainGroup.rotation.x = 0.32;
      mainGroup.rotation.y = -0.4;
      scene.add(mainGroup);

      // Warm Rising Steam Particle System (650 golden-amber particles)
      const steamCount = 650;
      const steamGeo = new THREE.BufferGeometry();
      const steamPositions = new Float32Array(steamCount * 3);
      const steamVelocities = new Float32Array(steamCount);
      const steamDrifts = new Float32Array(steamCount);

      for (let i = 0; i < steamCount; i++) {
        const i3 = i * 3;
        steamPositions[i3] = (Math.random() - 0.5) * 0.9;
        steamPositions[i3 + 1] = 0.6 + Math.random() * 2.8;
        steamPositions[i3 + 2] = (Math.random() - 0.5) * 0.9;
        steamVelocities[i] = 0.008 + Math.random() * 0.012;
        steamDrifts[i] = Math.random() * Math.PI * 2;
      }

      steamGeo.setAttribute('position', new THREE.BufferAttribute(steamPositions, 3));
      const steamMat = new THREE.PointsMaterial({
        color: 0xf59e0b,
        size: 0.052,
        transparent: true,
        opacity: 0.75,
        blending: THREE.AdditiveBlending
      });
      const steamSystem = new THREE.Points(steamGeo, steamMat);
      scene.add(steamSystem);

      // Dynamic Lights
      const ambientLight = new THREE.AmbientLight(0xffedd5, 0.85);
      scene.add(ambientLight);
      const pointLight1 = new THREE.PointLight(0xf59e0b, 3.2, 50);
      pointLight1.position.set(3, 4, 3);
      scene.add(pointLight1);
      const pointLight2 = new THREE.PointLight(0xea580c, 2.2, 50);
      pointLight2.position.set(-3, -2, 2);
      scene.add(pointLight2);

      // HUD Button Callbacks
      let steamActive = true;
      window.toggleCustom1 = function(btn) {
        steamActive = !steamActive;
        steamSystem.visible = steamActive;
        if (btn) btn.classList.toggle('active', steamActive);
        playSpatialTone(steamActive ? 587 : 440, 'sine', 0.2);
      };

      const roastColors = [
        { name: 'Dark Roast', cup: 0x18100e, liquid: 0x0a0504, glow: 0xf59e0b },
        { name: 'Medium Roast', cup: 0x2b1d18, liquid: 0x1f110c, glow: 0xfbbf24 },
        { name: 'Light Roast', cup: 0x3d2b24, liquid: 0x2c1a12, glow: 0xfcd34d }
      ];
      let roastIdx = 0;
      window.toggleCustom2 = function(btn) {
        roastIdx = (roastIdx + 1) % roastColors.length;
        const r = roastColors[roastIdx];
        ceramicMat.color.setHex(r.cup);
        liquidMat.color.setHex(r.liquid);
        steamMat.color.setHex(r.glow);
        if (btn) btn.textContent = `Roast: ${r.name.split(' ')[0]}`;
        playSpatialTone(659, 'triangle', 0.2);
      };

      window.cycleCustomTheme = function(btn) {
        ceramicMat.wireframe = !ceramicMat.wireframe;
        if (btn) btn.textContent = ceramicMat.wireframe ? '🎨 Wireframe' : '🎨 Glazed';
        playSpatialTone(520, 'sine', 0.18);
      };

      function updateSceneAnimation(time, rotSpeed) {
        mainGroup.rotation.y += 0.006 * rotSpeed;
        if (steamActive) {
          const sPos = steamGeo.attributes.position.array;
          for (let i = 0; i < steamCount; i++) {
            const i3 = i * 3;
            sPos[i3 + 1] += steamVelocities[i] * rotSpeed;
            sPos[i3] += Math.sin(time * 0.002 + steamDrifts[i]) * 0.003;
            sPos[i3 + 2] += Math.cos(time * 0.002 + steamDrifts[i]) * 0.003;
            if (sPos[i3 + 1] > 3.6) {
              sPos[i3 + 1] = 0.6;
              sPos[i3] = (Math.random() - 0.5) * 0.8;
              sPos[i3 + 2] = (Math.random() - 0.5) * 0.8;
            }
          }
          steamGeo.attributes.position.needsUpdate = true;
        }
      }
"""

    
    elif scene_type == "cybersecurity":
        return """
      // --- Domain Scene: Procedural Cyber Defense Radar & Laser Firewall ---
      const mainGroup = new THREE.Group();

      // Cyber Defense Core Shield (Icosahedron wireframe)
      const coreGeo = new THREE.IcosahedronGeometry(1.2, 2);
      const coreMat = new THREE.MeshStandardMaterial({
        color: 0x00f0ff,
        wireframe: true,
        emissive: 0x003344,
        roughness: 0.2
      });
      const coreMesh = new THREE.Mesh(coreGeo, coreMat);
      mainGroup.add(coreMesh);

      // Inner Glowing Kernel Core
      const innerGeo = new THREE.SphereGeometry(0.55, 16, 16);
      const innerMat = new THREE.MeshBasicMaterial({ color: 0x10b981 });
      const innerMesh = new THREE.Mesh(innerGeo, innerMat);
      mainGroup.add(innerMesh);

      // Laser Firewall Orbital Ring
      const ringGeo = new THREE.TorusGeometry(1.9, 0.04, 16, 48);
      const ringMat = new THREE.MeshBasicMaterial({ color: 0x00f0ff });
      const ringMesh = new THREE.Mesh(ringGeo, ringMat);
      ringMesh.rotation.x = Math.PI / 2.5;
      mainGroup.add(ringMesh);

      mainGroup.rotation.x = 0.25;
      scene.add(mainGroup);

      // 800 Matrix Code / Laser Stream Particles
      const streamCount = 800;
      const streamGeo = new THREE.BufferGeometry();
      const streamPositions = new Float32Array(streamCount * 3);
      for (let i = 0; i < streamCount; i++) {
        const i3 = i * 3;
        streamPositions[i3] = (Math.random() - 0.5) * 6;
        streamPositions[i3 + 1] = (Math.random() - 0.5) * 6;
        streamPositions[i3 + 2] = (Math.random() - 0.5) * 6;
      }
      streamGeo.setAttribute('position', new THREE.BufferAttribute(streamPositions, 3));
      const streamMat = new THREE.PointsMaterial({
        color: 0x00f0ff,
        size: 0.05,
        transparent: true,
        opacity: 0.85,
        blending: THREE.AdditiveBlending
      });
      const streamPoints = new THREE.Points(streamGeo, streamMat);
      scene.add(streamPoints);

      // Dynamic Lights
      const pLight = new THREE.PointLight(0x00f0ff, 3.5, 40);
      pLight.position.set(3, 3, 3);
      scene.add(pLight);
      const pLight2 = new THREE.PointLight(0x10b981, 2.5, 40);
      pLight2.position.set(-3, -2, 2);
      scene.add(pLight2);

      let scanning = true;
      window.toggleCustom1 = function(btn) {
        scanning = !scanning;
        if (btn) btn.textContent = scanning ? 'Beam: Scan' : 'Beam: Pause';
        playSpatialTone(scanning ? 880 : 440, 'sine', 0.15);
      };

      let speedFactor = 1.0;
      window.toggleCustom2 = function(btn) {
        speedFactor = speedFactor === 1.0 ? 2.5 : 1.0;
        if (btn) btn.textContent = `Speed: ${speedFactor}x`;
        playSpatialTone(660, 'sine', 0.15);
      };

      function updateSceneAnimation(time, rotSpeed) {
        if (scanning) {
          mainGroup.rotation.y += 0.012 * speedFactor * rotSpeed;
          coreMesh.rotation.x += 0.008 * speedFactor * rotSpeed;
          ringMesh.rotation.z += 0.015 * speedFactor * rotSpeed;
          streamPoints.rotation.y -= 0.003 * speedFactor * rotSpeed;
        }
      }
"""

    elif scene_type == "luxury_watch":
        return """
      // --- Domain Scene: Procedural Skeleton Tourbillon Movement with Jewel Rubies ---
      const mainGroup = new THREE.Group();

      // Outer Tourbillon Gold Bezel
      const bezelGeo = new THREE.TorusGeometry(1.6, 0.09, 16, 64);
      const goldMat = new THREE.MeshStandardMaterial({
        color: 0xd4af37,
        metalness: 0.95,
        roughness: 0.12,
        emissive: 0x241a05
      });
      const bezelMesh = new THREE.Mesh(bezelGeo, goldMat);
      mainGroup.add(bezelMesh);

      // Rotating Balance Wheel (3 Spoke Wheel)
      const balanceGroup = new THREE.Group();
      const wheelRimGeo = new THREE.TorusGeometry(1.1, 0.04, 16, 48);
      const balanceMat = new THREE.MeshStandardMaterial({ color: 0xd4af37, metalness: 0.9, roughness: 0.2 });
      const wheelRimMesh = new THREE.Mesh(wheelRimGeo, balanceMat);
      balanceGroup.add(wheelRimMesh);

      for (let i = 0; i < 3; i++) {
        const spokeGeo = new THREE.CylinderGeometry(0.02, 0.02, 1.1, 8);
        const spokeMesh = new THREE.Mesh(spokeGeo, balanceMat);
        spokeMesh.rotation.z = (i * Math.PI * 2) / 3;
        balanceGroup.add(spokeMesh);
      }
      mainGroup.add(balanceGroup);

      // Center Escapement Gear
      const gearGeo = new THREE.CylinderGeometry(0.35, 0.35, 0.08, 18);
      const gearMat = new THREE.MeshStandardMaterial({ color: 0x94a3b8, metalness: 0.85, roughness: 0.3 });
      const gearMesh = new THREE.Mesh(gearGeo, gearMat);
      gearMesh.rotation.x = Math.PI / 2;
      mainGroup.add(gearMesh);

      // Jewel Rubies (Corundum red bearings)
      const rubyMat = new THREE.MeshBasicMaterial({ color: 0xef4444 });
      for (let i = 0; i < 4; i++) {
        const rubyGeo = new THREE.SphereGeometry(0.08, 12, 12);
        const rubyMesh = new THREE.Mesh(rubyGeo, rubyMat);
        const ang = (i * Math.PI) / 2;
        rubyMesh.position.set(Math.cos(ang) * 0.7, Math.sin(ang) * 0.7, 0.05);
        mainGroup.add(rubyMesh);
      }

      mainGroup.rotation.x = 0.3;
      scene.add(mainGroup);

      // Golden Dust Particles
      const pCount = 500;
      const pGeo = new THREE.BufferGeometry();
      const pPos = new Float32Array(pCount * 3);
      for (let i = 0; i < pCount; i++) {
        const i3 = i * 3;
        pPos[i3] = (Math.random() - 0.5) * 5;
        pPos[i3 + 1] = (Math.random() - 0.5) * 5;
        pPos[i3 + 2] = (Math.random() - 0.5) * 5;
      }
      pGeo.setAttribute('position', new THREE.BufferAttribute(pPos, 3));
      const pMat = new THREE.PointsMaterial({ color: 0xd4af37, size: 0.04, transparent: true, opacity: 0.75 });
      const pSystem = new THREE.Points(pGeo, pMat);
      scene.add(pSystem);

      const pLight = new THREE.PointLight(0xd4af37, 3.2, 30);
      pLight.position.set(3, 4, 3);
      scene.add(pLight);

      let tourbillonFast = false;
      window.toggleCustom1 = function(btn) {
        tourbillonFast = !tourbillonFast;
        if (btn) btn.textContent = tourbillonFast ? 'Tourbillon: Fast' : 'Tourbillon: 60s';
        playSpatialTone(740, 'triangle', 0.1);
      };

      window.toggleCustom2 = function(btn) {
        goldMat.color.setHex(goldMat.color.getHex() === 0xd4af37 ? 0xe2e8f0 : 0xd4af37);
        if (btn) btn.textContent = goldMat.color.getHex() === 0xd4af37 ? 'Bezel: Gold' : 'Bezel: Platinum';
        playSpatialTone(880, 'sine', 0.1);
      };

      function updateSceneAnimation(time, rotSpeed) {
        const mult = tourbillonFast ? 3.0 : 1.0;
        mainGroup.rotation.z += 0.005 * mult * rotSpeed;
        balanceGroup.rotation.z = Math.sin(time * 0.015 * mult) * 0.85; // Oscillating hairspring
        gearMesh.rotation.z -= 0.02 * mult * rotSpeed;
        pSystem.rotation.y += 0.001 * rotSpeed;
      }
"""

    elif scene_type == "aerospace":
        return """
      // --- Domain Scene: Procedural Orbital Satellite with Solar Arrays ---
      const mainGroup = new THREE.Group();

      // Main Satellite Bus Chassis
      const satGeo = new THREE.BoxGeometry(0.9, 1.4, 0.9);
      const satMat = new THREE.MeshStandardMaterial({
        color: 0xe2e8f0,
        metalness: 0.92,
        roughness: 0.18,
        emissive: 0x0f172a
      });
      const satMesh = new THREE.Mesh(satGeo, satMat);
      mainGroup.add(satMesh);

      // Dual Solar Panel Arrays
      const panelGeo = new THREE.BoxGeometry(2.4, 0.8, 0.05);
      const panelMat = new THREE.MeshStandardMaterial({
        color: 0x1e3a8a,
        metalness: 0.85,
        roughness: 0.1,
        emissive: 0x0284c7
      });
      const leftPanel = new THREE.Mesh(panelGeo, panelMat);
      leftPanel.position.set(-1.8, 0, 0);
      mainGroup.add(leftPanel);

      const rightPanel = new THREE.Mesh(panelGeo, panelMat);
      rightPanel.position.set(1.8, 0, 0);
      mainGroup.add(rightPanel);

      // Earth Orbit Trajectory Arc
      const arcGeo = new THREE.TorusGeometry(2.8, 0.02, 16, 64, Math.PI * 1.5);
      const arcMat = new THREE.MeshBasicMaterial({ color: 0x38bdf8 });
      const arcMesh = new THREE.Mesh(arcGeo, arcMat);
      arcMesh.rotation.x = Math.PI / 2.3;
      mainGroup.add(arcMesh);

      mainGroup.rotation.x = 0.35;
      scene.add(mainGroup);

      // 1,200 Starfield Warp Particles
      const starCount = 1200;
      const starGeo = new THREE.BufferGeometry();
      const starPos = new Float32Array(starCount * 3);
      for (let i = 0; i < starCount; i++) {
        const i3 = i * 3;
        starPos[i3] = (Math.random() - 0.5) * 8;
        starPos[i3 + 1] = (Math.random() - 0.5) * 8;
        starPos[i3 + 2] = (Math.random() - 0.5) * 8;
      }
      starGeo.setAttribute('position', new THREE.BufferAttribute(starPos, 3));
      const starMat = new THREE.PointsMaterial({ color: 0xffffff, size: 0.035, transparent: true, opacity: 0.8 });
      const starPoints = new THREE.Points(starGeo, starMat);
      scene.add(starPoints);

      const pLight = new THREE.PointLight(0x38bdf8, 3.2, 40);
      pLight.position.set(3, 4, 3);
      scene.add(pLight);

      function updateSceneAnimation(time, rotSpeed) {
        mainGroup.rotation.y += 0.008 * rotSpeed;
        starPoints.rotation.y -= 0.001 * rotSpeed;
      }
"""

    elif scene_type == "automotive":
        return """
      // --- Domain Scene: Procedural Aerodynamic Hypercar with Speed Trails ---
      const mainGroup = new THREE.Group();

      // Sleek aerodynamic monocoque hull
      const bodyGeo = new THREE.ConeGeometry(0.85, 3.4, 4);
      const carMat = new THREE.MeshStandardMaterial({
        color: 0x0f172a,
        metalness: 0.92,
        roughness: 0.16,
        wireframe: false,
        emissive: 0x020617
      });
      const bodyMesh = new THREE.Mesh(bodyGeo, carMat);
      bodyMesh.rotation.z = Math.PI / 2;
      bodyMesh.rotation.y = Math.PI / 4;
      bodyMesh.scale.set(0.65, 1.0, 0.35);
      mainGroup.add(bodyMesh);

      // Glowing Cockpit Canopy Glass
      const canopyGeo = new THREE.SphereGeometry(0.62, 16, 16);
      const canopyMat = new THREE.MeshStandardMaterial({
        color: 0x00f0ff,
        metalness: 0.95,
        roughness: 0.05,
        transparent: true,
        opacity: 0.85,
        emissive: 0x003344
      });
      const canopyMesh = new THREE.Mesh(canopyGeo, canopyMat);
      canopyMesh.scale.set(0.42, 0.28, 0.9);
      canopyMesh.position.set(0, 0.24, -0.1);
      mainGroup.add(canopyMesh);

      // Active Hydraulic Rear Aero Wing
      const wingGeo = new THREE.BoxGeometry(1.65, 0.05, 0.32);
      const wingMat = new THREE.MeshStandardMaterial({ color: 0xef4444, metalness: 0.85, roughness: 0.2 });
      const wingMesh = new THREE.Mesh(wingGeo, wingMat);
      wingMesh.position.set(0, 0.42, -1.35);
      mainGroup.add(wingMesh);

      // 4 High-Performance Wheels with glowing neon brake discs
      const wheelGeo = new THREE.CylinderGeometry(0.32, 0.32, 0.22, 24);
      const wheelMat = new THREE.MeshStandardMaterial({ color: 0x1e293b, roughness: 0.6 });
      const brakeMat = new THREE.MeshBasicMaterial({ color: 0x00f0ff });

      const wheelPositions = [
        [-0.85, -0.22, 0.95],
        [0.85, -0.22, 0.95],
        [-0.88, -0.22, -0.95],
        [0.88, -0.22, -0.95]
      ];

      wheelPositions.forEach(pos => {
        const wMesh = new THREE.Mesh(wheelGeo, wheelMat);
        wMesh.rotation.z = Math.PI / 2;
        wMesh.position.set(...pos);
        mainGroup.add(wMesh);

        const bRing = new THREE.RingGeometry(0.12, 0.22, 16);
        const bMesh = new THREE.Mesh(bRing, brakeMat);
        bMesh.position.set(pos[0] * 1.05, pos[1], pos[2]);
        bMesh.rotation.y = pos[0] > 0 ? Math.PI / 2 : -Math.PI / 2;
        mainGroup.add(bMesh);
      });

      mainGroup.rotation.y = -Math.PI / 3.2;
      mainGroup.rotation.x = 0.22;
      scene.add(mainGroup);

      // 1,600 Speed Trail Particles (Wind-tunnel smoke effect)
      const trailCount = 1600;
      const trailGeo = new THREE.BufferGeometry();
      const trailPositions = new Float32Array(trailCount * 3);
      const trailSpeeds = new Float32Array(trailCount);

      for (let i = 0; i < trailCount; i++) {
        const i3 = i * 3;
        trailPositions[i3] = (Math.random() - 0.5) * 5.0;
        trailPositions[i3 + 1] = (Math.random() - 0.5) * 2.8;
        trailPositions[i3 + 2] = (Math.random() - 0.5) * 9.0;
        trailSpeeds[i] = 0.08 + Math.random() * 0.12;
      }

      trailGeo.setAttribute('position', new THREE.BufferAttribute(trailPositions, 3));
      const trailMat = new THREE.PointsMaterial({
        color: 0x00f0ff,
        size: 0.045,
        transparent: true,
        opacity: 0.85,
        blending: THREE.AdditiveBlending
      });
      const speedTrails = new THREE.Points(trailGeo, trailMat);
      scene.add(speedTrails);

      // Lights
      const ambientLight = new THREE.AmbientLight(0xffffff, 0.75);
      scene.add(ambientLight);
      const pointLight1 = new THREE.PointLight(0x00f0ff, 3.2, 60);
      pointLight1.position.set(4, 4, 4);
      scene.add(pointLight1);
      const pointLight2 = new THREE.PointLight(0xef4444, 2.8, 60);
      pointLight2.position.set(-4, -2, 3);
      scene.add(pointLight2);

      // HUD Button Callbacks
      let aeroActive = true;
      window.toggleCustom1 = function(btn) {
        aeroActive = !aeroActive;
        wingMesh.visible = aeroActive;
        if (btn) btn.classList.toggle('active', aeroActive);
        playSpatialTone(aeroActive ? 784 : 440, 'triangle', 0.2);
      };

      let speedFactor = 1.0;
      window.toggleCustom2 = function(btn) {
        speedFactor = speedFactor === 1.0 ? 2.5 : 1.0;
        if (btn) btn.textContent = speedFactor > 1.0 ? 'Speed: 300 MPH' : 'Speed: 200 MPH';
        playSpatialTone(speedFactor > 1.0 ? 880 : 440, 'sine', 0.2);
      };

      const liveries = [
        { name: 'Racing Cyan', body: 0x0f172a, canopy: 0x00f0ff, trail: 0x00f0ff },
        { name: 'Crimson Redline', body: 0x180b0e, canopy: 0xef4444, trail: 0xef4444 },
        { name: 'Stealth Gold', body: 0x17120a, canopy: 0xf59e0b, trail: 0xfbbf24 }
      ];
      let liveryIdx = 0;
      window.cycleCustomTheme = function(btn) {
        liveryIdx = (liveryIdx + 1) % liveries.length;
        const l = liveries[liveryIdx];
        carMat.color.setHex(l.body);
        canopyMat.color.setHex(l.canopy);
        trailMat.color.setHex(l.trail);
        if (btn) btn.textContent = `🎨 ${l.name.split(' ')[0]}`;
        playSpatialTone(659, 'triangle', 0.25);
      };

      function updateSceneAnimation(time, rotSpeed) {
        mainGroup.rotation.y += 0.005 * rotSpeed;
        wingMesh.rotation.x = Math.sin(time * 0.003) * 0.12;

        const tPos = trailGeo.attributes.position.array;
        for (let i = 0; i < trailCount; i++) {
          const i3 = i * 3;
          tPos[i3 + 2] -= trailSpeeds[i] * speedFactor * rotSpeed;
          if (tPos[i3 + 2] < -5.0) {
            tPos[i3 + 2] = 5.0;
            tPos[i3] = (Math.random() - 0.5) * 4.5;
            tPos[i3 + 1] = (Math.random() - 0.5) * 2.5;
          }
        }
        trailGeo.attributes.position.needsUpdate = true;
      }
"""

    elif scene_type == "apple":
        return """
      // --- Domain Scene: Precision Titanium Flagship Device with Triple Optics ---
      const mainGroup = new THREE.Group();

      // Titanium chamfered body
      const bodyGeo = new THREE.BoxGeometry(1.6, 3.1, 0.14);
      const titaniumMat = new THREE.MeshStandardMaterial({
        color: 0x94a3b8,
        metalness: 0.95,
        roughness: 0.22,
        emissive: 0x1e293b
      });
      const phoneBody = new THREE.Mesh(bodyGeo, titaniumMat);
      mainGroup.add(phoneBody);

      // Front OLED Screen
      const screenGeo = new THREE.PlaneGeometry(1.5, 2.96);
      const screenMat = new THREE.MeshStandardMaterial({
        color: 0x0f172a,
        roughness: 0.05,
        metalness: 0.9,
        emissive: 0x0284c7
      });
      const screenMesh = new THREE.Mesh(screenGeo, screenMat);
      screenMesh.position.z = 0.075;
      mainGroup.add(screenMesh);

      // Camera Island Bump
      const bumpGeo = new THREE.BoxGeometry(0.72, 0.72, 0.08);
      const bumpMat = new THREE.MeshStandardMaterial({ color: 0x64748b, metalness: 0.9, roughness: 0.2 });
      const bumpMesh = new THREE.Mesh(bumpGeo, bumpMat);
      bumpMesh.position.set(-0.35, 0.98, -0.09);
      mainGroup.add(bumpMesh);

      // 3 Precision Glass Lens Rings
      const lensGeo = new THREE.CylinderGeometry(0.14, 0.14, 0.06, 24);
      const lensMat = new THREE.MeshStandardMaterial({ color: 0x0284c7, metalness: 0.95, roughness: 0.05 });
      const lensCoords = [[-0.45, 1.15], [-0.45, 0.82], [-0.22, 0.98]];
      lensCoords.forEach(([lx, ly]) => {
        const lMesh = new THREE.Mesh(lensGeo, lensMat);
        lMesh.rotation.x = Math.PI / 2;
        lMesh.position.set(lx, ly, -0.13);
        mainGroup.add(lMesh);
      });

      // Floating Orbital Glass Halo
      const haloGeo = new THREE.TorusGeometry(2.1, 0.025, 16, 64);
      const haloMat = new THREE.MeshBasicMaterial({ color: 0x38bdf8, transparent: true, opacity: 0.55 });
      const haloMesh = new THREE.Mesh(haloGeo, haloMat);
      haloMesh.rotation.x = Math.PI / 3;
      mainGroup.add(haloMesh);

      mainGroup.rotation.y = 0.35;
      mainGroup.rotation.x = 0.15;
      scene.add(mainGroup);

      // 800 Optical Bokeh Sparkle Particles
      const pCount = 800;
      const pGeo = new THREE.BufferGeometry();
      const pPos = new Float32Array(pCount * 3);
      for (let i = 0; i < pCount * 3; i += 3) {
        const r = 2.0 + Math.random() * 3.5;
        const th = Math.random() * Math.PI * 2;
        const ph = (Math.random() - 0.5) * Math.PI;
        pPos[i] = r * Math.cos(th) * Math.cos(ph);
        pPos[i + 1] = r * Math.sin(ph);
        pPos[i + 2] = r * Math.sin(th) * Math.cos(ph);
      }
      pGeo.setAttribute('position', new THREE.BufferAttribute(pPos, 3));
      const pMat = new THREE.PointsMaterial({ color: 0x38bdf8, size: 0.038, transparent: true, opacity: 0.8 });
      const particleSystem = new THREE.Points(pGeo, pMat);
      scene.add(particleSystem);

      // Studio Lights
      const ambientLight = new THREE.AmbientLight(0xffffff, 0.8);
      scene.add(ambientLight);
      const pointLight1 = new THREE.PointLight(0x38bdf8, 3.0, 50);
      pointLight1.position.set(3, 4, 3);
      scene.add(pointLight1);
      const pointLight2 = new THREE.PointLight(0xa855f7, 2.5, 50);
      pointLight2.position.set(-3, -3, 3);
      scene.add(pointLight2);

      // HUD Button Callbacks
      window.toggleCustom1 = function(btn) {
        bumpMesh.visible = !bumpMesh.visible;
        if (btn) btn.classList.toggle('active', bumpMesh.visible);
        playSpatialTone(659, 'sine', 0.2);
      };

      const titaniumFinishes = [
        { name: 'Natural', color: 0x94a3b8 },
        { name: 'Black', color: 0x334155 },
        { name: 'White', color: 0xe2e8f0 },
        { name: 'Blue', color: 0x0284c7 }
      ];
      let finIdx = 0;
      window.toggleCustom2 = function(btn) {
        finIdx = (finIdx + 1) % titaniumFinishes.length;
        const f = titaniumFinishes[finIdx];
        titaniumMat.color.setHex(f.color);
        if (btn) btn.textContent = `Finish: ${f.name}`;
        playSpatialTone(784, 'triangle', 0.2);
      };

      window.cycleCustomTheme = function(btn) {
        haloMesh.visible = !haloMesh.visible;
        if (btn) btn.textContent = haloMesh.visible ? '🎨 Halo: On' : '🎨 Halo: Off';
        playSpatialTone(520, 'sine', 0.18);
      };

      function updateSceneAnimation(time, rotSpeed) {
        mainGroup.rotation.y += 0.007 * rotSpeed;
        haloMesh.rotation.z += 0.004 * rotSpeed;
        particleSystem.rotation.y += 0.001 * rotSpeed;
      }
"""

    elif scene_type == "nature":
        return """
      // --- Domain Scene: Undulating Landscape Terrain with Living Eco-Sphere ---
      const mainGroup = new THREE.Group();

      // Undulating terrain wireframe/solid plane
      const planeGeo = new THREE.PlaneGeometry(3.8, 3.8, 28, 28);
      const planeMat = new THREE.MeshStandardMaterial({
        color: 0x10b981,
        wireframe: true,
        roughness: 0.35,
        metalness: 0.25,
        emissive: 0x064e3b
      });
      const terrainMesh = new THREE.Mesh(planeGeo, planeMat);
      terrainMesh.rotation.x = -Math.PI / 2.3;
      terrainMesh.position.y = -0.7;
      mainGroup.add(terrainMesh);

      // Central Floating Emerald Eco-Sphere
      const sphereGeo = new THREE.IcosahedronGeometry(0.72, 3);
      const sphereMat = new THREE.MeshStandardMaterial({
        color: 0x34d399,
        roughness: 0.15,
        metalness: 0.85,
        emissive: 0x065f46
      });
      const ecoSphere = new THREE.Mesh(sphereGeo, sphereMat);
      ecoSphere.position.y = 0.45;
      mainGroup.add(ecoSphere);

      scene.add(mainGroup);

      // 1,200 Bio-Spore & Pollen Dust Particles
      const sporeCount = 1200;
      const sporeGeo = new THREE.BufferGeometry();
      const sporePositions = new Float32Array(sporeCount * 3);
      for (let i = 0; i < sporeCount * 3; i += 3) {
        sporePositions[i] = (Math.random() - 0.5) * 4.8;
        sporePositions[i + 1] = (Math.random() - 0.5) * 3.2;
        sporePositions[i + 2] = (Math.random() - 0.5) * 4.8;
      }
      sporeGeo.setAttribute('position', new THREE.BufferAttribute(sporePositions, 3));
      const sporeMat = new THREE.PointsMaterial({
        color: 0x10b981,
        size: 0.042,
        transparent: true,
        opacity: 0.85
      });
      const sporeSystem = new THREE.Points(sporeGeo, sporeMat);
      scene.add(sporeSystem);

      // Lights
      const ambientLight = new THREE.AmbientLight(0xf0fdf4, 0.8);
      scene.add(ambientLight);
      const pointLight1 = new THREE.PointLight(0x10b981, 3.2, 50);
      pointLight1.position.set(3, 4, 3);
      scene.add(pointLight1);
      const pointLight2 = new THREE.PointLight(0xfacc15, 2.4, 50);
      pointLight2.position.set(-3, -2, 3);
      scene.add(pointLight2);

      // HUD Button Callbacks
      let waveActive = true;
      window.toggleCustom1 = function(btn) {
        waveActive = !waveActive;
        if (btn) btn.classList.toggle('active', waveActive);
        playSpatialTone(waveActive ? 659 : 440, 'sine', 0.2);
      };

      let windSpeed = 1.0;
      window.toggleCustom2 = function(btn) {
        windSpeed = windSpeed === 1.0 ? 2.2 : 1.0;
        if (btn) btn.textContent = `Wind: ${windSpeed}x`;
        playSpatialTone(windSpeed > 1.0 ? 784 : 440, 'triangle', 0.2);
      };

      window.cycleCustomTheme = function(btn) {
        planeMat.wireframe = !planeMat.wireframe;
        if (btn) btn.textContent = planeMat.wireframe ? '🎨 Wireframe' : '🎨 Solid';
        playSpatialTone(520, 'sine', 0.18);
      };

      function updateSceneAnimation(time, rotSpeed) {
        mainGroup.rotation.y += 0.005 * rotSpeed;
        ecoSphere.position.y = 0.45 + Math.sin(time * 0.003) * 0.12;

        if (waveActive) {
          const pos = planeGeo.attributes.position.array;
          for (let i = 0; i < pos.length; i += 3) {
            const u = pos[i];
            const v = pos[i + 1];
            pos[i + 2] = Math.sin(u * 1.6 + time * 0.002 * windSpeed) * 0.26 + Math.cos(v * 1.6 + time * 0.002 * windSpeed) * 0.26;
          }
          planeGeo.attributes.position.needsUpdate = true;
        }
        sporeSystem.rotation.y += 0.001 * windSpeed * rotSpeed;
      }
"""

    elif scene_type == "fitness":
        return """
      // --- Domain Scene: Dynamic Kinetic Dumbbell Core with Fiery Embers ---
      const mainGroup = new THREE.Group();

      // Hexagonal central hub
      const hexGeo = new THREE.CylinderGeometry(0.68, 0.68, 0.48, 6);
      const hexMat = new THREE.MeshStandardMaterial({
        color: 0xf97316,
        metalness: 0.85,
        roughness: 0.2,
        emissive: 0x7c2d12
      });
      const hexMesh = new THREE.Mesh(hexGeo, hexMat);
      mainGroup.add(hexMesh);

      // Opposed Barbells
      const barGeo = new THREE.CylinderGeometry(0.08, 0.08, 2.2, 16);
      const barMat = new THREE.MeshStandardMaterial({ color: 0x3f3f46, metalness: 0.95 });
      const barMesh = new THREE.Mesh(barGeo, barMat);
      barMesh.rotation.z = Math.PI / 4;
      mainGroup.add(barMesh);

      // Kinetic Energy Orbit Rings
      const ringGeo1 = new THREE.TorusGeometry(1.4, 0.04, 16, 48);
      const ringMat1 = new THREE.MeshBasicMaterial({ color: 0xef4444, transparent: true, opacity: 0.75 });
      const rMesh1 = new THREE.Mesh(ringGeo1, ringMat1);
      mainGroup.add(rMesh1);

      const ringGeo2 = new THREE.TorusGeometry(1.65, 0.04, 16, 48);
      const ringMat2 = new THREE.MeshBasicMaterial({ color: 0xf97316, transparent: true, opacity: 0.65 });
      const rMesh2 = new THREE.Mesh(ringGeo2, ringMat2);
      rMesh2.rotation.x = Math.PI / 2.5;
      mainGroup.add(rMesh2);

      scene.add(mainGroup);

      // 1,400 Fiery Dynamic Embers
      const emberCount = 1400;
      const emberGeo = new THREE.BufferGeometry();
      const emberPositions = new Float32Array(emberCount * 3);
      for (let i = 0; i < emberCount * 3; i += 3) {
        const rad = 0.8 + Math.random() * 2.8;
        const th = Math.random() * Math.PI * 2;
        const ph = (Math.random() - 0.5) * Math.PI;
        emberPositions[i] = rad * Math.cos(th) * Math.cos(ph);
        emberPositions[i + 1] = rad * Math.sin(ph);
        emberPositions[i + 2] = rad * Math.sin(th) * Math.cos(ph);
      }
      emberGeo.setAttribute('position', new THREE.BufferAttribute(emberPositions, 3));
      const emberMat = new THREE.PointsMaterial({ color: 0xf97316, size: 0.048, transparent: true, opacity: 0.85 });
      const emberSystem = new THREE.Points(emberGeo, emberMat);
      scene.add(emberSystem);

      // Lights
      const ambientLight = new THREE.AmbientLight(0xffedd5, 0.8);
      scene.add(ambientLight);
      const pointLight1 = new THREE.PointLight(0xf97316, 3.2, 50);
      pointLight1.position.set(3, 4, 3);
      scene.add(pointLight1);
      const pointLight2 = new THREE.PointLight(0xef4444, 2.6, 50);
      pointLight2.position.set(-3, -2, 3);
      scene.add(pointLight2);

      // HUD Button Callbacks
      let burstPulse = 1.0;
      window.toggleCustom1 = function(btn) {
        burstPulse = 1.5;
        playSpatialTone(880, 'triangle', 0.25);
      };

      let paceSpeed = 1.0;
      window.toggleCustom2 = function(btn) {
        paceSpeed = paceSpeed === 1.0 ? 2.4 : 1.0;
        if (btn) btn.textContent = `Pace: ${paceSpeed}x`;
        playSpatialTone(paceSpeed > 1.0 ? 784 : 440, 'sine', 0.2);
      };

      window.cycleCustomTheme = function(btn) {
        hexMat.wireframe = !hexMat.wireframe;
        if (btn) btn.textContent = hexMat.wireframe ? '🎨 Wireframe' : '🎨 Solid';
        playSpatialTone(520, 'sine', 0.18);
      };

      function updateSceneAnimation(time, rotSpeed) {
        mainGroup.rotation.y += 0.012 * paceSpeed * rotSpeed;
        rMesh1.rotation.x += 0.01 * rotSpeed;
        rMesh2.rotation.y -= 0.01 * rotSpeed;
        if (burstPulse > 1.0) burstPulse -= 0.02;
        hexMesh.scale.set(burstPulse, burstPulse, burstPulse);
        emberSystem.rotation.y += 0.002 * paceSpeed * rotSpeed;
      }
"""

    elif scene_type == "business":
        return """
      // --- Domain Scene: Logarithmic Growth Candlestick Pillars with Capital Flow ---
      const mainGroup = new THREE.Group();

      const pillarMat = new THREE.MeshStandardMaterial({
        color: 0x10b981,
        metalness: 0.88,
        roughness: 0.18,
        emissive: 0x064e3b
      });

      const pillars = [];
      for (let i = 0; i < 5; i++) {
        const h = 0.8 + i * 0.45;
        const pGeo = new THREE.BoxGeometry(0.35, h, 0.35);
        const pMesh = new THREE.Mesh(pGeo, pillarMat);
        pMesh.position.set(-1.2 + i * 0.6, h / 2 - 1.0, 0);
        mainGroup.add(pMesh);
        pillars.push({ mesh: pMesh, baseH: h });
      }

      // Glowing Trend Vector Beam
      const beamGeo = new THREE.CylinderGeometry(0.04, 0.04, 3.2, 16);
      const beamMat = new THREE.MeshBasicMaterial({ color: 0xf59e0b });
      const beamMesh = new THREE.Mesh(beamGeo, beamMat);
      beamMesh.rotation.z = -Math.PI / 3.4;
      beamMesh.position.set(0, 0.2, 0.25);
      mainGroup.add(beamMesh);

      mainGroup.rotation.y = -0.32;
      scene.add(mainGroup);

      // 1,200 Golden Capital Flow Particles
      const goldCount = 1200;
      const goldGeo = new THREE.BufferGeometry();
      const goldPositions = new Float32Array(goldCount * 3);
      for (let i = 0; i < goldCount * 3; i += 3) {
        goldPositions[i] = (Math.random() - 0.5) * 4.5;
        goldPositions[i + 1] = -1.2 + Math.random() * 3.2;
        goldPositions[i + 2] = (Math.random() - 0.5) * 3.5;
      }
      goldGeo.setAttribute('position', new THREE.BufferAttribute(goldPositions, 3));
      const goldMat = new THREE.PointsMaterial({ color: 0xf59e0b, size: 0.045, transparent: true, opacity: 0.85 });
      const goldSystem = new THREE.Points(goldGeo, goldMat);
      scene.add(goldSystem);

      // Lights
      const ambientLight = new THREE.AmbientLight(0xf8fafc, 0.8);
      scene.add(ambientLight);
      const pointLight1 = new THREE.PointLight(0x10b981, 3.0, 50);
      pointLight1.position.set(3, 4, 3);
      scene.add(pointLight1);
      const pointLight2 = new THREE.PointLight(0xf59e0b, 2.5, 50);
      pointLight2.position.set(-3, -2, 3);
      scene.add(pointLight2);

      // HUD Button Callbacks
      let bullMode = true;
      window.toggleCustom1 = function(btn) {
        bullMode = !bullMode;
        pillarMat.color.setHex(bullMode ? 0x10b981 : 0x0284c7);
        if (btn) btn.textContent = bullMode ? 'Pillars: Bull' : 'Pillars: Yield';
        playSpatialTone(bullMode ? 784 : 520, 'sine', 0.2);
      };

      let velSpeed = 1.0;
      window.toggleCustom2 = function(btn) {
        velSpeed = velSpeed === 1.0 ? 2.2 : 1.0;
        if (btn) btn.textContent = `Velocity: ${velSpeed}x`;
        playSpatialTone(velSpeed > 1.0 ? 880 : 440, 'triangle', 0.2);
      };

      window.cycleCustomTheme = function(btn) {
        beamMesh.visible = !beamMesh.visible;
        if (btn) btn.textContent = beamMesh.visible ? '🎨 Trend: On' : '🎨 Trend: Off';
        playSpatialTone(659, 'sine', 0.18);
      };

      function updateSceneAnimation(time, rotSpeed) {
        mainGroup.rotation.y += 0.005 * rotSpeed;
        pillars.forEach((p, idx) => {
          const osc = 1.0 + Math.sin(time * 0.003 + idx) * 0.12;
          p.mesh.scale.set(1.0, osc, 1.0);
        });
        goldSystem.rotation.y += 0.001 * velSpeed * rotSpeed;
      }
"""

    else:
        # Default: Hyper-dimensional Quantum Torus Knot with pulsing crystalline nucleus
        return """
      // --- Domain Scene: Hyper-Dimensional Quantum Torus Knot & Electron Cloud ---
      const mainGroup = new THREE.Group();

      const knotGeo = new THREE.TorusKnotGeometry(1.05, 0.32, 128, 32);
      const knotMat = new THREE.MeshStandardMaterial({
        color: 0x00f0ff,
        roughness: 0.25,
        metalness: 0.85,
        wireframe: true,
        emissive: 0x022b3a
      });
      const knotMesh = new THREE.Mesh(knotGeo, knotMat);
      mainGroup.add(knotMesh);

      // Inner Glowing Core (Icosahedron Nucleus)
      const coreGeo = new THREE.IcosahedronGeometry(0.55, 2);
      const coreMat = new THREE.MeshStandardMaterial({
        color: 0x8b5cf6,
        wireframe: false,
        roughness: 0.12,
        metalness: 0.9,
        emissive: 0x3b0764
      });
      const coreMesh = new THREE.Mesh(coreGeo, coreMat);
      mainGroup.add(coreMesh);

      // Orbiting Cyber Ring
      const ringGeo = new THREE.RingGeometry(1.65, 1.72, 64);
      const ringMat = new THREE.MeshBasicMaterial({
        color: 0x00f0ff,
        side: THREE.DoubleSide,
        transparent: true,
        opacity: 0.45
      });
      const ringMesh = new THREE.Mesh(ringGeo, ringMat);
      ringMesh.rotation.x = Math.PI / 2.5;
      mainGroup.add(ringMesh);

      scene.add(mainGroup);

      // 2,000 Particle Orbital Nebula
      const particleCount = 2000;
      const pGeometry = new THREE.BufferGeometry();
      const positions = new Float32Array(particleCount * 3);
      const basePositions = new Float32Array(particleCount * 3);

      for (let i = 0; i < particleCount * 3; i += 3) {
        const r = 2.0 + Math.random() * 4.5;
        const theta = Math.random() * Math.PI * 2;
        const phi = (Math.random() - 0.5) * Math.PI;
        positions[i] = r * Math.cos(theta) * Math.cos(phi);
        positions[i + 1] = r * Math.sin(phi);
        positions[i + 2] = r * Math.sin(theta) * Math.cos(phi);
        basePositions[i] = positions[i];
        basePositions[i + 1] = positions[i + 1];
        basePositions[i + 2] = positions[i + 2];
      }

      pGeometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
      const pMaterial = new THREE.PointsMaterial({
        color: 0x00f0ff,
        size: 0.038,
        transparent: true,
        opacity: 0.8
      });
      const particleSystem = new THREE.Points(pGeometry, pMaterial);
      scene.add(particleSystem);

      // Lights
      const ambientLight = new THREE.AmbientLight(0xffffff, 0.7);
      scene.add(ambientLight);
      const pointLight1 = new THREE.PointLight(0x00f0ff, 2.8, 60);
      pointLight1.position.set(4, 4, 4);
      scene.add(pointLight1);
      const pointLight2 = new THREE.PointLight(0x8b5cf6, 2.4, 60);
      pointLight2.position.set(-4, -3, 3);
      scene.add(pointLight2);

      // HUD Button Callbacks
      let isWireframe = true;
      window.toggleCustom1 = function(btn) {
        isWireframe = !isWireframe;
        knotMat.wireframe = isWireframe;
        if (btn) btn.classList.toggle('active', isWireframe);
        playSpatialTone(isWireframe ? 520 : 640, 'sine', 0.18);
      };

      let rotSpeedFactor = 1.0;
      window.toggleCustom2 = function(btn) {
        rotSpeedFactor = rotSpeedFactor === 1.0 ? 2.4 : 1.0;
        if (controls) controls.autoRotateSpeed = 1.3 * rotSpeedFactor;
        if (btn) btn.textContent = rotSpeedFactor === 1.0 ? 'Speed: 1x' : 'Speed: 2.4x';
        playSpatialTone(rotSpeedFactor > 1.0 ? 880 : 440, 'triangle', 0.2);
      };

      const themes = [
        { name: 'Cyan', color: 0x00f0ff, emissive: 0x022b3a, light: 0x00f0ff },
        { name: 'Violet', color: 0x8b5cf6, emissive: 0x2e1065, light: 0xa855f7 },
        { name: 'Emerald', color: 0x10b981, emissive: 0x064e3b, light: 0x34d399 },
        { name: 'Amber', color: 0xf59e0b, emissive: 0x451a03, light: 0xfbbf24 }
      ];
      let themeIdx = 0;
      window.cycleCustomTheme = function(btn) {
        themeIdx = (themeIdx + 1) % themes.length;
        const t = themes[themeIdx];
        knotMat.color.setHex(t.color);
        knotMat.emissive.setHex(t.emissive);
        pMaterial.color.setHex(t.light);
        ringMat.color.setHex(t.color);
        pointLight1.color.setHex(t.light);
        if (btn) btn.textContent = `🎨 ${t.name}`;
        playSpatialTone(587, 'sine', 0.25);
      };

      function updateSceneAnimation(time, rotSpeed) {
        knotMesh.rotation.y += 0.008 * rotSpeedFactor * rotSpeed;
        knotMesh.rotation.x += 0.005 * rotSpeedFactor * rotSpeed;
        const pulse = 1.0 + Math.sin(time * 0.003) * 0.08;
        coreMesh.scale.set(pulse, pulse, pulse);
        coreMesh.rotation.y -= 0.012 * rotSpeedFactor * rotSpeed;
        ringMesh.rotation.z += 0.004 * rotSpeedFactor * rotSpeed;
        particleSystem.rotation.y += 0.0012 * rotSpeedFactor * rotSpeed;
      }
"""


def get_free_port() -> int:
    """Finds an unused local TCP port."""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("localhost", 0))
    port = s.getsockname()[1]
    s.close()
    return port


def serve_directory(directory: str, port: int):
    """Spins up a lightweight static HTTP server for the generated web application."""
    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=directory, **kwargs)
        def log_message(self, format, *args):
            pass  # Suppress console HTTP access logs

    with socketserver.TCPServer(("", port), Handler) as httpd:
        httpd.serve_forever()


def generate_advanced_flagship_html(topic: str) -> str:
    """
    Autonomous Master Web Designer Engine (Domain-Adaptive 3D WebGL & Spatial Web Architecture):
    Constructs an advanced, 3D-enhanced, multi-section flagship web application featuring:
    1. Domain-Specific Three.js WebGL Scene (Coffee Cup + Steam, Hypercar + Speed Trails,
       Titanium Phone + Optics, Undulating Terrain + Bio-Spores, Kinetic Barbell + Embers,
       Growth Pillars + Golden Vectors, or Quantum Torus Knot + Electron Nebula).
    2. Dynamic CSS Token Palette and typography tailored to the industry mood.
    3. Interactive 3D HUD controls: live wireframe/steam toggles, speed controls, and audio synth.
    4. True CSS 3D Stereoscopic Card Tilt Physics (perspective: 1200px, preserve-3d, translateZ depth).
    5. Domain-Specific Live Stat Counters, Features, Showcases, and Verified Testimonials.
    """
    profile = _detect_thematic_profile(topic)
    c = profile["colors"]
    brand_name = profile["brand_name"]
    brand_icon = profile["brand_icon"]
    images = profile["images"]

    hero_img, hero_alt = images[0]
    card_img_1, card_alt_1 = images[1]
    card_img_2, card_alt_2 = images[2]
    card_img_3, card_alt_3 = images[3]

    threejs_scene_code = _generate_threejs_scene_code(profile)

    # Dispatch to Bespoke Domain Layout Architectures (Banning Cookie-Cutter Monoliths)
    domain = profile.get("domain", "quantum")
    try:
        import web_architect_layout_templates
        import importlib
        importlib.reload(web_architect_layout_templates)
        if domain == "fitness":
            return web_architect_layout_templates.build_fitness_layout(profile, threejs_scene_code)
        elif domain in ["coffee", "culinary", "food"]:
            return web_architect_layout_templates.build_culinary_layout(profile, threejs_scene_code)
        elif domain in ["automotive", "car"]:
            return web_architect_layout_templates.build_automotive_layout(profile, threejs_scene_code)
        elif domain in ["cybersecurity", "security", "soc"]:
            return web_architect_layout_templates.build_cybersecurity_layout(profile, threejs_scene_code)
        elif domain in ["luxury_watch", "horlogerie", "watch"]:
            return web_architect_layout_templates.build_luxury_watch_layout(profile, threejs_scene_code)
        elif domain in ["aerospace", "space", "orbital"]:
            return web_architect_layout_templates.build_aerospace_layout(profile, threejs_scene_code)
        elif domain in ["business", "finance", "quant"]:
            return web_architect_layout_templates.build_finance_layout(profile, threejs_scene_code)
        elif domain in ["music_synth", "audio", "music"]:
            return web_architect_layout_templates.build_music_synth_layout(profile, threejs_scene_code)
        elif domain in ["biotech", "genomics"]:
            return web_architect_layout_templates.build_biotech_layout(profile, threejs_scene_code)
        elif domain in ["architecture", "real_estate"]:
            return web_architect_layout_templates.build_architecture_layout(profile, threejs_scene_code)
        else:
            return web_architect_layout_templates.build_adaptive_layout(profile, threejs_scene_code)
    except Exception as e:
        print(f"[WebArchitect] Bespoke layout dispatch warning: {e}")

    # Build Stat HTML
    stats_html = "".join([
        f'<div class="stat-item"><h3>{val}</h3><p>{label}</p></div>'
        for val, label in profile["stats"]
    ])

    # Build Features HTML
    f1, f2, f3 = profile["features"]
    features_html = f"""
      <div class="feature-card">
        <div class="feature-img-box">
          <img src="{card_img_1}" alt="{card_alt_1}" loading="lazy">
        </div>
        <div class="feature-body">
          <span class="feature-tag">{f1[0]}</span>
          <h3>{f1[1]}</h3>
          <p>{f1[2]}</p>
          <a href="#get-started" class="card-link">{f1[3]}</a>
        </div>
      </div>

      <div class="feature-card">
        <div class="feature-img-box">
          <img src="{card_img_2}" alt="{card_alt_2}" loading="lazy">
        </div>
        <div class="feature-body">
          <span class="feature-tag">{f2[0]}</span>
          <h3>{f2[1]}</h3>
          <p>{f2[2]}</p>
          <a href="#get-started" class="card-link">{f2[3]}</a>
        </div>
      </div>

      <div class="feature-card">
        <div class="feature-img-box">
          <img src="{card_img_3}" alt="{card_alt_3}" loading="lazy">
        </div>
        <div class="feature-body">
          <span class="feature-tag">{f3[0]}</span>
          <h3>{f3[1]}</h3>
          <p>{f3[2]}</p>
          <a href="#get-started" class="card-link">{f3[3]}</a>
        </div>
      </div>
    """

    # Build Testimonials HTML
    t1, t2 = profile["testimonials"]
    testimonials_html = f"""
      <div class="testimonial-card">
        <div class="stars">{t1[0]}</div>
        <p class="quote-text">"{t1[1]}"</p>
        <div class="client-info">
          <img src="{t1[4]}" alt="{t1[2]}" class="client-avatar">
          <div>
            <div class="client-name">{t1[2]}</div>
            <div class="client-role">{t1[3]}</div>
          </div>
        </div>
      </div>

      <div class="testimonial-card">
        <div class="stars">{t2[0]}</div>
        <p class="quote-text">"{t2[1]}"</p>
        <div class="client-info">
          <img src="{t2[4]}" alt="{t2[2]}" class="client-avatar">
          <div>
            <div class="client-name">{t2[2]}</div>
            <div class="client-role">{t2[3]}</div>
          </div>
        </div>
      </div>
    """

    # Build FAQs HTML
    faqs_html = "".join([
        f'<details><summary>{q}</summary><p>{a}</p></details>'
        for q, a in profile["faqs"]
    ])

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=5.0">
  <title>{brand_name} | Advanced 3D Spatial Experience</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800;900&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
  <!-- Three.js WebGL 3D Spatial Library & OrbitControls -->
  <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
  <style>
    :root {{
      --bg: {c["bg"]};
      --surface: {c["surface"]};
      --surface-glass: {c["surface_glass"]};
      --surface-border: {c["surface_border"]};
      --surface-border-hover: {c["surface_border_hover"]};
      --primary: {c["primary"]};
      --primary-glow: {c["primary_glow"]};
      --accent: {c["accent"]};
      --accent-glow: {c["accent_glow"]};
      --emerald: #10b981;
      --text: {c["text"]};
      --text-muted: {c["text_muted"]};
      --radius-lg: 24px;
      --radius-md: 16px;
      --radius-sm: 10px;
      --transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
    }}

    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    html {{ scroll-behavior: smooth; font-family: 'Plus Jakarta Sans', sans-serif; background: var(--bg); color: var(--text); }}
    body {{ overflow-x: hidden; min-height: 100vh; line-height: 1.6; }}

    /* Ambient background glow spheres */
    .ambient-glow-1 {{
      position: fixed; width: 680px; height: 680px; border-radius: 50%;
      background: radial-gradient(circle, var(--primary-glow) 0%, rgba(0,0,0,0) 70%);
      top: -220px; left: -200px; z-index: -1; pointer-events: none; filter: blur(80px);
    }}
    .ambient-glow-2 {{
      position: fixed; width: 580px; height: 580px; border-radius: 50%;
      background: radial-gradient(circle, var(--accent-glow) 0%, rgba(0,0,0,0) 70%);
      bottom: -160px; right: -150px; z-index: -1; pointer-events: none; filter: blur(80px);
    }}

    /* Navigation */
    nav {{
      position: sticky; top: 0; z-index: 100;
      backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px);
      background: rgba(10, 14, 22, 0.85);
      border-bottom: 1px solid var(--surface-border);
      padding: 16px 32px; display: flex; align-items: center; justify-content: space-between;
    }}
    .nav-brand {{
      display: flex; align-items: center; gap: 12px; font-family: 'Outfit', sans-serif;
      font-size: 1.35rem; font-weight: 800; color: var(--text); text-decoration: none;
      letter-spacing: -0.5px;
    }}
    .brand-icon {{
      width: 40px; height: 40px; border-radius: 10px;
      background: linear-gradient(135deg, var(--primary), var(--accent));
      display: flex; align-items: center; justify-content: center; color: #000;
      font-weight: 900; font-size: 1.25rem; box-shadow: 0 0 20px var(--primary-glow);
    }}
    .nav-links {{ display: flex; gap: 28px; list-style: none; align-items: center; }}
    .nav-links a {{
      color: var(--text-muted); text-decoration: none; font-size: 0.95rem; font-weight: 500;
      transition: var(--transition);
    }}
    .nav-links a:hover {{ color: var(--primary); }}
    .nav-cta {{
      background: linear-gradient(135deg, var(--primary), var(--accent)); color: #fff !important;
      padding: 10px 22px; border-radius: var(--radius-sm); font-weight: 700 !important;
      box-shadow: 0 4px 15px var(--primary-glow); transition: var(--transition);
    }}
    .nav-cta:hover {{ transform: translateY(-2px); box-shadow: 0 6px 25px var(--primary-glow); }}

    /* Hero Section */
    .hero {{
      max-width: 1320px; margin: 0 auto; padding: 70px 24px 60px;
      display: grid; grid-template-columns: 1fr 1fr; gap: 50px; align-items: center;
    }}
    .hero-badge {{
      display: inline-flex; align-items: center; gap: 8px;
      padding: 6px 16px; border-radius: 30px; background: rgba(255, 255, 255, 0.05);
      border: 1px solid var(--surface-border-hover); color: var(--primary);
      font-size: 0.82rem; font-weight: 700; text-transform: uppercase; letter-spacing: 1px;
      margin-bottom: 24px;
    }}
    .pulse-dot {{
      width: 8px; height: 8px; border-radius: 50%; background: var(--emerald);
      box-shadow: 0 0 10px var(--emerald); animation: pulse 2s infinite;
    }}
    @keyframes pulse {{
      0%, 100% {{ transform: scale(1); opacity: 1; }}
      50% {{ transform: scale(1.4); opacity: 0.6; }}
    }}
    .hero h1 {{
      font-family: 'Outfit', sans-serif; font-size: 3.4rem; font-weight: 900;
      line-height: 1.12; letter-spacing: -1.5px; margin-bottom: 20px;
    }}
    .gradient-text {{
      background: linear-gradient(135deg, #ffffff 25%, var(--primary) 70%, var(--accent) 100%);
      -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }}
    .hero p {{
      color: var(--text-muted); font-size: 1.15rem; line-height: 1.7; margin-bottom: 34px;
      max-width: 520px;
    }}
    .hero-actions {{ display: flex; gap: 16px; align-items: center; flex-wrap: wrap; margin-bottom: 28px; }}
    .btn-primary {{
      background: linear-gradient(135deg, var(--primary), var(--accent)); color: #fff;
      padding: 16px 36px; border-radius: var(--radius-md); font-weight: 700;
      text-decoration: none; font-size: 1.05rem; box-shadow: 0 10px 30px var(--primary-glow);
      transition: var(--transition); display: inline-flex; align-items: center; gap: 10px;
    }}
    .btn-primary:hover {{ transform: translateY(-3px); box-shadow: 0 15px 40px var(--primary-glow); }}
    .btn-secondary {{
      background: var(--surface-glass); color: var(--text); padding: 16px 28px;
      border-radius: var(--radius-md); font-weight: 600; text-decoration: none;
      border: 1px solid var(--surface-border); transition: var(--transition);
    }}
    .btn-secondary:hover {{ border-color: var(--primary); background: rgba(255,255,255,0.08); }}

    /* 3D WebGL Spatial Canvas Hero Viewport */
    .canvas-3d-wrapper {{
      position: relative; width: 100%; height: 460px;
      border-radius: var(--radius-lg); overflow: hidden;
      border: 1px solid var(--surface-border);
      background: radial-gradient(circle at center, rgba(25, 30, 45, 0.4) 0%, rgba(8, 10, 15, 0.95) 100%);
      box-shadow: 0 25px 60px rgba(0,0,0,0.8), 0 0 45px var(--primary-glow);
    }}
    #webgl-canvas-container {{
      width: 100%; height: 100%; display: block; position: relative; cursor: grab;
    }}
    #webgl-canvas-container:active {{ cursor: grabbing; }}
    .canvas-3d-hud {{
      position: absolute; top: 16px; left: 18px; right: 18px;
      display: flex; justify-content: space-between; align-items: center;
      pointer-events: none; z-index: 10;
    }}
    .hud-pill {{
      display: inline-flex; align-items: center; gap: 8px;
      padding: 6px 14px; background: rgba(10, 15, 25, 0.85);
      backdrop-filter: blur(16px); -webkit-backdrop-filter: blur(16px);
      border: 1px solid var(--surface-border-hover); border-radius: 30px;
      font-size: 0.72rem; font-weight: 700; color: var(--primary);
      letter-spacing: 0.8px; text-transform: uppercase;
    }}
    .hud-controls {{
      pointer-events: auto; display: flex; gap: 8px;
    }}
    .hud-btn {{
      background: rgba(14, 20, 32, 0.85); border: 1px solid var(--surface-border);
      color: var(--text-muted); padding: 6px 12px; border-radius: 8px;
      font-size: 0.75rem; font-weight: 600; cursor: pointer; transition: var(--transition);
    }}
    .hud-btn:hover, .hud-btn.active {{
      background: rgba(255, 255, 255, 0.12); border-color: var(--primary); color: #fff;
    }}

    .floating-glass-card {{
      position: absolute; bottom: 16px; left: 18px; z-index: 10;
      background: rgba(10, 15, 25, 0.85); backdrop-filter: blur(25px);
      border: 1px solid var(--surface-border-hover); border-radius: var(--radius-md);
      padding: 14px 20px; box-shadow: 0 15px 35px rgba(0,0,0,0.6);
      display: flex; align-items: center; gap: 14px; pointer-events: none;
    }}
    .metric-bubble {{
      width: 40px; height: 40px; border-radius: 10px; background: var(--primary-glow);
      color: var(--primary); display: flex; align-items: center; justify-content: center;
      font-size: 1.25rem; font-weight: 900;
    }}
    .metric-label {{ font-size: 0.72rem; text-transform: uppercase; color: var(--text-muted); font-weight: 700; }}
    .metric-val {{ font-family: 'Outfit', sans-serif; font-size: 1.15rem; font-weight: 800; color: #fff; }}

    /* Stat Counter Strip */
    .stat-strip {{
      max-width: 1320px; margin: 40px auto 80px; padding: 32px;
      background: var(--surface-glass); backdrop-filter: blur(20px);
      border: 1px solid var(--surface-border); border-radius: var(--radius-lg);
      display: grid; grid-template-columns: repeat(4, 1fr); gap: 24px; text-align: center;
    }}
    .stat-item h3 {{ font-family: 'Outfit', sans-serif; font-size: 2.5rem; font-weight: 800; color: var(--primary); margin-bottom: 4px; }}
    .stat-item p {{ color: var(--text-muted); font-size: 0.9rem; font-weight: 500; text-transform: uppercase; letter-spacing: 0.5px; }}

    /* Features Grid with True CSS 3D Depth & Mouse Parallax Tilt */
    .section-header {{ text-align: center; max-width: 680px; margin: 0 auto 60px; }}
    .section-tag {{ color: var(--primary); font-size: 0.85rem; font-weight: 700; text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 12px; display: block; }}
    .section-header h2 {{ font-family: 'Outfit', sans-serif; font-size: 2.6rem; font-weight: 800; letter-spacing: -1px; }}

    .features-grid {{
      max-width: 1320px; margin: 0 auto 100px; padding: 0 24px;
      display: grid; grid-template-columns: repeat(3, 1fr); gap: 32px;
      perspective: 1200px;
    }}
    .feature-card {{
      background: var(--surface-glass); border: 1px solid var(--surface-border);
      border-radius: var(--radius-lg); overflow: hidden;
      display: flex; flex-direction: column; position: relative;
      transform-style: preserve-3d;
      transform: perspective(1000px) rotateX(0deg) rotateY(0deg);
      transition: transform 0.15s ease-out, border-color 0.3s, box-shadow 0.3s;
      will-change: transform;
    }}
    .feature-card:hover {{
      border-color: var(--surface-border-hover);
      box-shadow: 0 25px 50px rgba(0,0,0,0.6), 0 0 35px var(--primary-glow);
    }}
    .feature-card::after {{
      content: ''; position: absolute; inset: 0; border-radius: var(--radius-lg);
      background: radial-gradient(circle at var(--mouse-x, 50%) var(--mouse-y, 50%), rgba(255,255,255,0.14) 0%, transparent 60%);
      pointer-events: none; opacity: 0; transition: opacity 0.3s; transform: translateZ(50px);
    }}
    .feature-card:hover::after {{ opacity: 1; }}

    .feature-img-box {{ height: 210px; overflow: hidden; position: relative; transform: translateZ(25px); transform-style: preserve-3d; }}
    .feature-img-box img {{
      width: 100%; height: 100%; object-fit: cover; transition: transform 0.6s ease;
    }}
    .feature-card:hover .feature-img-box img {{ transform: scale(1.08); }}
    .feature-body {{ padding: 28px; flex: 1; display: flex; flex-direction: column; transform: translateZ(35px); transform-style: preserve-3d; }}
    .feature-tag {{
      display: inline-block; padding: 4px 10px; background: rgba(255, 255, 255, 0.08);
      color: var(--primary); border-radius: 8px; font-size: 0.75rem; font-weight: 700;
      margin-bottom: 14px; text-transform: uppercase; transform: translateZ(40px);
    }}
    .feature-body h3 {{ font-family: 'Outfit', sans-serif; font-size: 1.35rem; font-weight: 700; margin-bottom: 10px; transform: translateZ(20px); }}
    .feature-body p {{ color: var(--text-muted); font-size: 0.95rem; line-height: 1.6; margin-bottom: 20px; transform: translateZ(15px); }}
    .card-link {{ margin-top: auto; color: var(--primary); font-weight: 700; font-size: 0.9rem; text-decoration: none; display: inline-flex; align-items: center; gap: 6px; transform: translateZ(25px); }}
    .card-link:hover {{ text-decoration: underline; }}

    /* 3D Visual Showcase Gallery */
    .showcase-section {{ max-width: 1320px; margin: 0 auto 100px; padding: 0 24px; }}
    .showcase-grid {{ display: grid; grid-template-columns: 1.2fr 0.8fr; gap: 28px; align-items: center; }}
    .showcase-img-card {{
      border-radius: var(--radius-lg); overflow: hidden; border: 1px solid var(--surface-border);
      box-shadow: 0 20px 45px rgba(0,0,0,0.6); position: relative;
    }}
    .showcase-img-card img {{ width: 100%; height: 100%; object-fit: cover; display: block; }}
    .showcase-desc {{ padding: 20px; }}
    .showcase-desc h3 {{ font-family: 'Outfit', sans-serif; font-size: 2rem; font-weight: 800; margin-bottom: 16px; }}
    .showcase-desc p {{ color: var(--text-muted); font-size: 1.05rem; line-height: 1.7; margin-bottom: 24px; }}

    /* Testimonials Section */
    .testimonials {{
      max-width: 1320px; margin: 0 auto 100px; padding: 0 24px;
    }}
    .testimonial-grid {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 32px; }}
    .testimonial-card {{
      background: var(--surface-glass); border: 1px solid var(--surface-border);
      border-radius: var(--radius-lg); padding: 36px; position: relative;
    }}
    .stars {{ color: #fbbf24; font-size: 1.1rem; margin-bottom: 16px; }}
    .quote-text {{ font-size: 1.05rem; line-height: 1.7; color: #e2e8f0; margin-bottom: 24px; font-style: italic; }}
    .client-info {{ display: flex; align-items: center; gap: 14px; }}
    .client-avatar {{ width: 48px; height: 48px; border-radius: 50%; object-fit: cover; border: 2px solid var(--primary); }}
    .client-name {{ font-weight: 700; font-size: 1rem; color: #fff; }}
    .client-role {{ font-size: 0.85rem; color: var(--text-muted); }}

    /* Interactive FAQ */
    .faq-section {{ max-width: 820px; margin: 0 auto 100px; padding: 0 24px; }}
    details {{
      background: var(--surface-glass); border: 1px solid var(--surface-border);
      border-radius: var(--radius-md); padding: 18px 24px; margin-bottom: 16px;
      transition: var(--transition);
    }}
    details[open] {{ border-color: var(--primary); background: rgba(20, 25, 38, 0.9); }}
    summary {{ font-family: 'Outfit', sans-serif; font-size: 1.1rem; font-weight: 700; cursor: pointer; outline: none; list-style: none; display: flex; justify-content: space-between; align-items: center; }}
    summary::-webkit-details-marker {{ display: none; }}
    summary::after {{ content: '+'; font-size: 1.4rem; color: var(--primary); transition: transform 0.3s; }}
    details[open] summary::after {{ content: '−'; transform: rotate(180deg); }}
    details p {{ color: var(--text-muted); margin-top: 14px; font-size: 0.95rem; line-height: 1.7; }}

    /* Footer */
    footer {{
      border-top: 1px solid var(--surface-border); background: rgba(5, 7, 11, 0.95);
      padding: 60px 32px 30px; text-align: center;
    }}
    .footer-content {{ max-width: 1320px; margin: 0 auto; display: flex; flex-direction: column; align-items: center; gap: 20px; }}
    .footer-note {{ color: var(--text-muted); font-size: 0.88rem; }}

    /* Responsive */
    @media (max-width: 992px) {{
      .hero {{ grid-template-columns: 1fr; text-align: center; gap: 40px; }}
      .hero p {{ margin: 0 auto 30px; }}
      .hero-actions {{ justify-content: center; }}
      .canvas-3d-wrapper {{ height: 380px; }}
      .stat-strip {{ grid-template-columns: repeat(2, 1fr); }}
      .features-grid {{ grid-template-columns: 1fr; }}
      .showcase-grid {{ grid-template-columns: 1fr; }}
      .testimonial-grid {{ grid-template-columns: 1fr; }}
    }}
    @media (max-width: 600px) {{
      .hero h1 {{ font-size: 2.4rem; }}
      .canvas-3d-wrapper {{ height: 320px; }}
      .stat-strip {{ grid-template-columns: 1fr; }}
      nav {{ padding: 14px 20px; }}
      .nav-links {{ display: none; }}
    }}
  </style>
</head>
<body>
  <div class="ambient-glow-1"></div>
  <div class="ambient-glow-2"></div>

  <!-- Sticky Glass Navigation -->
  <nav>
    <a href="#home" class="nav-brand">
      <div class="brand-icon">{brand_icon}</div>
      <span>{brand_name}</span>
    </a>
    <ul class="nav-links">
      <li><a href="#features">Features</a></li>
      <li><a href="#showcase">Showcase</a></li>
      <li><a href="#reviews">Reviews</a></li>
      <li><a href="#faq">FAQ</a></li>
      <li><a href="#get-started" class="nav-cta">{profile['btn_primary']}</a></li>
    </ul>
  </nav>

  <!-- Hero Section -->
  <header class="hero" id="home">
    <div class="hero-content">
      <div class="hero-badge">
        <span class="pulse-dot"></span>
        <span>{profile['hero_badge']}</span>
      </div>
      <h1>
        {profile['headline_prefix']} <br>
        <span class="gradient-text">{brand_name}</span>
      </h1>
      <p>
        {profile['hero_desc']}
      </p>
      <div class="hero-actions">
        <a href="#features" class="btn-primary" onclick="alert('Welcome to {brand_name}! Experience engaged.')">
          {profile['btn_primary']}
        </a>
        <a href="#showcase" class="btn-secondary">
          {profile['btn_secondary']}
        </a>
      </div>
    </div>
    <div class="canvas-3d-wrapper">
      <div class="canvas-3d-hud">
        <div class="hud-pill">
          <span class="pulse-dot"></span>
          <span id="hud-fps-label">{profile['hud_pill']}</span>
        </div>
        <div class="hud-controls">
          <button class="hud-btn active" id="btn-custom-1" onclick="toggleCustom1(this)" title="Toggle Component 1">{profile['hud_btn1']}</button>
          <button class="hud-btn" id="btn-custom-2" onclick="toggleCustom2(this)" title="Toggle Component 2">{profile['hud_btn2']}</button>
          <button class="hud-btn" id="btn-theme" onclick="cycleCustomTheme(this)" title="Cycle Color / Style">{profile['hud_btn3']}</button>
          <button class="hud-btn" id="btn-sound" onclick="toggleAudioFX(this)" title="Toggle Audio Synthesizer">🔊 Audio</button>
        </div>
      </div>
      <div id="webgl-canvas-container" title="Click & Drag to Orbit in 360° &bull; Scroll to Zoom"></div>
      <div class="floating-glass-card">
        <div class="metric-bubble">{brand_icon}</div>
        <div>
          <div class="metric-label">{profile['hud_metric_label']}</div>
          <div class="metric-val" id="metric-poly-val">{profile['hud_metric_val']}</div>
        </div>
      </div>
    </div>
  </header>

  <!-- Live Metrics Strip -->
  <section class="stat-strip">
    {stats_html}
  </section>

  <!-- Features Grid with True CSS 3D Depth & Mouse Parallax Tilt -->
  <section id="features">
    <div class="section-header">
      <span class="section-tag">{profile['features_tag']}</span>
      <h2>{profile['features_title']}</h2>
    </div>
    <div class="features-grid">
      {features_html}
    </div>
  </section>

  <!-- 3D Spatial Showcase Gallery -->
  <section class="showcase-section" id="showcase">
    <div class="section-header">
      <span class="section-tag">{profile['showcase_tag']}</span>
      <h2>{profile['showcase_title']}</h2>
    </div>
    <div class="showcase-grid">
      <div class="showcase-img-card">
        <img src="{hero_img}" alt="{hero_alt}" loading="lazy">
      </div>
      <div class="showcase-desc">
        <h3>Mastery in Every Dimension</h3>
        <p>
          {profile['showcase_desc']}
        </p>
        <a href="#get-started" class="btn-primary">{profile['showcase_btn']}</a>
      </div>
    </div>
  </section>

  <!-- Testimonials -->
  <section class="testimonials" id="reviews">
    <div class="section-header">
      <span class="section-tag">Verified Acclaim</span>
      <h2>Trusted By Industry Pioneers</h2>
    </div>
    <div class="testimonial-grid">
      {testimonials_html}
    </div>
  </section>

  <!-- Interactive FAQ -->
  <section class="faq-section" id="faq">
    <div class="section-header">
      <span class="section-tag">Common Inquiries</span>
      <h2>Frequently Asked Questions</h2>
    </div>
    {faqs_html}
  </section>

  <!-- Footer -->
  <footer id="get-started">
    <div class="footer-content">
      <a href="#home" class="nav-brand">
        <div class="brand-icon">{brand_icon}</div>
        <span>{brand_name}</span>
      </a>
      <p class="footer-note">
        Autonomous Sovereign Workstation Engineering &bull; Architected by D.E.E.P for Mr. Ramadeep Singh &bull; All Rights Reserved 2026.
      </p>
    </div>
  </footer>

  <!-- Interactive 3D WebGL, OrbitControls & CSS Parallax Tilt Scripts -->
  <script>
    // --- Studio-Grade Web Audio Synthesizer (Zero External Dependencies) ---
    let audioCtx = null;
    let audioEnabled = true;

    function initAudio() {{
      if (!audioCtx) {{
        const AudioContext = window.AudioContext || window.webkitAudioContext;
        if (AudioContext) audioCtx = new AudioContext();
      }}
      if (audioCtx && audioCtx.state === 'suspended') {{
        audioCtx.resume();
      }}
    }}

    function playSpatialTone(freq = 520, type = 'sine', duration = 0.22) {{
      if (!audioEnabled) return;
      initAudio();
      if (!audioCtx) return;
      try {{
        const osc = audioCtx.createOscillator();
        const gain = audioCtx.createGain();
        osc.type = type;
        osc.frequency.setValueAtTime(freq, audioCtx.currentTime);
        gain.gain.setValueAtTime(0.08, audioCtx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.0001, audioCtx.currentTime + duration);
        osc.connect(gain);
        gain.connect(audioCtx.destination);
        osc.start();
        osc.stop(audioCtx.currentTime + duration);
      }} catch (e) {{}}
    }}

    window.toggleAudioFX = function(btn) {{
      initAudio();
      audioEnabled = !audioEnabled;
      if (btn) {{
        btn.textContent = audioEnabled ? '🔊 Audio: On' : '🔇 Audio: Muted';
        btn.classList.toggle('active', audioEnabled);
      }}
      if (audioEnabled) playSpatialTone(660, 'sine', 0.2);
    }};

    // --- 3D WebGL Three.js Spatial Engine with OrbitControls ---
    (function initThreeScene() {{
      const container = document.getElementById('webgl-canvas-container');
      if (!container || typeof THREE === 'undefined') return;

      const scene = new THREE.Scene();
      const camera = new THREE.PerspectiveCamera(45, container.clientWidth / container.clientHeight, 0.1, 1000);
      camera.position.set(0, 0, 4.8);

      const renderer = new THREE.WebGLRenderer({{ alpha: true, antialias: true }});
      renderer.setSize(container.clientWidth, container.clientHeight);
      renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
      container.appendChild(renderer.domElement);

      // Three.js OrbitControls (Full 360° Click-Drag Rotation & Scroll Zoom)
      let controls = null;
      if (typeof THREE.OrbitControls !== 'undefined') {{
        controls = new THREE.OrbitControls(camera, renderer.domElement);
        controls.enableDamping = true;
        controls.dampingFactor = 0.05;
        controls.autoRotate = true;
        controls.autoRotateSpeed = 1.3;
        controls.maxDistance = 8.5;
        controls.minDistance = 2.0;
        controls.enablePan = false;
      }}

{threejs_scene_code}

      // Responsive Resize
      window.addEventListener('resize', () => {{
        if (!container || !renderer || !camera) return;
        camera.aspect = container.clientWidth / container.clientHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(container.clientWidth, container.clientHeight);
      }});

      // FPS Calculation & Real-time Render Loop
      let lastTime = performance.now();
      let frameCount = 0;
      const fpsLabel = document.getElementById('hud-fps-label');
      let rotSpeed = 1.0;

      function animate(time) {{
        requestAnimationFrame(animate);

        if (controls) {{
          controls.update();
        }}

        if (typeof updateSceneAnimation === 'function') {{
          updateSceneAnimation(time, rotSpeed);
        }}

        renderer.render(scene, camera);

        frameCount++;
        if (time - lastTime >= 1000) {{
          const fps = Math.round((frameCount * 1000) / (time - lastTime));
          if (fpsLabel && !fpsLabel.dataset.locked) {{
            fpsLabel.innerHTML = `{profile['hud_pill']} &bull; ${{fps}} FPS`;
          }}
          frameCount = 0;
          lastTime = time;
        }}
      }}
      requestAnimationFrame(animate);
    }})();

    // --- Interactive CSS 3D Tilt & Specular Physics Engine ---
    (function init3DTiltCards() {{
      const cards = document.querySelectorAll('.feature-card');
      cards.forEach(card => {{
        card.addEventListener('mousemove', (e) => {{
          const rect = card.getBoundingClientRect();
          const x = e.clientX - rect.left;
          const y = e.clientY - rect.top;
          const centerX = rect.width / 2;
          const centerY = rect.height / 2;
          const rotateX = ((y - centerY) / centerY) * -12;
          const rotateY = ((x - centerX) / centerX) * 12;
          card.style.transform = `perspective(1000px) rotateX(${{rotateX}}deg) rotateY(${{rotateY}}deg) scale3d(1.03, 1.03, 1.03)`;
          card.style.setProperty('--mouse-x', `${{(x / rect.width) * 100}}%`);
          card.style.setProperty('--mouse-y', `${{(y / rect.height) * 100}}%`);
        }});
        card.addEventListener('mouseenter', () => {{
          playSpatialTone(480, 'sine', 0.12);
        }});
        card.addEventListener('mouseleave', () => {{
          card.style.transform = 'perspective(1000px) rotateX(0deg) rotateY(0deg) scale3d(1, 1, 1)';
        }});
      }});
    }})();
  </script>
</body>
</html>"""


def generate_html_with_ollama(topic: str) -> str:
    """
    Attempts to prompt local Ollama models with a strict domain-adaptive 3D web design directive.
    If Ollama is offline or generates insufficient code, seamlessly falls back to
    the Autonomous Master Web Designer Engine (packed with domain Three.js WebGL canvas, 3D tilt, and rich visuals).
    """
    system_prompt = (
        "You are an ELITE senior 3D UI/UX engineer and front-end architect. "
        "The user demands an ADVANCED LEVEL, 3D-enhanced, visually stunning website. "
        "STRICT MANDATE: Never produce plain text, basic 2D boxes, or a generic Torus Knot for all websites. "
        "The 3D WebGL scene MUST represent the requested topic: e.g. a ceramic coffee cup with rising steam particles "
        "for coffee, an aerodynamic hypercar chassis with speed streaks for cars, a titanium phone with camera optics for gadgets, "
        "or an undulating terrain grid for nature. "
        "Include CSS 3D perspective transforms with card tilt physics (perspective: 1200px, preserve-3d, translateZ), "
        "Sticky Glassmorphism Header, Hero Section with high-impact Unsplash imagery, "
        "Feature Grid with high-res photos and cards, Stat Counters, Testimonials, Interactive FAQ, and Footer. "
        "Return ONLY the complete raw HTML code starting with <!DOCTYPE html> and ending with </html>."
    )

    prompt = f"Topic: {topic}\nBuild a breathtaking, multi-section flagship 3D HTML5 website tailored specifically to this industry with Three.js WebGL and modern styling now:"
    url = "http://127.0.0.1:11434/api/generate"
    models_to_try = ["qwen2.5-coder:7b", "qwen2.5:3b", "qwen2.5:7b"]

    for model_name in models_to_try:
        try:
            payload = {"model": model_name, "prompt": prompt, "system": system_prompt, "stream": False}
            response = requests.post(url, json=payload, timeout=20)
            if response.status_code == 200:
                res_data = json.loads(response.text)
                text = res_data.get("response", "").strip()
                html_match = re.search(r'(<!DOCTYPE html.*?>.*?</html>|<html.*?>.*?</html>)', text, re.IGNORECASE | re.DOTALL)
                if html_match:
                    content = html_match.group(1).strip()
                    if len(content) > 1500 and ("<canvas" in content or "three.js" in content.lower() or "<img" in content):
                        return content
        except Exception:
            pass

    # Master Autonomous Fallback (Domain-Specific 3D WebGL Canvas, High-Res Photography, CSS 3D Tilt)
    return generate_advanced_flagship_html(topic)


def build_premium_website(project_name: str, topic: str) -> str:
    """
    Builds, saves, and spins up a dedicated live local HTTP server for the advanced website.
    """
    base_dir = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "generated_apps", project_name
    )
    os.makedirs(base_dir, exist_ok=True)

    index_path = os.path.join(base_dir, "index.html")
    html_content = generate_advanced_flagship_html(topic)

    with open(index_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    main_server_url = f"http://127.0.0.1:5000/generated_apps/{project_name}/index.html"
    port = get_free_port()
    live_url = f"http://127.0.0.1:{port}"

    meta_path = os.path.join(base_dir, "metadata.json")
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump({
            "project": project_name,
            "topic": topic,
            "url": live_url,
            "permanent_url": main_server_url,
            "has_rich_images": True,
            "generated_at": time.strftime("%Y-%m-%d %H:%M:%S")
        }, f, indent=4)

    # Start server in a background thread
    server_thread = threading.Thread(
        target=serve_directory, args=(base_dir, port), daemon=True
    )
    server_thread.start()

    return f"Deployed successfully to {main_server_url} (Standalone: {live_url}) | Path: {index_path}"


if __name__ == "__main__":
    print("[WebArchitect] Testing Advanced Domain-Adaptive Web Builder...")
    res = build_premium_website("test-coffee-adaptive", "Artisan Coffee Roastery and Cafe")
    print(res)
    res2 = build_premium_website("test-hypercar-adaptive", "Cyberpunk Electric Hypercar")
    print(res2)
