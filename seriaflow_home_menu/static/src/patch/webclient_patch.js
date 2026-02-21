/** @odoo-module **/

import { registry } from "@web/core/registry";
import { HomeMenu } from "../home_menu/home_menu";

// We override the native "home" client action in Odoo with our Custom HomeMenu.
// This allows the user to access the menu naturally via URL: /odoo/home
// And ensures that whenever Odoo triggers "home" (like clicking the top-left logo),
// it instantly paints our HomeMenu instead of a hard browser reload.
registry.category("actions").add("home", HomeMenu, { force: true });
