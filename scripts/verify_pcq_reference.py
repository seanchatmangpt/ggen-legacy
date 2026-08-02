#!/usr/bin/env python3
import hashlib,json,pathlib,sys
root=pathlib.Path(__file__).resolve().parents[1]
app=root/'reference-implementations/pcq-marketplace'
required=['package.json','ggen.toml','schema/domain.ttl','app/page.tsx','app/api/stream/route.ts','app/api/orders/route.ts','components/deck-market.tsx','lib/market.ts','lib/pcq.ts','tests/market.test.ts','e2e/dashboard.spec.ts']
missing=[p for p in required if not (app/p).is_file()]
text='\n'.join((app/p).read_text() for p in required if (app/p).is_file())
checks={
 'missing_files':missing,
 'pcq_fixed_point':'initialSupplyMicros' in text and 'PCQ_SUPPLY_DRIFT_REFUSED' in text,
 'sse_boundary':'text/event-stream' in text and 'ReadableStream' in text,
 'deck_layers':all(name in text for name in ['ScatterplotLayer','ArcLayer','TripsLayer','ColumnLayer','TextLayer']),
 'settlement_receipt':'pcq.market.settlement' in text and 'receiptDigest' in text,
 'browser_witness':"locator('canvas')" in text,
 'no_external_fx':'from_currency' not in text and 'exchangeRate' not in text,
}
status='ALIVE' if not missing and all(v is True for k,v in checks.items() if k!='missing_files') else 'BLOCKED'
report={'schema':'urn:ggen-legacy:pcq-reference-static-report:v1','checks':checks,'status':status}
report['digest']=hashlib.sha256(json.dumps(report,sort_keys=True,separators=(',',':')).encode()).hexdigest()
out=root/'.build/pcq-reference-static-report.json';out.parent.mkdir(exist_ok=True);out.write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report))
sys.exit(0 if status=='ALIVE' else 1)
