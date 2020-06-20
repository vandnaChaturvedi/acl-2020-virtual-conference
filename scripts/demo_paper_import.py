import argparse
import csv
import itertools
import re

import yaml

re_author_split = re.compile(" and |, ")
re_curly_brace = re.compile("{([A-Za-z0-9 ]+)}")

acceptable_chars = r"['`\/:\-()?\w\s\d.,]+"
re_newline = re.compile("[ ]*\n[ ]*")
re_inline_italics = re.compile(r"{\\(?:em|it) (" + acceptable_chars + ")}")
re_italics = re.compile(r"\\(?:emph|textit){(" + acceptable_chars + ")}")
re_inline_sc = re.compile(r"{\\sc (" + acceptable_chars + ")}")
re_textsc = re.compile(r"\\textsc{(" + acceptable_chars + ")}")
re_inline_bf = re.compile(r"{\\bf (" + acceptable_chars + ")}")
re_textbf = re.compile(r"\\textbf{(" + acceptable_chars + ")}")
re_textrm = re.compile(r"\\textrm{(" + acceptable_chars + ")}")
re_url = re.compile(r"\\url{(" + acceptable_chars + ")}")
re_footnote = re.compile(r"\\footnote{(" + acceptable_chars + ")}")
re_mathmode = re.compile(r"\$(.*?)\$")
re_cite = re.compile(r"~?\\cite[pt]?{(" + acceptable_chars + ")}")
re_multi_space = re.compile(r"\s+")
re_superscript = re.compile(r"\\textsuperscript{(\d+)}")
re_subscript = re.compile(r"\\textsubscript{(\d+)}")


direct_replacements = {
    "\\%": "%",
    "\\&": "&",
    "$\\sim$": "~",
    "\\alpha": "ɑ",
    "\\beta": "β",
    "\\gamma": "ɣ",
    "\\propto": "∝",
    "\\Rightarrow": "⇒",
    "\\Leftrightarrow": "⇔",
    "\\Leftarrow": "⇐",
}

subscript_map = {
    "0": "₀",
    "1": "₁",
    "2": "₂",
    "3": "₃",
    "4": "₄",
    "5": "₅",
    "6": "₆",
    "7": "₇",
    "8": "₈",
    "9": "₉",
}
superscript_map = {
    "0": "⁰",
    "1": "¹",
    "2": "²",
    "3": "³",
    "4": "⁴",
    "5": "⁵",
    "6": "⁶",
    "7": "⁷",
    "8": "⁸",
    "9": "⁹",
}


def convert_superscript_match(match):
    return "".join([superscript_map[char] for char in str(match.group(1))])


def convert_subscript_match(match):
    return "".join([subscript_map[char] for char in str(match.group(1))])


def clean_abstract(abstract):
    for source, dest in direct_replacements.items():
        abstract = abstract.replace(source, dest)
    abstract = re_newline.sub(" ", abstract)
    abstract = re_superscript.sub(convert_superscript_match, abstract)
    abstract = re_subscript.sub(convert_subscript_match, abstract)
    abstract = re_textsc.sub(r"\1", abstract)
    abstract = re_inline_sc.sub(r"\1", abstract)
    abstract = re_textrm.sub(r"\1", abstract)
    abstract = re_textbf.sub(r"\1", abstract)
    abstract = re_inline_bf.sub(r"\1", abstract)
    abstract = re_cite.sub(" ", abstract)
    abstract = re_url.sub(r"\1", abstract)
    abstract = re_footnote.sub(r" (\1)", abstract)
    abstract = re_mathmode.sub(r"\1", abstract)
    abstract = re_inline_italics.sub(r"\1", abstract)
    abstract = re_italics.sub(r"\1", abstract)
    abstract = " ".join(abstract.split('"'))
    abstract = " ".join(abstract.split("'"))
    abstract = re_multi_space.sub(" ", abstract)
    return abstract


def clean_title(paper_title):
    for source, dest in direct_replacements.items():
        paper_title = paper_title.replace(source, dest)
    paper_title = re_curly_brace.sub(r"\1", paper_title)
    paper_title = " ".join(paper_title.split('"'))
    paper_title = " ".join(paper_title.split("'"))
    paper_title = re_multi_space.sub(" ", paper_title)
    return paper_title


def miniconf_join_list(lst):
    return "|".join(lst)


def parse_authors(author_string):
    return re_author_split.split(author_string)


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Format paper details into MiniConf format"
    )
    parser.add_argument(
        "--demo-papers-file",
        help="CSV of paper title, authors, abstract, and submission type",
        action="store",
        type=str,
        default="ACL2020 Accepted Papers Information (to share with other chairs) - Sheet1.csv",
    )
    return parser.parse_args()


def read_demo_paper_tsv(inp):
    with open(inp, "r") as fd:
        data = list(csv.DictReader(fd, delimiter="\t"))
    key = lambda datum: datum["UID"]
    data.sort(key=key)
    result = [
        {"UID": key, "value": list(group)}
        for key, group in itertools.groupby(data, key=key)
    ]

    def merge(ds):
        out = {}
        out["UID"] = ds[0]["UID"]
        out["URL"] = ds[0]["URL"].strip()
        out["title"] = clean_title(ds[0]["title"])
        out["abstract"] = clean_abstract(ds[0]["abstract"])
        out["authors"] = parse_authors(ds[0]["authors"])
        out["paper_type"] = ds[0]["paper_type"]
        out["sessions"] = [
            {
                "track": d["track"],
                "day": d["Day Date"].split(",")[0],
                "date": " ".join(d["Day Date"].split(" ")[1:-1]),
                "start_time": d["Ses Time"],
                "end_time": d["Ses End Time"],
                "timezone": "UTC+0",
            }
            for d in ds
        ]
        return out

    result = [merge(r["value"]) for r in result]
    return result


def main():
    args = parse_arguments()
    demo_papers = read_demo_paper_tsv(args.demo_papers_file)
    with open("demo_papers.yml", "w") as fd:
        yaml.safe_dump(demo_papers, fd, default_flow_style=False)


if __name__ == "__main__":
    main()
