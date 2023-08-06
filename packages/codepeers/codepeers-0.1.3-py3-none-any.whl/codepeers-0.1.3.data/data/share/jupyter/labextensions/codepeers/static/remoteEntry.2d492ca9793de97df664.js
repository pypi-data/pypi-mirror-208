var _JUPYTERLAB;
/******/ (() => { // webpackBootstrap
/******/ 	"use strict";
/******/ 	var __webpack_modules__ = ({

/***/ "webpack/container/entry/codepeers":
/*!***********************!*\
  !*** container entry ***!
  \***********************/
/***/ ((__unused_webpack_module, exports, __webpack_require__) => {

var moduleMap = {
	"./index": () => {
		return Promise.all([__webpack_require__.e("vendors-node_modules_css-loader_dist_runtime_api_js-node_modules_css-loader_dist_runtime_cssW-72eba1"), __webpack_require__.e("vendors-node_modules_clsx_dist_clsx_m_js-node_modules_stream-chat-react_dist_css_index_css"), __webpack_require__.e("webpack_sharing_consume_default_react"), __webpack_require__.e("lib_index_js")]).then(() => (() => ((__webpack_require__(/*! ./lib/index.js */ "./lib/index.js")))));
	},
	"./extension": () => {
		return Promise.all([__webpack_require__.e("vendors-node_modules_css-loader_dist_runtime_api_js-node_modules_css-loader_dist_runtime_cssW-72eba1"), __webpack_require__.e("vendors-node_modules_clsx_dist_clsx_m_js-node_modules_stream-chat-react_dist_css_index_css"), __webpack_require__.e("webpack_sharing_consume_default_react"), __webpack_require__.e("lib_index_js")]).then(() => (() => ((__webpack_require__(/*! ./lib/index.js */ "./lib/index.js")))));
	},
	"./style": () => {
		return Promise.all([__webpack_require__.e("vendors-node_modules_css-loader_dist_runtime_api_js-node_modules_css-loader_dist_runtime_cssW-72eba1"), __webpack_require__.e("style_index_js")]).then(() => (() => ((__webpack_require__(/*! ./style/index.js */ "./style/index.js")))));
	}
};
var get = (module, getScope) => {
	__webpack_require__.R = getScope;
	getScope = (
		__webpack_require__.o(moduleMap, module)
			? moduleMap[module]()
			: Promise.resolve().then(() => {
				throw new Error('Module "' + module + '" does not exist in container.');
			})
	);
	__webpack_require__.R = undefined;
	return getScope;
};
var init = (shareScope, initScope) => {
	if (!__webpack_require__.S) return;
	var name = "default"
	var oldScope = __webpack_require__.S[name];
	if(oldScope && oldScope !== shareScope) throw new Error("Container initialization failed as it has already been initialized with a different share scope");
	__webpack_require__.S[name] = shareScope;
	return __webpack_require__.I(name, initScope);
};

// This exports getters to disallow modifications
__webpack_require__.d(exports, {
	get: () => (get),
	init: () => (init)
});

/***/ })

/******/ 	});
/************************************************************************/
/******/ 	// The module cache
/******/ 	var __webpack_module_cache__ = {};
/******/ 	
/******/ 	// The require function
/******/ 	function __webpack_require__(moduleId) {
/******/ 		// Check if module is in cache
/******/ 		var cachedModule = __webpack_module_cache__[moduleId];
/******/ 		if (cachedModule !== undefined) {
/******/ 			return cachedModule.exports;
/******/ 		}
/******/ 		// Create a new module (and put it into the cache)
/******/ 		var module = __webpack_module_cache__[moduleId] = {
/******/ 			id: moduleId,
/******/ 			loaded: false,
/******/ 			exports: {}
/******/ 		};
/******/ 	
/******/ 		// Execute the module function
/******/ 		__webpack_modules__[moduleId].call(module.exports, module, module.exports, __webpack_require__);
/******/ 	
/******/ 		// Flag the module as loaded
/******/ 		module.loaded = true;
/******/ 	
/******/ 		// Return the exports of the module
/******/ 		return module.exports;
/******/ 	}
/******/ 	
/******/ 	// expose the modules object (__webpack_modules__)
/******/ 	__webpack_require__.m = __webpack_modules__;
/******/ 	
/******/ 	// expose the module cache
/******/ 	__webpack_require__.c = __webpack_module_cache__;
/******/ 	
/************************************************************************/
/******/ 	/* webpack/runtime/compat get default export */
/******/ 	(() => {
/******/ 		// getDefaultExport function for compatibility with non-harmony modules
/******/ 		__webpack_require__.n = (module) => {
/******/ 			var getter = module && module.__esModule ?
/******/ 				() => (module['default']) :
/******/ 				() => (module);
/******/ 			__webpack_require__.d(getter, { a: getter });
/******/ 			return getter;
/******/ 		};
/******/ 	})();
/******/ 	
/******/ 	/* webpack/runtime/create fake namespace object */
/******/ 	(() => {
/******/ 		var getProto = Object.getPrototypeOf ? (obj) => (Object.getPrototypeOf(obj)) : (obj) => (obj.__proto__);
/******/ 		var leafPrototypes;
/******/ 		// create a fake namespace object
/******/ 		// mode & 1: value is a module id, require it
/******/ 		// mode & 2: merge all properties of value into the ns
/******/ 		// mode & 4: return value when already ns object
/******/ 		// mode & 16: return value when it's Promise-like
/******/ 		// mode & 8|1: behave like require
/******/ 		__webpack_require__.t = function(value, mode) {
/******/ 			if(mode & 1) value = this(value);
/******/ 			if(mode & 8) return value;
/******/ 			if(typeof value === 'object' && value) {
/******/ 				if((mode & 4) && value.__esModule) return value;
/******/ 				if((mode & 16) && typeof value.then === 'function') return value;
/******/ 			}
/******/ 			var ns = Object.create(null);
/******/ 			__webpack_require__.r(ns);
/******/ 			var def = {};
/******/ 			leafPrototypes = leafPrototypes || [null, getProto({}), getProto([]), getProto(getProto)];
/******/ 			for(var current = mode & 2 && value; typeof current == 'object' && !~leafPrototypes.indexOf(current); current = getProto(current)) {
/******/ 				Object.getOwnPropertyNames(current).forEach((key) => (def[key] = () => (value[key])));
/******/ 			}
/******/ 			def['default'] = () => (value);
/******/ 			__webpack_require__.d(ns, def);
/******/ 			return ns;
/******/ 		};
/******/ 	})();
/******/ 	
/******/ 	/* webpack/runtime/define property getters */
/******/ 	(() => {
/******/ 		// define getter functions for harmony exports
/******/ 		__webpack_require__.d = (exports, definition) => {
/******/ 			for(var key in definition) {
/******/ 				if(__webpack_require__.o(definition, key) && !__webpack_require__.o(exports, key)) {
/******/ 					Object.defineProperty(exports, key, { enumerable: true, get: definition[key] });
/******/ 				}
/******/ 			}
/******/ 		};
/******/ 	})();
/******/ 	
/******/ 	/* webpack/runtime/ensure chunk */
/******/ 	(() => {
/******/ 		__webpack_require__.f = {};
/******/ 		// This file contains only the entry chunk.
/******/ 		// The chunk loading function for additional chunks
/******/ 		__webpack_require__.e = (chunkId) => {
/******/ 			return Promise.all(Object.keys(__webpack_require__.f).reduce((promises, key) => {
/******/ 				__webpack_require__.f[key](chunkId, promises);
/******/ 				return promises;
/******/ 			}, []));
/******/ 		};
/******/ 	})();
/******/ 	
/******/ 	/* webpack/runtime/get javascript chunk filename */
/******/ 	(() => {
/******/ 		// This function allow to reference async chunks
/******/ 		__webpack_require__.u = (chunkId) => {
/******/ 			// return url for filenames based on template
/******/ 			return "" + chunkId + "." + {"vendors-node_modules_css-loader_dist_runtime_api_js-node_modules_css-loader_dist_runtime_cssW-72eba1":"2da9652cea63f46ea142","vendors-node_modules_clsx_dist_clsx_m_js-node_modules_stream-chat-react_dist_css_index_css":"b7f7c0ad4ff2eecc7490","webpack_sharing_consume_default_react":"9163a100a76613afdde2","lib_index_js":"10def9c2bfc6f07981ec","style_index_js":"9f757aac102ef93a27f6","vendors-node_modules_emotion_serialize_dist_emotion-serialize_browser_esm_js-node_modules_emo-e86cc9":"bd81b38dcf89361a4a48","vendors-node_modules_emotion_cache_dist_emotion-cache_browser_esm_js":"c7f480962160df63711b","node_modules_emotion_css_dist_emotion-css_esm_js":"2729bee2f0df352465f4","vendors-node_modules_emotion_react_dist_emotion-react_browser_esm_js":"60f4620b0e3773ccca25","node_modules_babel_runtime_helpers_esm_extends_js-node_modules_emotion_use-insertion-effect-w-a0de1f0":"1cef6002dc3e07cd2358","vendors-node_modules_emotion_styled_dist_emotion-styled_browser_esm_js":"da61df9f29ff44f19145","webpack_sharing_consume_default_emotion_react_emotion_react-webpack_sharing_consume_default_e-169b09":"1dbae2672a2ac61d3b2b","vendors-node_modules_fortawesome_fontawesome-svg-core_index_mjs":"bb3b60c9397b069dc5b7","vendors-node_modules_fortawesome_free-regular-svg-icons_index_mjs":"d82321ee48885d54c671","vendors-node_modules_fortawesome_free-solid-svg-icons_index_mjs":"64d57007c17689c47a87","vendors-node_modules_prop-types_index_js":"4e0774a1364e36a5f803","vendors-node_modules_fortawesome_react-fontawesome_index_es_js":"a283212acdfad9e15893","webpack_sharing_consume_default_fortawesome_fontawesome-svg-core_fortawesome_fontawesome-svg-core":"0c899eb87dccea75bf0f","node_modules_hodlen_sse_ts_lib_index_js":"854e7a4fb8191a802ca0","vendors-node_modules_tslib_tslib_es6_js-node_modules_use-composed-ref_dist_use-composed-ref_e-fe27b0":"c3926740f3cf27dd2a54","vendors-node_modules_mantine_core_esm_index_js":"729377d2c7d237c7a355","webpack_sharing_consume_default_react-dom":"d3966f9f348e90db4f83","webpack_sharing_consume_default_emotion_react_emotion_react-webpack_sharing_consume_default_m-38c153":"f9c6c1037530c1fe3c28","node_modules_babel_runtime_helpers_esm_extends_js-node_modules_babel_runtime_helpers_esm_obje-98d5600":"a98da92d39cd97a649b1","vendors-node_modules_mantine_hooks_esm_index_js":"a352b7be4d1611190dcd","vendors-node_modules_mantine_notifications_esm_index_js":"7d35c51451663ee4e98a","webpack_sharing_consume_default_mantine_core_mantine_core-webpack_sharing_consume_default_man-9cadb8":"225fa73c73ee8f4894ae","vendors-node_modules_react-async_dist-web_index_js":"fc843ebdab58f404db99","vendors-node_modules_babel_runtime_helpers_esm_classCallCheck_js-node_modules_babel_runtime_h-966518":"4a931b98cd49240f52a3","vendors-node_modules_babel_runtime_helpers_esm_asyncToGenerator_js-node_modules_babel_runtime-a7b07c":"c2042eb0a548f0fd80a9","vendors-node_modules_react-code-blocks_dist_react-code-blocks_esm_js":"39a20135cab869a7488b","vendors-node_modules_stream-chat-react_dist_index_js":"35caee1f7adf1638c731","webpack_sharing_consume_default_stream-chat_stream-chat":"22c10a8fa36ce0e48ccb","node_modules_clsx_dist_clsx_m_js":"e6d5770594d0a2c279bb","vendors-node_modules_stream-chat_dist_browser_es_js":"68b3ecdd66bc79931c37","node_modules_babel_runtime_helpers_esm_arrayWithHoles_js-node_modules_babel_runtime_helpers_e-8366c0":"8eeeecb9ea24267db44b","node_modules_tiny-invariant_dist_esm_tiny-invariant_js":"2c54d0ac72d67359e068","vendors-node_modules_zod_lib_index_mjs":"d030257d4ade489995a5","node_modules_babel_runtime_helpers_esm_extends_js-node_modules_babel_runtime_helpers_esm_obje-98d5601":"d818e12b40eea3c99093","node_modules_babel_runtime_helpers_esm_extends_js-node_modules_emotion_use-insertion-effect-w-a0de1f1":"fd74d56559d38c62080c","node_modules_emotion_use-insertion-effect-with-fallbacks_dist_emotion-use-insertion-effect-wi-1033ad":"84b2533e6666a285fda7","react-syntax-highlighter/refractor-core-import":"82aec44c110d914781fc","react-syntax-highlighter_languages_refractor_abap":"d6ebfb7ad6270b528fce","react-syntax-highlighter_languages_refractor_actionscript":"d175720eeb30451acd42","react-syntax-highlighter_languages_refractor_ada":"935e779fd354806fb645","react-syntax-highlighter_languages_refractor_apacheconf":"8a1d07cd844bbbde351c","react-syntax-highlighter_languages_refractor_apl":"d215a5706da5c5bebfcf","react-syntax-highlighter_languages_refractor_applescript":"267d07de99d3d8162440","react-syntax-highlighter_languages_refractor_arduino":"d590297eaaca214c3ce2","react-syntax-highlighter_languages_refractor_arff":"fd25eeb7236429ef75fc","react-syntax-highlighter_languages_refractor_asciidoc":"bd3032280b357372ea63","react-syntax-highlighter_languages_refractor_asm6502":"344f6e8ec76af6c510e2","react-syntax-highlighter_languages_refractor_aspnet":"67c0cd063df9cbe8bcd7","react-syntax-highlighter_languages_refractor_autohotkey":"2df0bb6d94a6643519f2","react-syntax-highlighter_languages_refractor_autoit":"f4ec0af72e4ca40e089a","react-syntax-highlighter_languages_refractor_bash":"83f0295fc08428debc48","react-syntax-highlighter_languages_refractor_basic":"93b63bba184f9e8a4f5d","react-syntax-highlighter_languages_refractor_batch":"c8a8eab08776e3da3dde","react-syntax-highlighter_languages_refractor_bison":"fa4bd14474f8e9733fe0","react-syntax-highlighter_languages_refractor_brainfuck":"1b4288bcf7cfe8881b52","react-syntax-highlighter_languages_refractor_bro":"33c9f1f0bcd1964b52b6","react-syntax-highlighter_languages_refractor_c":"b48a6978658c5a8a639f","react-syntax-highlighter_languages_refractor_clike":"203ee215bdf9a3e06664","react-syntax-highlighter_languages_refractor_clojure":"de4d46fe806cd9a98d4d","react-syntax-highlighter_languages_refractor_coffeescript":"0b1486ea4cde04438dfb","react-syntax-highlighter_languages_refractor_cpp":"fa3ff41becddcb07ef6a","react-syntax-highlighter_languages_refractor_crystal":"fc49d9c2a05e31afd7fe","react-syntax-highlighter_languages_refractor_csharp":"3f0bbb9ce4db7e98f9bc","react-syntax-highlighter_languages_refractor_csp":"b9472ab90d26efe2b183","react-syntax-highlighter_languages_refractor_cssExtras":"50032c2e22551cf2b5e6","react-syntax-highlighter_languages_refractor_css":"7d1ef7b09ac616d21412","react-syntax-highlighter_languages_refractor_d":"511dc0d41b810ef1686e","react-syntax-highlighter_languages_refractor_dart":"2a1995df91568d2b652b","react-syntax-highlighter_languages_refractor_diff":"d433167a82b35677d70b","react-syntax-highlighter_languages_refractor_django":"3e2f42d4c4440960f834","react-syntax-highlighter_languages_refractor_docker":"373ec29e71b7682255e2","react-syntax-highlighter_languages_refractor_eiffel":"1dc433e15a4c789003e7","react-syntax-highlighter_languages_refractor_elixir":"a4025f2d47234cfdaaf1","react-syntax-highlighter_languages_refractor_elm":"e969b329e8ecf0706d53","react-syntax-highlighter_languages_refractor_erb":"3a4ac91638ea3faeed06","react-syntax-highlighter_languages_refractor_erlang":"6e281ec530f668de98fb","react-syntax-highlighter_languages_refractor_flow":"c476e9c62d22b0f9bcae","react-syntax-highlighter_languages_refractor_fortran":"8cbbfc03a9736354365b","react-syntax-highlighter_languages_refractor_fsharp":"2109b711f54eff2d273b","react-syntax-highlighter_languages_refractor_gedcom":"43c7c66637a46f6b532b","react-syntax-highlighter_languages_refractor_gherkin":"81980f7fab066452b3af","react-syntax-highlighter_languages_refractor_git":"8f14924a3e5af4711f61","react-syntax-highlighter_languages_refractor_glsl":"f461f0316dec50b7fd87","react-syntax-highlighter_languages_refractor_go":"d4ba4c630c762db87185","react-syntax-highlighter_languages_refractor_graphql":"486b928dc0d0473c2cee","react-syntax-highlighter_languages_refractor_groovy":"5e1d5b29552571d3ec87","react-syntax-highlighter_languages_refractor_haml":"0bffd0b50fbefc6f0039","react-syntax-highlighter_languages_refractor_handlebars":"9c95affc62dc60bcfc47","react-syntax-highlighter_languages_refractor_haskell":"31c1e6d830f81eab0b15","react-syntax-highlighter_languages_refractor_haxe":"47a976a4c9890024172c","react-syntax-highlighter_languages_refractor_hpkp":"ed780d6dc086298cd126","react-syntax-highlighter_languages_refractor_hsts":"1d962d61b8316ccb4f26","react-syntax-highlighter_languages_refractor_http":"f07f8c5099bd68c50f3b","react-syntax-highlighter_languages_refractor_ichigojam":"4e1b21e0bce527bb2975","react-syntax-highlighter_languages_refractor_icon":"e4c425cd4930f1ff6308","react-syntax-highlighter_languages_refractor_inform7":"fc1150b41e1198b1a190","react-syntax-highlighter_languages_refractor_ini":"ed2fe0f6080987fb515c","react-syntax-highlighter_languages_refractor_io":"3f832076aee3128c0b5c","react-syntax-highlighter_languages_refractor_j":"ff870f3c33e7a0da3706","react-syntax-highlighter_languages_refractor_java":"d95d23ef4a7113bdb877","react-syntax-highlighter_languages_refractor_javascript":"1297d6f4ac1f53d219a7","react-syntax-highlighter_languages_refractor_jolie":"98565235c18468a9f186","react-syntax-highlighter_languages_refractor_json":"a7abb8fa399e2f124e9d","react-syntax-highlighter_languages_refractor_jsx":"fc61640427079a8ef9ea","react-syntax-highlighter_languages_refractor_julia":"fdd2d6b5bbd0f94f6f76","react-syntax-highlighter_languages_refractor_keyman":"1a9d316af980f1d62768","react-syntax-highlighter_languages_refractor_kotlin":"08a4a52f620a98ff3535","react-syntax-highlighter_languages_refractor_latex":"3aa4429a1cc045111197","react-syntax-highlighter_languages_refractor_less":"02d5eb79e5dfa4be2843","react-syntax-highlighter_languages_refractor_liquid":"d327abf5ba1f34bdc3ec","react-syntax-highlighter_languages_refractor_lisp":"803de5837653f8cb49e7","react-syntax-highlighter_languages_refractor_livescript":"7ab67401cf5de8e0779f","react-syntax-highlighter_languages_refractor_lolcode":"1dbc2866d931343bfd2e","react-syntax-highlighter_languages_refractor_lua":"26306f2dcce1626e557b","react-syntax-highlighter_languages_refractor_makefile":"e2edd4e57d494d4e40f6","react-syntax-highlighter_languages_refractor_markdown":"868ce77524d3391d6ab0","react-syntax-highlighter_languages_refractor_markupTemplating":"4216eba112c01a27204f","react-syntax-highlighter_languages_refractor_markup":"2c7091e0922816a40d62","react-syntax-highlighter_languages_refractor_matlab":"92ad62907f35265a4083","react-syntax-highlighter_languages_refractor_mel":"e305e907025559e25d39","react-syntax-highlighter_languages_refractor_mizar":"496e9fb5e1205c9b767b","react-syntax-highlighter_languages_refractor_monkey":"c52321a28d3b86afe3d8","react-syntax-highlighter_languages_refractor_n4js":"39094b6579a0149182c0","react-syntax-highlighter_languages_refractor_nasm":"1d9f913310d1ed025b01","react-syntax-highlighter_languages_refractor_nginx":"5b9fb0388ebe0752e6be","react-syntax-highlighter_languages_refractor_nim":"afddba729afb2e34a7d0","react-syntax-highlighter_languages_refractor_nix":"64ae482d9b6437dd53ce","react-syntax-highlighter_languages_refractor_nsis":"4f57d144a7dc4850ab78","react-syntax-highlighter_languages_refractor_objectivec":"81a738d8a0cae2575656","react-syntax-highlighter_languages_refractor_ocaml":"7126dac736f3868f40c3","react-syntax-highlighter_languages_refractor_opencl":"0a8ae07f74c6ee99a70f","react-syntax-highlighter_languages_refractor_oz":"12fe7c96ccf6786493d0","react-syntax-highlighter_languages_refractor_parigp":"27ecf700cce0e129fcad","react-syntax-highlighter_languages_refractor_parser":"403ac6beb25758418cec","react-syntax-highlighter_languages_refractor_pascal":"dbf7ed251529e39cc7c8","react-syntax-highlighter_languages_refractor_perl":"2063d678f8db44f6811a","react-syntax-highlighter_languages_refractor_phpExtras":"d83107aab1c4f0a245a1","react-syntax-highlighter_languages_refractor_php":"ef3667fc57605b852b14","react-syntax-highlighter_languages_refractor_plsql":"9044676429a1634cc978","react-syntax-highlighter_languages_refractor_powershell":"f53eab229bdac3047bce","react-syntax-highlighter_languages_refractor_processing":"f7993c77179713541b4f","react-syntax-highlighter_languages_refractor_prolog":"66fe0043748b0b8e7c29","react-syntax-highlighter_languages_refractor_properties":"cf7f00537a4bb773452e","react-syntax-highlighter_languages_refractor_protobuf":"3904c2fa24c77f02c981","react-syntax-highlighter_languages_refractor_pug":"c79daee00b3c8492156f","react-syntax-highlighter_languages_refractor_puppet":"d10c088aacf4d8c02a6e","react-syntax-highlighter_languages_refractor_pure":"763ac4c8ef7a2ad660b8","react-syntax-highlighter_languages_refractor_python":"87bd31864133bd0e5bfb","react-syntax-highlighter_languages_refractor_q":"216c46aa8d8d9c020572","react-syntax-highlighter_languages_refractor_qore":"95e87dd9362afcda32b2","react-syntax-highlighter_languages_refractor_r":"aaeef90905a34bad6d08","react-syntax-highlighter_languages_refractor_reason":"1a698c8108dbe4b53e8f","react-syntax-highlighter_languages_refractor_renpy":"0fcec48012cae4ec15db","react-syntax-highlighter_languages_refractor_rest":"7079a00eda6c99879b0a","react-syntax-highlighter_languages_refractor_rip":"ba48274c5c0672afa263","react-syntax-highlighter_languages_refractor_roboconf":"984136139367a38fcf4a","react-syntax-highlighter_languages_refractor_ruby":"8b34b0b4f8eff2f25fbb","react-syntax-highlighter_languages_refractor_rust":"bc66c26110ca8770baec","react-syntax-highlighter_languages_refractor_sas":"c69d8c3446ceabbd8ad3","react-syntax-highlighter_languages_refractor_sass":"971b78f05123e3c4d513","react-syntax-highlighter_languages_refractor_scala":"404d30309a88e4d4c07b","react-syntax-highlighter_languages_refractor_scheme":"77483c70b1e0b297b6dc","react-syntax-highlighter_languages_refractor_scss":"83e86f19469bc0589c4b","react-syntax-highlighter_languages_refractor_smalltalk":"80b4493410f2cc5a228e","react-syntax-highlighter_languages_refractor_smarty":"495eab13e651c3adf20c","react-syntax-highlighter_languages_refractor_soy":"c56970b375ed98693987","react-syntax-highlighter_languages_refractor_sql":"13dbf1b37d1d1b8ce422","react-syntax-highlighter_languages_refractor_stylus":"ea8be369beb609b5512b","react-syntax-highlighter_languages_refractor_swift":"f2bd4184380b2c824e00","react-syntax-highlighter_languages_refractor_tap":"73febdd6065b0dc26b77","react-syntax-highlighter_languages_refractor_tcl":"7884af2fdfd74bc71ba6","react-syntax-highlighter_languages_refractor_textile":"e488eda2681fba663c92","react-syntax-highlighter_languages_refractor_tsx":"aa7decde9cab8890bc25","react-syntax-highlighter_languages_refractor_tt2":"cf4f01acaf81f261447c","react-syntax-highlighter_languages_refractor_twig":"71dd5e733bf328bdb725","react-syntax-highlighter_languages_refractor_typescript":"1ad4e39c8be58ac28b7c","react-syntax-highlighter_languages_refractor_vbnet":"589e1b3ec12c973ec456","react-syntax-highlighter_languages_refractor_velocity":"d5a11ef6961b77f1c9a1","react-syntax-highlighter_languages_refractor_verilog":"4dcf4c9fb9b4c31a998c","react-syntax-highlighter_languages_refractor_vhdl":"088af64065be728882e0","react-syntax-highlighter_languages_refractor_vim":"5e4fdbf4db959bf62793","react-syntax-highlighter_languages_refractor_visualBasic":"25b54c4b9d379ad89886","react-syntax-highlighter_languages_refractor_wasm":"7b241008f1d3bcc4495f","react-syntax-highlighter_languages_refractor_wiki":"6be58ffcd442afa8f3a2","react-syntax-highlighter_languages_refractor_xeora":"ecbf0cb8a9c4e142c5fe","react-syntax-highlighter_languages_refractor_xojo":"2435c4604b088dfbd1f6","react-syntax-highlighter_languages_refractor_xquery":"12aabf0b9d359ab0b4f7","react-syntax-highlighter_languages_refractor_yaml":"60f891ddd206dcf601de","vendors-node_modules_emoji-mart_dist_components_emoji_nimble-emoji_js":"64019b19c2bf26675e4a","node_modules_stream-chat-react_dist_context_DefaultEmoji_js":"b82cd1135c50b691ae47","vendors-node_modules_stream-chat-react_dist_context_DefaultEmojiPicker_js":"41ed3375b66789bd67e9","vendors-node_modules_stream-io_transliterate_dist_index_modern_js":"dd9cc680be82d7c609c6","vendors-node_modules_mml-react_dist_mml-react_esm_js":"02bbd3bf53d871d638bc"}[chunkId] + ".js";
/******/ 		};
/******/ 	})();
/******/ 	
/******/ 	/* webpack/runtime/global */
/******/ 	(() => {
/******/ 		__webpack_require__.g = (function() {
/******/ 			if (typeof globalThis === 'object') return globalThis;
/******/ 			try {
/******/ 				return this || new Function('return this')();
/******/ 			} catch (e) {
/******/ 				if (typeof window === 'object') return window;
/******/ 			}
/******/ 		})();
/******/ 	})();
/******/ 	
/******/ 	/* webpack/runtime/hasOwnProperty shorthand */
/******/ 	(() => {
/******/ 		__webpack_require__.o = (obj, prop) => (Object.prototype.hasOwnProperty.call(obj, prop))
/******/ 	})();
/******/ 	
/******/ 	/* webpack/runtime/load script */
/******/ 	(() => {
/******/ 		var inProgress = {};
/******/ 		var dataWebpackPrefix = "codepeers:";
/******/ 		// loadScript function to load a script via script tag
/******/ 		__webpack_require__.l = (url, done, key, chunkId) => {
/******/ 			if(inProgress[url]) { inProgress[url].push(done); return; }
/******/ 			var script, needAttach;
/******/ 			if(key !== undefined) {
/******/ 				var scripts = document.getElementsByTagName("script");
/******/ 				for(var i = 0; i < scripts.length; i++) {
/******/ 					var s = scripts[i];
/******/ 					if(s.getAttribute("src") == url || s.getAttribute("data-webpack") == dataWebpackPrefix + key) { script = s; break; }
/******/ 				}
/******/ 			}
/******/ 			if(!script) {
/******/ 				needAttach = true;
/******/ 				script = document.createElement('script');
/******/ 		
/******/ 				script.charset = 'utf-8';
/******/ 				script.timeout = 120;
/******/ 				if (__webpack_require__.nc) {
/******/ 					script.setAttribute("nonce", __webpack_require__.nc);
/******/ 				}
/******/ 				script.setAttribute("data-webpack", dataWebpackPrefix + key);
/******/ 				script.src = url;
/******/ 			}
/******/ 			inProgress[url] = [done];
/******/ 			var onScriptComplete = (prev, event) => {
/******/ 				// avoid mem leaks in IE.
/******/ 				script.onerror = script.onload = null;
/******/ 				clearTimeout(timeout);
/******/ 				var doneFns = inProgress[url];
/******/ 				delete inProgress[url];
/******/ 				script.parentNode && script.parentNode.removeChild(script);
/******/ 				doneFns && doneFns.forEach((fn) => (fn(event)));
/******/ 				if(prev) return prev(event);
/******/ 			}
/******/ 			var timeout = setTimeout(onScriptComplete.bind(null, undefined, { type: 'timeout', target: script }), 120000);
/******/ 			script.onerror = onScriptComplete.bind(null, script.onerror);
/******/ 			script.onload = onScriptComplete.bind(null, script.onload);
/******/ 			needAttach && document.head.appendChild(script);
/******/ 		};
/******/ 	})();
/******/ 	
/******/ 	/* webpack/runtime/make namespace object */
/******/ 	(() => {
/******/ 		// define __esModule on exports
/******/ 		__webpack_require__.r = (exports) => {
/******/ 			if(typeof Symbol !== 'undefined' && Symbol.toStringTag) {
/******/ 				Object.defineProperty(exports, Symbol.toStringTag, { value: 'Module' });
/******/ 			}
/******/ 			Object.defineProperty(exports, '__esModule', { value: true });
/******/ 		};
/******/ 	})();
/******/ 	
/******/ 	/* webpack/runtime/node module decorator */
/******/ 	(() => {
/******/ 		__webpack_require__.nmd = (module) => {
/******/ 			module.paths = [];
/******/ 			if (!module.children) module.children = [];
/******/ 			return module;
/******/ 		};
/******/ 	})();
/******/ 	
/******/ 	/* webpack/runtime/sharing */
/******/ 	(() => {
/******/ 		__webpack_require__.S = {};
/******/ 		var initPromises = {};
/******/ 		var initTokens = {};
/******/ 		__webpack_require__.I = (name, initScope) => {
/******/ 			if(!initScope) initScope = [];
/******/ 			// handling circular init calls
/******/ 			var initToken = initTokens[name];
/******/ 			if(!initToken) initToken = initTokens[name] = {};
/******/ 			if(initScope.indexOf(initToken) >= 0) return;
/******/ 			initScope.push(initToken);
/******/ 			// only runs once
/******/ 			if(initPromises[name]) return initPromises[name];
/******/ 			// creates a new share scope if needed
/******/ 			if(!__webpack_require__.o(__webpack_require__.S, name)) __webpack_require__.S[name] = {};
/******/ 			// runs all init snippets from all modules reachable
/******/ 			var scope = __webpack_require__.S[name];
/******/ 			var warn = (msg) => (typeof console !== "undefined" && console.warn && console.warn(msg));
/******/ 			var uniqueName = "codepeers";
/******/ 			var register = (name, version, factory, eager) => {
/******/ 				var versions = scope[name] = scope[name] || {};
/******/ 				var activeVersion = versions[version];
/******/ 				if(!activeVersion || (!activeVersion.loaded && (!eager != !activeVersion.eager ? eager : uniqueName > activeVersion.from))) versions[version] = { get: factory, from: uniqueName, eager: !!eager };
/******/ 			};
/******/ 			var initExternal = (id) => {
/******/ 				var handleError = (err) => (warn("Initialization of sharing external failed: " + err));
/******/ 				try {
/******/ 					var module = __webpack_require__(id);
/******/ 					if(!module) return;
/******/ 					var initFn = (module) => (module && module.init && module.init(__webpack_require__.S[name], initScope))
/******/ 					if(module.then) return promises.push(module.then(initFn, handleError));
/******/ 					var initResult = initFn(module);
/******/ 					if(initResult && initResult.then) return promises.push(initResult['catch'](handleError));
/******/ 				} catch(err) { handleError(err); }
/******/ 			}
/******/ 			var promises = [];
/******/ 			switch(name) {
/******/ 				case "default": {
/******/ 					register("@emotion/css", "11.10.6", () => (Promise.all([__webpack_require__.e("vendors-node_modules_emotion_serialize_dist_emotion-serialize_browser_esm_js-node_modules_emo-e86cc9"), __webpack_require__.e("vendors-node_modules_emotion_cache_dist_emotion-cache_browser_esm_js"), __webpack_require__.e("node_modules_emotion_css_dist_emotion-css_esm_js")]).then(() => (() => (__webpack_require__(/*! ./node_modules/@emotion/css/dist/emotion-css.esm.js */ "./node_modules/@emotion/css/dist/emotion-css.esm.js"))))));
/******/ 					register("@emotion/react", "11.10.6", () => (Promise.all([__webpack_require__.e("vendors-node_modules_emotion_serialize_dist_emotion-serialize_browser_esm_js-node_modules_emo-e86cc9"), __webpack_require__.e("vendors-node_modules_emotion_cache_dist_emotion-cache_browser_esm_js"), __webpack_require__.e("vendors-node_modules_emotion_react_dist_emotion-react_browser_esm_js"), __webpack_require__.e("webpack_sharing_consume_default_react"), __webpack_require__.e("node_modules_babel_runtime_helpers_esm_extends_js-node_modules_emotion_use-insertion-effect-w-a0de1f0")]).then(() => (() => (__webpack_require__(/*! ./node_modules/@emotion/react/dist/emotion-react.browser.esm.js */ "./node_modules/@emotion/react/dist/emotion-react.browser.esm.js"))))));
/******/ 					register("@emotion/styled", "11.10.8", () => (Promise.all([__webpack_require__.e("vendors-node_modules_emotion_serialize_dist_emotion-serialize_browser_esm_js-node_modules_emo-e86cc9"), __webpack_require__.e("vendors-node_modules_emotion_styled_dist_emotion-styled_browser_esm_js"), __webpack_require__.e("webpack_sharing_consume_default_react"), __webpack_require__.e("webpack_sharing_consume_default_emotion_react_emotion_react-webpack_sharing_consume_default_e-169b09")]).then(() => (() => (__webpack_require__(/*! ./node_modules/@emotion/styled/dist/emotion-styled.browser.esm.js */ "./node_modules/@emotion/styled/dist/emotion-styled.browser.esm.js"))))));
/******/ 					register("@fortawesome/fontawesome-svg-core", "6.3.0", () => (__webpack_require__.e("vendors-node_modules_fortawesome_fontawesome-svg-core_index_mjs").then(() => (() => (__webpack_require__(/*! ./node_modules/@fortawesome/fontawesome-svg-core/index.mjs */ "./node_modules/@fortawesome/fontawesome-svg-core/index.mjs"))))));
/******/ 					register("@fortawesome/free-regular-svg-icons", "6.3.0", () => (__webpack_require__.e("vendors-node_modules_fortawesome_free-regular-svg-icons_index_mjs").then(() => (() => (__webpack_require__(/*! ./node_modules/@fortawesome/free-regular-svg-icons/index.mjs */ "./node_modules/@fortawesome/free-regular-svg-icons/index.mjs"))))));
/******/ 					register("@fortawesome/free-solid-svg-icons", "6.3.0", () => (__webpack_require__.e("vendors-node_modules_fortawesome_free-solid-svg-icons_index_mjs").then(() => (() => (__webpack_require__(/*! ./node_modules/@fortawesome/free-solid-svg-icons/index.mjs */ "./node_modules/@fortawesome/free-solid-svg-icons/index.mjs"))))));
/******/ 					register("@fortawesome/react-fontawesome", "0.2.0", () => (Promise.all([__webpack_require__.e("vendors-node_modules_prop-types_index_js"), __webpack_require__.e("vendors-node_modules_fortawesome_react-fontawesome_index_es_js"), __webpack_require__.e("webpack_sharing_consume_default_react"), __webpack_require__.e("webpack_sharing_consume_default_fortawesome_fontawesome-svg-core_fortawesome_fontawesome-svg-core")]).then(() => (() => (__webpack_require__(/*! ./node_modules/@fortawesome/react-fontawesome/index.es.js */ "./node_modules/@fortawesome/react-fontawesome/index.es.js"))))));
/******/ 					register("@hodlen/sse.ts", "0.0.3", () => (__webpack_require__.e("node_modules_hodlen_sse_ts_lib_index_js").then(() => (() => (__webpack_require__(/*! ./node_modules/@hodlen/sse.ts/lib/index.js */ "./node_modules/@hodlen/sse.ts/lib/index.js"))))));
/******/ 					register("@mantine/core", "6.0.2", () => (Promise.all([__webpack_require__.e("vendors-node_modules_emotion_serialize_dist_emotion-serialize_browser_esm_js-node_modules_emo-e86cc9"), __webpack_require__.e("vendors-node_modules_emotion_cache_dist_emotion-cache_browser_esm_js"), __webpack_require__.e("vendors-node_modules_tslib_tslib_es6_js-node_modules_use-composed-ref_dist_use-composed-ref_e-fe27b0"), __webpack_require__.e("vendors-node_modules_mantine_core_esm_index_js"), __webpack_require__.e("webpack_sharing_consume_default_react"), __webpack_require__.e("webpack_sharing_consume_default_react-dom"), __webpack_require__.e("webpack_sharing_consume_default_emotion_react_emotion_react-webpack_sharing_consume_default_m-38c153"), __webpack_require__.e("node_modules_babel_runtime_helpers_esm_extends_js-node_modules_babel_runtime_helpers_esm_obje-98d5600")]).then(() => (() => (__webpack_require__(/*! ./node_modules/@mantine/core/esm/index.js */ "./node_modules/@mantine/core/esm/index.js"))))));
/******/ 					register("@mantine/hooks", "6.0.2", () => (Promise.all([__webpack_require__.e("vendors-node_modules_mantine_hooks_esm_index_js"), __webpack_require__.e("webpack_sharing_consume_default_react")]).then(() => (() => (__webpack_require__(/*! ./node_modules/@mantine/hooks/esm/index.js */ "./node_modules/@mantine/hooks/esm/index.js"))))));
/******/ 					register("@mantine/notifications", "6.0.7", () => (Promise.all([__webpack_require__.e("vendors-node_modules_prop-types_index_js"), __webpack_require__.e("vendors-node_modules_mantine_notifications_esm_index_js"), __webpack_require__.e("webpack_sharing_consume_default_react"), __webpack_require__.e("webpack_sharing_consume_default_react-dom"), __webpack_require__.e("webpack_sharing_consume_default_mantine_core_mantine_core-webpack_sharing_consume_default_man-9cadb8")]).then(() => (() => (__webpack_require__(/*! ./node_modules/@mantine/notifications/esm/index.js */ "./node_modules/@mantine/notifications/esm/index.js"))))));
/******/ 					register("codepeers", "0.1.2", () => (Promise.all([__webpack_require__.e("vendors-node_modules_css-loader_dist_runtime_api_js-node_modules_css-loader_dist_runtime_cssW-72eba1"), __webpack_require__.e("vendors-node_modules_clsx_dist_clsx_m_js-node_modules_stream-chat-react_dist_css_index_css"), __webpack_require__.e("webpack_sharing_consume_default_react"), __webpack_require__.e("lib_index_js")]).then(() => (() => (__webpack_require__(/*! ./lib/index.js */ "./lib/index.js"))))));
/******/ 					register("react-async", "10.0.1", () => (Promise.all([__webpack_require__.e("vendors-node_modules_prop-types_index_js"), __webpack_require__.e("vendors-node_modules_react-async_dist-web_index_js"), __webpack_require__.e("webpack_sharing_consume_default_react")]).then(() => (() => (__webpack_require__(/*! ./node_modules/react-async/dist-web/index.js */ "./node_modules/react-async/dist-web/index.js"))))));
/******/ 					register("react-code-blocks", "0.0.9-0", () => (Promise.all([__webpack_require__.e("vendors-node_modules_babel_runtime_helpers_esm_classCallCheck_js-node_modules_babel_runtime_h-966518"), __webpack_require__.e("vendors-node_modules_babel_runtime_helpers_esm_asyncToGenerator_js-node_modules_babel_runtime-a7b07c"), __webpack_require__.e("vendors-node_modules_react-code-blocks_dist_react-code-blocks_esm_js"), __webpack_require__.e("webpack_sharing_consume_default_react")]).then(() => (() => (__webpack_require__(/*! ./node_modules/react-code-blocks/dist/react-code-blocks.esm.js */ "./node_modules/react-code-blocks/dist/react-code-blocks.esm.js"))))));
/******/ 					register("stream-chat-react", "10.7.3", () => (Promise.all([__webpack_require__.e("vendors-node_modules_prop-types_index_js"), __webpack_require__.e("vendors-node_modules_tslib_tslib_es6_js-node_modules_use-composed-ref_dist_use-composed-ref_e-fe27b0"), __webpack_require__.e("vendors-node_modules_babel_runtime_helpers_esm_classCallCheck_js-node_modules_babel_runtime_h-966518"), __webpack_require__.e("vendors-node_modules_stream-chat-react_dist_index_js"), __webpack_require__.e("webpack_sharing_consume_default_react"), __webpack_require__.e("webpack_sharing_consume_default_react-dom"), __webpack_require__.e("webpack_sharing_consume_default_stream-chat_stream-chat"), __webpack_require__.e("node_modules_clsx_dist_clsx_m_js")]).then(() => (() => (__webpack_require__(/*! ./node_modules/stream-chat-react/dist/index.js */ "./node_modules/stream-chat-react/dist/index.js"))))));
/******/ 					register("stream-chat", "8.4.1", () => (Promise.all([__webpack_require__.e("vendors-node_modules_babel_runtime_helpers_esm_classCallCheck_js-node_modules_babel_runtime_h-966518"), __webpack_require__.e("vendors-node_modules_babel_runtime_helpers_esm_asyncToGenerator_js-node_modules_babel_runtime-a7b07c"), __webpack_require__.e("vendors-node_modules_stream-chat_dist_browser_es_js"), __webpack_require__.e("node_modules_babel_runtime_helpers_esm_arrayWithHoles_js-node_modules_babel_runtime_helpers_e-8366c0")]).then(() => (() => (__webpack_require__(/*! ./node_modules/stream-chat/dist/browser.es.js */ "./node_modules/stream-chat/dist/browser.es.js"))))));
/******/ 					register("tiny-invariant", "0", () => (__webpack_require__.e("node_modules_tiny-invariant_dist_esm_tiny-invariant_js").then(() => (() => (__webpack_require__(/*! ./node_modules/tiny-invariant/dist/esm/tiny-invariant.js */ "./node_modules/tiny-invariant/dist/esm/tiny-invariant.js"))))));
/******/ 					register("zod", "3.21.4", () => (__webpack_require__.e("vendors-node_modules_zod_lib_index_mjs").then(() => (() => (__webpack_require__(/*! ./node_modules/zod/lib/index.mjs */ "./node_modules/zod/lib/index.mjs"))))));
/******/ 				}
/******/ 				break;
/******/ 			}
/******/ 			if(!promises.length) return initPromises[name] = 1;
/******/ 			return initPromises[name] = Promise.all(promises).then(() => (initPromises[name] = 1));
/******/ 		};
/******/ 	})();
/******/ 	
/******/ 	/* webpack/runtime/publicPath */
/******/ 	(() => {
/******/ 		var scriptUrl;
/******/ 		if (__webpack_require__.g.importScripts) scriptUrl = __webpack_require__.g.location + "";
/******/ 		var document = __webpack_require__.g.document;
/******/ 		if (!scriptUrl && document) {
/******/ 			if (document.currentScript)
/******/ 				scriptUrl = document.currentScript.src;
/******/ 			if (!scriptUrl) {
/******/ 				var scripts = document.getElementsByTagName("script");
/******/ 				if(scripts.length) scriptUrl = scripts[scripts.length - 1].src
/******/ 			}
/******/ 		}
/******/ 		// When supporting browsers where an automatic publicPath is not supported you must specify an output.publicPath manually via configuration
/******/ 		// or pass an empty string ("") and set the __webpack_public_path__ variable from your code to use your own logic.
/******/ 		if (!scriptUrl) throw new Error("Automatic publicPath is not supported in this browser");
/******/ 		scriptUrl = scriptUrl.replace(/#.*$/, "").replace(/\?.*$/, "").replace(/\/[^\/]+$/, "/");
/******/ 		__webpack_require__.p = scriptUrl;
/******/ 	})();
/******/ 	
/******/ 	/* webpack/runtime/consumes */
/******/ 	(() => {
/******/ 		var parseVersion = (str) => {
/******/ 			// see webpack/lib/util/semver.js for original code
/******/ 			var p=p=>{return p.split(".").map((p=>{return+p==p?+p:p}))},n=/^([^-+]+)?(?:-([^+]+))?(?:\+(.+))?$/.exec(str),r=n[1]?p(n[1]):[];return n[2]&&(r.length++,r.push.apply(r,p(n[2]))),n[3]&&(r.push([]),r.push.apply(r,p(n[3]))),r;
/******/ 		}
/******/ 		var versionLt = (a, b) => {
/******/ 			// see webpack/lib/util/semver.js for original code
/******/ 			a=parseVersion(a),b=parseVersion(b);for(var r=0;;){if(r>=a.length)return r<b.length&&"u"!=(typeof b[r])[0];var e=a[r],n=(typeof e)[0];if(r>=b.length)return"u"==n;var t=b[r],f=(typeof t)[0];if(n!=f)return"o"==n&&"n"==f||("s"==f||"u"==n);if("o"!=n&&"u"!=n&&e!=t)return e<t;r++}
/******/ 		}
/******/ 		var rangeToString = (range) => {
/******/ 			// see webpack/lib/util/semver.js for original code
/******/ 			var r=range[0],n="";if(1===range.length)return"*";if(r+.5){n+=0==r?">=":-1==r?"<":1==r?"^":2==r?"~":r>0?"=":"!=";for(var e=1,a=1;a<range.length;a++){e--,n+="u"==(typeof(t=range[a]))[0]?"-":(e>0?".":"")+(e=2,t)}return n}var g=[];for(a=1;a<range.length;a++){var t=range[a];g.push(0===t?"not("+o()+")":1===t?"("+o()+" || "+o()+")":2===t?g.pop()+" "+g.pop():rangeToString(t))}return o();function o(){return g.pop().replace(/^\((.+)\)$/,"$1")}
/******/ 		}
/******/ 		var satisfy = (range, version) => {
/******/ 			// see webpack/lib/util/semver.js for original code
/******/ 			if(0 in range){version=parseVersion(version);var e=range[0],r=e<0;r&&(e=-e-1);for(var n=0,i=1,a=!0;;i++,n++){var f,s,g=i<range.length?(typeof range[i])[0]:"";if(n>=version.length||"o"==(s=(typeof(f=version[n]))[0]))return!a||("u"==g?i>e&&!r:""==g!=r);if("u"==s){if(!a||"u"!=g)return!1}else if(a)if(g==s)if(i<=e){if(f!=range[i])return!1}else{if(r?f>range[i]:f<range[i])return!1;f!=range[i]&&(a=!1)}else if("s"!=g&&"n"!=g){if(r||i<=e)return!1;a=!1,i--}else{if(i<=e||s<g!=r)return!1;a=!1}else"s"!=g&&"n"!=g&&(a=!1,i--)}}var t=[],o=t.pop.bind(t);for(n=1;n<range.length;n++){var u=range[n];t.push(1==u?o()|o():2==u?o()&o():u?satisfy(u,version):!o())}return!!o();
/******/ 		}
/******/ 		var ensureExistence = (scopeName, key) => {
/******/ 			var scope = __webpack_require__.S[scopeName];
/******/ 			if(!scope || !__webpack_require__.o(scope, key)) throw new Error("Shared module " + key + " doesn't exist in shared scope " + scopeName);
/******/ 			return scope;
/******/ 		};
/******/ 		var findVersion = (scope, key) => {
/******/ 			var versions = scope[key];
/******/ 			var key = Object.keys(versions).reduce((a, b) => {
/******/ 				return !a || versionLt(a, b) ? b : a;
/******/ 			}, 0);
/******/ 			return key && versions[key]
/******/ 		};
/******/ 		var findSingletonVersionKey = (scope, key) => {
/******/ 			var versions = scope[key];
/******/ 			return Object.keys(versions).reduce((a, b) => {
/******/ 				return !a || (!versions[a].loaded && versionLt(a, b)) ? b : a;
/******/ 			}, 0);
/******/ 		};
/******/ 		var getInvalidSingletonVersionMessage = (scope, key, version, requiredVersion) => {
/******/ 			return "Unsatisfied version " + version + " from " + (version && scope[key][version].from) + " of shared singleton module " + key + " (required " + rangeToString(requiredVersion) + ")"
/******/ 		};
/******/ 		var getSingleton = (scope, scopeName, key, requiredVersion) => {
/******/ 			var version = findSingletonVersionKey(scope, key);
/******/ 			return get(scope[key][version]);
/******/ 		};
/******/ 		var getSingletonVersion = (scope, scopeName, key, requiredVersion) => {
/******/ 			var version = findSingletonVersionKey(scope, key);
/******/ 			if (!satisfy(requiredVersion, version)) typeof console !== "undefined" && console.warn && console.warn(getInvalidSingletonVersionMessage(scope, key, version, requiredVersion));
/******/ 			return get(scope[key][version]);
/******/ 		};
/******/ 		var getStrictSingletonVersion = (scope, scopeName, key, requiredVersion) => {
/******/ 			var version = findSingletonVersionKey(scope, key);
/******/ 			if (!satisfy(requiredVersion, version)) throw new Error(getInvalidSingletonVersionMessage(scope, key, version, requiredVersion));
/******/ 			return get(scope[key][version]);
/******/ 		};
/******/ 		var findValidVersion = (scope, key, requiredVersion) => {
/******/ 			var versions = scope[key];
/******/ 			var key = Object.keys(versions).reduce((a, b) => {
/******/ 				if (!satisfy(requiredVersion, b)) return a;
/******/ 				return !a || versionLt(a, b) ? b : a;
/******/ 			}, 0);
/******/ 			return key && versions[key]
/******/ 		};
/******/ 		var getInvalidVersionMessage = (scope, scopeName, key, requiredVersion) => {
/******/ 			var versions = scope[key];
/******/ 			return "No satisfying version (" + rangeToString(requiredVersion) + ") of shared module " + key + " found in shared scope " + scopeName + ".\n" +
/******/ 				"Available versions: " + Object.keys(versions).map((key) => {
/******/ 				return key + " from " + versions[key].from;
/******/ 			}).join(", ");
/******/ 		};
/******/ 		var getValidVersion = (scope, scopeName, key, requiredVersion) => {
/******/ 			var entry = findValidVersion(scope, key, requiredVersion);
/******/ 			if(entry) return get(entry);
/******/ 			throw new Error(getInvalidVersionMessage(scope, scopeName, key, requiredVersion));
/******/ 		};
/******/ 		var warnInvalidVersion = (scope, scopeName, key, requiredVersion) => {
/******/ 			typeof console !== "undefined" && console.warn && console.warn(getInvalidVersionMessage(scope, scopeName, key, requiredVersion));
/******/ 		};
/******/ 		var get = (entry) => {
/******/ 			entry.loaded = 1;
/******/ 			return entry.get()
/******/ 		};
/******/ 		var init = (fn) => (function(scopeName, a, b, c) {
/******/ 			var promise = __webpack_require__.I(scopeName);
/******/ 			if (promise && promise.then) return promise.then(fn.bind(fn, scopeName, __webpack_require__.S[scopeName], a, b, c));
/******/ 			return fn(scopeName, __webpack_require__.S[scopeName], a, b, c);
/******/ 		});
/******/ 		
/******/ 		var load = /*#__PURE__*/ init((scopeName, scope, key) => {
/******/ 			ensureExistence(scopeName, key);
/******/ 			return get(findVersion(scope, key));
/******/ 		});
/******/ 		var loadFallback = /*#__PURE__*/ init((scopeName, scope, key, fallback) => {
/******/ 			return scope && __webpack_require__.o(scope, key) ? get(findVersion(scope, key)) : fallback();
/******/ 		});
/******/ 		var loadVersionCheck = /*#__PURE__*/ init((scopeName, scope, key, version) => {
/******/ 			ensureExistence(scopeName, key);
/******/ 			return get(findValidVersion(scope, key, version) || warnInvalidVersion(scope, scopeName, key, version) || findVersion(scope, key));
/******/ 		});
/******/ 		var loadSingleton = /*#__PURE__*/ init((scopeName, scope, key) => {
/******/ 			ensureExistence(scopeName, key);
/******/ 			return getSingleton(scope, scopeName, key);
/******/ 		});
/******/ 		var loadSingletonVersionCheck = /*#__PURE__*/ init((scopeName, scope, key, version) => {
/******/ 			ensureExistence(scopeName, key);
/******/ 			return getSingletonVersion(scope, scopeName, key, version);
/******/ 		});
/******/ 		var loadStrictVersionCheck = /*#__PURE__*/ init((scopeName, scope, key, version) => {
/******/ 			ensureExistence(scopeName, key);
/******/ 			return getValidVersion(scope, scopeName, key, version);
/******/ 		});
/******/ 		var loadStrictSingletonVersionCheck = /*#__PURE__*/ init((scopeName, scope, key, version) => {
/******/ 			ensureExistence(scopeName, key);
/******/ 			return getStrictSingletonVersion(scope, scopeName, key, version);
/******/ 		});
/******/ 		var loadVersionCheckFallback = /*#__PURE__*/ init((scopeName, scope, key, version, fallback) => {
/******/ 			if(!scope || !__webpack_require__.o(scope, key)) return fallback();
/******/ 			return get(findValidVersion(scope, key, version) || warnInvalidVersion(scope, scopeName, key, version) || findVersion(scope, key));
/******/ 		});
/******/ 		var loadSingletonFallback = /*#__PURE__*/ init((scopeName, scope, key, fallback) => {
/******/ 			if(!scope || !__webpack_require__.o(scope, key)) return fallback();
/******/ 			return getSingleton(scope, scopeName, key);
/******/ 		});
/******/ 		var loadSingletonVersionCheckFallback = /*#__PURE__*/ init((scopeName, scope, key, version, fallback) => {
/******/ 			if(!scope || !__webpack_require__.o(scope, key)) return fallback();
/******/ 			return getSingletonVersion(scope, scopeName, key, version);
/******/ 		});
/******/ 		var loadStrictVersionCheckFallback = /*#__PURE__*/ init((scopeName, scope, key, version, fallback) => {
/******/ 			var entry = scope && __webpack_require__.o(scope, key) && findValidVersion(scope, key, version);
/******/ 			return entry ? get(entry) : fallback();
/******/ 		});
/******/ 		var loadStrictSingletonVersionCheckFallback = /*#__PURE__*/ init((scopeName, scope, key, version, fallback) => {
/******/ 			if(!scope || !__webpack_require__.o(scope, key)) return fallback();
/******/ 			return getStrictSingletonVersion(scope, scopeName, key, version);
/******/ 		});
/******/ 		var installedModules = {};
/******/ 		var moduleToHandlerMapping = {
/******/ 			"webpack/sharing/consume/default/react": () => (loadSingletonVersionCheck("default", "react", [1,17,0,1])),
/******/ 			"webpack/sharing/consume/default/@jupyterlab/apputils": () => (loadSingletonVersionCheck("default", "@jupyterlab/apputils", [1,3,6,1])),
/******/ 			"webpack/sharing/consume/default/@jupyterlab/cell-toolbar": () => (loadSingletonVersionCheck("default", "@jupyterlab/cell-toolbar", [1,3,6,1])),
/******/ 			"webpack/sharing/consume/default/@jupyterlab/notebook": () => (loadSingletonVersionCheck("default", "@jupyterlab/notebook", [1,3,6,1])),
/******/ 			"webpack/sharing/consume/default/@jupyterlab/settingregistry": () => (loadSingletonVersionCheck("default", "@jupyterlab/settingregistry", [1,3,6,1])),
/******/ 			"webpack/sharing/consume/default/@jupyterlab/translation": () => (loadSingletonVersionCheck("default", "@jupyterlab/translation", [1,3,6,1])),
/******/ 			"webpack/sharing/consume/default/stream-chat-react/stream-chat-react": () => (loadStrictVersionCheckFallback("default", "stream-chat-react", [1,10,7,3], () => (Promise.all([__webpack_require__.e("vendors-node_modules_prop-types_index_js"), __webpack_require__.e("vendors-node_modules_tslib_tslib_es6_js-node_modules_use-composed-ref_dist_use-composed-ref_e-fe27b0"), __webpack_require__.e("vendors-node_modules_babel_runtime_helpers_esm_classCallCheck_js-node_modules_babel_runtime_h-966518"), __webpack_require__.e("vendors-node_modules_stream-chat-react_dist_index_js"), __webpack_require__.e("webpack_sharing_consume_default_react-dom"), __webpack_require__.e("webpack_sharing_consume_default_stream-chat_stream-chat")]).then(() => (() => (__webpack_require__(/*! stream-chat-react */ "./node_modules/stream-chat-react/dist/index.js"))))))),
/******/ 			"webpack/sharing/consume/default/@emotion/css/@emotion/css": () => (loadStrictVersionCheckFallback("default", "@emotion/css", [1,11,10,6], () => (Promise.all([__webpack_require__.e("vendors-node_modules_emotion_serialize_dist_emotion-serialize_browser_esm_js-node_modules_emo-e86cc9"), __webpack_require__.e("vendors-node_modules_emotion_cache_dist_emotion-cache_browser_esm_js"), __webpack_require__.e("node_modules_emotion_css_dist_emotion-css_esm_js")]).then(() => (() => (__webpack_require__(/*! @emotion/css */ "./node_modules/@emotion/css/dist/emotion-css.esm.js"))))))),
/******/ 			"webpack/sharing/consume/default/stream-chat/stream-chat?e0f2": () => (loadStrictVersionCheckFallback("default", "stream-chat", [1,8,4,1], () => (Promise.all([__webpack_require__.e("vendors-node_modules_babel_runtime_helpers_esm_classCallCheck_js-node_modules_babel_runtime_h-966518"), __webpack_require__.e("vendors-node_modules_babel_runtime_helpers_esm_asyncToGenerator_js-node_modules_babel_runtime-a7b07c"), __webpack_require__.e("vendors-node_modules_stream-chat_dist_browser_es_js"), __webpack_require__.e("node_modules_babel_runtime_helpers_esm_arrayWithHoles_js-node_modules_babel_runtime_helpers_e-8366c0")]).then(() => (() => (__webpack_require__(/*! stream-chat */ "./node_modules/stream-chat/dist/browser.es.js"))))))),
/******/ 			"webpack/sharing/consume/default/@mantine/core/@mantine/core?2426": () => (loadStrictVersionCheckFallback("default", "@mantine/core", [1,6,0,1], () => (Promise.all([__webpack_require__.e("vendors-node_modules_emotion_serialize_dist_emotion-serialize_browser_esm_js-node_modules_emo-e86cc9"), __webpack_require__.e("vendors-node_modules_emotion_cache_dist_emotion-cache_browser_esm_js"), __webpack_require__.e("vendors-node_modules_tslib_tslib_es6_js-node_modules_use-composed-ref_dist_use-composed-ref_e-fe27b0"), __webpack_require__.e("vendors-node_modules_mantine_core_esm_index_js"), __webpack_require__.e("webpack_sharing_consume_default_react-dom"), __webpack_require__.e("webpack_sharing_consume_default_emotion_react_emotion_react-webpack_sharing_consume_default_m-38c153"), __webpack_require__.e("node_modules_babel_runtime_helpers_esm_extends_js-node_modules_babel_runtime_helpers_esm_obje-98d5601")]).then(() => (() => (__webpack_require__(/*! @mantine/core */ "./node_modules/@mantine/core/esm/index.js"))))))),
/******/ 			"webpack/sharing/consume/default/@mantine/notifications/@mantine/notifications": () => (loadStrictVersionCheckFallback("default", "@mantine/notifications", [1,6,0,7], () => (Promise.all([__webpack_require__.e("vendors-node_modules_prop-types_index_js"), __webpack_require__.e("vendors-node_modules_mantine_notifications_esm_index_js"), __webpack_require__.e("webpack_sharing_consume_default_react-dom"), __webpack_require__.e("webpack_sharing_consume_default_mantine_core_mantine_core-webpack_sharing_consume_default_man-9cadb8")]).then(() => (() => (__webpack_require__(/*! @mantine/notifications */ "./node_modules/@mantine/notifications/esm/index.js"))))))),
/******/ 			"webpack/sharing/consume/default/@emotion/react/@emotion/react?185d": () => (loadStrictVersionCheckFallback("default", "@emotion/react", [1,11,10,6], () => (Promise.all([__webpack_require__.e("vendors-node_modules_emotion_serialize_dist_emotion-serialize_browser_esm_js-node_modules_emo-e86cc9"), __webpack_require__.e("vendors-node_modules_emotion_cache_dist_emotion-cache_browser_esm_js"), __webpack_require__.e("vendors-node_modules_emotion_react_dist_emotion-react_browser_esm_js"), __webpack_require__.e("node_modules_babel_runtime_helpers_esm_extends_js-node_modules_emotion_use-insertion-effect-w-a0de1f1")]).then(() => (() => (__webpack_require__(/*! @emotion/react */ "./node_modules/@emotion/react/dist/emotion-react.browser.esm.js"))))))),
/******/ 			"webpack/sharing/consume/default/react-async/react-async": () => (loadStrictVersionCheckFallback("default", "react-async", [1,10,0,1], () => (Promise.all([__webpack_require__.e("vendors-node_modules_prop-types_index_js"), __webpack_require__.e("vendors-node_modules_react-async_dist-web_index_js")]).then(() => (() => (__webpack_require__(/*! react-async */ "./node_modules/react-async/dist-web/index.js"))))))),
/******/ 			"webpack/sharing/consume/default/tiny-invariant/tiny-invariant": () => (loadStrictVersionCheckFallback("default", "tiny-invariant", [1,1,3,1], () => (__webpack_require__.e("node_modules_tiny-invariant_dist_esm_tiny-invariant_js").then(() => (() => (__webpack_require__(/*! tiny-invariant */ "./node_modules/tiny-invariant/dist/esm/tiny-invariant.js"))))))),
/******/ 			"webpack/sharing/consume/default/@mantine/hooks/@mantine/hooks?7129": () => (loadStrictVersionCheckFallback("default", "@mantine/hooks", [1,6,0,1], () => (__webpack_require__.e("vendors-node_modules_mantine_hooks_esm_index_js").then(() => (() => (__webpack_require__(/*! @mantine/hooks */ "./node_modules/@mantine/hooks/esm/index.js"))))))),
/******/ 			"webpack/sharing/consume/default/zod/zod": () => (loadStrictVersionCheckFallback("default", "zod", [1,3,21,4], () => (__webpack_require__.e("vendors-node_modules_zod_lib_index_mjs").then(() => (() => (__webpack_require__(/*! zod */ "./node_modules/zod/lib/index.mjs"))))))),
/******/ 			"webpack/sharing/consume/default/@hodlen/sse.ts/@hodlen/sse.ts": () => (loadStrictVersionCheckFallback("default", "@hodlen/sse.ts", [3,0,0,3], () => (__webpack_require__.e("node_modules_hodlen_sse_ts_lib_index_js").then(() => (() => (__webpack_require__(/*! @hodlen/sse.ts */ "./node_modules/@hodlen/sse.ts/lib/index.js"))))))),
/******/ 			"webpack/sharing/consume/default/@emotion/styled/@emotion/styled": () => (loadStrictVersionCheckFallback("default", "@emotion/styled", [1,11,10,8], () => (Promise.all([__webpack_require__.e("vendors-node_modules_emotion_serialize_dist_emotion-serialize_browser_esm_js-node_modules_emo-e86cc9"), __webpack_require__.e("vendors-node_modules_emotion_styled_dist_emotion-styled_browser_esm_js"), __webpack_require__.e("webpack_sharing_consume_default_emotion_react_emotion_react-webpack_sharing_consume_default_e-169b09")]).then(() => (() => (__webpack_require__(/*! @emotion/styled */ "./node_modules/@emotion/styled/dist/emotion-styled.browser.esm.js"))))))),
/******/ 			"webpack/sharing/consume/default/@fortawesome/free-regular-svg-icons/@fortawesome/free-regular-svg-icons": () => (loadStrictVersionCheckFallback("default", "@fortawesome/free-regular-svg-icons", [1,6,3,0], () => (__webpack_require__.e("vendors-node_modules_fortawesome_free-regular-svg-icons_index_mjs").then(() => (() => (__webpack_require__(/*! @fortawesome/free-regular-svg-icons */ "./node_modules/@fortawesome/free-regular-svg-icons/index.mjs"))))))),
/******/ 			"webpack/sharing/consume/default/@fortawesome/free-solid-svg-icons/@fortawesome/free-solid-svg-icons": () => (loadStrictVersionCheckFallback("default", "@fortawesome/free-solid-svg-icons", [1,6,3,0], () => (__webpack_require__.e("vendors-node_modules_fortawesome_free-solid-svg-icons_index_mjs").then(() => (() => (__webpack_require__(/*! @fortawesome/free-solid-svg-icons */ "./node_modules/@fortawesome/free-solid-svg-icons/index.mjs"))))))),
/******/ 			"webpack/sharing/consume/default/@fortawesome/react-fontawesome/@fortawesome/react-fontawesome": () => (loadStrictVersionCheckFallback("default", "@fortawesome/react-fontawesome", [2,0,2,0], () => (Promise.all([__webpack_require__.e("vendors-node_modules_prop-types_index_js"), __webpack_require__.e("vendors-node_modules_fortawesome_react-fontawesome_index_es_js"), __webpack_require__.e("webpack_sharing_consume_default_fortawesome_fontawesome-svg-core_fortawesome_fontawesome-svg-core")]).then(() => (() => (__webpack_require__(/*! @fortawesome/react-fontawesome */ "./node_modules/@fortawesome/react-fontawesome/index.es.js"))))))),
/******/ 			"webpack/sharing/consume/default/react-code-blocks/react-code-blocks": () => (loadStrictVersionCheckFallback("default", "react-code-blocks", [3,0,0,9,,0], () => (Promise.all([__webpack_require__.e("vendors-node_modules_babel_runtime_helpers_esm_classCallCheck_js-node_modules_babel_runtime_h-966518"), __webpack_require__.e("vendors-node_modules_babel_runtime_helpers_esm_asyncToGenerator_js-node_modules_babel_runtime-a7b07c"), __webpack_require__.e("vendors-node_modules_react-code-blocks_dist_react-code-blocks_esm_js")]).then(() => (() => (__webpack_require__(/*! react-code-blocks */ "./node_modules/react-code-blocks/dist/react-code-blocks.esm.js"))))))),
/******/ 			"webpack/sharing/consume/default/@jupyterlab/ui-components": () => (loadSingletonVersionCheck("default", "@jupyterlab/ui-components", [1,3,6,1])),
/******/ 			"webpack/sharing/consume/default/@emotion/react/@emotion/react?8f22": () => (loadFallback("default", "@emotion/react", () => (Promise.all([__webpack_require__.e("vendors-node_modules_emotion_cache_dist_emotion-cache_browser_esm_js"), __webpack_require__.e("vendors-node_modules_emotion_react_dist_emotion-react_browser_esm_js")]).then(() => (() => (__webpack_require__(/*! @emotion/react */ "./node_modules/@emotion/react/dist/emotion-react.browser.esm.js"))))))),
/******/ 			"webpack/sharing/consume/default/@emotion/react/@emotion/react?1cec": () => (loadStrictVersionCheckFallback("default", "@emotion/react", [1,11,0,0,,"rc",0], () => (Promise.all([__webpack_require__.e("vendors-node_modules_emotion_cache_dist_emotion-cache_browser_esm_js"), __webpack_require__.e("vendors-node_modules_emotion_react_dist_emotion-react_browser_esm_js")]).then(() => (() => (__webpack_require__(/*! @emotion/react */ "./node_modules/@emotion/react/dist/emotion-react.browser.esm.js"))))))),
/******/ 			"webpack/sharing/consume/default/@fortawesome/fontawesome-svg-core/@fortawesome/fontawesome-svg-core": () => (loadStrictVersionCheckFallback("default", "@fortawesome/fontawesome-svg-core", [,[2,6],[2,1],1], () => (__webpack_require__.e("vendors-node_modules_fortawesome_fontawesome-svg-core_index_mjs").then(() => (() => (__webpack_require__(/*! @fortawesome/fontawesome-svg-core */ "./node_modules/@fortawesome/fontawesome-svg-core/index.mjs"))))))),
/******/ 			"webpack/sharing/consume/default/react-dom": () => (loadSingletonVersionCheck("default", "react-dom", [1,17,0,1])),
/******/ 			"webpack/sharing/consume/default/@emotion/react/@emotion/react?497c": () => (loadStrictVersionCheckFallback("default", "@emotion/react", [0,11,9,0], () => (Promise.all([__webpack_require__.e("vendors-node_modules_emotion_react_dist_emotion-react_browser_esm_js"), __webpack_require__.e("node_modules_emotion_use-insertion-effect-with-fallbacks_dist_emotion-use-insertion-effect-wi-1033ad")]).then(() => (() => (__webpack_require__(/*! @emotion/react */ "./node_modules/@emotion/react/dist/emotion-react.browser.esm.js"))))))),
/******/ 			"webpack/sharing/consume/default/@mantine/hooks/@mantine/hooks?8580": () => (loadStrictVersionCheckFallback("default", "@mantine/hooks", [4,6,0,2], () => (__webpack_require__.e("vendors-node_modules_mantine_hooks_esm_index_js").then(() => (() => (__webpack_require__(/*! @mantine/hooks */ "./node_modules/@mantine/hooks/esm/index.js"))))))),
/******/ 			"webpack/sharing/consume/default/@mantine/core/@mantine/core?d8d7": () => (loadStrictVersionCheckFallback("default", "@mantine/core", [4,6,0,7], () => (Promise.all([__webpack_require__.e("vendors-node_modules_emotion_serialize_dist_emotion-serialize_browser_esm_js-node_modules_emo-e86cc9"), __webpack_require__.e("vendors-node_modules_emotion_cache_dist_emotion-cache_browser_esm_js"), __webpack_require__.e("vendors-node_modules_tslib_tslib_es6_js-node_modules_use-composed-ref_dist_use-composed-ref_e-fe27b0"), __webpack_require__.e("vendors-node_modules_mantine_core_esm_index_js"), __webpack_require__.e("webpack_sharing_consume_default_emotion_react_emotion_react-webpack_sharing_consume_default_m-38c153")]).then(() => (() => (__webpack_require__(/*! @mantine/core */ "./node_modules/@mantine/core/esm/index.js"))))))),
/******/ 			"webpack/sharing/consume/default/@mantine/hooks/@mantine/hooks?1f61": () => (loadStrictVersionCheckFallback("default", "@mantine/hooks", [4,6,0,7], () => (__webpack_require__.e("vendors-node_modules_mantine_hooks_esm_index_js").then(() => (() => (__webpack_require__(/*! @mantine/hooks */ "./node_modules/@mantine/hooks/esm/index.js"))))))),
/******/ 			"webpack/sharing/consume/default/stream-chat/stream-chat?5b26": () => (loadStrictVersionCheckFallback("default", "stream-chat", [1,8,0,0], () => (Promise.all([__webpack_require__.e("vendors-node_modules_babel_runtime_helpers_esm_asyncToGenerator_js-node_modules_babel_runtime-a7b07c"), __webpack_require__.e("vendors-node_modules_stream-chat_dist_browser_es_js")]).then(() => (() => (__webpack_require__(/*! stream-chat */ "./node_modules/stream-chat/dist/browser.es.js")))))))
/******/ 		};
/******/ 		// no consumes in initial chunks
/******/ 		var chunkMapping = {
/******/ 			"webpack_sharing_consume_default_react": [
/******/ 				"webpack/sharing/consume/default/react"
/******/ 			],
/******/ 			"lib_index_js": [
/******/ 				"webpack/sharing/consume/default/@jupyterlab/apputils",
/******/ 				"webpack/sharing/consume/default/@jupyterlab/cell-toolbar",
/******/ 				"webpack/sharing/consume/default/@jupyterlab/notebook",
/******/ 				"webpack/sharing/consume/default/@jupyterlab/settingregistry",
/******/ 				"webpack/sharing/consume/default/@jupyterlab/translation",
/******/ 				"webpack/sharing/consume/default/stream-chat-react/stream-chat-react",
/******/ 				"webpack/sharing/consume/default/@emotion/css/@emotion/css",
/******/ 				"webpack/sharing/consume/default/stream-chat/stream-chat?e0f2",
/******/ 				"webpack/sharing/consume/default/@mantine/core/@mantine/core?2426",
/******/ 				"webpack/sharing/consume/default/@mantine/notifications/@mantine/notifications",
/******/ 				"webpack/sharing/consume/default/@emotion/react/@emotion/react?185d",
/******/ 				"webpack/sharing/consume/default/react-async/react-async",
/******/ 				"webpack/sharing/consume/default/tiny-invariant/tiny-invariant",
/******/ 				"webpack/sharing/consume/default/@mantine/hooks/@mantine/hooks?7129",
/******/ 				"webpack/sharing/consume/default/zod/zod",
/******/ 				"webpack/sharing/consume/default/@hodlen/sse.ts/@hodlen/sse.ts",
/******/ 				"webpack/sharing/consume/default/@emotion/styled/@emotion/styled",
/******/ 				"webpack/sharing/consume/default/@fortawesome/free-regular-svg-icons/@fortawesome/free-regular-svg-icons",
/******/ 				"webpack/sharing/consume/default/@fortawesome/free-solid-svg-icons/@fortawesome/free-solid-svg-icons",
/******/ 				"webpack/sharing/consume/default/@fortawesome/react-fontawesome/@fortawesome/react-fontawesome",
/******/ 				"webpack/sharing/consume/default/react-code-blocks/react-code-blocks",
/******/ 				"webpack/sharing/consume/default/@jupyterlab/ui-components"
/******/ 			],
/******/ 			"webpack_sharing_consume_default_emotion_react_emotion_react-webpack_sharing_consume_default_e-169b09": [
/******/ 				"webpack/sharing/consume/default/@emotion/react/@emotion/react?8f22",
/******/ 				"webpack/sharing/consume/default/@emotion/react/@emotion/react?1cec"
/******/ 			],
/******/ 			"webpack_sharing_consume_default_fortawesome_fontawesome-svg-core_fortawesome_fontawesome-svg-core": [
/******/ 				"webpack/sharing/consume/default/@fortawesome/fontawesome-svg-core/@fortawesome/fontawesome-svg-core"
/******/ 			],
/******/ 			"webpack_sharing_consume_default_react-dom": [
/******/ 				"webpack/sharing/consume/default/react-dom"
/******/ 			],
/******/ 			"webpack_sharing_consume_default_emotion_react_emotion_react-webpack_sharing_consume_default_m-38c153": [
/******/ 				"webpack/sharing/consume/default/@emotion/react/@emotion/react?497c",
/******/ 				"webpack/sharing/consume/default/@mantine/hooks/@mantine/hooks?8580"
/******/ 			],
/******/ 			"webpack_sharing_consume_default_mantine_core_mantine_core-webpack_sharing_consume_default_man-9cadb8": [
/******/ 				"webpack/sharing/consume/default/@mantine/core/@mantine/core?d8d7",
/******/ 				"webpack/sharing/consume/default/@mantine/hooks/@mantine/hooks?1f61"
/******/ 			],
/******/ 			"webpack_sharing_consume_default_stream-chat_stream-chat": [
/******/ 				"webpack/sharing/consume/default/stream-chat/stream-chat?5b26"
/******/ 			]
/******/ 		};
/******/ 		__webpack_require__.f.consumes = (chunkId, promises) => {
/******/ 			if(__webpack_require__.o(chunkMapping, chunkId)) {
/******/ 				chunkMapping[chunkId].forEach((id) => {
/******/ 					if(__webpack_require__.o(installedModules, id)) return promises.push(installedModules[id]);
/******/ 					var onFactory = (factory) => {
/******/ 						installedModules[id] = 0;
/******/ 						__webpack_require__.m[id] = (module) => {
/******/ 							delete __webpack_require__.c[id];
/******/ 							module.exports = factory();
/******/ 						}
/******/ 					};
/******/ 					var onError = (error) => {
/******/ 						delete installedModules[id];
/******/ 						__webpack_require__.m[id] = (module) => {
/******/ 							delete __webpack_require__.c[id];
/******/ 							throw error;
/******/ 						}
/******/ 					};
/******/ 					try {
/******/ 						var promise = moduleToHandlerMapping[id]();
/******/ 						if(promise.then) {
/******/ 							promises.push(installedModules[id] = promise.then(onFactory)['catch'](onError));
/******/ 						} else onFactory(promise);
/******/ 					} catch(e) { onError(e); }
/******/ 				});
/******/ 			}
/******/ 		}
/******/ 	})();
/******/ 	
/******/ 	/* webpack/runtime/jsonp chunk loading */
/******/ 	(() => {
/******/ 		// no baseURI
/******/ 		
/******/ 		// object to store loaded and loading chunks
/******/ 		// undefined = chunk not loaded, null = chunk preloaded/prefetched
/******/ 		// [resolve, reject, Promise] = chunk loading, 0 = chunk loaded
/******/ 		var installedChunks = {
/******/ 			"codepeers": 0
/******/ 		};
/******/ 		
/******/ 		__webpack_require__.f.j = (chunkId, promises) => {
/******/ 				// JSONP chunk loading for javascript
/******/ 				var installedChunkData = __webpack_require__.o(installedChunks, chunkId) ? installedChunks[chunkId] : undefined;
/******/ 				if(installedChunkData !== 0) { // 0 means "already installed".
/******/ 		
/******/ 					// a Promise means "currently loading".
/******/ 					if(installedChunkData) {
/******/ 						promises.push(installedChunkData[2]);
/******/ 					} else {
/******/ 						if(!/^webpack_sharing_consume_default_(emotion_react_emotion_react\-webpack_sharing_consume_default_(e\-169b09|m\-38c153)|react(|\-dom)|fortawesome_fontawesome\-svg\-core_fortawesome_fontawesome\-svg\-core|mantine_core_mantine_core\-webpack_sharing_consume_default_man\-9cadb8|stream\-chat_stream\-chat)$/.test(chunkId)) {
/******/ 							// setup Promise in chunk cache
/******/ 							var promise = new Promise((resolve, reject) => (installedChunkData = installedChunks[chunkId] = [resolve, reject]));
/******/ 							promises.push(installedChunkData[2] = promise);
/******/ 		
/******/ 							// start chunk loading
/******/ 							var url = __webpack_require__.p + __webpack_require__.u(chunkId);
/******/ 							// create error before stack unwound to get useful stacktrace later
/******/ 							var error = new Error();
/******/ 							var loadingEnded = (event) => {
/******/ 								if(__webpack_require__.o(installedChunks, chunkId)) {
/******/ 									installedChunkData = installedChunks[chunkId];
/******/ 									if(installedChunkData !== 0) installedChunks[chunkId] = undefined;
/******/ 									if(installedChunkData) {
/******/ 										var errorType = event && (event.type === 'load' ? 'missing' : event.type);
/******/ 										var realSrc = event && event.target && event.target.src;
/******/ 										error.message = 'Loading chunk ' + chunkId + ' failed.\n(' + errorType + ': ' + realSrc + ')';
/******/ 										error.name = 'ChunkLoadError';
/******/ 										error.type = errorType;
/******/ 										error.request = realSrc;
/******/ 										installedChunkData[1](error);
/******/ 									}
/******/ 								}
/******/ 							};
/******/ 							__webpack_require__.l(url, loadingEnded, "chunk-" + chunkId, chunkId);
/******/ 						} else installedChunks[chunkId] = 0;
/******/ 					}
/******/ 				}
/******/ 		};
/******/ 		
/******/ 		// no prefetching
/******/ 		
/******/ 		// no preloaded
/******/ 		
/******/ 		// no HMR
/******/ 		
/******/ 		// no HMR manifest
/******/ 		
/******/ 		// no on chunks loaded
/******/ 		
/******/ 		// install a JSONP callback for chunk loading
/******/ 		var webpackJsonpCallback = (parentChunkLoadingFunction, data) => {
/******/ 			var [chunkIds, moreModules, runtime] = data;
/******/ 			// add "moreModules" to the modules object,
/******/ 			// then flag all "chunkIds" as loaded and fire callback
/******/ 			var moduleId, chunkId, i = 0;
/******/ 			if(chunkIds.some((id) => (installedChunks[id] !== 0))) {
/******/ 				for(moduleId in moreModules) {
/******/ 					if(__webpack_require__.o(moreModules, moduleId)) {
/******/ 						__webpack_require__.m[moduleId] = moreModules[moduleId];
/******/ 					}
/******/ 				}
/******/ 				if(runtime) var result = runtime(__webpack_require__);
/******/ 			}
/******/ 			if(parentChunkLoadingFunction) parentChunkLoadingFunction(data);
/******/ 			for(;i < chunkIds.length; i++) {
/******/ 				chunkId = chunkIds[i];
/******/ 				if(__webpack_require__.o(installedChunks, chunkId) && installedChunks[chunkId]) {
/******/ 					installedChunks[chunkId][0]();
/******/ 				}
/******/ 				installedChunks[chunkId] = 0;
/******/ 			}
/******/ 		
/******/ 		}
/******/ 		
/******/ 		var chunkLoadingGlobal = self["webpackChunkcodepeers"] = self["webpackChunkcodepeers"] || [];
/******/ 		chunkLoadingGlobal.forEach(webpackJsonpCallback.bind(null, 0));
/******/ 		chunkLoadingGlobal.push = webpackJsonpCallback.bind(null, chunkLoadingGlobal.push.bind(chunkLoadingGlobal));
/******/ 	})();
/******/ 	
/******/ 	/* webpack/runtime/nonce */
/******/ 	(() => {
/******/ 		__webpack_require__.nc = undefined;
/******/ 	})();
/******/ 	
/************************************************************************/
/******/ 	
/******/ 	// module cache are used so entry inlining is disabled
/******/ 	// startup
/******/ 	// Load entry module and return exports
/******/ 	var __webpack_exports__ = __webpack_require__("webpack/container/entry/codepeers");
/******/ 	(_JUPYTERLAB = typeof _JUPYTERLAB === "undefined" ? {} : _JUPYTERLAB).codepeers = __webpack_exports__;
/******/ 	
/******/ })()
;
//# sourceMappingURL=remoteEntry.2d492ca9793de97df664.js.map