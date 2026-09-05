You are a senior delivery analyst preparing a briefing for the engineering manager at Helios Group about where the request-to-release process is losing time. You are precise with numbers and you never round in a way that changes the story.

Please read data/helios-tickets.csv in full. It has one row per ticket, with a workflow column and a timestamp for each stage a ticket passed through: created, triaged, analysis_start, analysis_done, design_start, design_done, build_start, build_done, test_start, test_done, deployed, closed. It also has a rework_count and a rework_reason. Please consider only the rows where workflow is request_to_release.

Please then calculate, for each pair of consecutive stages, the median duration in hours and the 90th percentile duration in hours, across all the request_to_release tickets. Please show your working so that I can check it. Please also calculate the median end-to-end duration from created to closed, the percentage of tickets with a rework_count above zero, and the three most common rework reasons with their counts. Please do all of the arithmetic carefully and please double check it.

Please also read docs/process/request-to-release.md so that you can say, for each of the three longest stage transitions, which step of the process it corresponds to and whether the ticket is waiting (a queue) or being worked on (effort).

Then please write a briefing memo for the engineering manager with these sections: an executive summary of three sentences; a table of all eleven stage transitions with median and p90; a bar chart of the medians drawn in ASCII characters; a section on the three worst transitions with the process step and the queue or effort judgement for each; a section on rework with the rate and the top reasons; three recommendations, each with the evidence that supports it; and a closing paragraph. Please aim for a memo that reads well when printed and would take about ten minutes to read.

Please make sure every number in the memo can be traced back to the CSV, and please state at the top how many tickets the numbers are based on, because the manager will ask. Please do not estimate; calculate. Please make sure the ASCII chart is aligned properly.

Write the memo to week2/out/stage-summary-v0.md and then in the chat give me the executive summary and the table of the three worst transitions, and tell me how confident you are in the arithmetic.
