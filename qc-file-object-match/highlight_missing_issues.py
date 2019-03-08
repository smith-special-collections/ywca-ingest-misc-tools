from colorama import Fore, Style

def file2list(fileName):
    mylist = []
    with open(fileName, 'r') as fp:
        for line in fp:
            mylist.append(line.strip())
    return mylist

def makeComplex(mylist):
    complexList = []
    for item in mylist:
        complexList.append({'path': item, 'missing': None})
    return complexList

missingIssues = file2list('missing-serials-issues.list')
allIssues = file2list('ywcasr-batch-0003-issues-notitledirs.list')
missingIssues.sort()
allIssues.sort()
allIssuesComplex = makeComplex(allIssues)

for issue in allIssuesComplex:
    if issue['path'].split('/')[-1] in missingIssues:
        issue['missing'] = True
    else:
        issue['missing'] = False

for issue in allIssuesComplex:
    if issue['missing']:
        print(issue['path'])
#        print(Fore.RED + issue['path'] + Style.RESET_ALL)
    else:
        print("x " + issue['path'])
#    print("%s %s" % (issue['missing'], issue['path']))
import pdb; pdb.set_trace()
