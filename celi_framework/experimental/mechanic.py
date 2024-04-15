# TODO:
#   This is going to take queued items that get sent from post-monitor, and fix 'em up
#   The moonitor is going to write to the prompt_and_completion-generated document and give the completion a quality score
#   When a task gets a score of x or below, there is a second monitor that will evaluate the ongoing_chat
#   (all the prompt completion docs appended) all the way  up to the completion at hand and it will make a
#   recommendation for changing the prompt. When it makes that recomendation it will be in the form of (could be json?)
#   template_id, config section, config subsection, new content. The mechanic is going to stop (for now, with option to
#   start new process on a different thread), take that info and create a new master template through the factory which
#   will get a new hash ID and will be integrated with the process runner instance, when we restart the process. In
#   the restart method we need to call on the state attribute to call out to mongo to reset the state by looking up the
#   state info that we need, just as it was immediately before the bad completion happened.
#   HOW YOU DO THIS:
#   All you need to know is the process ID, and the task num, you will write over the existing doc with those IDs (set
#   a new version number (that will contain the fixed prompt content for the specific section)
