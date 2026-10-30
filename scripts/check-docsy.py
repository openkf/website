"""Exercise the installed Docsy production CSS pipeline in a temporary site."""

from html.parser import HTMLParser
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
from urllib.parse import unquote, urlsplit


class StylesheetLinks(HTMLParser):
    def __init__(self):
        super().__init__()
        self.hrefs = []

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if tag == "link" and "stylesheet" in values.get("rel", "").split():
            if values.get("href"):
                self.hrefs.append(values["href"])


def verify_output(public):
    page = public / "__ci_docsy_contract" / "index.html"
    html = page.read_text(encoding="utf-8")
    if "CI_DOCSY_PRODUCTION_CONTRACT" not in html:
        raise AssertionError("Docsy did not render the synthetic contract page")
    links = StylesheetLinks()
    links.feed(html)
    if not links.hrefs:
        raise AssertionError("Docsy did not link a production stylesheet")
    styles = []
    for href in links.hrefs:
        url = urlsplit(href)
        if url.netloc and url.netloc != "example.invalid":
            raise AssertionError("The contract must use a locally built stylesheet")
        css = (public / unquote(url.path).lstrip("/")).resolve()
        if not css.is_relative_to(public.resolve()):
            raise AssertionError("Stylesheet path escaped the temporary output")
        styles.append(css.read_text(encoding="utf-8"))
    output = "\n".join(styles)
    rules = re.findall(r"([^{}]+)\{([^{}]*)\}", output)
    prefixed = any(
        ".ci-docsy-contract" in [item.strip() for item in selectors.split(",")]
        and re.search(r"(?:^|;)\s*-ms-user-select\s*:\s*none(?:;|$)", body)
        for selectors, body in rules
    )
    if not prefixed:
        raise AssertionError("The synthetic style did not run real autoprefixer")


def main():
    repo = Path(__file__).resolve().parent.parent
    with tempfile.TemporaryDirectory(prefix="openkf-docsy-", dir=repo) as scratch:
        site = Path(scratch) / "site"
        site.mkdir()
        for name in ("hugo.toml", "go.mod", "go.sum", "postcss.config.cjs"):
            shutil.copy2(repo / name, site / name)
        for name in ("assets", "config", "content", "data", "i18n", "layouts", "static"):
            if (repo / name).is_dir():
                shutil.copytree(repo / name, site / name)
        page = site / "content" / "__ci_docsy_contract.md"
        page.parent.mkdir(parents=True, exist_ok=True)
        with page.open("x", encoding="utf-8") as target:
            target.write(
                "---\ntitle: Synthetic CI dependency contract\ntype: docs\n"
                "url: /__ci_docsy_contract/\n---\nCI_DOCSY_PRODUCTION_CONTRACT\n"
            )
        (site / ".browserslistrc").write_text("ie 11\n", encoding="utf-8")
        style = site / "assets" / "scss" / "_styles_project.scss"
        style.parent.mkdir(parents=True, exist_ok=True)
        with style.open("a", encoding="utf-8") as target:
            target.write("\n.ci-docsy-contract { user-select: none; }\n")
        env = os.environ.copy()
        env["PATH"] = str(repo / "node_modules" / ".bin") + os.pathsep + env["PATH"]
        env["NODE_PATH"] = str(repo / "node_modules")
        env["HUGO_CACHEDIR"] = str(Path(scratch) / "hugo-cache")
        subprocess.run(
            ["hugo", "--source", str(site), "--destination", str(site / "public"),
             "--environment", "production", "--baseURL", "https://example.invalid/",
             "--minify"],
            check=True, env=env, cwd=site, timeout=180,
        )
        verify_output(site / "public")
    print("Actual Docsy production HTML/CSS and PostCSS/autoprefixer contract passed")


if __name__ == "__main__":
    main()
