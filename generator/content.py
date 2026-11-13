"""Everything the profile says. Edit text here; nothing else needs to change.

Keep the README's alt text and links in step when you edit a project.
"""

LEETCODE_USER = "000433430"

# Spelled out in the hero heatmap. Only letters in blocks/hero.py GLYPHS work.
NAME = "Simon Cao"

TAGLINE = "Software Engineer · full-stack web"

# `cat profile.txt` rows, in order. STATUS is printed last, with a green dot.
PROFILE = [
    ("now", "Software Development Intern, ShyftFi LLC"),
    ("focus", "Full-stack web development"),
    ("stack", "React, TypeScript, Next.js, Python"),
    ("education", "B.S. Computer Science, UW–Stout '26"),
]
STATUS = ("status", "Open to full-time roles")

HERO_ALT = (
    "Terminal. whoami prints the name Simon Cao drawn as a contribution heatmap, "
    "then: Software Engineer, full-stack web. "
    "Now: Software Development Intern, ShyftFi LLC. Focus: full-stack web development. "
    "Stack: React, TypeScript, Next.js, Python. "
    "Education: B.S. Computer Science, UW–Stout, 2026. Status: open to full-time roles."
)

# `ls -l ~/projects`. `slug` names the image file; `date` is when work ended.
PROJECTS = [
    dict(slug="manifest-editor", dir="manifest-editor", date="May 2026",
         body="Browser editor for IIIF manifests and 3D scenes, built for stakeholders in London.",
         stack="react · typescript · tailwind · indexeddb"),
    dict(slug="kintsugi", dir="kintsugi3d-builder", date="May 2026",
         body="Research software for 3D texture reconstruction at UW–Stout.",
         stack="java · javafx · maven"),
    dict(slug="church-site", dir="gishen-debre-kerbe", date="Aug 2023",
         body="Website and content management system for a church community.",
         stack="next.js · typescript · sanity"),
    dict(slug="unimentor", dir="unimentor", date="Sep 2022",
         body="iOS app that connects university students with peer tutors.",
         stack="swift · swiftui · firebase"),
]

# `cat stack.txt`, straight from the resume's Technical Skills section.
STACK = [
    ("languages", "TypeScript, JavaScript, Python, Java, SQL, Swift, HTML/CSS"),
    ("frameworks", "React, Next.js, React Router, Tailwind CSS, Odoo ERP, JavaFX, SwiftUI"),
    ("data", "IndexedDB, Firebase, Sanity CMS, MySQL, MongoDB"),
    ("tools", "AWS, Git, GitHub, Jira, Vite, Maven, Figma, Claude Code, Codex"),
]
