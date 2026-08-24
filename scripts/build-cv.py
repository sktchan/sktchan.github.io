#!/usr/bin/env python3
"""Render cv/cv.tex from the site's own data files.

    ./scripts/build-cv.py            # writes cv/cv.tex
    ./scripts/build-cv.py --check    # exits 1 if the file on disk is stale

WHY THIS EXISTS
The CV used to be a page on the site, generated from _data/cv.yml with the
papers and talks pulled out of _data/research.yml. It is now a PDF, and the
point of generating the LaTeX rather than hand-writing it is to keep that
single source: the publication list still comes from research.yml, so adding a
paper there updates the site and the CV together instead of drifting apart.

Edit the YAML, not cv/cv.tex. Anything written directly into the .tex is lost
the next time this runs, and the deploy workflow runs it on every push.

The preamble is Serena's own template, kept as-is apart from fontenc — see the
note where it is defined.
"""

import argparse
import datetime as dt
import pathlib
import re
import sys

try:
    import yaml
except ImportError:
    sys.exit("PyYAML is required: pip3 install pyyaml")

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "cv" / "cv.tex"


# ── LaTeX escaping ──────────────────────────────────────────────────────────
# The data is prose written for HTML, so it carries characters that are markup
# in TeX. "$10,000" and "Data Structures & Algorithms" both appear verbatim in
# cv.yml and both break the build unescaped.
_ESCAPES = {
    "\\": r"\textbackslash{}",
    "&": r"\&",
    "%": r"\%",
    "$": r"\$",
    "#": r"\#",
    "_": r"\_",
    "{": r"\{",
    "}": r"\}",
    "~": r"\textasciitilde{}",
    "^": r"\textasciicircum{}",
}


def tex(value):
    """Escape a plain string for LaTeX."""
    if value is None:
        return ""
    return "".join(_ESCAPES.get(ch, ch) for ch in str(value))


def href(url, label):
    return r"\href{%s}{%s}" % (url, tex(label))


def split_place(value):
    """Separate an institution from its city.

    cv.yml writes these as one field and is inconsistent about it: some entries
    carry a city ("Ubineer" vs "AI Atlas, Hamilton, ON"). The template puts the
    institution in bold and the city beside it, so they have to come apart. A
    trailing two-letter province code is the reliable marker.
    """
    parts = [p.strip() for p in str(value).split(",")]
    if len(parts) >= 3 and re.fullmatch(r"[A-Z]{2}", parts[-1]):
        return ", ".join(parts[:-2]), ", ".join(parts[-2:])
    if len(parts) == 2 and re.fullmatch(r"[A-Z]{2}", parts[-1]):
        return parts[0], parts[1]
    return str(value), ""


def bullets(detail):
    """cv.yml allows `detail` to be a string or a list; normalise to a list."""
    if not detail:
        return []
    return list(detail) if isinstance(detail, list) else [detail]


def load(name):
    with open(ROOT / "_data" / f"{name}.yml", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def itemize(lines):
    """The one list style in the document.

    This is what the publications block always used - \\small with the item
    spacing pulled in - and it is now what every list uses. Education and the
    two experience sections were each doing something slightly different, which
    is most of why the CV ran to three pages.

    `lines` must already be escaped.
    """
    if not lines:
        return ""
    out = ["\\begin{itemize}\n    \\setlength\\itemsep{-2pt}\n    \\small\n"]
    out += ["    \\item %s\n" % l for l in lines]
    out.append("\\end{itemize}\n")
    return "".join(out)


# ── preamble ────────────────────────────────────────────────────────────────
# Serena's template, unchanged except for one addition: [T1]{fontenc}. Without
# it pdflatex renders "Montréal", "Université" and "Québec" with broken accents,
# and those appear throughout. It changes no metric and no typeface — the
# document is still Computer Modern at 10pt.
PREAMBLE = r"""%------------------------
% Author : Serena Chan
%
% GENERATED FILE - do not edit.
% Written by scripts/build-cv.py from _data/cv.yml and _data/research.yml.
% Edit those and re-run the script; edits made here are overwritten.
% Generated @@STAMP@@
%------------------------

\documentclass[a4paper,10pt]{extarticle}

\usepackage[T1]{fontenc}
\usepackage{latexsym}
\usepackage[empty]{fullpage}
\usepackage{titlesec}
\usepackage{marvosym}
\usepackage[usenames,dvipsnames]{color}
\usepackage{verbatim}
\usepackage{enumitem}
\usepackage[pdftex]{hyperref}
\usepackage{fancyhdr}

\pagestyle{fancy}
\fancyhf{}
\fancyfoot[C]{\thepage}
\renewcommand{\headrulewidth}{0pt}
\renewcommand{\footrulewidth}{0pt}

\addtolength{\oddsidemargin}{-0.50in}
\addtolength{\evensidemargin}{-0.35in}
\addtolength{\textwidth}{1in}
\addtolength{\topmargin}{-0.6in}
\addtolength{\textheight}{0.005in}

\urlstyle{rm}

\raggedbottom
\raggedright
\setlength{\tabcolsep}{0in}

\titleformat{\section}{
  \vspace{-18pt}\scshape\raggedright\large
}{}{0em}{}[\color{black}\titlerule \vspace{-6pt}]

\newcommand{\resumeItem}[1]{
  \item\small{
    #1 \vspace{-2pt}
  }
}

\newcommand{\resumeSubItem}[2]{\resumeItem{#1}{#2}\vspace{-3pt}}

\renewcommand{\labelitemii}{$\circ$}

% enumitem is already loaded, so the space LaTeX puts around and inside every
% list can be set once here rather than fought entry by entry. topsep and
% parsep are the two that add up: at default they contribute roughly a blank
% line above and below each of the ~20 lists in this document.
\setlist[itemize]{topsep=1pt, partopsep=0pt, parsep=0pt, itemsep=-2pt}

\newcommand{\resumeSubHeadingListStart}{\begin{itemize}[leftmargin=*]}
\newcommand{\resumeSubHeadingListEnd}{\end{itemize}}

\hypersetup{%
    pdfborder = {0 0 0},
    pdftitle  = {@@PDFTITLE@@},
    pdfauthor = {@@AUTHOR@@}
}

\begin{document}
"""


def header(cfg, cv, links):
    """Name and headline on the left, contact links stacked on the right.

    No phone number: links.yml keeps it off the public site deliberately, and
    this PDF is linked from that site.
    """
    author = tex(cfg.get("author", ""))
    site = cfg.get("url", "").rstrip("/")

    left = [
        r"\textbf{{\Huge %s}}" % author,
        r"\textbf{{%s}}" % tex("Computer Science Graduate Student"),
        r"\textbf{{%s}}" % tex("Université de Montréal @ IRIC & Mila"),
    ]

    right = []
    if links.get("email"):
        right.append(href("mailto:" + links["email"], links["email"]))
    if links.get("linkedin"):
        right.append(href(links["linkedin"], links["linkedin"].replace("https://www.", "")))
    if site:
        right.append(href(site, site.replace("https://", "")))
    if cv.get("location"):
        right.append(tex(cv["location"]))

    rows = []
    for i in range(max(len(left), len(right))):
        l = left[i] if i < len(left) else ""
        r = right[i] if i < len(right) else ""
        rows.append("  %s\n  \\vspace{0.1pt} & \n  %s \\\\" % (l, r))

    return (
        "\n\\begin{tabular*}{\\textwidth}{l@{\\extracolsep{\\fill}}r}\n"
        + "\n".join(rows)
        + "\n\\end{tabular*}\n"
    )


def section(name):
    return "\n%s\n\\vspace{0,25\\baselineskip}\n\\section{%s}\n\\vspace{0,15\\baselineskip}\n" % (
        "%" * 78,
        tex(name),
    )


def education(items):
    out = [section("Education")]
    for it in items:
        where, city = split_place(it.get("where", ""))
        out.append(
            "\n\\textbf{%s} {%s}\n\\hfill \\textit{%s} \\\\\n%s\\\\\n"
            % (tex(where), tex(city), tex(it.get("when", "")), tex(it.get("title", "")))
        )
        out.append(itemize([tex(d) for d in bullets(it.get("detail"))]))
    return "".join(out)


def skills(items):
    out = [section("Skills Summary"), "\\resumeSubHeadingListStart\n"]
    for it in items:
        out.append(
            "\\resumeSubItem{\\textbf{%s:}}{{ %s}}\n"
            % (tex(it.get("when", "")), tex(it.get("title", "")))
        )
    out.append("\\resumeSubHeadingListEnd\n\\vspace{0,15\\baselineskip}\n")
    return "".join(out)


def experience(items):
    out = [section("Research & Professional Experience")]
    for it in items:
        where, city = split_place(it.get("where", ""))
        out.append(
            "\n\\vspace{0,15\\baselineskip}\n"
            "\\textbf{%s} {%s} \\\\\\vspace{0.2pt}\n%s\n\\hfill \\textit{%s}\\hfill\n"
            % (tex(where), tex(city), tex(it.get("title", "")), tex(it.get("when", "")))
        )
        out.append(itemize([tex(d) for d in bullets(it.get("detail"))]))
    return "".join(out)


def projects(research, extra):
    """Every project the site lists, in the order the site lists them.

    That order is deliberate rather than chronological: research.yml holds the
    three shown under "Relevant works" and projects.yml the rest under
    "Additional works", each already curated strongest-first. Sorting the
    combined list by date would put a coursework project above the thesis work,
    which is not what either the site or a CV wants.

    The bold line is the project title, not the institution - that is the whole
    point of a projects section, and the supervisor and lab are carried in the
    `role` line underneath, exactly as on the site.

    Talks attached to these projects are NOT emitted here; they flatten into
    Conferences & Publications so they appear once.
    """
    items = list(research.get("projects", []) or []) + list(extra or [])
    out = [section("Projects")]
    for it in items:
        out.append(
            "\n\\vspace{0,15\\baselineskip}\n"
            "\\textbf{%s}\n\\hfill \\textit{%s}\\hfill \\\\\\vspace{0.2pt}\n%s\n"
            % (tex(it.get("title", "")), tex(it.get("year", "")), tex(it.get("role", "")))
        )
        out.append(itemize([tex(b) for b in (it.get("bullets") or [])]))
    return "".join(out)


def awards(items):
    lines = []
    for it in items:
        bits = [b for b in (it.get("detail"), it.get("when")) if b]
        suffix = " (%s)" % tex(", ".join(str(b) for b in bits)) if bits else ""
        lines.append("%s%s" % (tex(it.get("title", "")), suffix))
    return section("Awards") + itemize(lines)


def publications(research, author):
    """Papers first, then every talk, newest first.

    Talks live inside the projects they came out of in research.yml, which is
    what keeps them attached to their work on the site; here they flatten into
    one list, exactly as the CV page used to do.
    """
    lines = []

    surname = author.split()[-1]
    for p in research.get("papers", []) or []:
        # Bold the author's own name in the citation, as the site does.
        authors = tex(p.get("authors", ""))
        authors = re.sub(r"\b(%s\s+\w+)" % re.escape(surname), r"\\textbf{\1}", authors, count=1)
        doi = next((l["url"] for l in p.get("links", []) or [] if l.get("name") == "DOI"), None)
        line = "%s. \\textit{%s}. %s, %s." % (
            authors, tex(p.get("title", "")), tex(p.get("venue", "")), tex(p.get("year", "")),
        )
        if doi:
            line += " " + href(doi, doi.replace("https://", ""))
        lines.append(line)

    talks = []
    for proj in research.get("projects", []) or []:
        talks.extend(proj.get("presentations", []) or [])
    for t in talks:
        lines.append(
            "\\textbf{%s} (%s): \\textit{%s}"
            % (tex(t.get("venue", "")), tex(t.get("year", "")), tex(t.get("title", "")))
        )

    return section("Conferences & Publications") + itemize(lines)


def build():
    cv, research, links = load("cv"), load("research"), load("links")
    with open(ROOT / "_config.yml", encoding="utf-8") as fh:
        cfg = yaml.safe_load(fh)
    author = cfg.get("author", "")

    doc = [
        (PREAMBLE
            .replace("@@STAMP@@", dt.date.today().isoformat())
            .replace("@@PDFTITLE@@", "%s - Curriculum Vitae" % author)
            .replace("@@AUTHOR@@", author)),
        header(cfg, cv, links),
        education(cv.get("education", []) or []),
        skills(cv.get("skills", []) or []),
        experience(cv.get("experience", []) or []),
        projects(research, load("projects")),
        awards(cv.get("awards", []) or []),
        publications(research, author),
        "\n\\vspace{2pt}\n\\end{document}\n",
    ]
    return "".join(doc)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--check", action="store_true",
                    help="exit 1 if cv/cv.tex differs from what would be generated")
    args = ap.parse_args()

    rendered = build()

    if args.check:
        current = OUT.read_text(encoding="utf-8") if OUT.exists() else ""
        # The date stamp changes daily and would make every check fail.
        strip = lambda s: re.sub(r"^% Generated .*$", "", s, flags=re.M)
        if strip(current) != strip(rendered):
            sys.exit("cv/cv.tex is stale - run ./scripts/build-cv.py")
        print("cv/cv.tex is up to date")
        return

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(rendered, encoding="utf-8")
    print("wrote %s (%d lines)" % (OUT.relative_to(ROOT), rendered.count("\n")))


if __name__ == "__main__":
    main()
