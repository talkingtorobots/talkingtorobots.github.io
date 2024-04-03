import os
import yaml

# Load Publications 
pubs = yaml.load(open("../generation_code/publications.yaml"), Loader=yaml.CLoader)

# Load Students
stud = yaml.load(open("students.yaml"), Loader=yaml.CLoader)

website = "".join([line for line in open("group_template.html")])

students = []
for S in stud:
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
    students.append(template)

block = ""
for i in range(0,len(students),3):
    block += '<div class="card-group">'
    block += students[i] + "\n\n"
    block += students[i+1] + "\n\n"
    block += students[i+2] + "\n\n"
    block += '</div> <!-- group -->'

website = website.replace("#PHD#", block)

out = open("index.html",'wt')
out.write(website)
out.close()
