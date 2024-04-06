import os
import yaml

# Load Publications 
pubs = yaml.load(open("publications.yaml"), Loader=yaml.CLoader)

# Load Author urls
webs = yaml.load(open("websites.yaml"), Loader=yaml.CLoader)

# Students
student_yaml = yaml.load(open("students.yaml"), Loader=yaml.CLoader)
student_names = set([s["NAME"] for s in student_yaml])


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

def create_html(entry):
    return f"<div class=\"card {entry['FIELD']}\">\n"\
          f"    <div class=\"card-body\" "\
          f"         style=\"background-color: {'#FFFFFF;' if entry['TYPE'] in ['journal', 'conference'] else '#EBEBEB;'}\">\n"\
          f"      <div class=\"row\">\n"\
          f"        <div class=\"col-md-1\">\n"\
          f"          <button type=\"button\" disabled "\
          f"                  class=\"btn ybtn btn-outline-{colors[entry['FIELD']]}\">{entry['YEAR']}</button>\n"\
          f"            {entry['STUDENTPHOTO']}\n"\
          f"        </div>\n"\
          f"        <div class=\"col-md-11\">\n"\
          f"          <b style=\"font-weight: 500; font-size:15pt\" >\n"\
          f"              {entry['TITLE']}\n"\
          f"          </b><br>\n"\
          f"          <div class=\"card-text\">\n"\
          f"            <i style=\"font-weight: 300; font-size:11pt\">\n"\
          f"              {entry['VENUE']} ({entry['VENUE-ACR']})\n"\
          f"            </i><br>\n"\
          f"            <font style=\"font-weight: 300; font-size:11pt\">\n"\
          f"              {entry['AUTHORS']}\n"\
          f"            </font><br>\n"\
          f"            {entry['PAPER-BUTTON']}\n"\
          f"            <a class=\"sbtn\" title\n"\
          f"                data-original-title=\"Copy BibTex\" id=\"buttonidx{entry['IDX']}\"\n"\
          f"                href=\"javascript:void(0)\" onclick=\"show(\'idx{entry['IDX']}\')\">\n"\
          f"                BibTeX\n"\
          f"              </a>\n"\
          f"              {entry['EXTRA']}\n"\
          f"              <div id=\"idx{entry['IDX']}\"  class=\"dynamic_link\">\n"\
          f"                <pre>\n"\
          f"@{types[entry['TYPE']][0]}{{{entry['CITEKEY']},\n"\
          f"    author    = {{{entry['AUTH-BIB']}}},\n"\
          f"    title     = {{{{{entry['TITLE']}}}}},\n"\
          f"    {types[entry['TYPE']][1]} = {{{entry['VENUE']}}},\n"\
          f"    year      = {{{entry['YEAR']}}},\n"\
          f"    url       = {{{entry['URL']}}},\n"\
          f"}}\n"\
          f"              </pre>\n"\
          f"              </div>\n"\
          f"          </div> <!-- text -->\n"\
          f"        </div>\n"\
          f"      </div>\n"\
          f"  </div> <!-- body -->\n"\
          f"</div> <!-- card -->\n"


def create_publication_entry(entry):
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

  # Add links to all co-authors
  for v in webs:
    entry["AUTHORS"] = entry["AUTHORS"].replace(v, "<a href={}>{}</a>".format(webs[v], v))
  for p in student_names:
    entry["AUTHORS"] = entry["AUTHORS"].replace(p, f"<div class=\"name\">{p}</div>")
  entry["AUTHORS"] = entry["AUTHORS"].replace("Yonatan Bisk", f"<div class=\"name\">Yonatan Bisk</div>")


    # Include extra links
  entry["EXTRA"] = ""
  btn = "&nbsp; <a class=\"sbtn\" "
  if "EXTRAS" in entry:
    for key in entry["EXTRAS"]:
      link = entry["EXTRAS"][key]
      entry["EXTRA"] += " {} href=\"{}\">{}</a>".format(btn, link, key)

  return create_html(entry)

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

def student_card_html(entry):
    return f"<!-- {entry['NAME']} -->\n"\
          f"    <div class=\"col card student\" style=\"max-width: 270px; min-width:200px;\">\n"\
          f"      <a href=\"{entry['WEB']}\">\n"\
          f"        <img src=images/students/{entry['PIC']} class=\"card-img-top\" alt=\"{entry['NAME']}\">\n"\
          f"      </a>\n"\
          f"      <img src=\"images/{entry['DEPT']}.png\" height=40px class=\"logo\" alt=\"{entry['DEPT']} logo\">\n"\
          f"      <div class=\"card-body\">\n"\
          f"        <h5 class=\"card-title\">\n"\
          f"            <p class=\"m-flip js-flip\" style=\"font-weight:200; font-size: 20px;\">\n"\
          f"              <span class=\"m-flip_item\"><a href=\"{entry['WEB']}\"><b>{entry['NAME']}</b></a></span>\n"\
          f"              <span class=\"m-flip_item\"><a href=\"{entry['WEB']}\"><b>{entry['NATIVE']}</b></a></span>\n"\
          f"            </p>\n"\
          f"          <h6><a href=\"https://twitter.com/{entry['X']}\">@{entry['X']}</a>\n"\
          f"              <font class=\"pronoun\">{entry['PRON']}</font></h6>\n"\
          f"          <img width=50 src=\"images/WSs/WS{entry['WS']}_small.webp\" \n"\
          f"               style=\"margin-bottom:0px;margin-top:0px;width:50;border:0px;display:inline;float:right;\" \n"\
          f"               alt=\"small robot\">\n"\
          f"        </h5>\n"\
          f"        <p class=\"card-text\">\n"\
          f"        <br>\n"\
          f"        <h6>{entry['COADVISOR']} </h6>\n"\
          f"        </p>\n"\
          f"        <hr>\n"\
          f"        <h6>\n"\
          f"          {entry['RESEARCH']}\n"\
          f"        </h6>\n"\
          f"      </div> <!-- card-body -->\n"\
          f"    </div> <!-- card --> \n"

def create_student_card(S):
    if "CO" in S:
        S["COADVISOR"] = f"<h6>(co- <a href=\"{S['CO-WEB']}\">{S['CO']}</a>)</h6>"
    else:
        S["COADVISOR"] = "<h6>&nbsp;</h6>"

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
    return student_card_html(S)


## Generate Publications Website ##
website = "".join([line for line in open("pub_template.html")])
idx = len(pubs)
peer_reviewed = ""
workshop_tech = ""
for entry in pubs:
  entry["IDX"] = idx
  generated_html = create_publication_entry({v:entry[v] for v in entry})
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
block = '<div class="container" id="students"><div class="row row-cols-1 row-cols-3 g-0">'
students = [create_student_card(stud) for stud in student_yaml]
for student in students:
  block += student + "\n\n"
block += '</div></div>' 

website = website.replace("#PHD#", block)

out = open("../CLAW/index.html",'wt')
out.write(website)
out.close()
