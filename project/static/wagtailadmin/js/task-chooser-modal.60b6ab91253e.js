!function(){"use strict";var t={28432:function(t,e,a){var n=this&&this.__importDefault||function(t){return t&&t.__esModule?t:{default:t}};e.__esModule=!0;var r=n(a(73609)),o={chooser:function(t,e){function a(e){r.default("a.task-type-choice, a.choose-different-task-type, a.task-choice",e).on("click",(function(){return t.loadUrl(this.href),!1})),r.default(".pagination a",e).on("click",(function(){return t=this.getAttribute("data-page"),e=r.default("#id_q").val().length?{q:r.default("#id_q").val(),p:t}:{p:t},n=r.default.ajax({url:o,data:e,success:function(t){n=null,r.default("#search-results").html(t),a(r.default("#search-results"))},error:function(){n=null}}),!1;var t,e})),r.default("a.create-one-now").on("click",(function(t){r.default('a[href="#new"]').tab("show"),t.preventDefault()}))}var n,o=r.default("form.task-search",t.body).attr("action");function u(){return n=r.default.ajax({url:o,data:{q:r.default("#id_q").val(),task_type:r.default("#id_task_type").val()},success:function(t){n=null,r.default("#search-results").html(t),a(r.default("#search-results"))},error:function(){n=null}}),!1}a(t.body),r.default("form.task-create",t.body).on("submit",(function(){var a=new FormData(this);return r.default.ajax({url:this.action,data:a,processData:!1,contentType:!1,type:"POST",dataType:"text",success:t.loadResponseText,error:function(t,a,n){var o=e.error_message+"<br />"+n+" - "+t.status;r.default("#new").append('<div class="help-block help-critical"><strong>'+e.error_label+": </strong>"+o+"</div>")}}),!1})),r.default("form.task-search",t.body).on("submit",u),r.default("#id_q").on("input",(function(){n&&n.abort(),clearTimeout(r.default.data(this,"timer"));var t=setTimeout(u,50);r.default(this).data("timer",t)})),r.default("#id_task_type").on("change",(function(){n&&n.abort(),clearTimeout(r.default.data(this,"timer"));var t=setTimeout(u,50);r.default(this).data("timer",t)}))},task_chosen:function(t,e){t.respond("taskChosen",e.result),t.close()}};window.TASK_CHOOSER_MODAL_ONLOAD_HANDLERS=o},73609:function(t){t.exports=jQuery}},e={};function a(n){if(e[n])return e[n].exports;var r=e[n]={exports:{}};return t[n].call(r.exports,r,r.exports,a),r.exports}a.m=t,a.x=function(){},a.g=function(){if("object"==typeof globalThis)return globalThis;try{return this||new Function("return this")()}catch(t){if("object"==typeof window)return window}}(),a.o=function(t,e){return Object.prototype.hasOwnProperty.call(t,e)},function(){var t={342:0},e=[[28432,751],[90971,751]],n=function(){},r=function(r,o){for(var u,i,l=o[0],s=o[1],c=o[2],f=o[3],d=0,h=[];d<l.length;d++)i=l[d],a.o(t,i)&&t[i]&&h.push(t[i][0]),t[i]=0;for(u in s)a.o(s,u)&&(a.m[u]=s[u]);for(c&&c(a),r&&r(o);h.length;)h.shift()();return f&&e.push.apply(e,f),n()},o=self.webpackChunkwagtail=self.webpackChunkwagtail||[];function u(){for(var n,r=0;r<e.length;r++){for(var o=e[r],u=!0,i=1;i<o.length;i++){var l=o[i];0!==t[l]&&(u=!1)}u&&(e.splice(r--,1),n=a(a.s=o[0]))}return 0===e.length&&(a.x(),a.x=function(){}),n}o.forEach(r.bind(null,0)),o.push=r.bind(null,o.push.bind(o));var i=a.x;a.x=function(){return a.x=i||function(){},(n=u)()}}(),a.x()}();
//# sourceMappingURL=task-chooser-modal.js.map