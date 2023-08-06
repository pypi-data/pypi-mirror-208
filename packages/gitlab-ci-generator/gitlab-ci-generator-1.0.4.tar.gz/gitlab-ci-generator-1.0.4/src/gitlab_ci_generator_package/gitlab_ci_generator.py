import jinja2
import os
import yaml
from pathlib import Path
import argparse
import sys


class JobItem:
    def __init__(self, name, folder, gitlab_yml_file,
                 parents, level, children=[]):
        self.name = name
        self.folder = folder
        self.gitlab_yml_file = gitlab_yml_file
        self.parents = parents
        self.children = children
        self.level = level


def get_parser():
    app_name = 'gitlab-ci-generator.py'
    description = 'Generates gitlab-ci.yml files from templates'

    parser = argparse.ArgumentParser(prog=app_name, description=description)
    optional_group = parser.add_argument_group("optional arguments")
    optional_group.add_argument(
        "-t",
        "--templatefile",
        type=Path,
        help="input template file."
    )
    optional_group.add_argument(
        "-o",
        "--outputfile",
        type=Path,
        help="output file."
    )
    required_group = parser.add_argument_group("required arguments")
    required_group.add_argument(
        "-f",
        "--inputfile",
        required=True,
        type=Path,
        help="input yaml file to define job hierarchy"
    )

    args = parser.parse_args()

    return parser


def parseYaml(yamlFile):
    with open(yamlFile, 'r') as stream:
        try:
            parsed_yaml = yaml.safe_load(stream)
            return parsed_yaml
        except yaml.YAMLError as exc:
            print(exc, file=sys.stderr)


def getJobs(dict):
    # get jobs dict
    if "jobs" in dict:
        dictJobs = dict["jobs"]
    else:
        raise Exception("Input file must have a jobs dictionary")

    # change yaml dictionary to objects
    arrayJobObjects = processJobs(dictJobs)
    # set children to objects
    for job in arrayJobObjects:
        tempChildren = []
        for job1 in arrayJobObjects:
            if job.name in job1.parents:
                tempChildren.append(job1)
        setattr(job, "children", tempChildren)
    # update parents to objects
    for job in arrayJobObjects:
        tempParents = []
        for parent in job.parents:
            for subArray in arrayJobObjects:
                if parent == subArray.name:
                    tempParents.append(subArray)
        setattr(job, "parents", tempParents)

    return arrayJobObjects


def processJobs(dictJobs, level=0, parents=""):
    arrayJobObjects = []
    for job in dictJobs:
        if "name" in job:
            tempJobName = job["name"]
        else:
            raise Exception("Input file jobs items must have name")
        if "folder" in job:
            tempJobFolder = job["folder"]
        else:
            raise Exception("Input file jobs items must have folder")
        if "gitlab_yml_file" in job:
            tempJobGitlabCiFile = job["gitlab_yml_file"]
        else:
            tempJobGitlabCiFile = ".gitlab-ci.yml"
        if parents == "":
            tempParents = []
        else:
            tempParents = parents.split(",")

        arrayJobObjects.append(
            JobItem(
                name=tempJobName,
                folder=tempJobFolder,
                gitlab_yml_file=tempJobGitlabCiFile,
                parents=tempParents,
                level=level
            )
        )

        if "dependent_jobs" in job:
            dictSubJobs = job["dependent_jobs"]
            if parents != "":
                tempParent = parents + ',' + tempJobName
            else:
                tempParent = tempJobName

            tempDependentJobs = processJobs(dictSubJobs, level+1, tempParent)
            for subJob in tempDependentJobs:
                arrayJobObjects.append(subJob)

    return arrayJobObjects


def readJinjaTemplate(templateFilePath):
    basePath = os.path.dirname(templateFilePath)
    fileName = os.path.basename(templateFilePath)

    templateLoader = jinja2.FileSystemLoader(searchpath=basePath)
    templateEnv = jinja2.Environment(
        loader=templateLoader,
        autoescape=True,
        trim_blocks=True
        )
    TEMPLATE_FILE = fileName
    template = templateEnv.get_template(TEMPLATE_FILE)

    return template


def getInfoDict(inputDict, dictSection, dictName):
    if dictSection in inputDict:
        dictSectionInfo = inputDict[dictSection]
    else:
        raise Exception(dictSection + " is missing from inputfile")

    if dictName in dictSectionInfo:
        dictOutput = dictSectionInfo[dictName]
    else:
        dictOutput = {}

    return dictOutput


def processTemplate(template, dict):
    # get pipelineInfo
    pipeline_info = dict['pipeline_info']
    # get jobs
    jobs = getJobs(dict)
    # render template
    outputText = template.render(jobs=jobs, pipeline_info=pipeline_info)

    return outputText


def writeOutputFile(output, outputFile):
    with open(outputFile, 'w') as f:
        f.write(output)
    print("Output was written to file " + str(outputFile), file=sys.stderr)


def main():
    args = get_parser().parse_args()
    # read and parse inputfile yaml
    dict = parseYaml(args.inputfile.resolve())
    # load in template
    if args.templatefile:
        templateFile = args.templatefile.resolve()
    else:
        print("defaulting to use built-in template", file=sys.stderr)
        templateDir = os.path.realpath(
            os.path.join(
                os.path.dirname(__file__), 'templates/'
                )
            )
        templateFile = os.path.join(templateDir, "gitlab-template.jinja")

    template = readJinjaTemplate(templateFile)
    output = processTemplate(template, dict)
    if args.outputfile:
        writeOutputFile(output, args.outputfile)
    else:
        print(output)


if __name__ == '__main__':
    sys.exit(main())
