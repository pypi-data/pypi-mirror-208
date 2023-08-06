"use strict";
(() => {
var exports = {};
exports.id = 72;
exports.ids = [72,726];
exports.modules = {

/***/ 677282:
/***/ ((module) => {

module.exports = require("process");

/***/ }),

/***/ 630970:
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "Z": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var process__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(677282);
/* harmony import */ var process__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(process__WEBPACK_IMPORTED_MODULE_0__);

const localConfig = {
    apiUrl: `${process__WEBPACK_IMPORTED_MODULE_0__.env.KANGAS_BACKEND_PROTOCOL || "http"}://${process__WEBPACK_IMPORTED_MODULE_0__.env.KANGAS_BACKEND_HOST}:${process__WEBPACK_IMPORTED_MODULE_0__.env.KANGAS_BACKEND_PORT}/datagrid/`,
    rootUrl: `${process__WEBPACK_IMPORTED_MODULE_0__.env.KANGAS_FRONTEND_PROTOCOL || "http"}://${process__WEBPACK_IMPORTED_MODULE_0__.env.KANGAS_FRONTEND_HOST}:${process__WEBPACK_IMPORTED_MODULE_0__.env.PORT}${process__WEBPACK_IMPORTED_MODULE_0__.env.KANGAS_FRONTEND_ROOT || ""}/`,
    rootPath: `${process__WEBPACK_IMPORTED_MODULE_0__.env.KANGAS_FRONTEND_ROOT || ""}/`,
    defaultDecimalPrecision: 5,
    locale: "en-US",
    hideSelector: process__WEBPACK_IMPORTED_MODULE_0__.env.KANGAS_HIDE_SELECTOR === "1",
    cache: true,
    prefetch: false,
    debug: false,
    dynamic: false
};
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (localConfig);


/***/ }),

/***/ 345261:
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "Z": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
const formatQueryArgs = (obj)=>{
    return Object.entries(obj).filter(([key, value])=>typeof value !== "undefined" && value !== null).map(([key, value])=>{
        if (value !== null && typeof value === "object") {
            value = JSON.stringify(value);
        }
        return `${key}=${encodeURIComponent(`${value}`)}`;
    }).join("&");
};
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (formatQueryArgs);


/***/ }),

/***/ 553445:
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var _kangas_config__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(630970);
/* harmony import */ var _kangas_lib_formatQueryArgs__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(345261);


const handler = async (req, res)=>{
    const { endpoint , ...query } = req.query;
    const queryString = (0,_kangas_lib_formatQueryArgs__WEBPACK_IMPORTED_MODULE_1__/* ["default"] */ .Z)(query);
    const result = await fetch(`${_kangas_config__WEBPACK_IMPORTED_MODULE_0__/* ["default"].apiUrl */ .Z.apiUrl}histogram?${queryString}`, {
        next: {
            revalidate: 100000
        }
    });
    const json = await result.json();
    res.setHeader("Cache-Control", "max-age=604800");
    res.send(json);
};
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (handler);


/***/ })

};
;

// load runtime
var __webpack_require__ = require("../../webpack-api-runtime.js");
__webpack_require__.C(exports);
var __webpack_exec__ = (moduleId) => (__webpack_require__(__webpack_require__.s = moduleId))
var __webpack_exports__ = (__webpack_exec__(553445));
module.exports = __webpack_exports__;

})();