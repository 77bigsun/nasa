import en from './messages/en.json'
import zh from './messages/zh-TW.json'

export type TaskCode = 'M1'|'M2'|'M3'|'M4'|'M5'|'M6'|'R1'|'R2'|'R3'|'R4'|'R5'|'R6'
export function taskName(code:string,locale:string):string {
 const messages=locale==='zh-TW'?zh:en
 return messages[('task_'+code) as keyof typeof messages]??code
}
export function expandTaskNames(text:string,locale:string):string {
 const separator=locale==='zh-TW'?'\u3001':', '
 const ranges=text.replace(/\b([MR])([1-6])\s*(?:~{1,2}|[-–—\uff5e])\s*\1([1-6])\b/g,(_,body:string,first:string,last:string)=>{
  const start=Number(first),end=Number(last)
  if(end<start)return taskName(body+first,locale)+separator+taskName(body+last,locale)
  return Array.from({length:end-start+1},(_,i)=>taskName(body+(start+i),locale)).join(separator)
 })
 return ranges.replace(/\b[MR][1-6]\b/g,code=>taskName(code,locale))
}

/** Format explanatory content without changing routing IDs or source URLs. */
export function readableTaskContent<T>(value:T,locale:string):T {
 function visit(item:unknown,key=''):unknown {
  if(/(^id$|_ids?$|url$|^href$|^path$|^sha256$)/.test(key))return item
  if(typeof item==='string')return expandTaskNames(item,locale)
  if(Array.isArray(item))return item.map(child=>visit(child,key))
  if(item&&typeof item==='object')return Object.fromEntries(Object.entries(item).map(([k,v])=>[k,visit(v,k)]))
  return item
 }
 return visit(value) as T
}

/** Replace visible text only; links and document metadata stay intact. */
export function readableTaskHtml(html:string,locale:string):string {
 const parsed=new DOMParser().parseFromString(html,'text/html')
 const walker=parsed.createTreeWalker(parsed.body,NodeFilter.SHOW_TEXT)
 let node:Node|null
 while((node=walker.nextNode()))node.textContent=expandTaskNames(node.textContent??'',locale)
 return parsed.body.innerHTML
}
