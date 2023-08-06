import * as m from "../../core/component.js";

class Card extends m.Component {
    render() {
        console.log(this.link)
        return m.html`
          <div class="card shadow-sm mb-1">
            <div class="card-title p-3">${this.title}</div>
            <div class="card-body">${this.body}</div>
            ${this.link
            ? m.html`<div class="card-footer">
              link
            </div>`
            : m.html``}
          </div>
        `
    }
}
customElements.define("kr-kanban-card", Card);

export { Card };
