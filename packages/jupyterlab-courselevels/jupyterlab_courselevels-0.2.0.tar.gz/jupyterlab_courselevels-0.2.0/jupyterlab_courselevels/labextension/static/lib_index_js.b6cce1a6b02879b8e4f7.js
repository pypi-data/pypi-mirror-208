"use strict";
(self["webpackChunkjupyterlab_courselevels"] = self["webpackChunkjupyterlab_courselevels"] || []).push([["lib_index_js"],{

/***/ "./lib/index.js":
/*!**********************!*\
  !*** ./lib/index.js ***!
  \**********************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @jupyterlab/apputils */ "webpack/sharing/consume/default/@jupyterlab/apputils");
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @jupyterlab/notebook */ "webpack/sharing/consume/default/@jupyterlab/notebook");
/* harmony import */ var _jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _lumino_disposable__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! @lumino/disposable */ "webpack/sharing/consume/default/@lumino/disposable");
/* harmony import */ var _lumino_disposable__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(_lumino_disposable__WEBPACK_IMPORTED_MODULE_2__);
/* harmony import */ var jupyterlab_celltagsclasses__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! jupyterlab-celltagsclasses */ "webpack/sharing/consume/default/jupyterlab-celltagsclasses/jupyterlab-celltagsclasses");
/* harmony import */ var jupyterlab_celltagsclasses__WEBPACK_IMPORTED_MODULE_3___default = /*#__PURE__*/__webpack_require__.n(jupyterlab_celltagsclasses__WEBPACK_IMPORTED_MODULE_3__);
/*
 * for attaching keybindings later on, see
 * https://towardsdatascience.com/how-to-customize-jupyterlab-keyboard-shortcuts-72321f73753d
 */





/**
 * Initialization data for the jupyterlab-courselevels extension.
 */
const plugin = {
    id: 'jupyterlab-courselevels:plugin',
    autoStart: true,
    requires: [_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__.ICommandPalette, _jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_1__.INotebookTracker],
    activate: (app, palette, notebookTracker) => {
        console.log('extension jupyterlab-courselevels is activating');
        // https://lumino.readthedocs.io/en/1.x/api/commands/interfaces/commandregistry.ikeybindingoptions.html
        // The supported modifiers are: Accel, Alt, Cmd, Ctrl, and Shift. The Accel
        // modifier is translated to Cmd on Mac and Ctrl on all other platforms. The
        // Cmd modifier is ignored on non-Mac platforms.
        // Alt is option on mac
        const cell_toggle_level = (cell, level) => {
            switch (level) {
                case 'basic':
                    if ((0,jupyterlab_celltagsclasses__WEBPACK_IMPORTED_MODULE_3__.md_has)(cell, 'tags', 'level_basic')) {
                        (0,jupyterlab_celltagsclasses__WEBPACK_IMPORTED_MODULE_3__.md_remove)(cell, 'tags', 'level_basic');
                    }
                    else {
                        (0,jupyterlab_celltagsclasses__WEBPACK_IMPORTED_MODULE_3__.md_insert)(cell, 'tags', 'level_basic');
                        (0,jupyterlab_celltagsclasses__WEBPACK_IMPORTED_MODULE_3__.md_remove)(cell, 'tags', 'level_intermediate');
                        (0,jupyterlab_celltagsclasses__WEBPACK_IMPORTED_MODULE_3__.md_remove)(cell, 'tags', 'level_advanced');
                    }
                    break;
                case 'intermediate':
                    if ((0,jupyterlab_celltagsclasses__WEBPACK_IMPORTED_MODULE_3__.md_has)(cell, 'tags', 'level_intermediate')) {
                        (0,jupyterlab_celltagsclasses__WEBPACK_IMPORTED_MODULE_3__.md_remove)(cell, 'tags', 'level_intermediate');
                    }
                    else {
                        (0,jupyterlab_celltagsclasses__WEBPACK_IMPORTED_MODULE_3__.md_remove)(cell, 'tags', 'level_basic');
                        (0,jupyterlab_celltagsclasses__WEBPACK_IMPORTED_MODULE_3__.md_insert)(cell, 'tags', 'level_intermediate');
                        (0,jupyterlab_celltagsclasses__WEBPACK_IMPORTED_MODULE_3__.md_remove)(cell, 'tags', 'level_advanced');
                    }
                    break;
                case 'advanced':
                    if ((0,jupyterlab_celltagsclasses__WEBPACK_IMPORTED_MODULE_3__.md_has)(cell, 'tags', 'level_advanced')) {
                        (0,jupyterlab_celltagsclasses__WEBPACK_IMPORTED_MODULE_3__.md_remove)(cell, 'tags', 'level_advanced');
                    }
                    else {
                        (0,jupyterlab_celltagsclasses__WEBPACK_IMPORTED_MODULE_3__.md_remove)(cell, 'tags', 'level_basic');
                        (0,jupyterlab_celltagsclasses__WEBPACK_IMPORTED_MODULE_3__.md_remove)(cell, 'tags', 'level_intermediate');
                        (0,jupyterlab_celltagsclasses__WEBPACK_IMPORTED_MODULE_3__.md_insert)(cell, 'tags', 'level_advanced');
                    }
                    break;
                default:
                    (0,jupyterlab_celltagsclasses__WEBPACK_IMPORTED_MODULE_3__.md_remove)(cell, 'tags', 'level_basic');
                    (0,jupyterlab_celltagsclasses__WEBPACK_IMPORTED_MODULE_3__.md_remove)(cell, 'tags', 'level_intermediate');
                    (0,jupyterlab_celltagsclasses__WEBPACK_IMPORTED_MODULE_3__.md_remove)(cell, 'tags', 'level_advanced');
            }
        };
        const toggle_level = (level) => {
            var _a;
            const notebook = (_a = notebookTracker.currentWidget) === null || _a === void 0 ? void 0 : _a.content;
            if (notebook === undefined) {
                return;
            }
            const activeCell = notebook.activeCell;
            if (activeCell === null) {
                return;
            }
            cell_toggle_level(activeCell, level);
        };
        let command;
        for (const [level, key] of [
            ['basic', 'Ctrl X'],
            ['intermediate', 'Ctrl Y'],
            ['advanced', 'Ctrl Z'],
        ]) {
            command = `courselevels:toggle-level-${level}`;
            app.commands.addCommand(command, {
                label: `toggle ${level} level`,
                execute: () => toggle_level(level)
            });
            palette.addItem({ command, category: 'CourseLevels' });
            app.commands.addKeyBinding({ command, keys: [key], selector: '.jp-Notebook' });
        }
        const toggle_frame = () => {
            var _a;
            const notebook = (_a = notebookTracker.currentWidget) === null || _a === void 0 ? void 0 : _a.content;
            if (notebook === undefined) {
                return;
            }
            const activeCell = notebook.activeCell;
            if (activeCell === null) {
                return;
            }
            if ((0,jupyterlab_celltagsclasses__WEBPACK_IMPORTED_MODULE_3__.md_has)(activeCell, 'tags', 'framed_cell')) {
                (0,jupyterlab_celltagsclasses__WEBPACK_IMPORTED_MODULE_3__.md_remove)(activeCell, 'tags', 'framed_cell');
            }
            else {
                (0,jupyterlab_celltagsclasses__WEBPACK_IMPORTED_MODULE_3__.md_insert)(activeCell, 'tags', 'framed_cell');
            }
        };
        command = 'courselevels:toggle-frame';
        app.commands.addCommand(command, {
            label: 'toggle frame',
            execute: () => toggle_frame()
        });
        palette.addItem({ command, category: 'CourseLevels' });
        app.commands.addKeyBinding({ command, keys: ['Ctrl M'], selector: '.jp-Notebook' });
        const toggle_licence = () => {
            var _a;
            const notebook = (_a = notebookTracker.currentWidget) === null || _a === void 0 ? void 0 : _a.content;
            if (notebook === undefined) {
                return;
            }
            const activeCell = notebook.activeCell;
            if (activeCell === null) {
                return;
            }
            if ((0,jupyterlab_celltagsclasses__WEBPACK_IMPORTED_MODULE_3__.md_has)(activeCell, 'tags', 'licence')) {
                (0,jupyterlab_celltagsclasses__WEBPACK_IMPORTED_MODULE_3__.md_remove)(activeCell, 'tags', 'licence');
            }
            else {
                (0,jupyterlab_celltagsclasses__WEBPACK_IMPORTED_MODULE_3__.md_insert)(activeCell, 'tags', 'licence');
            }
        };
        command = 'courselevels:toggle-licence';
        app.commands.addCommand(command, {
            label: 'toggle licence',
            execute: () => toggle_licence()
        });
        palette.addItem({ command, category: 'CourseLevels' });
        app.commands.addKeyBinding({ command, keys: ['Ctrl L'], selector: '.jp-Notebook' });
        // the buttons in the toolbar
        const find_spacer = (panel) => {
            let index = 0;
            for (const child of panel.toolbar.children()) {
                if (child.node.classList.contains('jp-Toolbar-spacer')) {
                    return index;
                }
                else {
                    index += 1;
                }
            }
            return 0;
        };
        class BasicButton {
            createNew(panel, context) {
                const button = new _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__.ToolbarButton({
                    className: 'courselevels-button',
                    iconClass: 'far fa-hand-pointer',
                    onClick: () => toggle_level('basic'),
                    tooltip: 'Toggle basic level',
                });
                // compute where to insert it
                const index = find_spacer(panel);
                panel.toolbar.insertItem(index, 'basicLevel', button);
                return new _lumino_disposable__WEBPACK_IMPORTED_MODULE_2__.DisposableDelegate(() => {
                    button.dispose();
                });
            }
        }
        app.docRegistry.addWidgetExtension('Notebook', new BasicButton());
        class IntermediateButton {
            createNew(panel, context) {
                const button = new _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__.ToolbarButton({
                    className: 'courselevels-button',
                    iconClass: 'far fa-hand-peace',
                    onClick: () => toggle_level('intermediate'),
                    tooltip: 'Toggle intermediate level',
                });
                // compute where to insert it
                const index = find_spacer(panel);
                panel.toolbar.insertItem(index, 'intermediateLevel', button);
                return new _lumino_disposable__WEBPACK_IMPORTED_MODULE_2__.DisposableDelegate(() => {
                    button.dispose();
                });
            }
        }
        app.docRegistry.addWidgetExtension('Notebook', new IntermediateButton());
        class AdvancedButton {
            createNew(panel, context) {
                const button = new _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__.ToolbarButton({
                    className: 'courselevels-button',
                    iconClass: 'far fa-hand-spock',
                    onClick: () => toggle_level('advanced'),
                    tooltip: 'Toggle advanced level',
                });
                // compute where to insert it
                const index = find_spacer(panel);
                panel.toolbar.insertItem(index, 'advancedLevel', button);
                return new _lumino_disposable__WEBPACK_IMPORTED_MODULE_2__.DisposableDelegate(() => {
                    button.dispose();
                });
            }
        }
        app.docRegistry.addWidgetExtension('Notebook', new AdvancedButton());
        class FrameButton {
            createNew(panel, context) {
                const button = new _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__.ToolbarButton({
                    className: 'courselevels-button',
                    iconClass: 'fas fa-crop-alt',
                    onClick: () => toggle_frame(),
                    tooltip: 'Toggle frame around cell',
                });
                // compute where to insert it
                const index = find_spacer(panel);
                panel.toolbar.insertItem(index, 'frameLevel', button);
                return new _lumino_disposable__WEBPACK_IMPORTED_MODULE_2__.DisposableDelegate(() => {
                    button.dispose();
                });
            }
        }
        app.docRegistry.addWidgetExtension('Notebook', new FrameButton());
    }
};
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (plugin);


/***/ })

}]);
//# sourceMappingURL=lib_index_js.b6cce1a6b02879b8e4f7.js.map