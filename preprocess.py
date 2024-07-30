import re

pattern = r'\{fs\}(.*)'
text = ""
with open("latex_project/main.tex", "r") as file:
    text = file.read()
    text = re.sub(r'%.*$', '', text, flags=re.MULTILINE)
    text = text.replace("\n", "<newline>")

matches = re.findall(pattern, text)
if matches:
    print(matches[0])
    inp_list = matches[0].split("<newline>")
    # find index of {fs} and remove left of it
    for i in range(len(inp_list)):
        if inp_list[i].strip() == "{fs}":
            inp_list = inp_list[i+1:]
            break
    print(inp_list)
    with open("latex_project/out2.tex", "w") as file:
        for inp in inp_list:
            if "}" in inp and "{" in inp and "input" not in inp:
                break
            if inp.strip() == "":
                continue
            if inp.strip().startswith("%"):
                continue
            if inp.strip().startswith("\\input"):
                file.write(inp.strip() + "\n") 