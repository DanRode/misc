#!/usr/bin/env python

auditfile = "/home/drode/audit.list"
dblist = "/home/drode/clouseau.list"
alines = filter(None, [line.strip() for line in open(auditfile)])
dblines = filter(None, [line.strip() for line in open(dblist)])

only_in_audit = []
only_in_db = []
for asset in alines:
    if asset not in dblines:
        only_in_audit.append(asset)

for asset in dblines:
    if asset not in alines:
        only_in_db.append(asset)

print "%s of %s assets found only in audit" % (len(only_in_audit), len(alines))
print "\n".join(only_in_audit)
print 
print "%s of %s assets found only in database" % (len(only_in_db), len(dblines))
print "\n".join(only_in_db)
