import * as m from "../core/component.js";


class EditButtonGroup extends m.Component {
    static properties = {
        is_open: {},
    }
    constructor() {
        super();
        this.is_open = false;
    }

    close(ev) {
        let path = ev.path || ev.composedPath();
        if (path.indexOf(this) === -1) {
            this.is_open = false;
        }
        document.removeEventListener("click", (ev) => { this.close(ev); }, false);
    }

    open(ev) {
        ev.preventDefault();
        document.addEventListener("click", (ev) => { this.close(ev); }, false);

        // this.querySelector('.dropdown-menu').classList.add('show');
        let parent_rect = this.querySelector('.parent').getBoundingClientRect();
        for (let el of this.getElementsByClassName('dropdown-menu')) {
            if (this.is_open || ev.target.classList.contains('dropdown-item')) {
                this.is_open = false;
                //el.classList.remove('show');
            } else {
                this.is_open = true;
                el.classList.add('show');
                let rect = el.getBoundingClientRect();
                if (rect.right > window.innerWidth) {
                    let left = rect.width - this.querySelector('button').getBoundingClientRect().width;
                    el.style['left'] = `-${left}px`;
                }

                if (rect.bottom > window.innerHeight) {
                    el.style['top'] = `-${rect.height}px`;
                }
            }
        }
    }

    render() {
        return m.html`
          <div class="parent" style="position: relative; display: inline-block;">
            <div class="btn-group">
              <button type="button" class="btn btn-outline-secondary dropdown-toggle" @click="${this.open}">${this.getAttribute('label')}</button>
            </div>
            <div class=${m.classMap({'dropdown-menu': true, 'show': this.is_open})}>${this.$children}</div>
          </div>
        `
    }
}
customElements.define("kr-button-group", EditButtonGroup)
