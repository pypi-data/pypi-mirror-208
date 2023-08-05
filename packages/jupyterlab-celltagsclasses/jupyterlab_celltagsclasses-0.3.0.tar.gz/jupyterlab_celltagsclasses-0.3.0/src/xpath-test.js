"use strict";
/* eslint-disable prettier/prettier */
Object.defineProperty(exports, "__esModule", { value: true });
var xpath_1 = require("./xpath");
/* not guaranteed to work by side-effects only */
var md = {};
// uncomment to debug
var checkpoint = function (md, message) {
    // console.log('------', message, '\n', JSON.stringify(md))
    message;
};
console.assert((0, xpath_1.xpath_get)(md, 'simple') === undefined, '001');
console.assert((0, xpath_1.xpath_set)(md, 'simple', 1) === 1, '002');
console.assert((0, xpath_1.xpath_get)(md, 'simple') === 1, '003');
checkpoint(md, "should have 'simple' set to 1");
// first time OK
console.assert((0, xpath_1.xpath_unset)(md, 'simple') === true, '011');
// then KO
console.assert((0, xpath_1.xpath_unset)(md, 'simple') === false, '012');
console.assert((0, xpath_1.xpath_get)(md, 'simple') === undefined, '013');
console.assert((0, xpath_1.xpath_set)(md, 'simple', 1) === 1, '014');
checkpoint(md, 'same');
console.assert((0, xpath_1.xpath_get)(md, 'nested.under') === undefined, '021');
console.assert((0, xpath_1.xpath_set)(md, 'nested.under', 2) === 2, '022');
console.assert((0, xpath_1.xpath_get)(md, 'nested.under') === 2, '023');
console.assert((0, xpath_1.xpath_unset)(md, 'nested.under') === true, '024');
console.assert((0, xpath_1.xpath_get)(md, 'nested.under') === undefined, '025');
console.assert((0, xpath_1.xpath_unset)(md, 'nested.under') === false, '026');
console.assert(JSON.stringify((0, xpath_1.xpath_get)(md, 'nested')) === '{}', '027');
console.assert((0, xpath_1.xpath_set)(md, 'nested.under', 2) === 2, '028');
checkpoint(md, "should have 'nested.under' set to 2");
console.assert((0, xpath_1.xpath_get)(md, 'jupyter') === undefined, '031');
console.assert((0, xpath_1.xpath_get)(md, 'jupyter.source_hidden') === undefined, '032');
console.assert((0, xpath_1.xpath_get)(md, ['jupyter', 'source_hidden']) === undefined, '033');
console.assert((0, xpath_1.xpath_set)(md, 'jupyter.source_hidden', true) === true, '034');
console.assert((0, xpath_1.xpath_get)(md, ['jupyter', 'source_hidden']) === true, '035');
console.assert((0, xpath_1.xpath_get)(md, 'jupyter.source_hidden') === true, '036');
checkpoint(md, 'jupyter.source_hidden=true');
// cannot insert in pre-existing non-array
console.assert((0, xpath_1.xpath_insert)(md, 'jupyter', 'anything') === undefined, '041');
console.assert((0, xpath_1.xpath_insert)(md, 'jupyter.source_hidden', 'anything') === undefined, '042');
checkpoint(md, 'same');
console.assert((0, xpath_1.xpath_get)(md, 'tags.hide-input') === undefined, '051');
// first time ok
console.assert((0, xpath_1.xpath_insert)(md, 'tags', 'hide-input') === 'hide-input', '052');
// then ko
console.assert((0, xpath_1.xpath_insert)(md, 'tags', 'hide-input') === undefined, '053');
console.assert((0, xpath_1.xpath_insert)(md, 'tags', 'foo') === 'foo', '054');
var fetch = (0, xpath_1.xpath_get)(md, 'tags');
console.assert(fetch instanceof Array, '055');
console.assert(fetch.length === 2, '056');
checkpoint(md, 'with 2 tags hide-input and foo');
console.assert((0, xpath_1.xpath_remove)(md, 'tags', 'foo') === 'foo', '061');
fetch = (0, xpath_1.xpath_get)(md, 'tags');
console.assert(fetch instanceof Array, '062');
console.assert(fetch.length === 1, '063');
checkpoint(md, 'foo removed from the tags');
console.assert((0, xpath_1.xpath_get)(md, 'hide_input') === undefined, '071');
console.assert((0, xpath_1.xpath_set)(md, 'hide_input', true) === true, '072');
console.assert((0, xpath_1.xpath_set)(md, 'hide_input', false) === false, '072-bis');
console.assert((0, xpath_1.xpath_unset)(md, 'hide_input') === true, '073');
console.assert((0, xpath_1.xpath_get)(md, 'hide_input') === undefined, '074');
checkpoint(md, 'unchanged');
var xpaths = ['empty-list', 'nested.empty-list'];
for (var _i = 0, xpaths_1 = xpaths; _i < xpaths_1.length; _i++) {
    var xpath = xpaths_1[_i];
    console.assert((0, xpath_1.xpath_insert)(md, xpath, 'foo') === 'foo', '081');
    console.assert((0, xpath_1.xpath_insert)(md, xpath, 'bar') === 'bar', '082');
    console.assert((0, xpath_1.xpath_remove)(md, xpath, 'foo') === 'foo', '083');
    console.assert((0, xpath_1.xpath_remove)(md, xpath, 'bar') === 'bar', '084');
    md = (0, xpath_1.xpath_clean)(md, '');
    console.assert((0, xpath_1.xpath_get)(md, xpath) === undefined, '085');
    checkpoint(md, "unchanged after inserting/cleaning in ".concat(xpath));
}
////////////////////////////////////////
var md2 = {
    'cells': [],
    'metadata': {
        'kernelspec': {},
        'language_info': [],
    },
};
console.assert(JSON.stringify((0, xpath_1.xpath_clean)(md2, '')) === "{}", '091');
console.assert(JSON.stringify((0, xpath_1.xpath_clean)(md2, 'cells')) === "[]", '092');
console.assert(JSON.stringify((0, xpath_1.xpath_clean)(md2, 'metadata')) === "{}", '093');
console.assert(JSON.stringify((0, xpath_1.xpath_clean)(md2, 'metadata.kernelspec')) === '{"cells":[],"metadata":{}}', '094');
var md3 = {
    'empty-string': '',
    'metadata': {
        'kernelspec': {},
        'language_info': [],
        'empty-string': "",
    },
};
console.assert(JSON.stringify((0, xpath_1.xpath_clean)(md3, '')) === "{}", '101');
console.assert(JSON.stringify((0, xpath_1.xpath_clean)(md3, 'empty-string')) === '""', '102');
console.assert(JSON.stringify((0, xpath_1.xpath_clean)(md3, 'metadata')) === "{}", '103');
console.assert(JSON.stringify((0, xpath_1.xpath_clean)(md3, 'metadata.kernelspec')) === '{"empty-string":"","metadata":{}}', '104');
