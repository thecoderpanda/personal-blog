#!/usr/bin/env python3
"""
Hugo → Substack Migration Script
Converts Hugo markdown posts to Ghost JSON format for Substack import.

Usage:
  pip install python-frontmatter markdown
  python3 export-to-substack.py
  
Then: Substack → Settings → Import → Ghost → Upload ghost-export.json
"""

import os
import json
import uuid
import hashlib
from datetime import datetime, timezone
import re

try:
    import frontmatter
except ImportError:
    print("Missing dependency. Run: pip install python-frontmatter markdown")
    exit(1)

try:
    import markdown as md_lib
except ImportError:
    print("Missing dependency. Run: pip install markdown")
    exit(1)


CONTENT_DIR = os.path.join(os.path.dirname(__file__), "content", "posts")
OUTPUT_FILE = os.path.join(os.path.dirname(__file__), "ghost-export.json")


def deterministic_id(slug: str, length: int = 24) -> str:
    h = hashlib.sha256(slug.encode()).hexdigest()
    return h[:length]


def deterministic_uuid(slug: str) -> str:
    namespace = uuid.UUID("a1b2c3d4-e5f6-7890-abcd-ef1234567890")
    return str(uuid.uuid5(namespace, slug))


def parse_date(date_str) -> int:
    if not date_str:
        return int(datetime.now(timezone.utc).timestamp() * 1000)
    if isinstance(date_str, datetime):
        dt = date_str
    else:
        date_str = str(date_str).strip()
        for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%SZ"):
            try:
                dt = datetime.strptime(date_str, fmt)
                dt = dt.replace(tzinfo=timezone.utc)
                break
            except ValueError:
                continue
        else:
            return int(datetime.now(timezone.utc).timestamp() * 1000)
    return int(dt.timestamp() * 1000)


def markdown_to_html(text: str) -> str:
    extensions = ["tables", "fenced_code", "codehilite", "toc", "nl2br"]
    try:
        return md_lib.markdown(text, extensions=extensions)
    except Exception:
        return md_lib.markdown(text)


def collect_posts():
    posts = []
    seen_slugs = set()

    for root, dirs, files in os.walk(CONTENT_DIR):
        dirs.sort()
        for filename in sorted(files):
            if not filename.endswith(".md"):
                continue
            filepath = os.path.join(root, filename)
            try:
                post = frontmatter.load(filepath)
            except Exception as e:
                print(f"  Skipping {filepath}: {e}")
                continue

            meta = post.metadata
            content_body = post.content.strip()

            title = meta.get("title") or filename.replace(".md", "").replace("-", " ").title()
            slug = meta.get("slug") or filename.replace(".md", "")

            if slug in seen_slugs:
                slug = slug + "-" + deterministic_id(filepath, 6)
            seen_slugs.add(slug)

            subtitle = meta.get("subtitle", "")
            date_val = meta.get("date")
            published_at = parse_date(date_val)
            feature_image = meta.get("featuredImage", "")
            tags_raw = meta.get("tags", [])
            tags = [str(t) for t in tags_raw] if isinstance(tags_raw, list) else []
            excerpt = meta.get("seoDescription") or subtitle or ""

            html_content = markdown_to_html(content_body)
            if subtitle:
                html_content = f"<p><em>{subtitle}</em></p>\n" + html_content

            post_id = deterministic_id(slug)
            post_uuid = deterministic_uuid(slug)

            posts.append({
                "id": post_id,
                "uuid": post_uuid,
                "title": title,
                "slug": slug,
                "html": html_content,
                "plaintext": re.sub(r"<[^>]+>", " ", html_content),
                "feature_image": feature_image or None,
                "custom_excerpt": excerpt[:500] if excerpt else None,
                "status": "published",
                "published_at": published_at,
                "created_at": published_at,
                "updated_at": published_at,
                "type": "post",
                "visibility": "public",
                "email_only": False,
            })

    posts.sort(key=lambda p: p["published_at"])
    return posts


def build_ghost_export(posts):
    now_ms = int(datetime.now(timezone.utc).timestamp() * 1000)

    all_tag_names = set()
    for p in posts:
        pass

    tag_map = {}
    tags_data = []

    def get_or_create_tag(name: str):
        slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
        if slug not in tag_map:
            tid = deterministic_id(slug, 24)
            tag_map[slug] = tid
            tags_data.append({
                "id": tid,
                "name": name,
                "slug": slug,
                "description": None,
                "feature_image": None,
                "parent_id": None,
                "visibility": "public",
            })
        return tag_map[slug]

    posts_tags = []

    for post in posts:
        pass

    export_data = {
        "db": [{
            "meta": {
                "exported_on": now_ms,
                "version": "5.0.0"
            },
            "data": {
                "posts": posts,
                "tags": tags_data,
                "posts_tags": posts_tags,
                "users": [],
                "posts_authors": [],
            }
        }]
    }
    return export_data


def rebuild_with_tags(posts):
    """Re-read files to get tag info (done separately to keep collect_posts clean)."""
    tag_map = {}
    tags_data = []
    posts_tags = []

    def normalize_tag(name: str) -> str:
        return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")

    def get_or_create_tag(name: str) -> str:
        slug = normalize_tag(name)
        if slug not in tag_map:
            tid = deterministic_id("tag-" + slug, 24)
            tag_map[slug] = tid
            tags_data.append({
                "id": tid,
                "name": name,
                "slug": slug,
                "description": None,
                "feature_image": None,
                "parent_id": None,
                "visibility": "public",
            })
        return tag_map[slug]

    for root, dirs, files in os.walk(CONTENT_DIR):
        for filename in sorted(files):
            if not filename.endswith(".md"):
                continue
            filepath = os.path.join(root, filename)
            try:
                post_fm = frontmatter.load(filepath)
            except Exception:
                continue
            meta = post_fm.metadata
            slug = meta.get("slug") or filename.replace(".md", "")
            post_id = deterministic_id(slug, 24)

            tags_raw = meta.get("tags", [])
            if isinstance(tags_raw, list):
                for i, tag_name in enumerate(tags_raw):
                    tag_id = get_or_create_tag(str(tag_name))
                    posts_tags.append({
                        "post_id": post_id,
                        "tag_id": tag_id,
                        "sort_order": i,
                    })
            category = meta.get("category")
            if category:
                tag_id = get_or_create_tag(str(category))
                posts_tags.append({
                    "post_id": post_id,
                    "tag_id": tag_id,
                    "sort_order": 100,
                })

    return tags_data, posts_tags


def main():
    print("Scanning posts from:", CONTENT_DIR)
    posts = collect_posts()
    print(f"Found {len(posts)} posts")

    tags_data, posts_tags = rebuild_with_tags(posts)
    print(f"Found {len(tags_data)} unique tags")

    now_ms = int(datetime.now(timezone.utc).timestamp() * 1000)
    export = {
        "db": [{
            "meta": {
                "exported_on": now_ms,
                "version": "5.0.0"
            },
            "data": {
                "posts": posts,
                "tags": tags_data,
                "posts_tags": posts_tags,
                "users": [],
                "posts_authors": [],
            }
        }]
    }

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(export, f, ensure_ascii=False, indent=2)

    size_kb = os.path.getsize(OUTPUT_FILE) / 1024
    print(f"\nExport written to: {OUTPUT_FILE} ({size_kb:.1f} KB)")
    print("\nNext steps:")
    print("  1. Go to your Substack publication settings")
    print("  2. Settings → Import → Import from Ghost")
    print("  3. Upload ghost-export.json")
    print("  4. Review imported posts and publish")
    print("\nNote: Substack will import all posts as drafts.")
    print("Review each post and publish when ready.")


if __name__ == "__main__":
    main()
