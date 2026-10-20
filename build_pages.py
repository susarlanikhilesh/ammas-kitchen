"""Generate docs/ recipe pages from ../moms-cookbook/recipes. Re-run after editing recipes."""
import re, os, pathlib, shutil
SRC = pathlib.Path(os.environ.get("RECIPES_DIR") or pathlib.Path(__file__).resolve().parent / "recipes"); DOCS = pathlib.Path("docs")
CATS = {"basics":("Basics","మసాలాలు & పోపు"),"dals-and-rasam":("Dals & Rasam","పప్పు & చారు"),
 "gravies-and-curries":("Gravies & Curries","కూరలు"),"pickles-and-chutneys":("Pickles & Chutneys","పచ్చళ్ళు"),
 "rice-and-tiffin":("Rice & Tiffin","టిఫిన్"),"snacks":("Snacks","పిండి వంటలు"),"unsorted":("Still to name","పేరు తెలియనివి")}
AUDIO = {"gongura-pachadi":["gongura-1.m4a","gongura-2.m4a"],"panipuri-masala":["panipuri-1.m4a","panipuri-2.m4a"],
 "chana-dal-recipe-unnamed":["chana-dal.m4a"],"tomato-recipe-unnamed":["tomato.m4a"]}
IMG = {"chuda":"chuda-page.png", **{k:"snacks-page.png" for k in ["chegodilu","chekkalu","namak-para","burelu"]}}
MARK = re.compile(r"\s*\[(\?|unclear|unconfirmed)([^\]]*)\]")
def note(text, indent):
    p = " "*indent
    return f"\n{p}!!! question \"Not sure — check with Amma\"\n{p}    {text[0].upper()+text[1:]}\n"
def convert(md):
    out=[]
    for line in md.splitlines():
        notes=[]
        def rep(m):
            kind, rest = m.group(1), m.group(2).strip(" :")
            notes.append(rest or ("Unconfirmed" if kind=="unconfirmed" else "Couldn't read this part"))
            return ""
        title = line.startswith("# ")
        new = MARK.sub(rep, line)
        if re.fullmatch(r"\s*(-|\d+\.)\s*", new): new = new.rstrip()+" …"
        out.append(new.rstrip())
        for n in notes:
            out.append(note(n, 0 if title else 4))
    return "\n".join(out)+"\n"
shutil.rmtree(DOCS/"recipes", ignore_errors=True)
nav=[]
for cat,(en,te) in CATS.items():
    d=SRC/cat
    if not d.exists(): continue
    (DOCS/"recipes"/cat).mkdir(parents=True)
    items=[]
    for f in sorted(d.glob("*.md")):
        body=convert(f.read_text())
        extra=""
        if f.stem in AUDIO:
            extra+="\n## Amma's voice notes\n\n"+"".join(f'<audio controls preload="none" src="../../../audio/{a}"></audio>\n\n' for a in AUDIO[f.stem])
        if f.stem in IMG:
            extra+=f"\n## Amma's handwriting\n\n![Amma's handwritten page](../../images/{IMG[f.stem]}){{ loading=lazy }}\n"
        (DOCS/"recipes"/cat/f.name).write_text(body+extra)
        t=re.sub(r"\s*\[.*?\]","",body.splitlines()[0][2:]).strip()
        items.append((t,f"recipes/{cat}/{f.name}"))
    lines=[f"# {en} ({te})\n"]+[f"- [{t}](../../{p})" for t,p in items]
    (DOCS/"recipes"/cat/"index.md").write_text("\n".join(lines)+"\n")
    nav.append((f"{en}",cat,items))
# home cards
cards="\n".join(f"-   **[{en} · {CATS[c][1]}](recipes/{c}/index.md)**\n\n    ---\n\n    "+", ".join(t for t,_ in it)+"\n" for en,c,it in nav)
(DOCS/"index.md").write_text(open("home_template.md").read().replace("{{CARDS}}",cards))
# nav yaml
y=["nav:","  - Home: index.md"]
for en,c,it in nav:
    y.append(f"  - \"{en}\":"); y.append(f"    - recipes/{c}/index.md")
    for t,p in it: y.append(f"    - \"{t}\": {p}")
cfg=open("mkdocs.base.yml").read()+"\n"+"\n".join(y)+"\n"
open("mkdocs.yml","w").write(cfg)
