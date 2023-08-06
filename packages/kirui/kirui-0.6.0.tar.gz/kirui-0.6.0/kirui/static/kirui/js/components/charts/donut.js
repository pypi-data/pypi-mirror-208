import { Chart, registerables } from './chart.esm.js';
import * as m from "../../core/component.js";

Chart.register(...registerables);

class DonutChart extends m.Component {
    render() {
        return m.html`
            <canvas></canvas>
        `
    }

    async connectedCallback() {
        super.connectedCallback();
        await this.updateComplete;

        console.log(this.updateComplete)
        let ctx = this.getElementsByTagName('canvas')[0];
        let data = {

        };

        new Chart(ctx, {
            type: "doughnut",
            data: {
                labels: Object.keys(this.values),
                datasets: [
                    {
                        data: Object.values(this.values),
                        backgroundColor: ["#0b84a5", "#f6c85f", "#6f4e7c", "#9dd866", "#ca472f", "#ffa056", "#8dddd0"],
                        borderColor: ["#0b84a5", "#f6c85f", "#6f4e7c", "#9dd866", "#ca472f", "#ffa056", "#8dddd0"],
                    }
                ]
            },
            options: Chart.defaults.doughnut
        });
    }
}
customElements.define("kr-chart-donut", DonutChart);

export { DonutChart };
