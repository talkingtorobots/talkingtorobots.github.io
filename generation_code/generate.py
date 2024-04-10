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

  # Authors and links to all co-authors
  entry["AUTHORS-PRETTY"] = pretty_author_names(", ".join(entry["AUTHORS"]))
  for v in webs:
    entry["AUTHORS-PRETTY"] = entry["AUTHORS-PRETTY"].replace(v, "<a href={}>{}</a>".format(webs[v], v))
  for p in student_names:
    entry["AUTHORS-PRETTY"] = entry["AUTHORS-PRETTY"].replace(p, f"<div class=\"name\">{p}</div>")
  entry["AUTHORS-PRETTY"] = entry["AUTHORS-PRETTY"].replace("Yonatan Bisk", f"<div class=\"name\">Yonatan Bisk</div>")

def add_student_papers(S):
    # This is inefficient but whatevs
    S['RESEARCH'] = []
    for pub in pubs:
        S['RESEARCH'].append(pub) if S["NAME"] in pub["AUTHORS"] and pub["TYPE"] != "workshop" else None
            
def generate_publications_website():
    with open("templates/pub_template.jinja2", 'r') as file:
      pub_template = Template(file.read())

    for entry in pubs:
      update_pub_entry(entry)

    ## Generate Plot ##
    data = {"WS1":0, "WS2":0, "WS3":0, "WS4":0, "WS5":0, "O":0}
    for entry in pubs:
        u = 1.0
        data[entry["FIELD"]] += u

    rendered = pub_template.render(publications=pubs, data=data, colors=colors, types=types)
    with open("../publications.html", 'wt') as output_file:
        output_file.write(rendered)

def number_pub(vals, pub_count=1):  
    for val in vals:
        val["idx"] = pub_count
        pub_count += 1
    return pub_count
        
def generate_CV():
    ## Generate CV ##
    with open("templates/CV_template.jinja2", 'r') as file:
      latex_template = Template(file.read())
    latex_papers = {"Journal": [],
                    "Conference": [],
                    "Workshop": [],
                    "Preprint": [],
                    }
    for entry in pubs:
      latex_papers[entry["TYPE"]].append(entry)

    # Hi dear reader, why is Yonatan doing this ugly thing? 
    # This categorization and numbering is a required format for submitting 
    # promotion materials
    pub_count = number_pub(latex_papers["Journal"])
    pub_count = number_pub(latex_papers["Conference"], pub_count)
    pub_count = number_pub(latex_papers["Workshop"], pub_count)
    number_pub(latex_papers["Preprint"], pub_count)

    latex_render = latex_template.render(pub_types=["Journal", "Conference", "Workshop", "Preprint"], 
                                        publications=latex_papers)
    with open("CV.tex", 'wt') as output_file:
        output_file.write(latex_render)
    os.system("pdflatex CV.tex")
    os.system("rm CV.tex CV.log CV.aux CV.out")
    os.system("mv CV.pdf ../")

def generate_group_page():
    ## Generate group page
    with open("templates/group_template.jinja2", 'r') as file:
      group_template = Template(file.read())
    for stud in student_yaml:
        add_student_papers(stud)
    masters = yaml.load(open("yaml/masters_interns.yaml"), Loader=yaml.CLoader)
    alumni = yaml.load(open("yaml/alumni.yaml"), Loader=yaml.CLoader)
    group_render = group_template.render(students=student_yaml, alumni=alumni, masters=masters)
    with open("../CLAW/index.html", 'wt') as output_file:
        output_file.write(group_render)

def main():
    generate_publications_website()
    generate_CV()
    generate_group_page()

if __name__ == "__main__":
    main()