// PDF.js and its worker are served locally; documents never leave this site.
let library;
const documents=new Map();
async function pdfDocument(url){
 if(!library)library=import('./vendor/pdfjs/pdf.min.js').then(pdf=>{
  pdf.GlobalWorkerOptions.workerSrc=new URL('./vendor/pdfjs/pdf.worker.min.js',import.meta.url).href;
  return pdf;
 });
 if(!documents.has(url))documents.set(url,library.then(pdf=>pdf.getDocument({
  url,cMapUrl:new URL('./vendor/pdfjs/cmaps/',import.meta.url).href,cMapPacked:true,
  standardFontDataUrl:new URL('./vendor/pdfjs/standard_fonts/',import.meta.url).href,
  wasmUrl:new URL('./vendor/pdfjs/wasm/',import.meta.url).href,
  isEvalSupported:false,
 }).promise).catch(error=>{documents.delete(url);throw error}));
 return documents.get(url);
}
export async function renderPdf({body,url,pageNumber,title,zoom='fit',isCurrent}){
 body.dataset.renderStatus='loading';
 const doc=await pdfDocument(url),page=await doc.getPage(pageNumber);
 if(!isCurrent())return;
 const base=page.getViewport({scale:1});
 const width=Math.max(260,body.clientWidth-32);
 const scale=zoom==='fit'?width/base.width:Number(zoom);
 const view=page.getViewport({scale}),ratio=Math.min(window.devicePixelRatio||1,2);
 const wrap=document.createElement('div');wrap.className='pdf-surface';wrap.dataset.zoom=zoom;
 const canvas=document.createElement('canvas');canvas.setAttribute('role','img');
 canvas.setAttribute('aria-label',`${title}, PDF strana ${pageNumber}. Pro přístupný text zvolte Text.`);
 canvas.width=Math.ceil(view.width*ratio);canvas.height=Math.ceil(view.height*ratio);
 canvas.style.width=`${view.width}px`;canvas.style.height=`${view.height}px`;
 wrap.append(canvas);body.replaceChildren(wrap);body.scrollTop=0;
 await page.render({canvasContext:canvas.getContext('2d'),viewport:view,transform:ratio===1?null:[ratio,0,0,ratio,0,0]}).promise;
 if(isCurrent())body.dataset.renderStatus='loaded';
}
