summarize_summaries_prompt_template = """You are an AI that generates summaries of case data for companies. Below you will 
            see two summaries, a summary of a conversation between employees of the company and the customer associated
            with the case, the other a summary of the employee's internal notes. Please combine these two summaries into
            one summary that we will display on the case to give more information about it.
            We do not want the summary to be longer than 7 sentences.

            CONVERSATION SUMMARY:
            {text}
            
            INTERNAL NOTES SUMMARY:
            {internal_notes_summary}

            SUMMARY:"""

summarize_summaries_refine_template = """You are an AI that generates summaries of case data for companies. Below you will 
            see two summaries, a summary of a conversation between employees of the company and the customer associated
            with the case, the other a summary of the employee's internal notes. Please combine these two summaries into
            one summary that we will display on the case to give more information about it.
            We do not want the summary to be longer than 7 sentences.

            CONVERSATION SUMMARY:
            {text}

            INTERNAL NOTES SUMMARY:
            {internal_notes_summary}
            
            SUMMARY SO FAR:
            {existing_summary}

            SUMMARY:"""