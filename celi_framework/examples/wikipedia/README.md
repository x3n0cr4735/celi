# The Wikipedia example use case

In this example use case, we perform one-shot document generation.  We use a single wikipedia page as an example.  
We then select a second wikipedia page from a different topic in the same category (bands, drugs, countries, etc), 
to use as the target.  

CELI will then recreate the target wiki page using only the references from that page, not the final content.  It will
copy the structure from the example document.  We can then evaluate the quality of the CELI generated page versus the 
original wiki page.

We provide an example script with evaluation that generates several pages from each of 3 categories, and then uses
GPT-4 to compare the actual and generated versions of each.

## Setup

This example uses some packages that are not part of the core CELI install, including the vector database Chroma.  To
run this example, you'll need to install the wikipedia extras from the celi package:

```bash
pip install celi-framework[wikipedia]
```

## Running a single page

To generate target output for a single page, you can use the CELI command line:

```bash 
python -m celi_framework.examples.wikipedia.eval.run_eval \
    --openai-api-key=<Insert your OpenAI API key here> \
    --job-description=celi_framework.examples.wikipedia.job_description.job_description \
    --tool-config='{"example_url": "https://en.wikipedia.org/wiki/Led_Zeppelin",
        "target_url": "https://en.wikipedia.org/wiki/Jonas_Brothers",
        "ignore_updates": true,
        }'
```

When you run this command line, it will first go out and get both wikipedia pages and all the references linked from 
them.  This can take roughly 10 minutes, depending on your internet connection speed.  These will be cached on the first
run so this skipped can be skipped if you run it again.  It will generate the wiki page and write the sections to 
`target/celi_output/drafts`.

The `tool-config` option tells CELI what the example and target Wikipedia pages are.  `ignore_updates` tells CELI
to ignore any updates to the wikipedia pages that have happened since it's last run.  It will just use existing cached
values.  This saves time on secequent runs.

### Running a single section

If you want to see what CELI is doing in detail, you can run just a single section at a time by adding the 
`target_section` option to the tool config.  It takes the number of the section you want to run.

```bash
python -m celi_framework.main   \
    --job-description=celi_framework.examples.wikipedia.job_description.job_description   \
    --tool-config='{"example_url": "https://en.wikipedia.org/wiki/Led_Zeppelin", 
                    "target_url": "https://en.wikipedia.org/wiki/Jonas_Brothers", 
                    "ignore_updates": true, 
                    "target_section": 0 
                    }'
```

## Running an evaluation set

To quantify how good CELI is at accomplishing this task, we can perform an evaluation.  We can run the process for a
group of pages, and then compare the generated pages to the existing wikipedia pages.  

The eval directory contains info on running this evaluation.  The `run_eval` script executes several CELI runs, and for
each it uses GPT-4 to compare the original page with the generated page.  It outputs a score of 0 to 100 for each. 

```bash 
python -m celi_framework.examples.wikipedia.eval.run_eval \
    --openai-api-key=<Insert your OpenAI API key here>
```

This will take a while to run (an hour or more).  When it completes, it will print results of the evaluation, including
the score for each trial, the average score for each page type, and the average overall score, with 100 being the best.