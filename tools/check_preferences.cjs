// Execute the actual browser script against a small browser boundary to verify preferences.
const {readFileSync} = require('node:fs');
const {runInNewContext} = require('node:vm');
const assert = require('node:assert/strict');
const script = readFileSync('theme.js', 'utf8');
function load({language='en', saved={}, path='/', referrer='', systemDark=false, blocked=false}={}) {
    const events={}, listeners={}, links={de:{dataset:{language:'de'}},en:{dataset:{language:'en'}}};
    for (const node of Object.values(links)) node.addEventListener=(name,fn)=>node[name]=fn;
    const button={setAttribute:(key,value)=>button[key]=value,addEventListener:(name,fn)=>listeners[name]=fn};
    const state={redirect:null};
    const root={dataset:{}};
    const media={matches:systemDark,addEventListener:(name,fn)=>state.systemChange=fn};
    runInNewContext(script,{
        URL,localStorage:{getItem:key=>{if(blocked)throw Error();return saved[key]},setItem:(key,value)=>{if(blocked)throw Error();saved[key]=value}},
        window:{matchMedia:()=>media},navigator:{languages:[language]},
        location:{pathname:path,origin:'https://luehr.dev',search:'?source=test',hash:'#training',replace:url=>state.redirect=url},
        document:{documentElement:root,referrer,body:{dataset:{autoLanguage:'true'}},getElementById:()=>button,querySelectorAll:()=>Object.values(links),addEventListener:(name,fn)=>events[name]=fn}
    });
    events.DOMContentLoaded();
    return {state,root,saved,links,listeners,button};
}
assert.equal(load({language:'de-DE'}).state.redirect,'/de/?source=test#training');
assert.equal(load({language:'fr-FR'}).state.redirect,null);
assert.equal(load({language:'de',saved:{language:'en'}}).state.redirect,null);
assert.equal(load({language:'en',saved:{language:'de'}}).state.redirect,'/de/?source=test#training');
assert.equal(load({language:'de',path:'/rust-basics-training.html'}).state.redirect,null);
assert.equal(load({language:'en',path:'/de/'}).state.redirect,null);
assert.equal(load({language:'de',referrer:'https://luehr.dev/de/'}).state.redirect,null);
assert.equal(load({systemDark:true}).root.dataset.theme,'dark');
assert.equal(load({systemDark:false}).root.dataset.theme,'light');
const session=load({systemDark:true});session.listeners.click();assert.equal(session.saved.theme,'light');assert.equal(session.button['aria-pressed'],'false');
session.links.en.click();assert.equal(session.saved.language,'en');
const system=load();system.state.systemChange({matches:true});assert.equal(system.root.dataset.theme,'dark');
const locked=load({saved:{theme:'light'}});locked.state.systemChange({matches:true});assert.equal(locked.root.dataset.theme,'light');
assert.doesNotThrow(()=>load({blocked:true,language:'de'}).listeners.click());
console.log('PASS: browser locale, saved language, explicit URLs, query/hash, theme and unavailable storage');
