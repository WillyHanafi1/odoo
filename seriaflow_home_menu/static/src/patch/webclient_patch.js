/** @odoo-module **/

import { WebClient } from "@web/webclient/webclient";
import { patch } from "@web/core/utils/patch";
import { registry } from "@web/core/registry";
import { HomeMenu } from "../home_menu/home_menu";

// 1. Register the HomeMenu as a client action
registry.category("actions").add("seriaflow.home_menu", HomeMenu);

// 2. Patch the WebClient to load out HomeMenu instead of the first app and intercept URL states
patch(WebClient.prototype, {
    async loadRouterState() {
        const { pathname, search } = window.location;

        // In Odoo 19, standard URLs are like /odoo/action-123 or /odoo/discuss
        // If the path is strictly /odoo or /web without any extra action paths,
        // we forcefully prevent Odoo from restoring the last opened app (Discuss/etc)
        // by returning _loadDefaultApp directly.
        if ((pathname === "/odoo" || pathname === "/web") && !search.includes("action=")) {
            // No specific action requested, force load Home Menu instead of Session State
            return this._loadDefaultApp();
        }

        // Otherwise, behave as normal (loading a specific record/app from URL)
        return super.loadRouterState(...arguments);
    },

    async _loadDefaultApp() {
        // Fallback to the original behavior if for some reason the action fails
        try {
            await this.actionService.doAction("seriaflow.home_menu", {
                clearBreadcrumbs: true,
            });
            // Overwrite the URL to just /odoo or / after loading it
            // Odoo's framework natively keeps `?action=seriaflow.home_menu`. 
            // We clear the router hash/search to keep the URL look clean.
            this.env.services.router.pushState({}, { replace: true });
        } catch (e) {
            console.error("Failed to load Seriaflow Home Menu", e);
            super._loadDefaultApp(...arguments);
        }
    }
});
