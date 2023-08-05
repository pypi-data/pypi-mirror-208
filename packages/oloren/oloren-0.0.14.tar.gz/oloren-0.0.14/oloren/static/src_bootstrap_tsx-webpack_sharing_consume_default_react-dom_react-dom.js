"use strict";
/*
 * ATTENTION: The "eval" devtool has been used (maybe by default in mode: "development").
 * This devtool is neither made for production nor for readable output files.
 * It uses "eval()" calls to create a separate source file in the browser devtools.
 * If you are trying to read the output file, select a different devtool (https://webpack.js.org/configuration/devtool/)
 * or disable the default devtool with "devtool: false".
 * If you are looking for production-ready output files, see mode: "production" (https://webpack.js.org/configuration/mode/).
 */
(self["webpackChunkfrontend"] = self["webpackChunkfrontend"] || []).push([["src_bootstrap_tsx-webpack_sharing_consume_default_react-dom_react-dom"],{

/***/ "./src/App.tsx":
/*!*********************!*\
  !*** ./src/App.tsx ***!
  \*********************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

eval("__webpack_require__.r(__webpack_exports__);\n/* harmony export */ __webpack_require__.d(__webpack_exports__, {\n/* harmony export */   \"Components\": () => (/* binding */ Components),\n/* harmony export */   \"default\": () => (/* binding */ App)\n/* harmony export */ });\n/* harmony import */ var styled_components__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! styled-components */ \"./node_modules/.pnpm/styled-components@5.3.10_7i5myeigehqah43i5u7wbekgba/node_modules/styled-components/dist/styled-components.browser.esm.js\");\n/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! react */ \"webpack/sharing/consume/default/react/react\");\n/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(react__WEBPACK_IMPORTED_MODULE_0__);\nObject(function webpackMissingModule() { var e = new Error(\"Cannot find module './nodes/PythonExecNode'\"); e.code = 'MODULE_NOT_FOUND'; throw e; }());\n/* harmony import */ var antd__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! antd */ \"./node_modules/.pnpm/antd@5.4.6_biqbaboplfbrettd7655fr4n2y/node_modules/antd/es/typography/index.js\");\n\n\n\n\n\nconst {\n  Title\n} = antd__WEBPACK_IMPORTED_MODULE_2__[\"default\"];\nfunction NodeTester({\n  Node\n}) {\n  const [node, setNode] = react__WEBPACK_IMPORTED_MODULE_0___default().useState({\n    id: \"node-1\",\n    data: {},\n    operator: \"\",\n    hierarchy: [],\n    num_inputs: 1,\n    num_outputs: 1,\n    remote: {\n      module: \"\",\n      url: \"\",\n      scope: \"\"\n    }\n  });\n  return /*#__PURE__*/react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_StyledDiv, null, /*#__PURE__*/react__WEBPACK_IMPORTED_MODULE_0___default().createElement(Title, null, Node.name), /*#__PURE__*/react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_StyledDiv2, null, /*#__PURE__*/react__WEBPACK_IMPORTED_MODULE_0___default().createElement(Node, {\n    node: node,\n    setNode: setNode\n  })), /*#__PURE__*/react__WEBPACK_IMPORTED_MODULE_0___default().createElement(\"pre\", null, /*#__PURE__*/react__WEBPACK_IMPORTED_MODULE_0___default().createElement(\"code\", null, JSON.stringify(node, null, 2))));\n}\nconst Components = [Object(function webpackMissingModule() { var e = new Error(\"Cannot find module './nodes/PythonExecNode'\"); e.code = 'MODULE_NOT_FOUND'; throw e; }())];\nfunction App() {\n  return Components.map((Node, i) => /*#__PURE__*/react__WEBPACK_IMPORTED_MODULE_0___default().createElement(NodeTester, {\n    key: i,\n    Node: Node\n  }));\n}\nvar _StyledDiv = (0,styled_components__WEBPACK_IMPORTED_MODULE_3__[\"default\"])(\"div\").withConfig({\n  displayName: \"App___StyledDiv\",\n  componentId: \"sc-12ae8gr-0\"\n})({\n  \"marginLeft\": \"auto\",\n  \"marginRight\": \"auto\",\n  \"display\": \"flex\",\n  \"width\": \"100%\",\n  \"maxWidth\": \"42rem\",\n  \"flexDirection\": \"column\"\n});\nvar _StyledDiv2 = (0,styled_components__WEBPACK_IMPORTED_MODULE_3__[\"default\"])(\"div\").withConfig({\n  displayName: \"App___StyledDiv2\",\n  componentId: \"sc-12ae8gr-1\"\n})({\n  \"width\": \"fit-content\",\n  \"borderWidth\": \"1px\",\n  \"borderStyle\": \"solid\",\n  \"--tw-border-opacity\": \"1\",\n  \"borderColor\": \"rgb(209 213 219 / var(--tw-border-opacity))\",\n  \"--tw-bg-opacity\": \"1\",\n  \"backgroundColor\": \"rgb(255 255 255 / var(--tw-bg-opacity))\",\n  \"padding\": \"0.5rem\"\n});\n\n//# sourceURL=webpack://frontend/./src/App.tsx?");

/***/ }),

/***/ "./src/bootstrap.tsx":
/*!***************************!*\
  !*** ./src/bootstrap.tsx ***!
  \***************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

eval("__webpack_require__.r(__webpack_exports__);\n/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! react */ \"webpack/sharing/consume/default/react/react\");\n/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(react__WEBPACK_IMPORTED_MODULE_0__);\n/* harmony import */ var react_dom_client__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! react-dom/client */ \"./node_modules/.pnpm/react-dom@18.2.0_react@18.2.0/node_modules/react-dom/client.js\");\n/* harmony import */ var _App__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ./App */ \"./src/App.tsx\");\n\n\n\nconst root = react_dom_client__WEBPACK_IMPORTED_MODULE_1__.createRoot(document.getElementById('root'));\nroot.render( /*#__PURE__*/react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_App__WEBPACK_IMPORTED_MODULE_2__[\"default\"], null));\n\n//# sourceURL=webpack://frontend/./src/bootstrap.tsx?");

/***/ })

}]);