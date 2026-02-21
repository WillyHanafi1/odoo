/** @odoo-module **/

import { Component, useState } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class HomeMenu extends Component {
    static template = "seriaflow_home_menu.HomeMenu";
    static props = ["*"];

    setup() {
        this.menuService = useService("menu");
        this.actionService = useService("action");

        // Exclude root and get all available apps
        this.apps = this.menuService.getApps();

        this.state = useState({
            searchQuery: "",
        });
    }

    get filteredApps() {
        if (!this.state.searchQuery) {
            return this.apps;
        }
        const query = this.state.searchQuery.toLowerCase();
        return this.apps.filter((app) =>
            app.name.toLowerCase().includes(query)
        );
    }

    onAppClick(app) {
        this.menuService.selectMenu(app);
    }
}
