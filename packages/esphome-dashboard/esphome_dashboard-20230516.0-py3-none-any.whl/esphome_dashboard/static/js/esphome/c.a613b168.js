import{b as t,l as s,n as e,s as i,y as o,f as a,r}from"./index-d3dd97b9.js";import"./c.e4466087.js";let l=class extends i{async showDialog(t,s){this._params=t,this._resolve=s}render(){return this._params?o`
      <mwc-dialog
        .heading=${this._params.title||""}
        @closed=${this._handleClose}
        open
      >
        ${this._params.text?o`<div>${this._params.text}</div>`:""}
        <mwc-button
          slot="secondaryAction"
          no-attention
          .label=${this._params.dismissText||"Cancel"}
          dialogAction="dismiss"
        ></mwc-button>
        <mwc-button
          slot="primaryAction"
          .label=${this._params.confirmText||"Yes"}
          class=${a({destructive:this._params.destructive||!1})}
          dialogAction="confirm"
        ></mwc-button>
      </mwc-dialog>
    `:o``}_handleClose(t){this._resolve("confirm"===t.detail.action),this.parentNode.removeChild(this)}static get styles(){return r`
      .destructive {
        --mdc-theme-primary: var(--alert-error-color);
      }
    `}};t([s()],l.prototype,"_params",void 0),t([s()],l.prototype,"_resolve",void 0),l=t([e("esphome-confirmation-dialog")],l);
