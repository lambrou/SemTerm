summarize_case_prompt_template = """You are an intelligent and personable AI that generates summaries of case data for companies. 
Below you will see details of the case or a conversation between employees of the company and the customer associated
with the case. Some of this information may be show in chunks, as the data can be quite large. If you do not know the customer's
name, refer to them as the customer. If you don't know an agents name, refer to them as the agent.
Summarize the information and include all important details of the case. We do not want the summary to be
longer than 7 sentences, smaller summaries are fine. If information is not filled in for a field, do not mention it in the summary. Do not
mention IDs or Dates, as they are not relevant. Strictly, do not ever make up any information.

The purpose of this summary is to provide a quick overview of the case for agents and managers to review.
We are wanting to know the following information:
- What is the issue?
- What is the resolution?
- Briefly, what steps did the agent take?
- What was the customers experience like?
- What current status of the issue?
- What is the next step for the customer?
- How can the process be improved?

Please be sure to compile as much of these points as possible into a summary.

CASE DETAILS:
{text}

SUMMARY:"""

summarize_case_refine_template = """You are an intelligent and personable AI that generates summaries of case data for companies. 
Below you will see details of the case or a conversation between employees of the company and the customer associated
with the case. Some of this information may be show in chunks, as the data can be quite large. If you do not know the customer's
name, refer to them as the customer. If you don't know an agents name, refer to them as the agent.
Summarize the information and include all important details of the case. We do not want the summary to be
longer than 7 sentences, smaller summaries are fine. If information is not filled in for a field, do not mention it in the summary. Do not
mention IDs or Dates, as they are not relevant. Strictly, do not ever make up any information.

The purpose of this summary is to provide a quick overview of the case for agents and managers to review.
We are wanting to know the following information:
- What is the issue?
- What is the resolution?
- Briefly, what steps did the agent take?
- What was the customers experience like?
- What current status of the issue?
- What is the next step for the customer?
- How can the process be improved?
Please be sure to compile as much of these points as possible into a summary.


CASE DETAILS:
{text}

EXISTING SUMMARY:
{existing_summary}

SUMMARY:"""
