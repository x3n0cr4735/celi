# Cheatsheet

The following cheatsheet provides some example command lines for common cases.

<table border="1">
   <tr>
      <th>Use</th>
      <th>Example Command</th>
   </tr>
   <tr>
      <td>Run the basic example</td>
<td>
<pre>python -m celi_framework.main \
   --job-description=celi_framework.examples.human_eval.job_description.job_description
</pre>
</td>
   </tr>
   <tr>
      <td>Pass parameters to the ToolImplmentations class</td>
<td>
<pre>python -m celi_framework.main \
   --job-description=celi_framework.examples.human_eval.job_description.job_description
   --tool-config='{"single_example":"HumanEval/3"}'
</pre>
</td>
   </tr>
   <tr>
      <td>Use Claude models</td>
<td>
<pre>python -m celi_framework.main \
   --job-description=celi_framework.examples.human_eval.job_description.job_description
   --anthropic-api-key=<Insert you ANthropic API key here>
   --primary-model-name=claude-3-5-sonnet-20240620
</pre>
</td>
   </tr>
   <tr>
      <td>Turn off parallelization and caching for debugging</td>
<td>
<pre>python -m celi_framework.main \
   --job-description=celi_framework.examples.human_eval.job_description.job_description
   --no-cache --serialize
</pre>
</td>
   </tr>
   <tr>
      <td>Set the size of an individual LLM response to 4096 and a total limit of 1M input and output tokens</td>
<td>
<pre>python -m celi_framework.main \
   --job-description=celi_framework.examples.human_eval.job_description.job_description
   --max-tokens=4096 --token-budget=1000000
</pre>
</td>
   </tr>
</table>
