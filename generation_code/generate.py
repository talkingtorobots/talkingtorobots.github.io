import os
import yaml
from jinja2 import Template

# Load Publications 
pubs = yaml.load(open("yaml/publications.yaml"), Loader=yaml.CLoader)

# Load Author urls
webs = yaml.load(open("yaml/websites.yaml"), Loader=yaml.CLoader)

# Students
student_yaml = yaml.load(open("yaml/students.yaml"), Loader=yaml.CLoader)
student_names = set([s["NAME"] for s in student_yaml])


# Load template
types = {
         "Conference": ["inproceedings", "booktitle"],
         "Journal": ["article", "journal"],
         "Preprint": ["article", "journal"],
         "Workshop": ["inproceedings", "booktitle"],
        }
colors = {
          "WS1":"primary", 
          "WS2":"primary", 
          "WS3": "success", 
          "WS4": "danger", 
          "WS5": "warning", 
          "O": "info", 
          "A": "secondary"
        }

accents = {"{\\'e}": "é", "{\\`e}": "è", "{\\'a}": "á", "{\\'o}": "ó", 
           "{\\'u}": "ú", "{\\'c}": "ć", "{\\'\\\\i}":"í",
           "{\\\"a}": "ä", "{\\o}": "ø", "{\\aa}": "å", "{\\l}": "ł", "{\\'y}": "ý",
           "{\\\"o}": "ö","{\\\"u}": "ü", "{\\'s}": "ś", "{\\^o}": "ô",
           "\\v{c}": "č", "\\v{s}": "š", "\\v{r}": "ř"}
def pretty_author_names(s):
  for k in accents:
    s = s.replace(k, accents[k])
    s = s.replace(k.upper(), accents[k].upper())
  if s[0] == "{" and s[-1] == "}":
    s = s[1:-1]
  return s

def update_pub_entry(entry):
  # Create a Paper button
  if "URL" in entry and len(entry["URL"].strip()) > 0:
    entry["PAPER-BUTTON"] = f"<a class=\"sbtn\" href={entry['URL']}>Paper</a>"
  else:
    entry["PAPER-BUTTON"] = ""

  # LaTeX compatible 
  entry["AUTH-BIB"] = ' and '.join(entry['AUTHORS'])

  # Before doing pretification
  entry["CITEKEY"] = entry["VENUE-ACR"].replace(' ','-') + ":" + entry["AUTHORS"][0].split()[-1] + str(entry["YEAR"])
  # if current student, add photo
  for author in entry["AUTHORS"]:
    if author in student_names:
      name = author.replace(" ","")
      entry["STUDENTPHOTO"] = f"<img class=\"align-self-start mr-3\" \
                               src=\"CLAW/images/students/{name.lower()}.webp\" \
                               height=44pt width=44pt alt=\"{entry['AUTHORS'][0]}\">"
      print(f'Photo for {entry["AUTHORS"][0]} on {entry["TITLE"]}')
      break
    else:
      entry["STUDENTPHOTO"] = ""

  # Authors
  entry["AUTHORS"] = pretty_author_names(", ".join(entry["AUTHORS"]))
  entry["AUTHORS-WEB"] = entry["AUTHORS"]

  # Add links to all co-authors
  for v in webs:
    entry["AUTHORS-WEB"] = entry["AUTHORS-WEB"].replace(v, "<a href={}>{}</a>".format(webs[v], v))
  for p in student_names:
    entry["AUTHORS-WEB"] = entry["AUTHORS-WEB"].replace(p, f"<div class=\"name\">{p}</div>")
  entry["AUTHORS-WEB"] = entry["AUTHORS-WEB"].replace("Yonatan Bisk", f"<div class=\"name\">Yonatan Bisk</div>")

  # Include extra links
  entry["EXTRA"] = ""
  btn = "&nbsp; <a class=\"sbtn\" "
  if "EXTRAS" in entry:
    for key in entry["EXTRAS"]:
      link = entry["EXTRAS"][key]
      entry["EXTRA"] += " {} href=\"{}\">{}</a>".format(btn, link, key)

def update_student_card(S):
    if "CO" in S:
        S["COADVISOR"] = f"<div class='coadvisor'>(co- <a href=\"{S['CO-WEB']}\">{S['CO']}</a>)</div>"
    else:
        S["COADVISOR"] = "<div class='coadvisor'>&nbsp;</div>"

    if "NATIVE" not in S: 
       S["NATIVE"] = S["NAME"]
    # This is inefficient but whatevs
    papers = ""
    for pub in pubs:
        if S["NAME"] in pub["AUTHORS"] and pub["TYPE"] != "workshop" :
            papers += f"<a href=\"{pub['URL']}\">{pub['TITLE']}</a><br><br>\n\n"

    collapse = ""
    if len(papers) > 0:
        collapse = f"<button class=\"collapsible\">Research</button>\n"
        collapse += "<div class=\"content\">\n"
        collapse += "<p style='margin-top:1rem;margin-bottom:0;'>" + papers + "</p>"
        collapse += "</div>"
    papers = collapse
    S["RESEARCH"] = papers

## Generate Publications Website ##
with open("templates/pub_template.jinja2", 'r') as file:
  pub_template = Template(file.read())

idx = len(pubs)
peer_reviewed = ""
for entry in pubs:
  entry["IDX"] = idx
  update_pub_entry(entry)
  idx -= 1

## Generate Plot ##
data = {"WS1":0, "WS2":0, "WS3":0, "WS4":0, "WS5":0, "O":0}
for entry in pubs:
    u = 1.0
    data[entry["FIELD"]] += u

rendered = pub_template.render(publications=pubs, data=data, colors=colors, types=types)
with open("../publications.html", 'wt') as output_file:
    output_file.write(rendered)


## Generate CV ##
with open("templates/CV_template.jinja2", 'r') as file:
  latex_template = Template(file.read())
latex_papers = {"Journal": [],
                "Conference": [],
                "Workshop": [],
                "Preprint": [],
                }
previous = 10000
for entry in pubs:
  entry["AUTHORS"] = entry["AUTHORS"].replace("Yonatan Bisk","\\YB{}")
  if "NOTE" in entry:
    entry["VENUE"] += "\\\\ -- \\textbf{" + entry["NOTE"] + "}"
  latex_papers[entry["TYPE"]].append(entry)

# Hi dear reader, why is Yonatan doing this ugly thing? 
# This categorization and numbering is a required format for submitting 
# promotion materials
pub_count = 1
def number_pub(vals):     
  global pub_count
  for val in vals:
    val["idx"] = pub_count
    pub_count += 1
number_pub(latex_papers["Journal"])
number_pub(latex_papers["Conference"])
number_pub(latex_papers["Workshop"])
number_pub(latex_papers["Preprint"])
#number_pub(latex_papers["phdthesis"])

latex_render = latex_template.render(pub_types=["Journal", "Conference", "Workshop", "Preprint"], 
                                     publications=latex_papers)
with open("CV.tex", 'wt') as output_file:
    output_file.write(latex_render)
os.system("pdflatex CV.tex")
os.system("rm CV.tex CV.log CV.aux CV.out")
os.system("mv CV.pdf ../")

## Generate group page
with open("templates/group_template.jinja2", 'r') as file:
  group_template = Template(file.read())
for stud in student_yaml:
    update_student_card(stud)
masters = yaml.load(open("yaml/masters_interns.yaml"), Loader=yaml.CLoader)
alumni = yaml.load(open("yaml/alumni.yaml"), Loader=yaml.CLoader)
group_render = group_template.render(students=student_yaml, alumni=alumni, masters=masters)
with open("../CLAW/index.html", 'wt') as output_file:
    output_file.write(group_render)
