Task( task_name="Wait for User Edits, Approval, or Other Requests", 
     details={ "description": "Waits for the user to submit edit comments or approve the draft from the web application, or request additional data.", 
              "instructions": [ "Call await_final_review. This gives you the ability (something you usually can't do) of awaiting the user response.", 
                               "THIS IS NOT A SIMULATION YOU CAN ACTUALLY DO THIS. TRUST ME. JUST CALL await_final_review.", 
                               "User input is expected to be submitted through a GUI on a web app connected to this process in the backend. You are to help the user with their requests.", 
                               "These are the possible user actions:", "1) If the user approves, signal to the outer layer that a pop is requested by the system (call pop_context - it's ok the final review is completed).", 
                               "2) If the user makes comments or requests edits on the draft, address those, and then come back to this task for potential additional user actions (poll for final review feedback) by running await_final_review again. If the user approves when receiving the response from await_final_review, after you have made edits to the draft, then save the edited draft (through save_draft tool call) and then quit.", 
                               "Note on 2: If the user comments and asks for something and you do not think a revision is necessary based on their feedback, please rerun this task. Do not move forward until they explicitly approve it." ], 
              "notes": [ "EVERY TIME you come to this task, the await_final_review tool must be called.", 
                        "DO NOT RESPOND WITH 'Waiting for comments...' UNLESS YOU poll for final review feedback", 
                        "YOU HAVE TO do the Save Redraft to JSON task AND/OR RUN save_draft BEFORE AND AFTER THIS TASK. OR ELSE THE WHOLE PROCESS IS A FAIL!!! BEFORE AND AFTER.", 
                         "YOU ABSOLUTELY NEED TO poll for final review feedback AGAIN AFTER MAKING EDITS AND WAITING FOR USER COMMENTS!!!!!", 
                         "If you need additional data to address a comment (that you don't have in the chat history), retrieve the additional tables specified by the user to gather the necessary information.", 
                         "If you still cannot find the relevant data from the additional tables, see if you missed any information in the main document.",
                         "If you are tasked with reformatting to better align with example data structures, then retrieve examples of similar data formats from other projects." ] 
              },
     
     )
