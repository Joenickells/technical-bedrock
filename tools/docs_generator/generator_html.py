import os
import shutil
import json
import pprint

#Credit: https://stackoverflow.com/questions/29959191/how-to-parse-json-file-with-c-style-comments
def GetJsonFromFile(fh):
    contents = ""
    for line in fh:
        cleanedLine = line.split("//", 1)[0]
        if len(cleanedLine) > 0 and line.endswith("\n") and "\n" not in cleanedLine:
            cleanedLine += "\n"
        contents += cleanedLine
    fh.close
    while "/*" in contents:
        preComment, postComment = contents.split("/*", 1)
        contents = preComment + postComment.split("*/", 1)[1]
    return json.loads(contents)

#Handle a single json file, return tuples of k/v pairs for stripped components
def strip_components(filename):
    print("Handling: " + filename)

    #Open file
    with open(filename) as json_file:
        data = GetJsonFromFile(json_file)

        #Setup components list
        components = []

        #Gather raw components and groups
        components_raw = data.get("minecraft:entity", {}).get("components", {})
        component_groups = data.get("minecraft:entity", {}).get("component_groups", {})

        #Bring components into a list
        for component in components_raw.items():
            components.append(component)

        #Bring component groups into a list
        for group_name in component_groups:
            group = component_groups.get(group_name)
            for component in group.items():
                components.append(component)

        marked_components = []

        for component in components:
            marked_components.append(
                {
                    "entity": filename,
                    "id": component[0],
                    "component": component[1]
                }
            )

        return marked_components        


def main():
    #Prep data structures
    outpath = os.getcwd()
    outfile = open(os.path.join(outpath,  "components.md"), "w+")

    filenames = os.listdir()
    components = []

    #Loop over filename
    for filename in filenames:
        #We only care about json files.
        if(filename.endswith(".json")):
            components.extend(strip_components(filename))
    
    components = sorted(components, key = lambda i: i['id'])

    #Prep outfile:
    outfile.write("# Vannila Components\n")
    outfile.write(
        "This documentation is auto-generated using a python script, written by SirLich. If there is an issue, please bring it to his attention by contacting him on discord: `SirLich#1658`\n\n"
    )
    
    outfile.write("# Table of contents\n")

    #Handle the table of contents:
    sections = set()

    #Gather non dupes
    for component in components:
        sections.add(component["id"])

    #Write out
    for section in sections:
        outfile.write(" - [{0}](#{0})\n".format(section))

    #Handle components:
    current = ""
    entity = ""
    for component in components:
        #Reset current, so we can create headers:
        if(component["id"] != current):
            current = component["id"]
            outfile.write("# " + current + "\n")
        
        if(component["entity"] != entity):
            entity = component["entity"]
            outfile.write("### " + entity + "\n")
        
        outfile.write("```JSON\n\"" + component["id"] + "\": " + json.dumps(component["component"], indent=4) + "\n```\n\n")



    
main()