import os
import yaml
from jinja2 import Template

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

def publication_html(entry):
    template_string = """
    <div class="card {{ entry['FIELD'] }}">
      <div class="card-body" 
          style="background-color: {{ '#FFFFFF' if entry['TYPE'] in ['journal', 'conference'] else '#EBEBEB' }};">
        <div class="row">
          <div class="col-md-1">
            <button type="button" disabled 
                    class="btn ybtn btn-outline-{{ colors[entry['FIELD']] }}">{{ entry['YEAR'] }}</button>
              {{ entry['STUDENTPHOTO'] | safe }}
          </div>
          <div class="col-md-11">
            <b style="font-weight: 500; font-size:15pt" >
                {{ entry['TITLE'] }}
            </b><br>
            <div class="card-text">
              <i style="font-weight: 300; font-size:11pt">
                {{ entry['VENUE'] }} ({{ entry['VENUE-ACR'] }})
              </i><br>
              <font style="font-weight: 300; font-size:11pt">
                {{ entry['AUTHORS'] }}
              </font><br>
              {{ entry['PAPER-BUTTON'] | safe }}
              <a class="sbtn" title
                  data-original-title="Copy BibTex" id="buttonidx{{ entry['IDX'] }}"
                  href="javascript:void(0)" onclick="show('idx{{ entry['IDX'] }}')">
                  BibTeX
                </a>
                {{ entry['EXTRA'] | safe }}
                <div id="idx{{ entry['IDX'] }}" class="dynamic_link">
                  <pre>
@{{types[entry['TYPE']][0] }}{ {{- entry['CITEKEY'] }},
    author    = { {{- entry['AUTH-BIB'] -}} },
    title     = { {{- entry['TITLE'] -}} },
    {{- types[entry['TYPE']][1] -}} = { {{- entry['VENUE'] -}} },
    year      = { {{- entry['YEAR'] -}} },
    url       = { {{- entry['URL'] -}} },
}
                  </pre>
                </div>
            </div> <!-- text -->
          </div>
        </div>
      </div> <!-- body -->
    </div> <!-- card -->
    """
    template = Template(template_string)
    return template.render(entry=entry, colors=colors, types=types)

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

  return publication_html(entry)

def create_latex_entry(entry):
  authors = ", ".join(entry["AUTHORS"])
  authors = authors.replace("Yonatan Bisk","\\YB{}")
  if "NOTE" in entry:
    entry["VENUE"] += "\\\\ -- \\textbf{" + entry["NOTE"] + "}"
  template_string = """
    {\\begin{minipage}[t]{5.2in}
    \\href{ {{ entry['URL'] if 'URL' in entry else '' }} }
          { {{ entry['TITLE'].replace('&', '\\&') }}     }
    \\end{minipage}\hfill \\textnormal{ {{ entry['YEAR'] }} } }
    \t{\\begin{tabular}{ @{}p{5.2in} }
        {{ authors }}
    \\end{tabular} }
    \t{\\begin{tabular}{@{}p{5in} }
        {{ entry['VENUE'] }} {{ entry['PRES'] if 'PRES' in entry else '' }}
    \\end{tabular} } { }{}
  """
  template = Template(template_string)
  return template.render(entry=entry, authors=authors)
  

def student_card_html(entry):
    template_string = """
        <!-- {{ entry['NAME'] }} -->
        <div class="col card student" style="max-width: 270px; min-width:200px;">
          <a href="{{ entry['WEB'] }}">
            <img src=images/students/{{ entry['PIC'] }} class="card-img-top" alt="{{ entry['NAME'] }}">
          </a>
          <img src="images/{{ entry['DEPT'] }}.png" height=40px class="logo" alt="{{ entry['DEPT'] }} logo">
          <div class="card-body">
            <h5 class="card-title">
              <p class="m-flip js-flip" style="font-weight:200; font-size: 20px;">
                <span class="m-flip_item"><a href="{{ entry['WEB'] }}"><b>{{ entry['NAME'] }}</b></a></span>
                <span class="m-flip_item"><a href="{{ entry['WEB'] }}"><b>{{ entry['NATIVE'] }}</b></a></span>
              </p>
              <h6><a href="https://twitter.com/{{ entry['X'] }}">@{{ entry['X'] }}</a>
                  <font class="pronoun">{{ entry['PRON'] }}</font></h6>
              <img width=50 src="images/WSs/WS{{ entry['WS'] }}_small.webp" 
                  style="margin-bottom:0px;margin-top:0px;width:50;border:0px;display:inline;float:right;" 
                  alt="small robot">
            </h5>
            <p class="card-text"><br><h6>{{ entry['COADVISOR'] }} </h6></p>
            <hr>
            <h6>{{ entry['RESEARCH'] }}</h6>
          </div> <!-- card-body -->
        </div> <!-- card -->
    """
    template = Template(template_string)
    return template.render(entry=entry)

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
with open("pub_template.jinja2", 'r') as file:
  pub_template = Template(file.read())

idx = len(pubs)
peer_reviewed = ""
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

rendered = pub_template.render(PEERREVIEW=peer_reviewed, data=data)
with open("../publications.html", 'wt') as output_file:
    output_file.write(rendered)


## Generate CV ##
with open("CV_template.jinja2", 'r') as file:
  latex_template = Template(file.read())
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
    comb += "\pub{" + str(pub_count) + ".}" + v
    pub_count += 1
  return comb

latex_render = latex_template.render(jour=number_pub(latex_papers["journal"]), 
                                     conf=number_pub(latex_papers["conference"]),
                                     work=number_pub(latex_papers["workshop"]),
                                     tech=number_pub(latex_papers["preprint"] + latex_papers["phdthesis"]))
with open("CV.tex", 'wt') as output_file:
    output_file.write(latex_render)
os.system("pdflatex CV.tex")
os.system("rm CV.tex CV.log CV.aux CV.out")
os.system("mv CV.pdf ../")


## Generate group page
with open("group_template.jinja2", 'r') as file:
  group_template = Template(file.read())
block = '<div class="container" id="students"><div class="row row-cols-1 row-cols-3 g-0">'
students = [create_student_card(stud) for stud in student_yaml]
for student in students:
  block += student + "\n\n"
block += '</div></div>' 

group_render = group_template.render(PHD=block)
with open("../CLAW/index.html", 'wt') as output_file:
    output_file.write(group_render)
