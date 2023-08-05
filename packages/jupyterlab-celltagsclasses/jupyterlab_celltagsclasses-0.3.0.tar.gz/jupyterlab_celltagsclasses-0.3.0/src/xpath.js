"use strict";
/* eslint-disable no-case-declarations */
/* eslint-disable prettier/prettier */
Object.defineProperty(exports, "__esModule", { value: true });
exports.xpath_clean = exports.xpath_remove = exports.xpath_insert = exports.xpath_unset = exports.xpath_set = exports.xpath_get = exports.normalize = void 0;
// helpers to manage a JS object
//
// in this module we are only concerned about doing side effects
// in a JavaScript object
// what to do on the passed object
var Action;
(function (Action) {
    Action[Action["Get"] = 0] = "Get";
    Action[Action["Set"] = 1] = "Set";
    Action[Action["Unset"] = 2] = "Unset";
    Action[Action["Insert"] = 3] = "Insert";
    Action[Action["Remove"] = 4] = "Remove";
})(Action || (Action = {}));
var normalize = function (xpath) {
    if (typeof xpath === 'string') {
        var string = xpath;
        if (string.length === 0) {
            return [];
        }
        return string.split('.');
    }
    else if (xpath instanceof Array) {
        return xpath;
    }
    else {
        console.error("xpath must be string or array, got ".concat(xpath));
        return [];
    }
};
exports.normalize = normalize;
var _manage_metadata = function (data, // intended to be cell.metadata
action, xpath, value) {
    var Get = Action.Get, Set = Action.Set, Unset = Action.Unset, Insert = Action.Insert, Remove = Action.Remove;
    var recurse = function (scanner, action, xpath, value) {
        // console.log(`in recurse with xpath=${xpath}`)
        if (xpath.length === 0) {
            switch (action) {
                case Get:
                    return scanner;
                default:
                    return undefined;
            }
        }
        else if (xpath.length === 1) {
            var step = xpath[0];
            //
            switch (action) {
                case Get:
                    return scanner[step];
                case Set:
                    scanner[step] = value;
                    return value;
                case Unset:
                    if (step in scanner) {
                        delete scanner[step];
                        return true;
                    }
                    else {
                        return false;
                    }
                case Insert:
                    // create list if needed
                    if (!(step in scanner)) {
                        scanner[step] = [];
                    }
                    if (!(scanner[step] instanceof Array)) {
                        return undefined;
                    }
                    // insert if not already present
                    {
                        var list_1 = scanner[step];
                        if (list_1.indexOf(value) < 0) {
                            list_1.push(value);
                            return value;
                        }
                        else {
                            return undefined;
                        }
                    }
                case Remove:
                    if (!(scanner[step] instanceof Array)) {
                        return undefined;
                    }
                    var list = (scanner[step]);
                    // list.pop(value) is not accepted by ts ?!?
                    var index = list.indexOf(value);
                    if (index >= 0) {
                        list.splice(index, 1);
                    }
                    return value;
            }
        }
        else {
            var first = xpath[0], rest = xpath.slice(1);
            if (first in scanner) {
                if (!(scanner[first] instanceof Object)) {
                    return undefined;
                }
                else {
                    var next = scanner[first];
                    return recurse(next, action, rest, value);
                }
            }
            else {
                switch (action) {
                    case Get:
                        return undefined;
                    case Set:
                        scanner[first] = {};
                        var next = scanner[first];
                        return recurse(next, action, rest, value);
                    case Unset:
                        return undefined;
                    case Insert:
                        if (rest.length === 0) {
                            scanner[first] = [];
                            return recurse(scanner[first], action, rest, value);
                        }
                        else {
                            scanner[first] = {};
                            return recurse(scanner[first], action, rest, value);
                        }
                    case Remove:
                        return undefined;
                }
            }
        }
    };
    var xpath_list = (0, exports.normalize)(xpath);
    return recurse(data, action, xpath_list, value);
};
var _clean_metadata = function (data, xpath) {
    var not_empty = function (x) {
        if (x instanceof Array) {
            return x.length !== 0;
        }
        else if (x instanceof Object) {
            return Object.keys(x).length !== 0;
        }
        else if ((typeof x) === 'string') {
            return x.length !== 0;
        }
        else {
            return true;
        }
    };
    var clean_array = function (data) {
        return data.map(clean).filter(not_empty);
    };
    var clean_object = function (data) {
        var result = {};
        for (var key in data) {
            var value = data[key];
            var cleaned = clean(value);
            if (not_empty(cleaned)) {
                result[key] = cleaned;
            }
        }
        return result;
    };
    var clean = function (data) {
        if (data instanceof Array) {
            return clean_array(data);
        }
        else if (data instanceof Object) {
            return clean_object(data);
        }
        else {
            return data;
        }
    };
    var xpath_list = (0, exports.normalize)(xpath);
    if (xpath_list.length === 0) {
        return clean(data);
    }
    else {
        var start = (0, exports.xpath_get)(data, xpath_list);
        if (start === undefined) {
            // nothing serious here, just a debug message
            //console.debug(`DBG: xpath_clean: nothing to clean at ${xpath} - from ${xpath_list}`)
            return data;
        }
        else {
            return (0, exports.xpath_set)(data, xpath_list, clean(start));
        }
    }
};
var xpath_get = function (metadata, xpath) {
    return _manage_metadata(metadata, Action.Get, xpath, undefined);
};
exports.xpath_get = xpath_get;
var xpath_set = function (metadata, xpath, value) {
    return _manage_metadata(metadata, Action.Set, xpath, value);
};
exports.xpath_set = xpath_set;
var xpath_unset = function (metadata, xpath) {
    return _manage_metadata(metadata, Action.Unset, xpath, undefined);
};
exports.xpath_unset = xpath_unset;
var xpath_insert = function (metadata, xpath, key) {
    return _manage_metadata(metadata, Action.Insert, xpath, key);
};
exports.xpath_insert = xpath_insert;
var xpath_remove = function (metadata, xpath, key) {
    return _manage_metadata(metadata, Action.Remove, xpath, key);
};
exports.xpath_remove = xpath_remove;
var xpath_clean = function (metadata, xpath) {
    return _clean_metadata(metadata, xpath);
};
exports.xpath_clean = xpath_clean;
