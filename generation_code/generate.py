import os
import yaml

# Load Publications 
pubs = yaml.load(open("publications.yaml"), Loader=yaml.CLoader)

# Load Author urls
webs = yaml.load(open("websites.yaml"), Loader=yaml.CLoader)

# Students
students = set(["Hao Zhu", "So Yeon Min", "Yingshan Chang", \
                "Vidhi Jain", "Jared Fernandez", "Quanting Xie"])
student_yaml = yaml.load(open("students.yaml"), Loader=yaml.CLoader)


# Load template
types = {
         "conference": ["inproceedings", "booktitle"],
         "journal": ["article", "journal"],
         "phdthesis": ["phdthesis", "school"],
         "preprint": ["article", "journal"],
         "workshop": ["inproceedings", "booktitle"],
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

# TODO: Redundant with library
accents = {"{\\'e}": "é", "{\\`e}": "è", "{\\'a}": "á", "{\\'o}": "ó", 
           "{\\'u}": "ú", "{\\'c}": "ć", "{\\'\\\\i}":"í",
           "{\\\"a}": "ä", "{\\o}": "ø", "{\\aa}": "å", "{\\l}": "ł", "{\\'y}": "ý",
           "{\\\"o}": "ö","{\\\"u}": "ü", "{\\'s}": "ś", "{\\^o}": "ô",
           "\\v{c}": "č", "\\v{s}": "š", "\\v{r}": "ř"}
def pretty(s):
  for k in accents:
    s = s.replace(k, accents[k])
    s = s.replace(k.upper(), accents[k].upper())
  if s[0] == "{" and s[-1] == "}":
    s = s[1:-1]
  return s

def create_html_entry(entry, idx):
  # Read entry template
  if "URL" in entry and len(entry["URL"].strip()) > 0:
    html = "".join([line for line in open("entry.html")])
  else:
    html = "".join([line for line in open("entry_nourl.html")])
  html = html.replace("#IDX#", str(idx))

  # Authors
  authors = pretty(", ".join(entry["AUTHORS"]))
  # Add links to all co-authors
  for v in webs:
    authors = authors.replace(v, "<a href={}>{}</a>".format(webs[v], v))
  for p in students:
    authors = authors.replace(p, f"<div class=\"name\">{p}</div>")
  authors = authors.replace("Yonatan Bisk", f"<div class=\"name\">Yonatan Bisk</div>")

  values = {
            "#TITLE#":     entry["TITLE"],
            "#YEAR#":      str(entry["YEAR"]),
            "#YEAR-btn#":  entry["YEAR"],
            "#VENUE#":     entry["VENUE"],
            "#VENUE-ACR#": entry["VENUE-ACR"],
            "#BIBREC#":    types[entry["TYPE"]][0],
            "#BOOK#":      types[entry["TYPE"]][1],
            "#FIELD#":     colors[entry["FIELD"]], 
            "#FIELDS#":    entry["FIELD"],
            "#CITEKEY#":   entry["VENUE-ACR"].replace(' ','-') + ":" + entry["AUTHORS"][0].split()[-1] + str(entry["YEAR"]),
            "#AUTH-BIB#":  " and ".join(entry["AUTHORS"]),
            "#AUTHORS#":   authors,
            "#URL#":       entry["URL"] if "URL" in entry else '',
            "#COLOR#":     '#FFFFFF;' if entry["TYPE"] in ["journal", "conference"] else '#EBEBEB;'
          }

  # Replace values
  for key in values:
    html = html.replace(key, values[key])

  # if current student, add photo
  for author in entry["AUTHORS"]:
    if author in students:
      name = author.replace(" ","")
      photo = f"<img class=\"align-self-start mr-3\" \
                src=\"CLAW/images/students/{name.lower()}.webp\" \
                height=44pt width=44pt alt=\"{entry['AUTHORS'][0]}\">"
      print(f'Photo for {entry["AUTHORS"][0]} on {entry["TITLE"]}')
      break
    else:
        photo = ""
  html = html.replace("#STUDENTPHOTO#",photo)

  # Include extra links
  additional = ""
  btn = "&nbsp; <a class=\"sbtn\" "
  if "EXTRAS" in entry:
    for key in entry["EXTRAS"]:
      link = entry["EXTRAS"][key]
      additional += " {} href=\"{}\">{}</a>".format(btn, link, key)
  html = html.replace("#EXTRA#", additional)

  return html

def create_latex_entry(entry):
  tex = "{\\begin{minipage}[t]{5.2in}\\href{#URL#}{#TITLE#}\end{minipage}\\hfill \\textnormal{#YEAR#}}\n" \
        "   \t{\\begin{tabular}{@{}p{5.2in}}" \
        "       #AUTHORS#" \
        "     \\end{tabular}}\n" \
        "   \t{\\begin{tabular}{@{}p{5in}}#VENUE# #PRESENTATION#\\end{tabular} }" \
        "      { }{}\n"
  tex = tex.replace("#YEAR#", entry["YEAR"])
  tex = tex.replace("#URL#", entry["URL"] if "URL" in entry else "")
  tex = tex.replace("#TITLE#", entry["TITLE"].replace("&","\\&"))
  if "NOTE" in entry:
    entry["VENUE"] += "\\\\ -- \\textbf{" + entry["NOTE"] + "}"
  tex = tex.replace("#VENUE#", entry["VENUE"])
  tex = tex.replace("#PRESENTATION#", f'({entry["PRES"]})' if "PRES" in entry else "")
  authors = ", ".join(entry["AUTHORS"])
  authors = authors.replace("Yonatan Bisk","\\YB{}")
  tex = tex.replace("#AUTHORS#", authors)
  return tex

def create_student_card(S):
    template = "".join([line for line in open("student.html")])
    for key in S:
        template = template.replace(f"#{key}#", str(S[key]))
    if "CO" in S:
        coadvisor = f"<h6>(co- <a href=\"{S['CO-WEB']}\">{S['CO']}</a>)</h6>"
    else:
        coadvisor = "<h6>&nbsp;</h6>"
    template = template.replace("#COADVISOR#",coadvisor)

    # This is inefficient but whatevs
    papers = ""
    for pub in pubs:
        if S["NAME"] in pub["AUTHORS"] and pub["TYPE"] != "workshop" :
            papers += f"<a href=\"{pub['URL']}\">{pub['TITLE']}</a><br><br>"

    collapse = ""
    if len(papers) > 0:
        collapse = f"<button class=\"collapsible\">Research</button>\n"
        collapse += "<div class=\"content\">\n"
        collapse += "<p style='margin-top:1rem;margin-bottom:0;'>" + papers + "</p>"
        collapse += "</div>"
    papers = collapse
    template = template.replace("#RESEARCH#", papers)
    return template


## Generate Publications Website ##
website = "".join([line for line in open("pub_template.html")])
idx = len(pubs)
peer_reviewed = ""
workshop_tech = ""
for entry in pubs:
  generated_html = create_html_entry(entry, idx)
  peer_reviewed += generated_html
  idx -= 1

## Generate Plot ##
data = {"WS1":0, "WS2":0, "WS3":0, "WS4":0, "WS5":0, "O":0}
for entry in pubs:
    u = 1.0
    data[entry["FIELD"]] += u

table = f"['Text',      {data['WS1'] + data['WS2']},'#007EF6'],\n"\
      + f"['Perception',{data['WS3']},'#53A351'],\n"\
      + f"['Action',    {data['WS4']},'#CB444A'],\n"\
      + f"['Social',    {data['WS5']},'#f6c144'],\n"\
      + f"['Other',     {data['O']},  '#49A0B5']\n"


website = website.replace("###PEERREVIEW###", peer_reviewed)
website = website.replace("###TECHREPORT###", workshop_tech)
website = website.replace("###PLOT###", table)
out = open("../publications.html",'wt')
out.write(website)
out.close()


## Generate CV ##
latex = "".join([line for line in open("CV_template.tex")])
latex_papers = {"journal": [],
                "conference": [],
                "workshop": [],
                "preprint": [],
                "phdthesis": [],
                }
previous = 10000
for entry in pubs:
  latex_papers[entry["TYPE"]].append(create_latex_entry(entry))

# Hi dear reader, why is Yonatan doing this ugly thing? 
# This categorization and numbering is a required format for submitting 
# promotion materials
pub_count = 1
def number_pub(vals):     
  global pub_count
  comb = ""
  for v in vals:
    comb += "\pub{" + str(pub_count) + ".}\n\t" + v
    pub_count += 1
  return comb

latex = latex.replace("##JOUR##", number_pub(latex_papers["journal"]))
latex = latex.replace("##CONF##", number_pub(latex_papers["conference"]))
latex = latex.replace("##WORK##", number_pub(latex_papers["workshop"]))
latex = latex.replace("##TECH##", number_pub(latex_papers["preprint"] + latex_papers["phdthesis"]))
out = open("CV.tex",'wt')
out.write(latex)
out.close()
os.system("pdflatex CV.tex")
os.system("rm CV.tex CV.log CV.aux CV.out")
os.system("mv CV.pdf ../")


## Generate group page
website = "".join([line for line in open("group_template.html")])
block = ""
students = [create_student_card(stud) for stud in student_yaml]
for i in range(0,len(students),3):
    block += '<div class="card-group">'
    block += students[i] + "\n\n"
    block += students[i+1] + "\n\n"
    block += students[i+2] + "\n\n"
    block += '</div> <!-- group -->'

website = website.replace("#PHD#", block)

out = open("../CLAW/index.html",'wt')
out.write(website)
out.close()
