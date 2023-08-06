"use strict";
(() => {
var exports = {};
exports.id = 917;
exports.ids = [917];
exports.modules = {

/***/ 677282:
/***/ ((module) => {

module.exports = require("process");

/***/ }),

/***/ 12781:
/***/ ((module) => {

module.exports = require("stream");

/***/ }),

/***/ 571806:
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var stream__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(12781);
/* harmony import */ var stream__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(stream__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _kangas_config__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(630970);
/* harmony import */ var _kangas_lib_formatQueryArgs__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(345261);



const handler = async (req, res)=>{
    const queryString = (0,_kangas_lib_formatQueryArgs__WEBPACK_IMPORTED_MODULE_2__/* ["default"] */ .Z)(req.query);
    const result = await fetch(`${_kangas_config__WEBPACK_IMPORTED_MODULE_1__/* ["default"].apiUrl */ .Z.apiUrl}embeddings-as-pca?${queryString}`, {
        next: {
            revalidate: 10000
        }
    });
    if (!req.query.thumbnail) {
        const json = await result.json();
        res.send(json);
    } else {
        const image = await result.body;
        const passthrough = new stream__WEBPACK_IMPORTED_MODULE_0__.Stream.PassThrough();
        stream__WEBPACK_IMPORTED_MODULE_0___default().pipeline(image, passthrough, (err)=>err ? console.error(err) : null);
        res.setHeader("Cache-Control", "max-age=604800");
        passthrough.pipe(res);
    }
};
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (handler);


/***/ })

};
;

// load runtime
var __webpack_require__ = require("../../webpack-api-runtime.js");
__webpack_require__.C(exports);
var __webpack_exec__ = (moduleId) => (__webpack_require__(__webpack_require__.s = moduleId))
var __webpack_exports__ = __webpack_require__.X(0, [726], () => (__webpack_exec__(571806)));
module.exports = __webpack_exports__;

})();