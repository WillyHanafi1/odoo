/** @odoo-module **/

import { WebClient } from "@web/webclient/webclient";
import { patch } from "@web/core/utils/patch";
import { registry } from "@web/core/registry";
import { HomeMenu } from "../home_menu/home_menu";

// 1. Register the HomeMenu as a client action
registry.category("actions").add("seriaflow.home_menu", HomeMenu);

// 2. Patch the WebClient to load out HomeMenu instead of the first app
patch(WebClient.prototype, {
    async _loadDefaultApp() {
        // Fallback to the original behavior if for some reason the action fails
        try {
            await this.actionService.doAction("seriaflow.home_menu", {
                clearBreadcrumbs: true,
            });
        } catch (e) {
            console.error("Failed to load Seriaflow Home Menu", e);
            super._loadDefaultApp(...arguments);
        }
    }
});
