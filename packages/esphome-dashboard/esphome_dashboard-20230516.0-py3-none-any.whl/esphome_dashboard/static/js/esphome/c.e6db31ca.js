import{b as o,d as t,l as s,n as e,s as i,y as r,H as n}from"./index-d3dd97b9.js";import"./c.1bc018ae.js";import{o as a}from"./c.61332c08.js";import"./c.e4466087.js";import"./c.7d2e85dd.js";import"./c.e683a7a9.js";let l=class extends i{render(){return r`
      <esphome-process-dialog
        always-show-close
        .heading=${`Logs ${this.configuration}`}
        .type=${"logs"}
        .spawnParams=${{configuration:this.configuration,port:this.target}}
        @closed=${this._handleClose}
        @process-done=${this._handleProcessDone}
      >
        <mwc-button
          slot="secondaryAction"
          dialogAction="close"
          label="Edit"
          @click=${this._openEdit}
        ></mwc-button>
        ${void 0===this._result||0===this._result?"":r`
              <mwc-button
                slot="secondaryAction"
                dialogAction="close"
                label="Retry"
                @click=${this._handleRetry}
              ></mwc-button>
            `}
      </esphome-process-dialog>
    `}_openEdit(){n(this.configuration)}_handleProcessDone(o){this._result=o.detail}_handleRetry(){a(this.configuration,this.target)}_handleClose(){this.parentNode.removeChild(this)}};o([t()],l.prototype,"configuration",void 0),o([t()],l.prototype,"target",void 0),o([s()],l.prototype,"_result",void 0),l=o([e("esphome-logs-dialog")],l);
