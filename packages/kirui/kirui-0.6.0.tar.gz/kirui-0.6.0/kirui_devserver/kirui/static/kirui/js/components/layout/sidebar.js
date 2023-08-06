import { Component, html, render } from "../../core/component.js";

class SideBarLayout extends Component {
    constructor() {
        super();
        this._is_pwa = Boolean(Number(this.getAttribute('is_pwa')));  // TODO: app-ról kellene leszedni
        this._sidebar_width = 256
        this._is_sidebar_pinned = true
        this._is_sidebar_toggled = false
        this._sidebar_is_moving = false
    }

    sidebar_width() {
        return `${this._sidebar_width}px`
    }

    navbar_pinner_clicked(ev) {
        ev.preventDefault();
        ev.stopPropagation();
        if (this._is_pwa) {
            if (this._is_sidebar_toggled) {
                this.querySelector('kr-sidebar-nav').style.left = `-${this.sidebar_width()}`;
                this.querySelector('#navbar-overflow').style.display = 'none';
                this._is_sidebar_toggled = false;
            } else {
                this.querySelector('kr-sidebar-nav').style.left = '0';
                this.querySelector('#navbar-overflow').style.display = 'block';
                this._is_sidebar_toggled = true;
            }
        } else {
            if (this._is_sidebar_pinned) {
                this.querySelector('kr-sidebar-nav').style.left = `-${this.sidebar_width()}`;
                this.querySelector('kr-sidebar-main').style['margin-left'] = '0';
                this._is_sidebar_pinned = false;
            } else {
                this.querySelector('kr-sidebar-nav').style.left = '0';
                this.querySelector('kr-sidebar-main').style['margin-left'] = `${this.sidebar_width()}`;
                this._is_sidebar_pinned = true;
            }
        }
    }

    show_navbar(ev) {
        ev.preventDefault();
        ev.stopPropagation();
        if (this._is_sidebar_pinned === false) {
            this.querySelector('kr-sidebar-nav').style.left = '0';
            this._is_sidebar_toggled = true;
        }
    }

    hide_navbar(ev) {
        ev.preventDefault();
        ev.stopPropagation();
        if (this._is_sidebar_toggled === true) {
            this.querySelector('kr-sidebar-nav').style.left = `-${this.sidebar_width()}`;
            this._is_sidebar_toggled = false;
        }
    }

    navbar_touch_start(ev) {
        this.querySelector('kr-sidebar-nav').style['transition'] = 'all 0s ease';
        let x_coord = ev.touches[0].pageX;
        if (this._is_sidebar_toggled === false && x_coord < 50) {
            ev.preventDefault();
            this._sidebar_is_moving = true;
        } else if (this._is_sidebar_toggled && this._sidebar_width - 50 <= x_coord <= this._sidebar_width + 50) {
            this._sidebar_is_moving = true;
        }
    }

    navbar_touch_move(ev) {
        if (this._sidebar_is_moving === false) {
            return
        }

        let left = ev.touches[0].pageX - this._sidebar_width
        if (left > 0) { left = 0; }
        this.querySelector('kr-sidebar-nav').style['left'] = `${left}px`
    }

    navbar_touch_end(ev) {
        if (this._sidebar_is_moving === false) { return }
        this.querySelector('kr-sidebar-nav').style['transition'] = 'all 0.5s ease';

        if (ev.changedTouches[0].pageX >= 256 / 2) {
            this.querySelector('kr-sidebar-nav').style['left'] = '0';
            this._is_sidebar_toggled = true;
            this.querySelector('#navbar-overflow').style['display'] = 'block';
        } else {
            this.querySelector('kr-sidebar-nav').style['left'] = `-${this.sidebar_width()}`;
            this._is_sidebar_toggled = false;
            this.querySelector('#navbar-overflow').style['display'] = 'none';
        }
        this._sidebar_is_moving = false;
    }

    dropdown_toggle(ev) {
        ev.preventDefault();
        ev.stopPropagation();
        let parent_rect = ev.target.parentElement.getBoundingClientRect();
        ev.target.classList.add('show');
        for (let el of ev.target.parentElement.getElementsByClassName('dropdown-menu')) {
            if (el.classList.contains('show')) {
                el.classList.remove('show');
            } else {
                el.classList.add('show');
                let rect = el.getBoundingClientRect()
                let offset_left = parent_rect.width - rect.width
                el.style['left'] = `${offset_left}px`
                el.style['top'] = `${parent_rect.top + parent_rect.height - 7}px`
            }
        }
    }

    expand_menu(ev) {
        ev.preventDefault()
        ev.stopPropagation()

        for (let submenu of ev.target.closest('li').querySelectorAll('ul')) {
            if (submenu.classList.contains('expanded')) {
                submenu.classList.remove('expanded')
            } else {
                submenu.classList.add('expanded')
            }
        }
    }

    window_click(ev) {
        /*console.log(ev.target.classList);
        if (ev.target.classList === undefined) { return }*/
        /*for (let el of document.body.querySelectorAll('.show')) {
            if (ev.target === window) {
                el.classList.remove('show');
            } else if ((ev.target !== el) && (!ev.target.classList.contains('collapse'))) {
                el.classList.remove('show');
            }
        }*/
    }

    render() {
        return html`${this.$children}<div id="loading"><div class="sr-only spinner-border"></div></div>`
    }

    async connectedCallback() {
        super.connectedCallback();
        await this.updateComplete;
        /* bal felső sarokban a menü kapcsoló gomb */
        this.querySelector('#navbar-pinner').addEventListener('click', (ev) => { this.navbar_pinner_clicked(ev); });
        if (this._is_pwa) {
            /* addEventListenerrel valamiért nem ment a touch event */
            $(this).find('kr-sidebar-main, kr-sidebar-nav').on('touchstart', (ev) => { this.navbar_touch_start(ev) });
            $(this).find('kr-sidebar-main, kr-sidebar-nav').on('touchmove', (ev) => { this.navbar_touch_move(ev) });
            $(this).find('kr-sidebar-main, kr-sidebar-nav').on('touchend', (ev) => { this.navbar_touch_end(ev) });
            this.querySelector('kr-sidebar-nav').style.left = `-${this.sidebar_width()}`;
            this.querySelector('kr-sidebar-main').style['margin-left'] = '0';
        } else {
            this.querySelector('#navbar-toggler').addEventListener('mouseover', (ev) => { this.show_navbar(ev); });
            this.querySelector('kr-sidebar-nav').addEventListener('mouseleave', (ev) => { this.hide_navbar(ev); })
        }

        this.querySelector('.dropdown-toggle').addEventListener('click', (ev) => { this.dropdown_toggle(ev); });
        $(this).find('.expand').on('click', (ev) => { this.expand_menu(ev) });
        window.addEventListener('click', (ev) => { this.window_click(ev); });
    }
}
customElements.define("kr-layout-sidebar", SideBarLayout)


class SidebarHeader extends Component {
    render() {
        return html`
          <div class="navbar fixed-top navbar-dark sidebar-header">
            <div class="container-fluid">
              <button class="navbar-toggler" id="navbar-pinner" type="button">
                <span class="navbar-toggler-icon"></span>
              </button>
              ${this.$children}
            </div>
          </div>`
    }
}
customElements.define("kr-sidebar-header", SidebarHeader)


class SidebarNavigation extends Component {
    render() {
        return html`${this.$children}`
    }
}
customElements.define("kr-sidebar-nav", SidebarNavigation)


class SidebarMain extends Component {
    render() {
        return html`
        <div id="navbar-toggler"></div>
        <div id="navbar-overflow"></div>
        <div class="container-fluid">
            <div class="row">
              ${this.$children}
            </div>
        </div>`
    }
}
customElements.define("kr-sidebar-main", SidebarMain)


export { SideBarLayout, SidebarHeader, SidebarNavigation, SidebarMain }
