#!/usr/bin/env python3
"""Script to validate project documentation against Open Knowledge Format (OKF) v0.1."""

import os
import re
import sys

# Define target directories relative to project root
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OKF_DIR = os.path.join(PROJECT_ROOT, "okf")
RESERVED_FILES = {"index.md", "log.md"}
EXCLUDE_FILES = {"SPEC.md"}


def parse_simple_frontmatter(yaml_text):
    """Simple parser for key-value frontmatter to avoid external dependencies."""
    data = {}
    for line in yaml_text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" in line:
            key, val = line.split(":", 1)
            key = key.strip()
            val = val.strip()
            # Strip outer quotes if present
            if (val.startswith('"') and val.endswith('"')) or (
                val.startswith("'") and val.endswith("'")
            ):
                val = val[1:-1]
            data[key] = val
    return data


def check_okf():
    """Verify that all markdown files in the okf directory conform to OKF v0.1."""
    if not os.path.exists(OKF_DIR):
        print(f"Error: okf directory not found at {OKF_DIR}")
        return 1

    all_files = []
    for root, _, files in os.walk(OKF_DIR):
        for file in files:
            if file.endswith(".md") and file not in EXCLUDE_FILES:
                all_files.append(os.path.relpath(os.path.join(root, file), OKF_DIR))

    errors = []

    for rel_path in all_files:
        filepath = os.path.join(OKF_DIR, rel_path)
        filename = os.path.basename(rel_path)
        # Convert path separators for consistent error reporting
        report_path = rel_path.replace("\\", "/")
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        is_reserved = filename in RESERVED_FILES
        has_frontmatter = content.startswith("---")
        frontmatter_data = {}

        if has_frontmatter:
            parts = content.split("---", 2)
            if len(parts) >= 3:
                yaml_text = parts[1]
                frontmatter_data = parse_simple_frontmatter(yaml_text)
            else:
                errors.append(f"{report_path}: Frontmatter is not closed with '---'")

        is_root_index = report_path == "index.md"

        if is_reserved:
            if has_frontmatter and not is_root_index:
                errors.append(
                    f"{report_path}: Reserved file must not have YAML frontmatter"
                )
            elif is_root_index:
                if not has_frontmatter:
                    errors.append(
                        f"{report_path}: Root index.md must have YAML frontmatter declaring okf_version"
                    )
                elif "okf_version" not in frontmatter_data:
                    errors.append(
                        f"{report_path}: Root index.md frontmatter must declare 'okf_version'"
                    )
        else:
            if not has_frontmatter:
                errors.append(f"{report_path}: Missing YAML frontmatter block")
            elif "type" not in frontmatter_data or not frontmatter_data["type"]:
                errors.append(
                    f"{report_path}: Missing or empty 'type' field in YAML frontmatter"
                )

        # Scan links
        # Remove code blocks to avoid false positives in code examples
        content_no_code = re.sub(r"```.*?```", "", content, flags=re.DOTALL)
        content_no_code = re.sub(r"`.*?`", "", content_no_code)

        # Find all markdown links [text](target)
        links = re.findall(r"\[([^\]]+)\]\(([^)]+)\)", content_no_code)
        for _, target in links:
            # We only care about internal references
            if (
                "://" not in target
                and not target.startswith("#")
                and not target.startswith("mailto:")
            ):
                # Clean target (remove anchors and query parameters)
                clean_target = target.split("#")[0].split("?")[0]
                if clean_target:
                    if clean_target.startswith("/"):
                        # Repository-root-relative link.
                        # Only /backend/..., /frontend/..., /okf/..., or /README.md are permitted.
                        if not re.match(r"^/(backend|frontend|okf)/|^/README\.md$", clean_target):
                            errors.append(
                                f"{report_path}: Root-relative link '{target}' must "
                                "start with '/backend/', '/frontend/', '/okf/', or be '/README.md'."
                            )
                        else:
                            # Resolve from the repository root and verify it exists.
                            target_path = os.path.normpath(
                                os.path.join(PROJECT_ROOT, clean_target.lstrip("/"))
                            )
                            if not os.path.exists(target_path):
                                errors.append(
                                    f"{report_path}: Broken link '{target}' "
                                    f"(resolved to '{target_path}')"
                                )
                    else:
                        # Document-to-document link: relative links are now prohibited
                        errors.append(
                            f"{report_path}: Relative link '{target}' is prohibited. "
                            "All internal links must use repository-root-relative absolute paths "
                            "starting with '/okf/', '/backend/', or '/frontend/'."
                        )

    # Output results
    if errors:
        print("=== OKF Validation Failed ===")
        for err in errors:
            print(f"  [ERROR] {err}")
        return 1

    print(f"=== OKF Validation Passed (Verified {len(all_files)} files) ===")
    return 0


if __name__ == "__main__":
    sys.exit(check_okf())
