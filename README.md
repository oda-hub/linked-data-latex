[![Build Status](https://travis-ci.org/volodymyrss/rich-draft-templating.png?branch=master)](https://travis-ci.org/volodymyrss/linked-data-latex)
[![codebeat badge](https://codebeat.co/badges/dc6f6224-26f1-45dc-b47f-31baefc92190)](https://codebeat.co/projects/github-com-volodymyrss-linked-data-latex-master)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/6f8743e35a02487981dd0b98660b8000)](https://app.codacy.com/app/vladimir.savchenko/linked-data-latex?utm_source=github.com&utm_medium=referral&utm_content=volodymyrss/linked-data-latex&utm_campaign=Badge_Grade_Dashboard)
[![Requirements Status](https://requires.io/github/volodymyrss/linked-data-latex/requirements.svg?branch=master)](https://requires.io/github/volodymyrss/linked-data-latex/requirements/?branch=master)


# Templating for scientific papers

This helper allows to embed symbolic references to the data into the scientific paper. 
The framework aims to help establishing transparent data-to-paper flow, and features:

* based on [Jinja2](http://jinja.pocoo.org/docs/2.10/)
* integraion with [Latex](https://www.latex-project.org/about/) 
* an alternative mode to generate any text-based format (e.g. for GCN, ATel, VOEvent, etc)
* automatic handling of physical units
* reading data from yaml
* reading data from workflow data
* integration with a Jupyter notebooks
* extensible with python modules

# Cite-by-meaning model

* comprehensive citing: cite by tag, title, author, statement
* cite by fact (expressed as rdf)
* integration with zotero

Encourages explaining the reason behind citing.
Typical literature work flow:

* interesting paper noticed (or possibly any paper) and integrated in zotero
* writing the draft in latex, a context (fact, review, etc) requires a citation
* citation by tag is inserted, but produces many references, some irrelevant
* the citation request as well as literature annotation base is refined until the citation is as desired
* final citation contains not only the tranditional bibliographic reference, but also the reason why it was included, captured in the citation command and the annotated literature base
