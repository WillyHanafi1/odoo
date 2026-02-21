/** @odoo-module **/

import { Component } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";

export class HomeMenuSystray extends Component {
    static template = "seriaflow_home_menu.HomeMenuSystray";
    static props = {};

    setup() {
        this.action = useService("action");
    }

    onGlobalHomeClick() {
        this.action.doAction("home", { clearBreadcrumbs: true });
    }
}

export const systrayItem = {
    Component: HomeMenuSystray,
};

// Register this at the very left of the systray (highest sequence, or lowest depending on sorting; usually higher is more right, 0 is rightmost in user_menu, some use sequence 10, 20 etc). 
// Since UserMenu is 0 and it's on the right, higher sequence means more towards the left. Let's use 100 to push it leftwards.
registry.category("systray").add("seriaflow_home_menu.global_home_btn", systrayItem, { sequence: 100 });
