"use strict";
/*
 * for attaching keybindings later on, see
 * https://towardsdatascience.com/how-to-customize-jupyterlab-keyboard-shortcuts-72321f73753d
 */
Object.defineProperty(exports, "__esModule", { value: true });
var apputils_1 = require("@jupyterlab/apputils");
var notebook_1 = require("@jupyterlab/notebook");
// import {
//   CodeCell,
//   MarkdownCell,
//   Cell,
// } from '@jupyterlab/cells'
//import { Widget } from '@lumino/widgets'
var jupyterlab_celltagsclasses_1 = require("jupyterlab-celltagsclasses");
/**
 * Initialization data for the jupyterlab-courselevels extension.
 */
var plugin = {
    id: 'jupyterlab-courselevels:plugin',
    autoStart: true,
    requires: [apputils_1.ICommandPalette, notebook_1.INotebookTracker],
    activate: function (app, palette, notebookTracker) {
        console.log('JupyterLab extension jupyterlab-courselevels is activating');
        // https://lumino.readthedocs.io/en/1.x/api/commands/interfaces/commandregistry.ikeybindingoptions.html
        // The supported modifiers are: Accel, Alt, Cmd, Ctrl, and Shift. The Accel
        // modifier is translated to Cmd on Mac and Ctrl on all other platforms. The
        // Cmd modifier is ignored on non-Mac platforms.
        // Alt is option on mac
        // let command
        // command = 'courselevels:metadata-clean'
        // app.commands.addCommand(command, {
        //   label: `clean metadata for all selected cells`,
        //   execute: () => apply_on_cells(notebookTracker, Scope.Multiple, (cell) => md_clean(cell, ''))
        // })
        // palette.addItem({ command, category: 'CourseLevels' })
        // app.commands.addKeyBinding({ command, keys: ['Alt Cmd 7'], selector: '.jp-Notebook' })
        jupyterlab_celltagsclasses_1.md_get;
        // xxx
    }
};
exports.default = plugin;
