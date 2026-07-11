import os
import sys
import yaml
import openpyxl
import argparse
from copy import copy
from datetime import date
from jinja2 import Environment, FileSystemLoader
from openpyxl.styles import Border, Side
from openpyxl.utils import range_boundaries, get_column_letter
from openpyxl.worksheet.table import Table
from pydantic import ValidationError

from schemas import Publication, Person, Affiliation
from authors import render_authors

parser = argparse.ArgumentParser(description='Generate Website, CV, COA')
parser.add_argument('--onepager', action='store_true',
                    help='One-pager vs full')
args = parser.parse_args()

jinja_env = Environment(loader=FileSystemLoader("templates"))

def load_yaml(path):
    return yaml.load(open(path), Loader=yaml.CLoader)

# Load Publications 
def load_validated(path, model):
    entries = load_yaml(path)
    validated = []
    for i, entry in enumerate(entries):
        try:
            validated.append(model(**entry).model_dump(exclude_unset=True))
        except ValidationError as e:
            sys.exit(f"{path}: entry {i} ({entry.get('name', entry.get('title', '?'))}) failed validation:\n{e}")
    return validated

pubs = load_validated("yaml/publications.yaml", Publication)
if args.onepager:
    pubs = [p for p in pubs if p.get("onepager")]

# Load Author urls
webs = load_yaml("yaml/websites.yaml")

# Students
student_yaml = load_validated("yaml/students/phd.yaml", Person)
student_names = set([s["name"] for s in student_yaml])
postdoc_yaml = load_validated("yaml/students/postdoc.yaml", Person)
alumni_phd = load_validated("yaml/students/phd_alumni.yaml", Person)
masters = load_validated("yaml/students/ms_intern.yaml", Person)
alumni = load_validated("yaml/students/alumni.yaml", Person)

# Theses
theses_yaml = load_yaml("yaml/theses.yaml")
teach_yaml = load_yaml("yaml/teaching.yaml")
areachair_yaml = load_yaml("yaml/area_chair.yaml")

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

def update_pub_entry(entry):
  # Authors and links to all co-authors
  entry["authors_pretty"] = render_authors(entry["authors"], webs, student_names)

def generate_publications_website():
    pub_template = jinja_env.get_template("pub_template.jinja2")

    for entry in pubs:
      update_pub_entry(entry)

    ## Generate Plot ##
    data = {"WS1":0, "WS2":0, "WS3":0, "WS4":0, "WS5":0, "O":0}
    for entry in pubs:
        u = 1.0
        data[entry["field"]] += u

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
    if args.onepager:
        template = "CV_template_1p.jinja2"
    else:
        template = "CV_template.jinja2"
    latex_template = jinja_env.get_template(template)
    latex_papers = {"Journal": [],
                    "Conference": [],
                    "Workshop": [],
                    "Preprint": [],
                    }
    for entry in pubs:
      latex_papers[entry["type"]].append(entry)

    # Hi dear reader, why is Yonatan doing this ugly thing? 
    # This categorization and numbering is a required format for submitting 
    # promotion materials
    pub_count = number_pub(latex_papers["Journal"])
    pub_count = number_pub(latex_papers["Conference"], pub_count)
    pub_count = number_pub(latex_papers["Workshop"], pub_count)
    number_pub(latex_papers["Preprint"], pub_count)

    if args.onepager:
      latex_render = latex_template.render(pub_types=["Journal", "Conference"], 
                                           publications=latex_papers,
                                           students=student_yaml,
                                           postdocs=postdoc_yaml,
                                           teaching=teach_yaml,
                                           areachair=areachair_yaml,
                                           theses=theses_yaml)
    else:
      latex_render = latex_template.render(pub_types=["Journal", "Conference", "Workshop", "Preprint"],
                                           publications=latex_papers,
                                           students=student_yaml,
                                           postdocs=postdoc_yaml,
                                           alumni_phd=alumni_phd,
                                           masters=masters,
                                           alumni=alumni,
                                           teaching=teach_yaml,
                                           areachair=areachair_yaml,
                                           theses=theses_yaml)
    with open("CV.tex", 'wt') as output_file:
        output_file.write(latex_render)
    if os.system("pdflatex -interaction=nonstopmode CV.tex") != 0 or not os.path.exists("CV.pdf"):
        sys.exit("pdflatex failed to produce CV.pdf; see CV.log. Leaving the previous CV.pdf untouched.")
    os.system("rm CV.tex CV.log CV.aux CV.out")
    os.system("mv CV.pdf ../")

def generate_group_page():
    ## Generate group page
    group_template = jinja_env.get_template("group_template.jinja2")
    for stud in student_yaml:
        stud["research"] = []
        for pub in pubs:
            if stud["name"] in pub["authors"] and pub["type"] != "workshop":
                stud["research"].append(pub)
    group_render = group_template.render(students=student_yaml,
                                         postdocs=postdoc_yaml, 
                                         alumni=alumni, 
                                         alumni_phd=alumni_phd, 
                                         masters=masters)
    with open("../CLAW/index.html", 'wt') as output_file:
        output_file.write(group_render)

def generate_COA():

    ## Create a list of collaborators from the last 48 months with affiliations (for NSF)
    collaborators = {}
    cutoff_year = date.today().year - 4
    for pub in pubs:
        if int(pub["year"]) > cutoff_year and "Open X-" not in pub["title"]:
            for a in pub["authors"]:
              if a != "Yonatan Bisk" and a not in student_names:
                parts = a.rsplit(' ',1)
                last_first = parts[1] + ", "+ parts[0]
                collaborators[last_first] = max(int(pub["year"]), collaborators.get(last_first, 0))

    aff_yaml = load_validated("yaml/affiliations.yaml", Affiliation)
    affiliations = {}
    for entry in aff_yaml:
        affiliations[entry["name"]] = entry["affiliation"]
    
    new_entries = len(collaborators)

    # Load the COA excel spreadsheet
    # Heavily ChatGPT based code here
    workbook = openpyxl.load_workbook('templates/COA.xlsx')
    sheet = workbook.active
    start_row = 52

    # Create a black border style
    border_style = Border(
        left=Side(style='thin', color='000000'),
        right=Side(style='thin', color='000000'),
        top=Side(style='thin', color='000000'),
        bottom=Side(style='thin', color='000000')
    )

    # Adjust merged cells ranges
    for merge in list(sheet.merged_cells.ranges):
        min_col, min_row, max_col, max_row = range_boundaries(str(merge))
        if min_row >= start_row:
            sheet.merged_cells.remove(merge)
            new_merge = f"{openpyxl.utils.get_column_letter(min_col)}{min_row + new_entries}:{openpyxl.utils.get_column_letter(max_col)}{max_row + new_entries}"
            sheet.merged_cells.add(new_merge)
    
    # Adjust the TableD5 position (this is the Editorial board)
    table_d5 = None
    for tbl in sheet.tables.values():
        if tbl.name == 'TableD5':
            table_d5 = tbl
            break

    if table_d5:
        min_col, min_row, max_col, max_row = range_boundaries(table_d5.ref)
        new_ref = f"{get_column_letter(min_col)}{min_row + new_entries}:{get_column_letter(max_col)}{max_row + new_entries}"
        table_d5.ref = new_ref

    sheet.insert_rows(start_row, amount=new_entries)

    for i, author in enumerate(collaborators, start=start_row):
        data = ['A:', 
                author, 
                affiliations[author] if author in affiliations else '',
                '',
                '1/1/' + str(collaborators[author])
                ]
        for col_num, value in enumerate(data, start=1):
            cell = sheet.cell(row=i, column=col_num, value=value)
            cell.border = border_style
    workbook.save('current_COA.xlsx')

def main():
    if not args.onepager:
        generate_publications_website()
    generate_CV()
    if not args.onepager:
        generate_group_page()
        generate_COA()

if __name__ == "__main__":
    main()
