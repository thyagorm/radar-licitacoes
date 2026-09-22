with open("static/dashboard.html", "r", encoding="utf-8") as f:
    html = f.read()

# Vincula o CSS na tag head
link_tag = '<link rel="stylesheet" href="/static/strike-theme.css">'
if link_tag not in html:
    pos_head = html.find("</head>")
    html = html[:pos_head] + "    " + link_tag + "\n" + html[pos_head:]
    print("✅ Link para strike-theme.css adicionado ao <head>!")

with open("static/dashboard.html", "w", encoding="utf-8") as f:
    f.write(html)
