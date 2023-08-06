#!/bin/python3

import os
import sys
import shutil
import markdown
from .mdx_bib.mdx_bib import CitationsExtension

PREPEND_PATH = os.path.dirname(os.path.realpath(__file__)) + "/../"
PWD_PATH = os.getcwd() + "/"

ARGUMENTS = ["head", "tail", "output", "bib", "css", "js", "help"]
ARGUMENTS_SHORTCUTS = ["e", "t", "o", "b", "c", "j", "h"]
ARGUMENTS_HELP = {
  "head": "Sets the path to the HTML head.",
  "tail": "Sets the path to the HTML tail.",
  "output": "Output directory.",
  "bib": "Sets the path to the .bib bibliography file.",
  "css": "Sets the path to the css directory.",
  "js": "Sets the path to the js directory.",
  "help": "Prints this help message.",
}
ARGUMENTS_VALUES = {
  "head": PWD_PATH + "template/head.html",
  "tail": PWD_PATH + "template/tail.html",
  "output": PWD_PATH + "out/",
  "bib": PWD_PATH + "bib/refs.bib",
  "css": PWD_PATH + "css/",
  "js": PWD_PATH + "js/",
  "help": None,
}
ARGUMENTS_HEADERS = [f"--{ARGUMENTS[i]}=<val> | -{ARGUMENTS_SHORTCUTS[i]} <val>" \
                     for i, a in enumerate(ARGUMENTS)]
ARGUMENTS_LJUST = len(max(ARGUMENTS_HEADERS, key=len))

def print_help():
  print("""pymdpages - A minimalistic python-markdown static academic pages generator.
Usage: pymdpages [options] [files]

OPTIONS\n""")
  for i, a in enumerate(ARGUMENTS):
    print("  " + ARGUMENTS_HEADERS[i].ljust(ARGUMENTS_LJUST, ' ') + " : " + ARGUMENTS_HELP[a])
    if ARGUMENTS_VALUES[a] is not None: print(f"      Default value: {ARGUMENTS_VALUES[a]}")

  print("\npymdpages is available at https://github.com/RenatoGeh/pymdpages.")
  print("Get help/report bugs via: https://github.com/RenatoGeh/pymdpages/issues.")

def try_arg(args: dict, a: str, pre: int, sep: str):
  if a.startswith(pre):
    T = a.split(sep)
    arg = T[0][len(pre):]
    if arg == "h" or arg == "help":
      print_help()
      sys.exit(0)
    is_shortcut = True
    try: arg = ARGUMENTS[ARGUMENTS_SHORTCUTS.index(arg)]
    except: is_shortcut = False
    if (arg not in ARGUMENTS) and (not is_shortcut):
      print(f"Unrecognized command: {T[0]}!")
      print_help()
      sys.exit(1)
    if len(T) != 2:
      print(f"Unable to parse argument-value: {a}!")
      print_help()
      sys.exit(1)
    args[arg] = T[1]
    return True
  return False

def parse_args() -> dict:
  args = {k: ARGUMENTS_VALUES[k] for k in ARGUMENTS}
  files = []
  I = enumerate(sys.argv[1:], start = 1)
  for i, a in I:
    # Hack to make sure the second try_arg only occurs when -- does not work.
    if (not try_arg(args, a, "--", "=")):
      if try_arg(args, a + " " + sys.argv[i+1] if i+1 < len(sys.argv) else a, "-", " "):
        next(I)
      else:
        files.append(a)

  return args, files

def echo(str): print(str, end=' ')
def echoln(str): print(str)

# Extensions for Python-Markdown.
extensions = ["extra", "smarty", "meta", "mdx_math", "toc", "admonition",
              CitationsExtension(bibtex_file=PWD_PATH + "bib/refs.bib", order="unsorted"),
              "pymdownx.highlight", "pymdownx.superfences", "pymdownx.inlinehilite"]
extension_configs = {
  "toc": {
    "permalink": True,
    "toc_depth": "3-5",
  },
  "smarty": {
    "substitutions": {
      "left-single-quote": "'",
      "right-single-quote": "'",
    },
  },
  "highlight": {
    "guess_lang": True,
    "use_pygments": True,
  },
}

def compile(f_head, f_tail, d_out, F):
  echo("Loading extensions and configuration...")
  M = markdown.Markdown(extensions=extensions, extension_configs=extension_configs)
  echoln("OK!")
  # Parse tail contents.
  echo("Parsing tail...")
  with open(f_tail, "r", encoding="utf-8") as f: tail = f.read()
  echoln("OK!")
  # Parse head contents.
  echo("Parsing head...")
  with open(f_head, "r", encoding="utf-8") as f: head = f.read()
  echoln("OK!")

  echo("Creating output directory...")
  from pathlib import Path
  Path(d_out).mkdir(parents=True, exist_ok=True)
  echoln("OK!")

  for filename in F:
    # Parse file content.
    echo(f"Parsing {filename}...")
    with open(filename, "r", encoding="utf-8") as f: body = M.convert(f.read())
    echoln("OK!")
    # If f has meta-data, then add the title accordingly.
    echo("Parsing meta data...")
    f_head = head.replace("{{title}}", M.Meta["title"][0] if hasattr(M, "Meta") \
                          and ("title" in M.Meta) else "dPASP")
    echoln("OK!")
    # Join head, body and tail together.
    html = f_head + body + tail
    # Write HTML contents to disk.
    echo(f"Writing HTML output for {filename}...")
    with open(f"{d_out}{os.path.splitext(filename)[0]}.html", "w", encoding="utf-8") as f: f.write(html)
    echoln("OK!")

def main():
  A, F = parse_args()
  if len(F) > 0:
    # Compile Markdown into HTML.
    compile(A["head"], A["tail"], A["output"], F)
    # Copy css and js.
    shutil.copytree(A["css"], A["output"] + "/css/", dirs_exist_ok=True)
    shutil.copytree(A["js"], A["output"] + "/js/", dirs_exist_ok=True)
  else:
    print_help()
    sys.exit(1)
  return 0

if __name__ == "__main__": main()

