import * as m from "../../core/component.js";

class KanbanBoard extends m.Component {
    static properties = {
        data: {attribute: false, state: true},
    };

    constructor() {
        super();
        this.data = [];
    }

    render() {
        return m.html`
          <div class="row">
            <h3 class="font-weight-light">${this.getAttribute('name')}</h3>
            <div class="row flex-row flex-sm-nowrap py-3">
              ${this.data.map((stage) =>
              m.html`<div class="col-sm-6 col-md-4 col-xl-3">
                <div class="card bg-light">
                  <div class="card-body">
                    <h6 class="card-title text-uppercase text-truncate py-2">${stage.name}</h6>
                      <div class="items border border-light">
                      ${stage.cards.map((card) =>
                        m.html`<kr-kanban-card .title=${card.title} .body=${card.body} .link=${card.link}></kr-kanban-card>`
                      )}
                      </div>
                    </div>
                  </div>
                </div>
              </div>`
              )}
            </div>
          </div>
        `
    }
}
customElements.define("kr-kanban-board", KanbanBoard);

export { KanbanBoard };
