# Quick start
To run CELI for the **GRE** task, run the following.  You will need to set the OPENAI_API_KEY environment variable to your key. 

```bash
python -m celi_framework.main   \
  --job-description=celi_framework.examples.GRE.job_description.job_description   \
  --primary-model-name=gpt-4o \
  --force-tool-every-n=15
```

Using the `force-tool-every-n` option here to increase the default from 3 to 15.  This option is used to get out of loops by limiting repetitive calls to the LLM,
but the tasks for this job require many consecutive calls.





