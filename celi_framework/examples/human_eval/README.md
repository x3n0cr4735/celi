# Quick start
To run CELI against the **HumanEval** benchmark, use the following JobDescription (probably set in your .env file): 
- Make sure your .env is set up correctly (look at .env.example) and set `JOB_DESCRIPTION=celi_framework.examples.human_eval.job_description.job_description` specifically.
- From a terminal, and from the human_eval project directory, run `python main.py`. This will output a json file (with timestamp) with the answers in human_eval/target/celi_output/drafts. That's the "output file".
- To see what score you got, from a terminal, run `python eval.py <output file>`

**For a single example (#143 here):**

```bash
python -m celi_framework.main   \
  --job-description=celi_framework.examples.human_eval.job_description.job_description   \
  --primary-model-name=gpt-4o \
  --tool-config='{"single_example":"HumanEval/143"}' \
  --token-budget=70000
```

**To reprodce our results below:**
Note: change the token budget to whatever is acceptable to you.

```bash
python -m celi_framework.main   \
  --job-description=celi_framework.examples.human_eval.job_description.job_description   \
  --primary-model-name=gpt-4-0125-preview \
  --token-budget=3000000
```

# HumanEval Pass@1 Results 
Note: This was run with GPT-4-Turbo (0125)

| Approach                          | HumanEval Pass@1 | Δ    |
|------------------------------------|------------------|------|
| GPT-4-Turbo (1106) Base¹           | 83.7%            | -    |
| GPT-4-Turbo (0125) Base²           | 86.6%            | -    |
| MapCoder (Islam et al. 2024)¹      | 93.9%            | +10.2|
| LATS (Zhou et al. 2023)¹           | 92.7%            | +9.0 |
| **CELI²**                          | 91.5%            | +4.9 |
| Reflexion (Shinn et al. 2023)¹     | 91.0%            | +7.3 |
| AgentCoder (Huang et al. 2024)¹    | 89.6%            | +5.9 |
| LDB (Zhong et al. 2024)¹           | 89.6%            | +5.9 |
| AgentVerse (Chen et al. 2023)¹     | 89.0%            | +5.3 |
¹ Comparison with best reported score of GPT-4-Turbo (1106)  
² Comparison with best reported score of GPT-4-Turbo (0125)

## Analysis

**CELI** outperformed the baseline GPT-4-Turbo (0125) model by 4.9 percentage points on the HumanEval benchmark. Notably, CELI's performance improvement (delta score) was within 1 percentage point of the majority of the specialized coding frameworks, highlighting its strong competitiveness despite its broader focus.

Key factors contributing to **CELI**'s strong performance include its ability to:
- Generate comprehensive test cases.
- Implement iterative solution refinement based on test results.
- Maintain context across multiple iterations.

These capabilities allow **CELI** to approach coding tasks with sophistication comparable to specialized frameworks while retaining flexibility for diverse task types. The results demonstrate **CELI**'s potential as a versatile framework for complex, multi-stage tasks requiring both natural language understanding and precise programmatic execution.

## References
Islam, Md Ashraful, Mohammed Eunus Ali, and Md Rizwan Parvez. (2024). MapCoder: Multi-Agent Code Generation for Competitive Problem Solving. arXiv preprint arXiv:2405.11403.
Zhou, A., Yan, K., Shlapentokh-Rothman, M., Wang, H., & Wang, Y. X. (2023). Language agent tree search unifies reasoning acting and planning in language models. arXiv preprint arXiv:2310.04406.
Shinn, N., Cassano, F., Berman, E., Gopinath, A., Narasimhan, K., & Yao, S. (2023). Reflexion: Language agents with verbal reinforcement learning. arXiv preprint arXiv:2303.11366v4. Retrieved from https://arxiv.org/abs/2303.11366v4.
Huang, D., Zhang, J. M., Luck, M., Bu, Q., Qing, Y., & Cui, H. (2024). AgentCoder: Multi-agent-based code generation with iterative testing and optimisation. arXiv. https://doi.org/10.48550/arXiv.2312.13010.
Zhong, L., Wang, Z., & Shang, J. (2024). Ldb: A large language model debugger via verifying runtime execution step-by-step. arXiv preprint arXiv:2402.16906.
Chen, W., Su, Y., Zuo, J., Yang, C., Yuan, C., Chan, C.-M., Yu, H., Lu, Y., Hung, Y.-H., Qian, C., Qin, Y., Cong, X., Xie, R., Liu, Z., Sun, M., & Zhou, J. (2023). AgentVerse: Facilitating multi-agent collaboration and exploring emergent behaviors. arXiv. https://doi.org/10.48550/arXiv.2308.10848.





