#!/usr/bin/env python3
"""
Fix duplicate Unsplash images across blog posts.
Extracts verified photo IDs from existing posts and redistributes them
evenly by category to minimize repetition.
"""

import os
import re
import glob
from collections import Counter, defaultdict

CONTENT_DIR = os.path.join(os.path.dirname(__file__), "content", "posts")

# Category preference map: which Unsplash photo IDs suit each category best
# Ordered by preference (first = best match)
CATEGORY_IMAGE_PREFS = {
    "ai": [
        "1677442135703-1787eea5ce01",  # AI circuit purple
        "1620712943543-bcc4688e7485",  # Futuristic AI
        "1655720828018-edd2daec9349",  # AI visualization
        "1461749280684-dccba630e2f6",  # Code monitors (tech)
        "1498050108023-c5249f4df085",  # Laptop code (tech)
        "1555066931-4365d14bab8c",     # Dark terminal
        "1516116216624-53e697fedbea",  # Multi-monitor
        "1587620962725-abab7fe55159",  # Developer desk
        "1540575467063-178a50c2df87",  # Learning/focus
        "1454165804606-c3d57bc86b40",  # Dark desk
    ],
    "coding": [
        "1461749280684-dccba630e2f6",  # Code monitors
        "1498050108023-c5249f4df085",  # Laptop with code
        "1555066931-4365d14bab8c",     # Dark terminal
        "1516116216624-53e697fedbea",  # Multiple monitors
        "1587620962725-abab7fe55159",  # Developer workspace
        "1540575467063-178a50c2df87",  # Focused learning
        "1454165804606-c3d57bc86b40",  # Dark code desk
        "1593642632559-0c6d3fc62b89",  # Home office
        "1531403009284-440f080d1e12",  # Keyboard
        "1677442135703-1787eea5ce01",  # AI/tech (shared)
    ],
    "entrepreneurship": [
        "1552664730-d307ca884978",     # Team whiteboard
        "1507003211169-0a1dd7228f2d",  # Person + laptop
        "1515187029135-18ee286d815b",  # Coffee + laptop
        "1522202176988-66273c2fd55f",  # Team meeting
        "1529156069898-49953e39b3ac",  # Group people
        "1531746790731-6c087fecd65a",  # Community/team
        "1521737604893-d14cc237f11d",  # Team energy
        "1573164713714-d95e436ab8d4",  # Conference
        "1455390582262-044cdead277a",  # Audience
        "1522071820081-009f0129c71c",  # Team at work
        "1531403009284-440f080d1e12",  # Professional
        "1593642632559-0c6d3fc62b89",  # Working from home
        "1540575467063-178a50c2df87",  # Focus/productivity
    ],
    "developer-relations": [
        "1531403009284-440f080d1e12",  # Keyboard typing
        "1593642632559-0c6d3fc62b89",  # Home office
        "1454165804606-c3d57bc86b40",  # Dark laptop desk
        "1573164713714-d95e436ab8d4",  # Conference speaking
        "1455390582262-044cdead277a",  # Conference audience
        "1522202176988-66273c2fd55f",  # Team meeting
        "1529156069898-49953e39b3ac",  # Community people
        "1531746790731-6c087fecd65a",  # Community
        "1521737604893-d14cc237f11d",  # Team
        "1522071820081-009f0129c71c",  # Team at computers
        "1587620962725-abab7fe55159",  # Developer desk
        "1507003211169-0a1dd7228f2d",  # Person working
    ],
    "community-building": [
        "1529156069898-49953e39b3ac",  # Diverse group
        "1531746790731-6c087fecd65a",  # Community
        "1573164713714-d95e436ab8d4",  # Conference
        "1455390582262-044cdead277a",  # Audience
        "1521737604893-d14cc237f11d",  # Team
        "1522071820081-009f0129c71c",  # Team work
        "1522202176988-66273c2fd55f",  # Group meeting
        "1552664730-d307ca884978",     # Whiteboard (collaborative)
        "1507003211169-0a1dd7228f2d",  # Person engaged
        "1515187029135-18ee286d815b",  # Relaxed work
    ],
    "tutorials": [
        "1540575467063-178a50c2df87",  # Focused learning
        "1461749280684-dccba630e2f6",  # Code on screen
        "1498050108023-c5249f4df085",  # Laptop tutorial
        "1555066931-4365d14bab8c",     # Terminal/code
        "1587620962725-abab7fe55159",  # Developer setup
        "1516116216624-53e697fedbea",  # Monitors
        "1593642632559-0c6d3fc62b89",  # Home learning
        "1531403009284-440f080d1e12",  # Keyboard
        "1454165804606-c3d57bc86b40",  # Dark code
        "1507003211169-0a1dd7228f2d",  # Person learning
    ],
}

# Descriptive alt text for each photo ID
ALT_TEXT = {
    "1677442135703-1787eea5ce01": "Glowing purple AI circuit network visualization",
    "1620712943543-bcc4688e7485": "Futuristic AI technology concept with glowing nodes",
    "1655720828018-edd2daec9349": "Data streams and AI visualization",
    "1461749280684-dccba630e2f6": "Monitors showing code in a developer workspace",
    "1498050108023-c5249f4df085": "Black MacBook with code on screen",
    "1555066931-4365d14bab8c": "Dark terminal with colorful code syntax",
    "1516116216624-53e697fedbea": "Multiple monitors with code in dark office",
    "1587620962725-abab7fe55159": "Clean modern developer desk with dual screens",
    "1552664730-d307ca884978": "Team brainstorming together at a whiteboard",
    "1507003211169-0a1dd7228f2d": "Person working thoughtfully on a laptop",
    "1515187029135-18ee286d815b": "Laptop with coffee on a wooden table",
    "1522202176988-66273c2fd55f": "Diverse team in a productive meeting",
    "1529156069898-49953e39b3ac": "Diverse group of smiling people collaborating",
    "1531746790731-6c087fecd65a": "Community members gathered and connected",
    "1521737604893-d14cc237f11d": "Energetic team celebrating at a startup office",
    "1573164713714-d95e436ab8d4": "Tech conference audience engaged with presentation",
    "1455390582262-044cdead277a": "Engaged conference audience from speaker perspective",
    "1522071820081-009f0129c71c": "Team collaborating at computers in open office",
    "1531403009284-440f080d1e12": "Hands typing on a mechanical keyboard",
    "1593642632559-0c6d3fc62b89": "Productive home office with monitor and plants",
    "1540575467063-178a50c2df87": "Person focused on learning with laptop and notebook",
    "1454165804606-c3d57bc86b40": "Dark laptop and desk setup for late-night work",
}


def get_unsplash_url(photo_id: str) -> str:
    return (
        f"https://images.unsplash.com/photo-{photo_id}"
        f"?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80"
    )


def extract_field(content: str, field: str) -> str:
    m = re.search(rf'^{re.escape(field)}: "([^"]*)"', content, re.MULTILINE)
    return m.group(1) if m else ""


def get_photo_id(url: str) -> str:
    m = re.search(r"photo-([\w-]+)\?", url)
    return m.group(1) if m else ""


def get_preferred_category(category: str, title: str) -> str:
    t = title.lower()
    c = category.lower()
    if any(k in t for k in ["ai", "llm", "gpt", "agent", "machine learning", "neural", "prompt", "model"]):
        return "ai"
    if any(k in t for k in ["tutorial", "how to", "getting started", "guide", "step by step", "beginner"]):
        return "tutorials"
    if any(k in t for k in ["community", "discord", "slack", "meetup", "network", "belonging"]):
        return "community-building"
    if any(k in t for k in ["devrel", "developer relation", "advocate", "developer experience"]):
        return "developer-relations"
    if any(k in t for k in ["code", "coding", "debug", "software", "programming", "engineer"]):
        return "coding"
    # Fall back to category field
    if "ai" in c or "agent" in c:
        return "ai"
    if "tutorial" in c:
        return "tutorials"
    if "community" in c:
        return "community-building"
    if "developer-relation" in c or "devrel" in c:
        return "developer-relations"
    if "coding" in c or "engineering" in c:
        return "coding"
    return "entrepreneurship"


def main():
    posts = sorted(glob.glob(os.path.join(CONTENT_DIR, "**", "*.md"), recursive=True))
    print(f"Found {len(posts)} posts")

    # Read all posts
    post_data = []
    for filepath in posts:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        cat = extract_field(content, "category")
        title = extract_field(content, "title")
        slug = extract_field(content, "slug")
        img_url = extract_field(content, "featuredImage")
        photo_id = get_photo_id(img_url)
        post_data.append({
            "filepath": filepath,
            "content": content,
            "category": cat,
            "title": title,
            "slug": slug,
            "photo_id": photo_id,
            "preferred_cat": get_preferred_category(cat, title),
        })

    # Count current state
    id_counts = Counter(p["photo_id"] for p in post_data)
    print(f"\nCurrent: {len(id_counts)} unique images, max reuse: {id_counts.most_common(1)[0][1]}x")

    # Track usage counts per image ID
    usage_count = defaultdict(int)
    # Track which posts keep their image vs need reassignment
    keeps = set()  # filepaths that keep their current image (first occurrence)
    needs_new = []  # posts that need a new image

    seen_ids = set()
    for post in post_data:
        pid = post["photo_id"]
        if pid and pid not in seen_ids:
            seen_ids.add(pid)
            keeps.add(post["filepath"])
            usage_count[pid] += 1
        else:
            needs_new.append(post)

    print(f"Keeping {len(keeps)} posts' images, reassigning {len(needs_new)} duplicates")

    # For each post needing a new image, assign from its preferred category pool
    # Greedy: pick the least-used image from its preferred pool
    updated = 0
    failed = 0

    # All available photo IDs from our preference maps
    all_pool_ids = set()
    for ids in CATEGORY_IMAGE_PREFS.values():
        all_pool_ids.update(ids)

    for post in needs_new:
        pref_cat = post["preferred_cat"]
        pref_list = CATEGORY_IMAGE_PREFS.get(pref_cat, [])

        # Try all categories in order of preference, then any remaining
        candidates = list(pref_list)
        for cat, ids in CATEGORY_IMAGE_PREFS.items():
            if cat != pref_cat:
                for pid in ids:
                    if pid not in candidates:
                        candidates.append(pid)

        # Pick the candidate with lowest usage count
        best_pid = min(candidates, key=lambda pid: usage_count[pid])
        usage_count[best_pid] += 1

        new_url = get_unsplash_url(best_pid)
        new_alt = ALT_TEXT.get(best_pid, "Developer and tech community workspace")

        content = post["content"]
        new_content = re.sub(
            r'^featuredImage: "https://images\.unsplash\.com/[^"]*"',
            f'featuredImage: "{new_url}"',
            content,
            flags=re.MULTILINE,
        )
        new_content = re.sub(
            r'^imageAlt: ".*?"',
            f'imageAlt: "{new_alt}"',
            new_content,
            flags=re.MULTILINE,
        )
        if new_content != content:
            with open(post["filepath"], "w", encoding="utf-8") as f:
                f.write(new_content)
            updated += 1

    print(f"\nUpdated: {updated} posts")

    # Final stats
    final_ids = []
    for filepath in posts:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        img = extract_field(content, "featuredImage")
        pid = get_photo_id(img)
        if pid:
            final_ids.append(pid)

    final_counts = Counter(final_ids)
    max_reuse = final_counts.most_common(1)[0][1] if final_counts else 0
    print(f"\nFinal: {len(set(final_ids))} unique images across {len(final_ids)} posts")
    print(f"Max reuse of any single image: {max_reuse}x (was up to 19x)")
    print("\nDistribution of reuse:")
    reuse_dist = Counter(final_counts.values())
    for count, num_images in sorted(reuse_dist.items()):
        print(f"  Used {count}x: {num_images} images")


if __name__ == "__main__":
    main()
