param($minutes = 150)

write "=============================="
write "Wakey-Wakey $minutes"
write "=============================="
write ""

 $myshell = New-Object -com "Wscript.Shell"

 for ($i = 0; $i -lt $minutes; $i++) {
 $remaining  = ($minutes-$i)
 write "Remaining: $remaining"
 Start-Sleep -Seconds 300
 $myshell.SendKeys("{F15}")
}
