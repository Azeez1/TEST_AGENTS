def check(pdf_path: str) -> dict:
    # Placeholder; in production, use a11y tools or a service
    return {
        "alt_text_ok": False,
        "tagged_ok": False,
        "reading_order_ok": True,
        "bookmarks_ok": True,
        "hints": [
            "Add alt text for all figures.",
            "Export as tagged PDF.",
            "Ensure H1/H2 structure is logical."
        ]
    }
