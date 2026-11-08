from pathlib import Path
import json, subprocess, time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'reports'/'screenshots'; OUT.mkdir(parents=True,exist_ok=True)
seed=subprocess.run(['python3','scripts/seed_demo.py','--email','visual-qa@inhouse-tx.local'],cwd=ROOT,text=True,capture_output=True,check=True)
password=next(x.split(': ',1)[1] for x in seed.stdout.splitlines() if x.startswith('One-time password:'))
opts=Options(); opts.binary_location='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'; opts.add_argument('--headless=new'); opts.add_argument('--no-sandbox'); opts.add_argument('--disable-dev-shm-usage'); opts.add_argument('--disable-gpu'); opts.add_argument('--window-size=1440,1100'); opts.set_capability('goog:loggingPrefs',{'browser':'ALL','performance':'ALL'})
d=webdriver.Chrome(service=Service(str(ROOT/'work/chromedriver-156/chromedriver-mac-x64/chromedriver')),options=opts); wait=WebDriverWait(d,12)
results={'screenshots':[],'checks':[],'console_errors':[],'failed_requests':[],'dimensions':[]}
def snap(name):
    time.sleep(.5)
    f=OUT/(name+'.png'); d.save_screenshot(str(f)); results['screenshots'].append(str(f.relative_to(ROOT)))
def bydata(attr,val): return d.find_element(By.CSS_SELECTOR,f'[{attr}="{val}"]')
def check(name,ok,detail=''):
    results['checks'].append({'name':name,'passed':bool(ok),'detail':detail})
def page(name,nav):
    bydata('data-page',nav).click(); wait.until(lambda x: name in x.find_element(By.CSS_SELECTOR,'.page-heading h1').text or name in x.title)
    snap(name.lower().replace(' ','_'))

try:
    d.get('http://127.0.0.1:3001/'); wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,'.landing-shell'))); snap('01_landing_desktop')
    check('Landing page renders',bool(d.find_elements(By.CSS_SELECTOR,'.landing-shell')))
    # Recovery is intentionally explicit and cannot claim a reset happened.
    bydata('data-auth','login').click(); wait.until(EC.presence_of_element_located((By.ID,'auth'))); snap('02_sign_in_desktop')
    bydata('data-auth','recovery').click(); wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,'.recovery-panel'))); snap('03_password_recovery_desktop')
    rec=d.find_element(By.CSS_SELECTOR,'.recovery-panel').text
    check('Recovery honestly states reset is unavailable','isn’t configured' in rec and 'cannot send a recovery link' in rec,rec[:160])
    bydata('data-auth','login').click(); wait.until(EC.presence_of_element_located((By.ID,'auth')))
    # Inspect signup, then return to the demo account.
    bydata('data-auth','signup').click(); wait.until(lambda x:'Create your account' in x.page_source); snap('04_registration_desktop')
    bydata('data-auth','login').click(); wait.until(EC.presence_of_element_located((By.ID,'auth')))
    d.find_element(By.NAME,'email').send_keys('visual-qa@inhouse-tx.local'); d.find_element(By.NAME,'password').send_keys(password); d.find_element(By.CSS_SELECTOR,'#auth button[type=submit]').click()
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,'.app-shell'))); wait.until(lambda x: 'TOTAL SPENDING' in x.page_source); snap('05_dashboard_desktop')
    check('Dashboard loads persisted demo transaction analytics','TOTAL SPENDING' in d.page_source and '14 recorded' in d.page_source,d.find_element(By.CSS_SELECTOR,'.page-content').text[:220])
    # Visit all primary app pages at desktop.
    for title,key in [('Transactions','Transactions'),('Analytics','Analytics'),('Anomaly centre','Anomalies'),('Your financial copilot','AI insights'),('Pay with PayPal Sandbox','PayPal checkout'),('Connections & preferences','Settings')]:
        bydata('data-page',key).click(); time.sleep(.5); snap('desktop_'+key.lower().replace(' ','_'))
        check('Navigate to '+key, bool(d.find_elements(By.CSS_SELECTOR,'.app-shell')) and key.lower().split()[0] in d.find_element(By.CSS_SELECTOR,'.page-heading').text.lower())
    # Return to transaction list, inspect detail and feedback dialog.
    bydata('data-page','Transactions').click(); wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,'[data-detail]')))
    bydata('data-detail',d.find_element(By.CSS_SELECTOR,'[data-detail]').get_attribute('data-detail')).click(); wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,'.detail-panel'))); snap('desktop_transaction_detail')
    check('Transaction detail contains classifier fields', 'Model confidence' in d.page_source and 'Category' in d.page_source)
    bydata('data-page','Transactions').click(); wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,'[data-feedback]'))); d.find_element(By.CSS_SELECTOR,'[data-feedback]').click(); wait.until(EC.presence_of_element_located((By.ID,'feedback-form'))); snap('desktop_feedback_dialog')
    check('Category feedback dialog opens accessibly',d.find_element(By.CSS_SELECTOR,'[role=dialog]').get_attribute('aria-modal')=='true')
    Select(d.find_element(By.NAME,'corrected_category')).select_by_visible_text('Shopping'); d.find_element(By.NAME,'comment').send_keys('Browser QA category correction'); d.find_element(By.CSS_SELECTOR,'#feedback-form button.primary').click(); wait.until(lambda x:'Correction saved' in x.page_source); check('Category correction submits to feedback API','Correction saved' in d.page_source)
    # Filters: apply a category filter and verify row values match, then reset.
    form=d.find_element(By.ID,'transaction-filter'); Select(form.find_element(By.NAME,'category')).select_by_visible_text('Groceries'); form.find_element(By.CSS_SELECTOR,'button.primary').click(); time.sleep(.6)
    cats=[x.text for x in d.find_elements(By.CSS_SELECTOR,'.category-pill')]; check('Transaction category filter applies',all(x=='Groceries' for x in cats),str(cats))
    form=d.find_element(By.ID,'transaction-filter'); form.find_element(By.CSS_SELECTOR,'button[type=reset]').click(); time.sleep(.5)
    # Insights must return a grounded answer from the API.
    bydata('data-page','AI insights').click(); ta=d.find_element(By.CSS_SELECTOR,'#question-form textarea'); ta.send_keys('How much did I spend this month?'); d.find_element(By.CSS_SELECTOR,'#question-form button[type=submit]').click(); wait.until(lambda x: bool(x.find_elements(By.CSS_SELECTOR,'.answer'))); snap('desktop_ai_insight_answer')
    check('AI insight returns a persisted-data answer',bool(d.find_elements(By.CSS_SELECTOR,'.answer')) and 'month' in d.find_element(By.CSS_SELECTOR,'.answer').text.lower(),d.find_element(By.CSS_SELECTOR,'.answer').text[:220])
    # Capture review centre before the state-changing review interaction.
    bydata('data-page','Anomalies').click(); time.sleep(.5); snap('desktop_anomaly_centre')
    if d.find_elements(By.CSS_SELECTOR,'[data-review]'):
       d.find_element(By.CSS_SELECTOR,'[data-review][data-status="reviewed"]').click(); time.sleep(.5); check('Anomaly review action responds', 'Alert status updated' in d.page_source)
    else: check('Anomaly screen shows an honest empty/baseline state',bool(d.find_elements(By.CSS_SELECTOR,'.empty-block')))
    # Checkout must remain unconfigured without server credentials; no success claim.
    bydata('data-page','PayPal checkout').click(); time.sleep(.4); snap('desktop_paypal_checkout')
    check('Unconfigured checkout does not offer false success','not configured' in d.page_source.lower() or 'needs setup' in d.page_source.lower(),d.find_element(By.CSS_SELECTOR,'.checkout-layout').text[:240])
    # capture current page at tablet + mobile, plus each primary page for responsive coverage
    for width,height,label in [(820,1180,'tablet'),(390,844,'mobile')]:
       d.set_window_size(width,height)
       for key in ['Overview','Transactions','Analytics','Anomalies','AI insights','PayPal checkout','Settings']:
          # sidebar navigation is hidden on mobile, use bottom navigation or run JS to click nav buttons at tablet
          if width>760: bydata('data-page',key).click()
          else:
             matches=d.find_elements(By.CSS_SELECTOR,f'.mobile-nav [data-page="{key}"]')
             if not matches: continue
             matches[0].click()
          time.sleep(.3); snap(f'{label}_{key.lower().replace(" ","_")}')
          dims=d.execute_script('return {inner:innerWidth,doc:document.documentElement.scrollWidth,body:document.body.scrollWidth,main:document.querySelector(".main").getBoundingClientRect().width}')
          results['dimensions'].append({'viewport':label,'page':key,**dims})
    # Browser console and failed HTTP responses from DevTools performance log.
    for row in d.get_log('browser'):
        if row.get('level')=='SEVERE': results['console_errors'].append(row)
    for row in d.get_log('performance'):
        try:
            msg=json.loads(row['message'])['message']
            if msg['method']=='Network.responseReceived':
               p=msg['params']; status=p['response'].get('status',0)
               if status>=400: results['failed_requests'].append({'status':status,'url':p['response'].get('url')})
            if msg['method']=='Network.loadingFailed': results['failed_requests'].append({'error':msg['params'].get('errorText'),'url':msg['params'].get('requestId')})
        except Exception: pass
finally:
    d.quit()
(ROOT/'reports'/'screenshots'/'visual_qa_results.json').write_text(json.dumps(results,indent=2))
print(json.dumps(results,indent=2))
