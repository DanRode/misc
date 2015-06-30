(14:24:32) loadtest@conference.chat.ag.com/jspencer: command line completion example
(14:24:43) loadtest@conference.chat.ag.com/jspencer: try this for fun
(14:24:51) loadtest@conference.chat.ag.com/jspencer: $ complete -W "ag-web1 ag-web2" mycommand
(14:24:59) loadtest@conference.chat.ag.com/jspencer: mycommand [TAB][TAB]
(14:25:01) loadtest@conference.chat.ag.com/jspencer: :)
(14:25:35) loadtest@conference.chat.ag.com/jspencer: complete has other options besides wordlist - you can list jobs, or a result of a bash function
(14:28:59) loadtest@conference.chat.ag.com/jspencer: here you go:
(14:29:01) loadtest@conference.chat.ag.com/jspencer: export IFS=$'\n'
(14:29:17) loadtest@conference.chat.ag.com/jspencer: complete -W `cfgroup bmaweb` mycommand
(14:29:26) loadtest@conference.chat.ag.com/jspencer: mycommand [TAB][TAB]
