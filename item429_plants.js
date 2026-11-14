// Item 429 forced scenarios, by gap. Each runs through a named writer with a not-fire twin, or reads "not-fire only" with the reason no writer can produce it (Items 421, 423, 427A).
// Reserved values only (the text plant-429, no client address). Every plant a writer can remove is removed through it and the state read after; a fresh load (the eval) proves nothing remains.
async()=>{const d=window.__dash; const W=ms=>new Promise(r=>setTimeout(r,ms)); const R={};
 const form=async(vals)=>{await W(150); const u=d._askUI; if(!u) return 'no form opened'; u.fields.forEach(f=>{ if(f.key in vals) f.value=String(vals[f.key]); }); d._askClose(true); await W(500); return 'submitted';};
 const go=async v=>{ d.setState({view:v}); await W(900); }; const rv=()=>d.renderVals(); const toast=()=>String(d.state.toast||'');
 const $=n=>(n<0?'-$':'$')+Math.abs(n).toLocaleString('en-US',{minimumFractionDigits:2,maximumFractionDigits:2});
 const wk=()=>rv().bdxweekVM;
 // ===== A · the sales operating week: cadence writer (Tune the Seat), template deal writer, target writer, close-deal writer =====
 await go('bdxweek'); let w=wk(); R.A_seed={mon:w.mon.state, tue:w.tue.state, tueRows:w.tue.rows.length, wed:w.wed.state, thu:w.thu.state, fri:w.fri.map(l=>l.k+': '+l.v), tiles:w.tiles.map(t=>t.k+': '+t.v)};
 await go('ssxtune'); rv().cadenceVM.set(); await form({k:'30', n:'20', f:'20', w:'13', q:''}); await go('ssxtune'); R.A_cadence_split_twin={toast:toast(), line:rv().cadenceVM.line};
 await go('ssxtune'); rv().cadenceVM.set(); await form({k:'30', n:'2', f:'28', w:'13', q:'3'}); await go('bdxweek'); w=wk(); R.A_cadence_fire={tue:w.tue.state, tueRows:w.tue.rows.length, cadence:w.cadence};
 await go('pipeline'); const tm=(rv().tmpl||{}).rows||[]; R.A_deal_writer=tm[0]?'tmpl.rows[0].use':'none'; if(tm[0]) tm[0].use(); await W(400);
 const deal=(d.state.deals||[])[0]||{}; const expW=(Number(deal.value)||0)*(Number(deal.p)||0);
 await go('bdxweek'); w=wk(); R.A_deal_fire={mon:w.mon.state, row:(w.mon.rows[0]||{}), thu_notfire:w.thu.state, fri_pipeline:w.fri[0].v, expected_weighted:$(expW), tile_forecast:w.tiles[0].v, tile_forecast_range:w.tiles[0].sub};
 R.A_target_seed=wk().tiles[2].v; await go('ssxtune'); d.renderVals().chairInputsVM.setTarget(); await form({v:'45000'}); await go('bdxweek'); w=wk(); R.A_target_fire={tile:w.tiles[2].v, sub:w.tiles[2].sub, expected_cover:Math.round(expW/45000*100)+'%'};
 d._frxCloseDeal(deal.id,'Lost','Price','plant-429'); await W(400); await go('bdxweek'); w=wk(); R.A_close_fire={winloss:w.tiles[1].v, sub:w.tiles[1].sub, mon_twin:w.mon.state, fri_closed:w.fri[1].v};
 await go('ssxtune'); rv().cadenceVM.set(); await form({k:'', n:'', f:'', w:'', q:''}); await go('bdxweek'); w=wk(); R.A_cadence_withdrawn={tue:w.tue.state, tueRows:w.tue.rows.length, cadence:w.cadence};
 const RU=d._r430Ruling(); await go('ssxtune'); rv().cadenceVM.set(); await form({k:String(RU.cadence.contactsPerWeek), n:String(RU.cadence.newPerWeek), f:String(RU.cadence.followPerWeek), w:String(RU.cadence.weeksPerQuarter), q:''}); await go('ssxtune'); R.A_cadence_restored=rv().cadenceVM.line;
 await go('ssxtune'); d.renderVals().chairInputsVM.setTarget(); await form({v:''}); await go('bdxweek'); R.A_target_withdrawn=wk().tiles[2].v; await go('ssxtune'); d.renderVals().chairInputsVM.setTarget(); await form({v:String(RU.quarterTarget)}); await go('bdxweek'); R.A_target_restored=wk().tiles[2].v;
 R.A_quiet_and_clinic='not-fire only: no writer ages a deal (the template and advance writers set since and days to 0, and no cadence can be declared at 0), so Quiet and the deal clinic are proven by not-fire above';
 R.A_wednesday='not-fire only: no writer adds a non-example draft to the outbox; the card reads Empty with the example rows excluded';
 // ===== B and G · forecast ranges and commentary: the close writer of fc.history (_retrainForecast, fired by Close & seal) =====
 await go('rollfc'); R.B_seed=rv().forecastVM.range.line; await go('qbxhome'); R.G_seed_boardpack={head:rv().fluxVM.head, forecastLines:rv().fluxVM.raw.filter(t=>/^Revenue for/.test(t)).length};
 d._retrainForecast('Sep 2026'); await W(500); await go('rollfc'); R.B_one_period_twin=rv().forecastVM.range.line;
 d._retrainForecast('Oct 2026'); await W(500); await go('rollfc'); const H=d.state.fc.history; const r=H.map(h=>h.actRev/h.fcRev).sort((x,y)=>x-y); const lo=r[0], hi=r[r.length-1], md=r.length%2?r[(r.length-1)/2]:(r[r.length/2-1]+r[r.length/2])/2;
 const fv=rv().forecastVM; const pt=Number(d.state.fc.base)*(1+Number(d.state.fc.drivers.growth)/100);
 R.B_fire={rollfc:fv.range.line, expected:{low:$(Math.min(pt*lo,pt*hi)), likely:$(pt*md), high:$(Math.max(pt*lo,pt*hi)), point:$(pt)}, history:H.map(h=>h.month+' fc '+$(h.fcRev)+' act '+$(h.actRev))};
 await go('bkfcst'); R.B_fire_bkfcst=rv().bkVM.forecast.range.line; await go('bkkpfcst'); R.B_fire_bkkpfcst=rv().bkkpVM.forecast.range.line; await go('projfin'); R.B_fire_projfin=(rv().pf.rows[0]||{}).range.line;
 R.G_fire_hist=fv.hist.map(h=>h.comment); await go('qbxhome'); R.G_fire_boardpack=rv().fluxVM.raw;
 R.G_blind='not-fire only: every account row on this book has a prior month on file and every row has a driver, so the two Blind rules read not-fire; no writer removes a prior month or writes a forecast of zero (_retrainForecast refuses a forecast of zero)';
 // ===== C · Go/No-Go (Item 430, rebuilt to the ruling): the five test writers on the ruled Illinois record =====
 const g=()=>rv().cbdgonogoVM; await go('cbdgonogo'); R.C_seed={verdict:g().verdict, market:g().market, note:g().note, rows:g().rows.map(x=>x.name+' · '+x.state)};
 const fileT=async(i,vals)=>{ await go('cbdgonogo'); g().rows[i].file(); await form(vals); await go('cbdgonogo'); };
 await fileT(0,{src:'plant-430 test record', vd:'Go', why:''}); R.C_demand_go_twin={verdict:g().verdict};
 await fileT(4,{src:'plant-430 test record', vd:'Go', why:''}); R.C_go_refused_fire={verdict:g().verdict};
 await fileT(1,{src:'plant-430 test record', vd:'Go', why:''}); R.C_go_fire={verdict:g().verdict};
 await fileT(2,{src:'plant-430 test record', vd:'maybe', why:''}); R.C_bad_verdict_twin={toast:toast(), state:g().rows[2].state};
 await fileT(3,{src:'', vd:'Go', why:''}); R.C_go_without_source_twin={toast:toast(), state:g().rows[3].state};
 const RG=d._r430Ruling().goNoGo.tests; await fileT(0,{src:'', vd:'', why:RG.demand.reason}); await fileT(1,{src:'', vd:'', why:RG.competition.reason}); await fileT(4,{src:RG.capacity.source, vd:RG.capacity.verdict, why:''});
 R.C_restored={verdict:g().verdict, rows:g().rows.map(x=>x.name+' · '+x.state), equals_seed:g().verdict===R.C_seed.verdict};
 // ===== D · Strategy against plan (Item 431): the strategy field writer on the authored text, and the initiative register writer =====
 const sv=()=>rv().cmdxstrategyVM; const R1=d._r431Ruling(); await go('cmdxstrategy'); R.D_seed={guard:sv().guard, marks:sv().strat.map(f=>f.mark)};
 await go('initreg'); let iv=rv().initVM; const ev=v=>({target:{value:v}}); iv.setName(ev('plant-431 initiative')); await W(150); iv=rv().initVM; iv.setArea(ev((iv.areaOpts&&iv.areaOpts[0]&&(iv.areaOpts[0].value||iv.areaOpts[0].label||iv.areaOpts[0]))||'Work')); await W(150);
 const t0=new Date(); const iso=t0.getFullYear()+'-'+String(t0.getMonth()+1).padStart(2,'0')+'-'+String(t0.getDate()).padStart(2,'0'); rv().initVM.setStart(ev(iso)); await W(150); rv().initVM.setStateD(ev('started')); await W(150); rv().initVM.setEvidence(ev('plant-431 evidence field')); await W(150); rv().initVM.add(); await W(500);
 await go('cmdxstrategy'); sv().strat[0].file(); await form({t:R1.strategy.market}); await go('cmdxstrategy'); R.D_same_text_twin={toast:toast(), text:sv().strat[0].text};
 sv().strat[0].file(); await form({t:'plant-431 market text'}); await go('cmdxstrategy'); R.D_writer_fire={text:sv().strat[0].text, mark:sv().strat[0].mark};
 for(let i=0;i<5;i++){ await go('cmdxstrategy'); sv().strat[i].file(); await form({t:''}); } await go('cmdxstrategy'); R.D_guard_fire={guard:sv().guard, bad:sv().guardBad, init:sv().init};
 const KS=['market','means','money','meaning','magic']; for(let i=0;i<5;i++){ await go('cmdxstrategy'); sv().strat[i].file(); await form({t:R1.strategy[KS[i]]}); } await go('cmdxstrategy'); R.D_restored={guard:sv().guard, verbatim:sv().strat.every((f,i)=>f.text===R1.strategy[KS[i]]), marks:sv().strat.map(f=>f.mark.split(' · ')[0])};
 R.D_initiative_removal='no writer deletes an initiative entry: removed by the fresh load the eval proves';
 // ===== E · the prompt and voice library: the filed set by the load merge, the prompt writer and the rule writer =====
 const pv=()=>rv().lrnxpromptsVM; const K=d._e429Filed(); await go('lrnxprompts'); R.E_seed={lib:pv().libState, voice:pv().voiceState, word:pv().wordList, cards:pv().cards.length, filed:K.promptLibrary.length, rules:pv().phrases.length, filedRules:K.voiceBanned.length};
 pv().addPrompt(); await form({title:'plant-429 prompt', does:'plant-429', tool:'plant-429', needs:'plant-429', text:'plant-429 prompt text', source:''}); await go('lrnxprompts'); R.E_nosource_twin={toast:toast(), cards:pv().cards.length};
 pv().addPrompt(); await form({title:'plant-429 prompt', does:'plant-429', tool:'plant-429', needs:'plant-429', text:'plant-429 prompt text', source:'plant-429 filed document'}); await go('lrnxprompts'); R.E_fire={lib:pv().libState, cards:pv().cards.length, last:pv().cards.slice(-1).map(c=>c.title+' · '+c.source)[0]};
 pv().addPhrase(); await form({phrase:'plant-429 rule', source:''}); await go('lrnxprompts'); R.E_rule_twin={toast:toast(), rules:pv().phrases.length};
 pv().addPhrase(); await form({phrase:'plant-429 rule', source:'plant-429 filed standard'}); await go('lrnxprompts'); R.E_rule_fire={voice:pv().voiceState, last:pv().phrases.slice(-1).map(p=>p.phrase+' · '+p.source)[0]};
 pv().cards.find(c=>c.title==='plant-429 prompt').remove(); await W(300); pv().phrases.find(p=>p.phrase==='plant-429 rule').remove(); await W(300); await go('lrnxprompts'); R.E_plant_removed={cards:pv().cards.length, rules:pv().phrases.length};
 const first=pv().cards[0]; first.remove(); await W(300); const st1=d.state; const again=d._e429Merge(st1); R.E_merge_notfire_marked={removed:first.id, returnedUntouched:again===st1, cards:pv().cards.length};
 const bare=Object.assign({}, st1, {connectors:Object.assign({}, st1.connectors, {e429Filed:undefined})}); const m=d._e429Merge(bare); R.E_merge_fire_unmarked={cards:(m.connectors.promptLibrary||[]).length, rules:(m.connectors.voiceBanned||[]).length, noDuplicateIds:new Set((m.connectors.promptLibrary||[]).map(p=>p.id)).size===(m.connectors.promptLibrary||[]).length, note:'computed on a copy; the book itself is not changed'};
 R.E_first_removal='the removed filed prompt is restored by the fresh load the eval proves (a fresh book takes the filed set once)';
 // ===== E · Document 113 (Item 431): the never-list writer =====
 await go('lrnxprompts'); R.E_never_seed={word:pv().wordList, n:pv().nevers.length};
 pv().addNever(); await form({never:'plant-431 never', why:'plant-431 reason', source:''}); await go('lrnxprompts'); R.E_never_nosource_twin={toast:toast(), n:pv().nevers.length};
 pv().addNever(); await form({never:'plant-431 never', why:'plant-431 reason', source:'plant-431 filed document'}); await go('lrnxprompts'); R.E_never_fire={word:pv().wordList, n:pv().nevers.length, last:pv().nevers.slice(-1)[0].never};
 pv().nevers.find(x=>x.never==='plant-431 never').remove(); await W(300); await go('lrnxprompts'); R.E_never_removed={n:pv().nevers.length, verbatim:pv().nevers.every((x,i)=>x.never===R1.doc113.entries[i].never && x.why===R1.doc113.entries[i].why)};
 // ===== F · the external benchmark writer on the one-seat book; H attrition =====
 await go('hrxtalent'); const bv=()=>rv().benchVM; R.F_seed={head:bv().head, answers:bv().rows[0].ans.map(a=>a.a)};
 bv().rows[0].file(); await form({comp:'plant-429 comparator', q1:'plant-429', q2:'plant-429', q3:'plant-429'}); await go('hrxtalent'); R.F_notfire_solo={comparator:bv().rows[0].comparator, answers:bv().rows[0].ans.map(a=>a.a)};
 bv().rows[0].file(); await form({comp:'', q1:'', q2:'', q3:''}); await go('hrxtalent'); R.F_removed={comparator:bv().rows[0].comparator, talentBench:Object.keys(((d.state.connectors||{}).talentBench)||{}).length};
 R.F_fire='not-fire only: no writer adds a second Active person to the People roster, so the comparator answers cannot be shown (Item 423)';
 R.H={attrition:bv().attrition, note:'not-fire only: no writer records a separation'};
 // ===== after removal =====
 const c=d.state.connectors||{}; R.after_removal={bdxCadence:JSON.stringify(c.bdxCadence||null), quarterTarget:String(c.quarterTarget), goNoGo:JSON.stringify(c.goNoGo||null), strategy:JSON.stringify(c.strategy||null), promptLibrary:(c.promptLibrary||[]).length, voiceBanned:(c.voiceBanned||[]).length, e429Filed:String(c.e429Filed||''), talentBench:Object.keys(c.talentBench||{}).length, fc_history:(d.state.fc.history||[]).length, deals:(d.state.deals||[]).length, initiatives:((c.initiatives||{}).entries||[]).length, note:'fc.history, the closed template deal and the initiative entry have no delete writer: removed by the fresh load the eval proves'};
 return R}
