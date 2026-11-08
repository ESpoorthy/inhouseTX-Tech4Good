from pathlib import Path
import subprocess, requests, json
ROOT=Path(__file__).resolve().parents[1]
seed=subprocess.run(['python3','scripts/seed_demo.py','--email','visual-qa@inhouse-tx.local'],cwd=ROOT,text=True,capture_output=True,check=True)
pw=next(x.split(': ',1)[1] for x in seed.stdout.splitlines() if x.startswith('One-time password:'))
s=requests.Session(); base='http://127.0.0.1:3001'; out=[]
def check(name,cond,detail=''): out.append({'name':name,'passed':bool(cond),'detail':detail})
r=s.get(base+'/');check('GET landing',r.status_code==200 and 'InHouseTX' in r.text,str(r.status_code))
r=s.get(base+'/api/health');check('Health endpoint',r.status_code==200,str(r.status_code))
r=s.get(base+'/api/auth/session');check('Unauthenticated session',r.status_code==200 and not r.json().get('authenticated'),str(r.json()))
r=s.post(base+'/api/auth/login',json={'email':'visual-qa@inhouse-tx.local','password':pw});check('Login',r.status_code==200,str(r.status_code));csrf=r.json().get('csrf_token');s.headers.update({'X-CSRF-Token':csrf})
for name,url in [('integrations','/api/settings/integrations'),('transactions','/api/transactions?limit=100'),('analytics','/api/analytics/summary'),('anomalies','/api/anomalies'),('budgets','/api/budgets')]:
 r=s.get(base+url);check(name,r.status_code==200,f'{r.status_code}; {r.text[:160]}')
tx=s.get(base+'/api/transactions?limit=100').json().get('items',[])
check('Seeded fixtures persisted',len(tx)==14,f'count={len(tx)}')
if tx:
 r=s.get(base+f"/api/transactions/{tx[0]['id']}");check('Transaction detail',r.status_code==200,str(r.status_code))
 r=s.post(base+f"/api/transactions/{tx[0]['id']}/feedback",json={'corrected_category':'Shopping','comment':'QA verification'});check('Feedback write',r.status_code in (200,201),f'{r.status_code};{r.text[:160]}')
r=s.get(base+'/api/analytics/summary?category=Groceries');check('Analytics filter',r.status_code==200,str(r.status_code))
r=s.post(base+'/api/insights/query',json={'question':'How much did I spend this month?'});check('Deterministic AI insight',r.status_code==200 and bool(r.json().get('answer')),f'{r.status_code};{r.text[:220]}')
r=s.post(base+'/api/categorization/predict',json={'description':'coffee shop cappuccino','merchant':'Neighborhood Cafe'});check('Categorisation inference',r.status_code==200 and bool(r.json().get('category')),f'{r.status_code};{r.text[:220]}')
r=s.post(base+'/api/paypal/orders',json={'amount':'18.50','currency':'USD','description':'Visual QA'});check('PayPal checkout fails honestly when unconfigured',r.status_code in (400,503),f'{r.status_code};{r.text[:220]}')
(ROOT/'reports'/'screenshots'/'api_visual_qa_results.json').write_text(json.dumps(out,indent=2)); print(json.dumps(out,indent=2))
