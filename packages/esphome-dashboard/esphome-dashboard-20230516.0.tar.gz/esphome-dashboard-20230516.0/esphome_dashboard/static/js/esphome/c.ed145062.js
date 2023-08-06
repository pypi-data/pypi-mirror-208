import{b as e,d as o,l as s,n as t,s as i,y as a,a5 as n}from"./index-d3dd97b9.js";import"./c.1bc018ae.js";import"./c.e4466087.js";let r=class extends i{render(){return a`
      <esphome-process-dialog
        always-show-close
        .heading=${`Rename ${this.configuration}`}
        .type=${"rename"}
        .spawnParams=${{configuration:this.configuration,newName:`${this.newName}`}}
        @closed=${this._handleClose}
        @process-done=${this._handleProcessDone}
      >
        ${void 0===this._result||0===this._result?"":a`
              <mwc-button
                slot="secondaryAction"
                dialogAction="close"
                label="Retry"
                @click=${this._handleRetry}
              ></mwc-button>
            `}
      </esphome-process-dialog>
    `}_handleProcessDone(e){this._result=e.detail}_handleRetry(){n(this.configuration,this.newName)}_handleClose(){this.parentNode.removeChild(this)}};e([o()],r.prototype,"configuration",void 0),e([o()],r.prototype,"newName",void 0),e([s()],r.prototype,"_result",void 0),r=e([t("esphome-rename-process-dialog")],r);
