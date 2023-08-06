import importlib.metadata
import subprocess
from pathlib import Path
from typing import TYPE_CHECKING, Any, Optional

from docutils import nodes
from sphinx.util import logging
from sphinx.writers.html5 import HTML5Translator

if TYPE_CHECKING:
    from sphinx.application import Sphinx
    from sphinx.config import Config


__name__ = "sphinx_shikijs"
__version__ = importlib.metadata.version(__name__)

SHIKIJS_MODES = ("cli", "browser")
logger = logging.getLogger(__name__)


def shiki_highlight(
    code: str, lang: str, theme: Optional[str] = None, cmd: Optional[str] = None
) -> str:
    args = [cmd or "shikijs-cli", "-l", lang]
    if theme:
        args += ["-t", theme]

    try:
        ret = subprocess.run(args, input=code.encode(), capture_output=True, check=True)
        return ret.stdout.decode()
    except subprocess.CalledProcessError as exc:
        raise RuntimeError(
            f"shikijs failed with code {exc.returncode}:\n{exc.stderr.decode()}"
        ) from exc


def visit_literal_block(self, node: nodes.Element) -> None:
    if node.rawsource != node.astext():
        # most probably a parsed-literal block -- don't highlight
        return HTML5Translator.visit_literal_block(self, node)

    if source_path := node.get("source"):
        lang = Path(source_path).suffix[1:]
    else:
        lang = node.get("language", self.config.highlight_language)

    linenos = node.get("linenos", False)
    highlight_args = node.get("highlight_args", {})
    highlight_args["force"] = node.get("force", False)

    # no highlight options for now
    # opts = self.config.highlight_options.get(lang, {})

    if linenos and self.config.html_codeblock_linenos_style:
        linenos = self.config.html_codeblock_linenos_style

    highlighted = None
    try:
        highlighted = (
            node.rawsource
            if self.config.shikijs_mode == "browser"
            else shiki_highlight(
                node.rawsource,
                lang,
                theme=self.config.shikijs_highlight_theme,
                cmd=self.config.shikijs_path,
            )
        )
    except RuntimeError as exc:
        logger.warning(
            f"failed to highlight code block due to error: {exc}",
            location=node,
            type="shikijs",
            subtype=self.app.env.docname,
        )

    starttag = self.starttag(
        node,
        "div",
        suffix="",
        CLASSES=["highlight", f"language-{lang}"],
        **{
            "data-hl-lines": ",".join(
                [str(a) for a in highlight_args.get("hl_lines", [])]
            )
        },
    )
    self.body.append(starttag + highlighted or node.rawsource + "</div>\n")
    raise nodes.SkipNode


def add_shiki_js(app: "Sphinx", config: "Config") -> None:
    app.add_js_file(
        "https://unpkg.com/shiki@0.14.1/dist/index.unpkg.iife.js", priority=500
    )
    app.add_js_file(
        None,
        body=f"var highlightTheme = '{config.shikijs_highlight_theme}';",
        priority=500,
    )

    with open((Path(__file__) / ".." / "highlight.js").resolve()) as f:
        app.add_js_file(None, body=f.read(), priority=500)


def add_emphasize_lines_js(app: "Sphinx", config: "Config") -> None:
    with open((Path(__file__) / ".." / "emphasizeLines.js").resolve()) as f:
        app.add_js_file(None, body=f.read(), priority=500, loading_method="defer")


def config_inited(app: "Sphinx", config: "Config") -> None:
    if config.shikijs_mode not in SHIKIJS_MODES:
        raise ValueError(
            f"Invalid shikijs_mode: {config.shikijs_mode}. "
            f"Must be one of {SHIKIJS_MODES}"
        )

    if config.shikijs_mode != "cli":
        add_shiki_js(app, config)

    add_emphasize_lines_js(app, config)


def setup(app: "Sphinx") -> dict[str, Any]:
    app.add_config_value("shikijs_mode", "cli", "env")  # cli or browser
    app.add_config_value("shikijs_path", "shiki-cli", "env")  # path to shiki-cli
    app.add_config_value("shikijs_highlight_theme", "dark-plus", "html")
    app.add_node(nodes.literal_block, html=(visit_literal_block, None), override=True)
    app.connect("config-inited", config_inited)

    return {
        "version": __version__,
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
