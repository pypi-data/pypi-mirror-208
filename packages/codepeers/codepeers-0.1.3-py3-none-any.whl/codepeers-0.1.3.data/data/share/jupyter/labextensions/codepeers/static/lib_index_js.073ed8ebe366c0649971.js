"use strict";
(self["webpackChunkcodepeers"] = self["webpackChunkcodepeers"] || []).push([["lib_index_js"],{

/***/ "./lib/api/openai-chat.js":
/*!********************************!*\
  !*** ./lib/api/openai-chat.js ***!
  \********************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "fetchStreamingCompletion": () => (/* binding */ fetchStreamingCompletion)
/* harmony export */ });
/* harmony import */ var _hodlen_sse_ts__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @hodlen/sse.ts */ "webpack/sharing/consume/default/@hodlen/sse.ts/@hodlen/sse.ts");
/* harmony import */ var _hodlen_sse_ts__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_hodlen_sse_ts__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _constants__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ../constants */ "./lib/constants.js");
/* harmony import */ var _types__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ../types */ "./lib/types/index.js");



const fetchStreamingCompletion = (prompt, emitData) => new Promise((resolve, reject) => {
    {
        if (prompt.length === 0) {
            reject(Error('no prompt given'));
        }
        const url = 'https://api.openai.com/v1/chat/completions';
        const data = {
            model: 'gpt-3.5-turbo',
            messages: prompt,
            temperature: 0.75,
            top_p: 0.95,
            max_tokens: 1000,
            stream: true,
            n: 1
        };
        const source = new _hodlen_sse_ts__WEBPACK_IMPORTED_MODULE_0__.SSE(url, {
            headers: {
                'Content-Type': 'application/json',
                Authorization: `Bearer ${_constants__WEBPACK_IMPORTED_MODULE_1__.OPENAI_API_KEY}`
            },
            method: _hodlen_sse_ts__WEBPACK_IMPORTED_MODULE_0__.SSEOptionsMethod.POST,
            payload: JSON.stringify(data)
        });
        let _localResult = '';
        const appendResult = (text) => {
            _localResult += text;
            emitData(text);
        };
        const terminate = () => {
            source.close();
            resolve(_localResult);
        };
        source.addEventListener('message', e => {
            const dataEvent = e;
            const responses = parseApiResponse(dataEvent.data);
            responses.forEach(res => {
                if (res === null) {
                    terminate();
                    return;
                }
                const responseText = res.choices[0].delta.content;
                if (responseText) {
                    appendResult(responseText);
                }
            });
        });
        source.addEventListener('readystatechange', e => {
            const stateEvent = e;
            if (stateEvent.readyState >= 2) {
                terminate();
            }
        });
        source.stream();
    }
});
const parseApiResponse = (data) => {
    const result = data
        .split('\n\n')
        .filter(Boolean)
        .map(chunk => {
        const jsonString = chunk
            .split('\n')
            .map(line => line.replace(/^data: /, ''))
            .join('');
        if (jsonString === '[DONE]') {
            return null;
        }
        try {
            return _types__WEBPACK_IMPORTED_MODULE_2__.ChatCompletionResponseSchema.parse(JSON.parse(jsonString));
        }
        catch (e) {
            console.error('Error parsing response: ', e);
            return null;
        }
    });
    return result;
};


/***/ }),

/***/ "./lib/command.js":
/*!************************!*\
  !*** ./lib/command.js ***!
  \************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "makeAskHelpElement": () => (/* binding */ makeAskHelpElement),
/* harmony export */   "makeCodeReviewElement": () => (/* binding */ makeCodeReviewElement),
/* harmony export */   "makeTriggerFrameCommand": () => (/* binding */ makeTriggerFrameCommand)
/* harmony export */ });
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @jupyterlab/apputils */ "webpack/sharing/consume/default/@jupyterlab/apputils");
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! react */ "webpack/sharing/consume/default/react");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(react__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _constants__WEBPACK_IMPORTED_MODULE_6__ = __webpack_require__(/*! ./constants */ "./lib/constants.js");
/* harmony import */ var _types__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! ./types */ "./lib/types/index.js");
/* harmony import */ var _utils__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! ./utils */ "./lib/utils/index.js");
/* harmony import */ var _views_regular_chat__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ./views/regular-chat */ "./lib/views/regular-chat.js");
/* harmony import */ var _views_code_list__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! ./views/code-list */ "./lib/views/code-list.js");



// import { requestAPI } from './requests';




const makeTriggerFrameCommand = (label, getCurrentPanel, onCreateElement) => {
    let toggled = false;
    return {
        label,
        isEnabled: () => true,
        isVisible: () => true,
        isToggled: () => toggled,
        execute: args => {
            const currentPanel = getCurrentPanel(args);
            if (currentPanel === null) {
                return;
            }
            const innerElement = onCreateElement(currentPanel);
            if (innerElement === null) {
                return;
            }
            openModal(label, innerElement);
            toggled = !toggled;
        }
    };
};
const makeAskHelpElement = (panel) => {
    const activeCellMeta = parseAppMetadata(panel);
    if (!activeCellMeta) {
        alert('Current cell or notebook does not support Codepeers sharing');
        return null;
    }
    const frameElement = react__WEBPACK_IMPORTED_MODULE_1___default().createElement(_views_regular_chat__WEBPACK_IMPORTED_MODULE_2__.RegularChatView, {
        codeBlock: activeCellMeta,
        channelId: `chat-${activeCellMeta.topic_id}`
    });
    return frameElement;
};
const makeCodeReviewElement = (panel) => {
    var _a, _b;
    const activeCellMeta = parseAppMetadata(panel);
    if (!activeCellMeta) {
        alert('Current cell or notebook does not support Codepeers sharing');
        return null;
    }
    if (activeCellMeta.admin_view) {
        const regularElement = react__WEBPACK_IMPORTED_MODULE_1___default().createElement(_views_regular_chat__WEBPACK_IMPORTED_MODULE_2__.RegularChatView, {
            codeBlock: activeCellMeta,
            channelId: `review-${activeCellMeta.topic_id}`
        });
        return regularElement;
    }
    const cellCodeContent = (_b = (_a = panel.content.activeCell) === null || _a === void 0 ? void 0 : _a.editor.model.value.text) !== null && _b !== void 0 ? _b : '';
    const frameElement = react__WEBPACK_IMPORTED_MODULE_1___default().createElement(_views_code_list__WEBPACK_IMPORTED_MODULE_3__.PeerCodeView, {
        codeBlock: {
            ...activeCellMeta,
            submission_id: (0,_utils__WEBPACK_IMPORTED_MODULE_4__.uuidv4)(),
            code: cellCodeContent
        }
    });
    return frameElement;
};
const parseAppMetadata = (panel) => {
    var _a, _b;
    const notebookAppMeta = parseNotebookMeta(panel);
    if (!notebookAppMeta) {
        return undefined;
    }
    const activeCellMeta = (_b = (_a = panel.content.activeCell) === null || _a === void 0 ? void 0 : _a.model.metadata.toJSON()) !== null && _b !== void 0 ? _b : {};
    const maybeCellAppMeta = _types__WEBPACK_IMPORTED_MODULE_5__.CellAppMetadataSchema.safeParse(activeCellMeta[_constants__WEBPACK_IMPORTED_MODULE_6__.METADATA_APP_KEY]);
    if (!maybeCellAppMeta.success) {
        console.error('cell metadata violation', maybeCellAppMeta.error);
        return undefined;
    }
    return { ...notebookAppMeta, ...maybeCellAppMeta.data };
};
const parseNotebookMeta = (panel) => {
    var _a, _b;
    const notebookMeta = (_b = (_a = panel.model) === null || _a === void 0 ? void 0 : _a.metadata.toJSON()) !== null && _b !== void 0 ? _b : {};
    const maybeNotebookAppMeta = _types__WEBPACK_IMPORTED_MODULE_5__.NotebookAppMetadataSchema.safeParse(notebookMeta[_constants__WEBPACK_IMPORTED_MODULE_6__.METADATA_APP_KEY]);
    if (!maybeNotebookAppMeta.success) {
        console.error('notebook metadata violation: ', maybeNotebookAppMeta.error);
        return undefined;
    }
    return maybeNotebookAppMeta.data;
};
const openModal = (title, body) => {
    (0,_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__.showDialog)({
        title,
        body,
        host: document.body,
        buttons: [],
        hasClose: true,
        renderer: undefined // To define customized dialog structure
    });
};


/***/ }),

/***/ "./lib/components/app-container.js":
/*!*****************************************!*\
  !*** ./lib/components/app-container.js ***!
  \*****************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "FramedAppContainer": () => (/* binding */ FramedAppContainer)
/* harmony export */ });
/* harmony import */ var _mantine_core__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @mantine/core */ "webpack/sharing/consume/default/@mantine/core/@mantine/core?2426");
/* harmony import */ var _mantine_core__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_mantine_core__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _mantine_notifications__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @mantine/notifications */ "webpack/sharing/consume/default/@mantine/notifications/@mantine/notifications");
/* harmony import */ var _mantine_notifications__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_mantine_notifications__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! react */ "webpack/sharing/consume/default/react");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(react__WEBPACK_IMPORTED_MODULE_2__);
/* harmony import */ var _customized_chat_style_fix__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! ./customized-chat/style-fix */ "./lib/components/customized-chat/style-fix.js");




const FramedAppContainer = ({ children }) => (react__WEBPACK_IMPORTED_MODULE_2___default().createElement(_mantine_core__WEBPACK_IMPORTED_MODULE_0__.MantineProvider, { withGlobalStyles: true, withNormalizeCSS: true },
    react__WEBPACK_IMPORTED_MODULE_2___default().createElement(_customized_chat_style_fix__WEBPACK_IMPORTED_MODULE_3__.GloablChatStylePatch, null),
    react__WEBPACK_IMPORTED_MODULE_2___default().createElement(_customized_chat_style_fix__WEBPACK_IMPORTED_MODULE_3__.GlobalJupyterStylePatch, null),
    react__WEBPACK_IMPORTED_MODULE_2___default().createElement(_mantine_core__WEBPACK_IMPORTED_MODULE_0__.Container, { fluid: true, style: { minHeight: '40vh', minWidth: '50rem' } }, children),
    react__WEBPACK_IMPORTED_MODULE_2___default().createElement(_mantine_notifications__WEBPACK_IMPORTED_MODULE_1__.Notifications, { zIndex: 99999 })));


/***/ }),

/***/ "./lib/components/base.js":
/*!********************************!*\
  !*** ./lib/components/base.js ***!
  \********************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "ClearButton": () => (/* binding */ ClearButton)
/* harmony export */ });
/* harmony import */ var _emotion_styled__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @emotion/styled */ "webpack/sharing/consume/default/@emotion/styled/@emotion/styled");
/* harmony import */ var _emotion_styled__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_emotion_styled__WEBPACK_IMPORTED_MODULE_0__);

const ClearButton = (_emotion_styled__WEBPACK_IMPORTED_MODULE_0___default().button) `
  background-color: transparent;
  border: none;
`;


/***/ }),

/***/ "./lib/components/code-block.js":
/*!**************************************!*\
  !*** ./lib/components/code-block.js ***!
  \**************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "PyCodeBlock": () => (/* binding */ PyCodeBlock)
/* harmony export */ });
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! react */ "webpack/sharing/consume/default/react");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(react__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var react_code_blocks__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! react-code-blocks */ "webpack/sharing/consume/default/react-code-blocks/react-code-blocks");
/* harmony import */ var react_code_blocks__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(react_code_blocks__WEBPACK_IMPORTED_MODULE_1__);


const PyCodeBlock = ({ code, styles }) => {
    return (react__WEBPACK_IMPORTED_MODULE_0___default().createElement(react_code_blocks__WEBPACK_IMPORTED_MODULE_1__.CodeBlock, { language: "python", text: code, showLineNumbers: false, customStyle: {
            fontFamily: 'Menlo, Consolas, "DejaVu Sans Mono", monospace',
            fontWeight: 400,
            ...styles
        } }));
};


/***/ }),

/***/ "./lib/components/customized-chat/code-message.js":
/*!********************************************************!*\
  !*** ./lib/components/customized-chat/code-message.js ***!
  \********************************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "CodeMessage": () => (/* binding */ CodeMessage),
/* harmony export */   "ThreadMessage": () => (/* binding */ ThreadMessage)
/* harmony export */ });
/* harmony import */ var _emotion_styled__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @emotion/styled */ "webpack/sharing/consume/default/@emotion/styled/@emotion/styled");
/* harmony import */ var _emotion_styled__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_emotion_styled__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _fortawesome_free_regular_svg_icons__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @fortawesome/free-regular-svg-icons */ "webpack/sharing/consume/default/@fortawesome/free-regular-svg-icons/@fortawesome/free-regular-svg-icons");
/* harmony import */ var _fortawesome_free_regular_svg_icons__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_fortawesome_free_regular_svg_icons__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _fortawesome_free_solid_svg_icons__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! @fortawesome/free-solid-svg-icons */ "webpack/sharing/consume/default/@fortawesome/free-solid-svg-icons/@fortawesome/free-solid-svg-icons");
/* harmony import */ var _fortawesome_free_solid_svg_icons__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(_fortawesome_free_solid_svg_icons__WEBPACK_IMPORTED_MODULE_2__);
/* harmony import */ var _fortawesome_react_fontawesome__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! @fortawesome/react-fontawesome */ "webpack/sharing/consume/default/@fortawesome/react-fontawesome/@fortawesome/react-fontawesome");
/* harmony import */ var _fortawesome_react_fontawesome__WEBPACK_IMPORTED_MODULE_3___default = /*#__PURE__*/__webpack_require__.n(_fortawesome_react_fontawesome__WEBPACK_IMPORTED_MODULE_3__);
/* harmony import */ var _mantine_core__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! @mantine/core */ "webpack/sharing/consume/default/@mantine/core/@mantine/core?2426");
/* harmony import */ var _mantine_core__WEBPACK_IMPORTED_MODULE_4___default = /*#__PURE__*/__webpack_require__.n(_mantine_core__WEBPACK_IMPORTED_MODULE_4__);
/* harmony import */ var clsx__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! clsx */ "./node_modules/clsx/dist/clsx.m.js");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_6__ = __webpack_require__(/*! react */ "webpack/sharing/consume/default/react");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_6___default = /*#__PURE__*/__webpack_require__.n(react__WEBPACK_IMPORTED_MODULE_6__);
/* harmony import */ var stream_chat_react__WEBPACK_IMPORTED_MODULE_7__ = __webpack_require__(/*! stream-chat-react */ "webpack/sharing/consume/default/stream-chat-react/stream-chat-react");
/* harmony import */ var stream_chat_react__WEBPACK_IMPORTED_MODULE_7___default = /*#__PURE__*/__webpack_require__.n(stream_chat_react__WEBPACK_IMPORTED_MODULE_7__);
/* harmony import */ var _context_user_code__WEBPACK_IMPORTED_MODULE_9__ = __webpack_require__(/*! ../../context/user-code */ "./lib/context/user-code.js");
/* harmony import */ var _utils__WEBPACK_IMPORTED_MODULE_12__ = __webpack_require__(/*! ../../utils */ "./lib/utils/props.js");
/* harmony import */ var _code_block__WEBPACK_IMPORTED_MODULE_11__ = __webpack_require__(/*! ../code-block */ "./lib/components/code-block.js");
/* harmony import */ var _reactive_popover__WEBPACK_IMPORTED_MODULE_10__ = __webpack_require__(/*! ../reactive-popover */ "./lib/components/reactive-popover.js");
/* harmony import */ var _mantine_hooks__WEBPACK_IMPORTED_MODULE_8__ = __webpack_require__(/*! @mantine/hooks */ "webpack/sharing/consume/default/@mantine/hooks/@mantine/hooks?7129");
/* harmony import */ var _mantine_hooks__WEBPACK_IMPORTED_MODULE_8___default = /*#__PURE__*/__webpack_require__.n(_mantine_hooks__WEBPACK_IMPORTED_MODULE_8__);













const CodeMessageWithCongtext = (props) => {
    var _a, _b, _c, _d, _e, _f, _g, _h, _j, _k, _l;
    const { handleReaction, handleOpenThread, handleRetry, initialMessage, message, messageWrapperRef, onMentionsClickMessage, onMentionsHoverMessage, onUserClick, onUserHover, threadList } = props;
    const { client } = (0,stream_chat_react__WEBPACK_IMPORTED_MODULE_7__.useChatContext)('MessageTeam');
    const { user_id: codeUserId } = (0,_context_user_code__WEBPACK_IMPORTED_MODULE_9__.useUserCodeContext)();
    const [viewdReplyCounts, setViewdReplyCounts] = (0,_mantine_hooks__WEBPACK_IMPORTED_MODULE_8__.useLocalStorage)({
        key: 'viewdReplyCounts',
        defaultValue: {},
        getInitialValueInEffect: false,
        deserialize: JSON.parse
    });
    const hasReacted = (reactionType) => { var _a, _b; return (_b = (_a = message.own_reactions) === null || _a === void 0 ? void 0 : _a.some(reaction => reaction.user &&
        reaction.type === reactionType &&
        client.userID === reaction.user.id)) !== null && _b !== void 0 ? _b : false; };
    const isMessageLiked = hasReacted('like');
    const replyCount = (_a = message.reply_count) !== null && _a !== void 0 ? _a : 0;
    const likeCount = (_c = (_b = message.reaction_counts) === null || _b === void 0 ? void 0 : _b.like) !== null && _c !== void 0 ? _c : 0;
    const isMyMessage = ((_d = message.codeMetadata) === null || _d === void 0 ? void 0 : _d.user_id) === codeUserId;
    const myLastReplyCount = isMyMessage
        ? (_e = viewdReplyCounts[message.id]) !== null && _e !== void 0 ? _e : 0 : undefined;
    const shouldNotifyReply = isMyMessage && replyCount !== myLastReplyCount;
    // Update the last reply count when the message is unmounted
    (0,react__WEBPACK_IMPORTED_MODULE_6__.useEffect)(() => {
        return () => {
            if (shouldNotifyReply) {
                setViewdReplyCounts(counts => ({
                    ...counts,
                    [message.id]: replyCount
                }));
            }
        };
    }, [isMyMessage, myLastReplyCount, replyCount]);
    if (message.deleted_at || !message.codeMetadata) {
        return null;
    }
    return (react__WEBPACK_IMPORTED_MODULE_6___default().createElement("div", { className: (0,clsx__WEBPACK_IMPORTED_MODULE_5__["default"])('str-chat__message', 'str-chat__message-team', 'str-chat__message-team--single', {
            'pinned-message': message.pinned,
            [`str-chat__message-team--${message.status}`]: message.status,
            [`str-chat__message-team--${message.type}`]: message.type,
            'str-chat__message--has-attachment': !!((_f = message.attachments) === null || _f === void 0 ? void 0 : _f.length),
            threadList: threadList
        }), ref: messageWrapperRef, style: { padding: '5px 10px' } },
        react__WEBPACK_IMPORTED_MODULE_6___default().createElement("div", { className: "str-chat__message-team-group" },
            react__WEBPACK_IMPORTED_MODULE_6___default().createElement(_mantine_core__WEBPACK_IMPORTED_MODULE_4__.Flex, { direction: isMyMessage ? 'row-reverse' : 'row', align: "center", justify: isMyMessage ? 'right' : 'left', mb: "xs" },
                react__WEBPACK_IMPORTED_MODULE_6___default().createElement(stream_chat_react__WEBPACK_IMPORTED_MODULE_7__.Avatar, { image: (_g = message.user) === null || _g === void 0 ? void 0 : _g.image, name: ((_h = message.user) === null || _h === void 0 ? void 0 : _h.name) || ((_j = message.user) === null || _j === void 0 ? void 0 : _j.id), onClick: onUserClick, onMouseOver: onUserHover, size: 34 }),
                react__WEBPACK_IMPORTED_MODULE_6___default().createElement("div", { className: "str-chat__message-team-meta" },
                    react__WEBPACK_IMPORTED_MODULE_6___default().createElement("div", { className: "str-chat__message-team-author", onClick: onUserClick },
                        react__WEBPACK_IMPORTED_MODULE_6___default().createElement(_mantine_core__WEBPACK_IMPORTED_MODULE_4__.Text, { weight: "bold" },
                            ((_k = message.user) === null || _k === void 0 ? void 0 : _k.name) || ((_l = message.user) === null || _l === void 0 ? void 0 : _l.id),
                            isMyMessage && ' (You)'),
                        message.type === 'error' && (react__WEBPACK_IMPORTED_MODULE_6___default().createElement("div", { className: "str-chat__message-team-error-header" }, 'Only visible to you'))),
                    react__WEBPACK_IMPORTED_MODULE_6___default().createElement("div", { style: { lineHeight: 1 } },
                        react__WEBPACK_IMPORTED_MODULE_6___default().createElement(stream_chat_react__WEBPACK_IMPORTED_MODULE_7__.MessageTimestamp, null)))),
            react__WEBPACK_IMPORTED_MODULE_6___default().createElement("div", null,
                message.quoted_message && react__WEBPACK_IMPORTED_MODULE_6___default().createElement(stream_chat_react__WEBPACK_IMPORTED_MODULE_7__.QuotedMessage, null),
                message.text && (react__WEBPACK_IMPORTED_MODULE_6___default().createElement("div", { className: (0,clsx__WEBPACK_IMPORTED_MODULE_5__["default"])('str-chat__message-team-text', {
                        'str-chat__message-team-text--is-emoji': (0,stream_chat_react__WEBPACK_IMPORTED_MODULE_7__.isOnlyEmojis)(message.text)
                    }), onClick: onMentionsClickMessage, onMouseOver: onMentionsHoverMessage, style: { position: 'relative' } },
                    !initialMessage && isMessageReactionEnabled(message) && (react__WEBPACK_IMPORTED_MODULE_6___default().createElement(ReactionGroup, { gap: "md" },
                        react__WEBPACK_IMPORTED_MODULE_6___default().createElement("span", { onClick: e => {
                                navigator.clipboard
                                    .writeText(message.text)
                                    .then(async () => {
                                    if (!hasReacted('love')) {
                                        return handleReaction('love', e);
                                    }
                                });
                            }, title: "Copy Code" },
                            react__WEBPACK_IMPORTED_MODULE_6___default().createElement(_reactive_popover__WEBPACK_IMPORTED_MODULE_10__.ReactivePopover, { popoverText: "Copied!", popoverTimeout: 1000 },
                                react__WEBPACK_IMPORTED_MODULE_6___default().createElement(ReactionIcon, { icon: _fortawesome_free_regular_svg_icons__WEBPACK_IMPORTED_MODULE_1__.faCopy }))),
                        react__WEBPACK_IMPORTED_MODULE_6___default().createElement("span", { onClick: e => handleReaction('like', e), title: isMessageLiked ? 'Unlike' : 'Like' },
                            react__WEBPACK_IMPORTED_MODULE_6___default().createElement(ReactionIcon, { icon: isMessageLiked ? _fortawesome_free_solid_svg_icons__WEBPACK_IMPORTED_MODULE_2__.faThumbsUp : _fortawesome_free_regular_svg_icons__WEBPACK_IMPORTED_MODULE_1__.faThumbsUp }),
                            likeCount > 0 && (react__WEBPACK_IMPORTED_MODULE_6___default().createElement(ReactionAuxText, null, likeCount))),
                        react__WEBPACK_IMPORTED_MODULE_6___default().createElement("span", { onClick: handleOpenThread, title: replyCount > 0
                                ? 'Show Replies' +
                                    (shouldNotifyReply
                                        ? `(${message.reply_count - myLastReplyCount} new replies)`
                                        : '')
                                : 'Start a Thread' },
                            react__WEBPACK_IMPORTED_MODULE_6___default().createElement(ReactionIcon, { icon: replyCount > 0 ? _fortawesome_free_solid_svg_icons__WEBPACK_IMPORTED_MODULE_2__.faComments : _fortawesome_free_regular_svg_icons__WEBPACK_IMPORTED_MODULE_1__.faComments }),
                            replyCount > 0 && (react__WEBPACK_IMPORTED_MODULE_6___default().createElement(ReactionAuxText, null, replyCount)),
                            shouldNotifyReply && (react__WEBPACK_IMPORTED_MODULE_6___default().createElement(_fortawesome_react_fontawesome__WEBPACK_IMPORTED_MODULE_3__.FontAwesomeIcon, { color: "red", opacity: 0.75, icon: _fortawesome_free_solid_svg_icons__WEBPACK_IMPORTED_MODULE_2__.faCircle, size: "xs", fade: true, style: { marginLeft: '4px' } }))))),
                    react__WEBPACK_IMPORTED_MODULE_6___default().createElement(_mantine_core__WEBPACK_IMPORTED_MODULE_4__.Box, { style: { borderRadius: '20px', overflow: 'hidden' } },
                        react__WEBPACK_IMPORTED_MODULE_6___default().createElement(_code_block__WEBPACK_IMPORTED_MODULE_11__.PyCodeBlock, { code: message.text, styles: isMyMessage ? { background: 'rgb(240, 240, 240)' } : {} })))),
                message.status === 'failed' && (react__WEBPACK_IMPORTED_MODULE_6___default().createElement("button", { className: "str-chat__message-team-failed", onClick: message.errorStatusCode !== 403
                        ? () => handleRetry(message)
                        : undefined },
                    react__WEBPACK_IMPORTED_MODULE_6___default().createElement(stream_chat_react__WEBPACK_IMPORTED_MODULE_7__.ErrorIcon, null),
                    message.errorStatusCode !== 403
                        ? 'Message Failed · Click to try again'
                        : 'Message Failed · Unauthorized'))))));
};
const isMessageReactionEnabled = (message) => message.status !== 'sending' &&
    message.status !== 'failed' &&
    message.type !== 'system' &&
    message.type !== 'ephemeral' &&
    message.type !== 'error';
const ReactionGroup = (0,_utils__WEBPACK_IMPORTED_MODULE_12__.withDefaultProps)(_emotion_styled__WEBPACK_IMPORTED_MODULE_0___default()(_mantine_core__WEBPACK_IMPORTED_MODULE_4__.Flex, { shouldForwardProp: () => true }) `
    position: absolute;
    top: 8px;
    right: 8px;
    height: 36px;
    border-radius: 18px;
    padding: 6px 12px;
    background-color: #ffffff;
    border: 1px solid #ebebeb;

    > * {
      display: inline-flex;
      align-items: center;
      opacity: 0.5;
      cursor: pointer;
      &:hover {
        opacity: 1;
      }
    }
  `, { direction: 'row', align: 'center' });
const ReactionAuxText = (0,_utils__WEBPACK_IMPORTED_MODULE_12__.withDefaultProps)(_mantine_core__WEBPACK_IMPORTED_MODULE_4__.Text, {
    size: 'sm',
    weight: 'bold',
    ml: '2px'
});
const ReactionIcon = (0,_utils__WEBPACK_IMPORTED_MODULE_12__.withDefaultProps)(_fortawesome_react_fontawesome__WEBPACK_IMPORTED_MODULE_3__.FontAwesomeIcon, {
    size: 'lg'
});
const MemoizedCodeMessage = react__WEBPACK_IMPORTED_MODULE_6___default().memo(CodeMessageWithCongtext, stream_chat_react__WEBPACK_IMPORTED_MODULE_7__.areMessageUIPropsEqual);
const CodeMessage = (props) => {
    const messageContext = (0,stream_chat_react__WEBPACK_IMPORTED_MODULE_7__.useMessageContext)('CodeMessage');
    const reactionSelectorRef = (0,react__WEBPACK_IMPORTED_MODULE_6__.useRef)(null);
    const messageWrapperRef = (0,react__WEBPACK_IMPORTED_MODULE_6__.useRef)(null);
    const message = props.message || messageContext.message;
    const { isReactionEnabled, onReactionListClick, showDetailedReactions } = (0,stream_chat_react__WEBPACK_IMPORTED_MODULE_7__.useReactionClick)(message, reactionSelectorRef, messageWrapperRef);
    const handleOpenThreadOverride = (event) => {
        messageContext.handleOpenThread(event);
    };
    return (react__WEBPACK_IMPORTED_MODULE_6___default().createElement("div", { className: message.pinned ? 'pinned-message' : 'unpinned-message' },
        react__WEBPACK_IMPORTED_MODULE_6___default().createElement(MemoizedCodeMessage, Object.assign({}, messageContext, { isReactionEnabled: isReactionEnabled, messageWrapperRef: messageWrapperRef, onReactionListClick: onReactionListClick, reactionSelectorRef: reactionSelectorRef, showDetailedReactions: showDetailedReactions, handleOpenThread: handleOpenThreadOverride }, props))));
};
const ThreadMessage = (props) => {
    const messageContext = (0,stream_chat_react__WEBPACK_IMPORTED_MODULE_7__.useMessageContext)('CodeMessage');
    const message = props.message || messageContext.message;
    if (message === null || message === void 0 ? void 0 : message.codeMetadata) {
        return react__WEBPACK_IMPORTED_MODULE_6___default().createElement(CodeMessage, Object.assign({}, props));
    }
    return (react__WEBPACK_IMPORTED_MODULE_6___default().createElement(_mantine_core__WEBPACK_IMPORTED_MODULE_4__.Flex, { direction: "row", ml: "md" },
        react__WEBPACK_IMPORTED_MODULE_6___default().createElement(stream_chat_react__WEBPACK_IMPORTED_MODULE_7__.MessageSimple, Object.assign({}, props))));
};


/***/ }),

/***/ "./lib/components/customized-chat/style-fix.js":
/*!*****************************************************!*\
  !*** ./lib/components/customized-chat/style-fix.js ***!
  \*****************************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "GloablChatStylePatch": () => (/* binding */ GloablChatStylePatch),
/* harmony export */   "GlobalJupyterStylePatch": () => (/* binding */ GlobalJupyterStylePatch)
/* harmony export */ });
/* harmony import */ var _emotion_react__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @emotion/react */ "webpack/sharing/consume/default/@emotion/react/@emotion/react?185d");
/* harmony import */ var _emotion_react__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_emotion_react__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! react */ "webpack/sharing/consume/default/react");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(react__WEBPACK_IMPORTED_MODULE_1__);


// Patches GetStream's style flaws
const GloablChatStylePatch = () => (react__WEBPACK_IMPORTED_MODULE_1___default().createElement(_emotion_react__WEBPACK_IMPORTED_MODULE_0__.Global, { styles: _emotion_react__WEBPACK_IMPORTED_MODULE_0__.css `
      .rfu-file-upload-button {
        line-height: 1 !important;
      }
    ` }));
const GlobalJupyterStylePatch = () => (react__WEBPACK_IMPORTED_MODULE_1___default().createElement(_emotion_react__WEBPACK_IMPORTED_MODULE_0__.Global, { styles: _emotion_react__WEBPACK_IMPORTED_MODULE_0__.css `
      .jp-Dialog-content {
        min-width: 300px;
        min-height: 200px;
        max-width: 80vw;
        max-height: 80vh;
        padding: 12px;
      }
    ` }));


/***/ }),

/***/ "./lib/components/customized-chat/thread-header.js":
/*!*********************************************************!*\
  !*** ./lib/components/customized-chat/thread-header.js ***!
  \*********************************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "SimpleReturnThreadHeader": () => (/* binding */ SimpleReturnThreadHeader)
/* harmony export */ });
/* harmony import */ var _emotion_styled__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @emotion/styled */ "webpack/sharing/consume/default/@emotion/styled/@emotion/styled");
/* harmony import */ var _emotion_styled__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_emotion_styled__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _fortawesome_free_solid_svg_icons__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @fortawesome/free-solid-svg-icons */ "webpack/sharing/consume/default/@fortawesome/free-solid-svg-icons/@fortawesome/free-solid-svg-icons");
/* harmony import */ var _fortawesome_free_solid_svg_icons__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_fortawesome_free_solid_svg_icons__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _fortawesome_react_fontawesome__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! @fortawesome/react-fontawesome */ "webpack/sharing/consume/default/@fortawesome/react-fontawesome/@fortawesome/react-fontawesome");
/* harmony import */ var _fortawesome_react_fontawesome__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(_fortawesome_react_fontawesome__WEBPACK_IMPORTED_MODULE_2__);
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! react */ "webpack/sharing/consume/default/react");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_3___default = /*#__PURE__*/__webpack_require__.n(react__WEBPACK_IMPORTED_MODULE_3__);




const ClickableBox = (_emotion_styled__WEBPACK_IMPORTED_MODULE_0___default().span) `
  cursor: pointer;
  width: 16px;
  height: 16px;
  margin: 6px;
  opacity: 0.5;
  &:hover {
    opacity: 1;
  }
`;
const SimpleReturnThreadHeader = (props) => {
    const { closeThread } = props;
    return (react__WEBPACK_IMPORTED_MODULE_3___default().createElement(ClickableBox, { onClick: closeThread, title: "Close Thread", style: { position: 'absolute', top: '0px', left: '0px', zIndex: 10000 } },
        react__WEBPACK_IMPORTED_MODULE_3___default().createElement(_fortawesome_react_fontawesome__WEBPACK_IMPORTED_MODULE_2__.FontAwesomeIcon, { icon: _fortawesome_free_solid_svg_icons__WEBPACK_IMPORTED_MODULE_1__.faClose })));
};


/***/ }),

/***/ "./lib/components/icons.js":
/*!*********************************!*\
  !*** ./lib/components/icons.js ***!
  \*********************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "ClickableFontAwesome": () => (/* binding */ ClickableFontAwesome),
/* harmony export */   "registerCustomIcons": () => (/* binding */ registerCustomIcons)
/* harmony export */ });
/* harmony import */ var _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @jupyterlab/ui-components */ "webpack/sharing/consume/default/@jupyterlab/ui-components");
/* harmony import */ var _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _constants__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! ../constants */ "./lib/constants.js");
/* harmony import */ var _fortawesome_react_fontawesome__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @fortawesome/react-fontawesome */ "webpack/sharing/consume/default/@fortawesome/react-fontawesome/@fortawesome/react-fontawesome");
/* harmony import */ var _fortawesome_react_fontawesome__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_fortawesome_react_fontawesome__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! react */ "webpack/sharing/consume/default/react");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(react__WEBPACK_IMPORTED_MODULE_2__);




const ClickableFontAwesome = ({ icon, onClick }) => (react__WEBPACK_IMPORTED_MODULE_2___default().createElement(_fortawesome_react_fontawesome__WEBPACK_IMPORTED_MODULE_1__.FontAwesomeIcon, { icon: icon, size: "lg", onClick: onClick, style: { cursor: 'pointer' } }));
const registerCustomIcons = () => {
    // we're registering this icon via LabIcon side effects.
    new _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_0__.LabIcon({
        name: _constants__WEBPACK_IMPORTED_MODULE_3__.APP_IDEA_ICON,
        svgstr: `<?xml version="1.0" encoding="utf-8"?><!-- Uploaded to: SVG Repo, www.svgrepo.com, Generator: SVG Repo Mixer Tools -->
    <svg fill="#000000" width="800px" height="800px" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
        <path class="jp-icon3" fill="" d="M7 13.33a7 7 0 1 1 6 0V16H7v-2.67zM7 17h6v1.5c0 .83-.67 1.5-1.5 1.5h-3A1.5 1.5 0 0 1 7 18.5V17zm2-5.1V14h2v-2.1a5 5 0 1 0-2 0z"/>
    </svg>`
    });
    new _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_0__.LabIcon({
        name: _constants__WEBPACK_IMPORTED_MODULE_3__.APP_REVIEW_ICON,
        svgstr: `<?xml version="1.0" encoding="utf-8"?><!-- Uploaded to: SVG Repo, www.svgrepo.com, Generator: SVG Repo Mixer Tools -->
    <svg fill="#000000" width="800px" height="800px" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path d="M10.3 6.74a.75.75 0 01-.04 1.06l-2.908 2.7 2.908 2.7a.75.75 0 11-1.02 1.1l-3.5-3.25a.75.75 0 010-1.1l3.5-3.25a.75.75 0 011.06.04zm3.44 1.06a.75.75 0 111.02-1.1l3.5 3.25a.75.75 0 010 1.1l-3.5 3.25a.75.75 0 11-1.02-1.1l2.908-2.7-2.908-2.7z"/><path fill-rule="evenodd" d="M1.5 4.25c0-.966.784-1.75 1.75-1.75h17.5c.966 0 1.75.784 1.75 1.75v12.5a1.75 1.75 0 01-1.75 1.75h-9.69l-3.573 3.573A1.457 1.457 0 015 21.043V18.5H3.25a1.75 1.75 0 01-1.75-1.75V4.25zM3.25 4a.25.25 0 00-.25.25v12.5c0 .138.112.25.25.25h2.5a.75.75 0 01.75.75v3.19l3.72-3.72a.75.75 0 01.53-.22h10a.25.25 0 00.25-.25V4.25a.25.25 0 00-.25-.25H3.25z"/></svg>`
    });
};


/***/ }),

/***/ "./lib/components/reactive-popover.js":
/*!********************************************!*\
  !*** ./lib/components/reactive-popover.js ***!
  \********************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "ReactivePopover": () => (/* binding */ ReactivePopover)
/* harmony export */ });
/* harmony import */ var _mantine_core__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @mantine/core */ "webpack/sharing/consume/default/@mantine/core/@mantine/core?2426");
/* harmony import */ var _mantine_core__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_mantine_core__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! react */ "webpack/sharing/consume/default/react");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(react__WEBPACK_IMPORTED_MODULE_1__);


const ReactivePopover = ({ popoverText, children, popoverTimeout = 5 * 1000 }) => {
    const [isActivated, setIsActivated] = (0,react__WEBPACK_IMPORTED_MODULE_1__.useState)(false);
    const popoverHideTimer = react__WEBPACK_IMPORTED_MODULE_1___default().useRef(null);
    return (react__WEBPACK_IMPORTED_MODULE_1___default().createElement(_mantine_core__WEBPACK_IMPORTED_MODULE_0__.Popover, { opened: isActivated },
        react__WEBPACK_IMPORTED_MODULE_1___default().createElement(_mantine_core__WEBPACK_IMPORTED_MODULE_0__.Popover.Target, null,
            react__WEBPACK_IMPORTED_MODULE_1___default().createElement("div", { onClick: () => {
                    if (popoverHideTimer.current) {
                        clearTimeout(popoverHideTimer.current);
                    }
                    setIsActivated(true);
                    popoverHideTimer.current = setTimeout(() => {
                        setIsActivated(false);
                    }, popoverTimeout);
                } }, children)),
        react__WEBPACK_IMPORTED_MODULE_1___default().createElement(_mantine_core__WEBPACK_IMPORTED_MODULE_0__.Popover.Dropdown, { p: "xs" },
            react__WEBPACK_IMPORTED_MODULE_1___default().createElement(_mantine_core__WEBPACK_IMPORTED_MODULE_0__.Text, { size: "sm" }, popoverText))));
};


/***/ }),

/***/ "./lib/components/stream-chat.js":
/*!***************************************!*\
  !*** ./lib/components/stream-chat.js ***!
  \***************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "StreamChatChannelView": () => (/* binding */ StreamChatChannelView)
/* harmony export */ });
/* harmony import */ var _emotion_css__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @emotion/css */ "webpack/sharing/consume/default/@emotion/css/@emotion/css");
/* harmony import */ var _emotion_css__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_emotion_css__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! react */ "webpack/sharing/consume/default/react");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(react__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var stream_chat_react__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! stream-chat-react */ "webpack/sharing/consume/default/stream-chat-react/stream-chat-react");
/* harmony import */ var stream_chat_react__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(stream_chat_react__WEBPACK_IMPORTED_MODULE_2__);
/* harmony import */ var stream_chat_react_dist_css_index_css__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! stream-chat-react/dist/css/index.css */ "./node_modules/stream-chat-react/dist/css/index.css");




const StreamChatChannelView = ({ chatClient, chatChannel }) => {
    return (react__WEBPACK_IMPORTED_MODULE_1___default().createElement(stream_chat_react__WEBPACK_IMPORTED_MODULE_2__.Chat, { client: chatClient, theme: "str-chat__theme-light", customClasses: {
            chat: _emotion_css__WEBPACK_IMPORTED_MODULE_0__.css `
          height: 100%;
          .str-chat__send-button {
            display: block !important;
          }
        `
        } },
        react__WEBPACK_IMPORTED_MODULE_1___default().createElement(stream_chat_react__WEBPACK_IMPORTED_MODULE_2__.Channel, { channel: chatChannel },
            react__WEBPACK_IMPORTED_MODULE_1___default().createElement(stream_chat_react__WEBPACK_IMPORTED_MODULE_2__.Window, null,
                react__WEBPACK_IMPORTED_MODULE_1___default().createElement(stream_chat_react__WEBPACK_IMPORTED_MODULE_2__.ChannelHeader, null),
                react__WEBPACK_IMPORTED_MODULE_1___default().createElement(stream_chat_react__WEBPACK_IMPORTED_MODULE_2__.MessageList, null),
                react__WEBPACK_IMPORTED_MODULE_1___default().createElement(stream_chat_react__WEBPACK_IMPORTED_MODULE_2__.MessageInput, null)),
            react__WEBPACK_IMPORTED_MODULE_1___default().createElement(stream_chat_react__WEBPACK_IMPORTED_MODULE_2__.Thread, null))));
};


/***/ }),

/***/ "./lib/constants.js":
/*!**************************!*\
  !*** ./lib/constants.js ***!
  \**************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "APP_ID": () => (/* binding */ APP_ID),
/* harmony export */   "APP_IDEA_ICON": () => (/* binding */ APP_IDEA_ICON),
/* harmony export */   "APP_REVIEW_ICON": () => (/* binding */ APP_REVIEW_ICON),
/* harmony export */   "COMMAND_CODE_IDEAS": () => (/* binding */ COMMAND_CODE_IDEAS),
/* harmony export */   "COMMAND_CODE_REVIEW": () => (/* binding */ COMMAND_CODE_REVIEW),
/* harmony export */   "GETSTREAM_API_KEY": () => (/* binding */ GETSTREAM_API_KEY),
/* harmony export */   "METADATA_APP_KEY": () => (/* binding */ METADATA_APP_KEY),
/* harmony export */   "OPENAI_API_KEY": () => (/* binding */ OPENAI_API_KEY),
/* harmony export */   "PLUGIN_ID": () => (/* binding */ PLUGIN_ID)
/* harmony export */ });
const APP_ID = 'codepeers';
const PLUGIN_ID = `${APP_ID}:plugin`;
const COMMAND_CODE_IDEAS = `${APP_ID}:cmd-code-ideas`;
const COMMAND_CODE_REVIEW = `${APP_ID}:cmd-code-review`;
const APP_IDEA_ICON = `${APP_ID}:icon-code-ideas`;
const APP_REVIEW_ICON = `${APP_ID}:icon-code-review`;
const METADATA_APP_KEY = APP_ID;
const GETSTREAM_API_KEY = '26b5bvn39b2x';
const OPENAI_API_KEY = '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';


/***/ }),

/***/ "./lib/context/user-code.js":
/*!**********************************!*\
  !*** ./lib/context/user-code.js ***!
  \**********************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "UserCodeContext": () => (/* binding */ UserCodeContext),
/* harmony export */   "UserCodeProvider": () => (/* binding */ UserCodeProvider),
/* harmony export */   "useUserCodeContext": () => (/* binding */ useUserCodeContext)
/* harmony export */ });
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! react */ "webpack/sharing/consume/default/react");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(react__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var tiny_invariant__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! tiny-invariant */ "webpack/sharing/consume/default/tiny-invariant/tiny-invariant");
/* harmony import */ var tiny_invariant__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(tiny_invariant__WEBPACK_IMPORTED_MODULE_1__);


const UserCodeContext = react__WEBPACK_IMPORTED_MODULE_0___default().createContext(undefined);
const useUserCodeContext = () => {
    const context = react__WEBPACK_IMPORTED_MODULE_0___default().useContext(UserCodeContext);
    tiny_invariant__WEBPACK_IMPORTED_MODULE_1___default()(context, 'useUserCodeContext must be used within a UserCodeProvider');
    return context;
};
const UserCodeProvider = ({ code, children }) => (react__WEBPACK_IMPORTED_MODULE_0___default().createElement(UserCodeContext.Provider, { value: code }, children));


/***/ }),

/***/ "./lib/hocs/check-props.js":
/*!*********************************!*\
  !*** ./lib/hocs/check-props.js ***!
  \*********************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "withPropsCheckDefined": () => (/* binding */ withPropsCheckDefined)
/* harmony export */ });
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! react */ "webpack/sharing/consume/default/react");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(react__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var stream_chat_react__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! stream-chat-react */ "webpack/sharing/consume/default/stream-chat-react/stream-chat-react");
/* harmony import */ var stream_chat_react__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(stream_chat_react__WEBPACK_IMPORTED_MODULE_1__);


const Loading = () => react__WEBPACK_IMPORTED_MODULE_0___default().createElement(stream_chat_react__WEBPACK_IMPORTED_MODULE_1__.LoadingIndicator, null);
const withPropsCheckDefined = (InnerComponent, FallbackComponent = Loading) => (props) => {
    const anyUndefinedProps = !props ||
        Object.keys(props).length === 0 ||
        Object.values(props).some(prop => prop === undefined);
    return anyUndefinedProps ? (react__WEBPACK_IMPORTED_MODULE_0___default().createElement(FallbackComponent, null)) : (react__WEBPACK_IMPORTED_MODULE_0___default().createElement(InnerComponent, Object.assign({}, props)));
};


/***/ }),

/***/ "./lib/hocs/refresh-chat.js":
/*!**********************************!*\
  !*** ./lib/hocs/refresh-chat.js ***!
  \**********************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "withChannelAutoRefresh": () => (/* binding */ withChannelAutoRefresh)
/* harmony export */ });
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! react */ "webpack/sharing/consume/default/react");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(react__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _hooks_rerender__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ../hooks/rerender */ "./lib/hooks/rerender.js");


function withChannelAutoRefresh(Component) {
    return props => {
        const { chatChannel } = props;
        const rerender = (0,_hooks_rerender__WEBPACK_IMPORTED_MODULE_1__.useRerender)();
        react__WEBPACK_IMPORTED_MODULE_0___default().useEffect(() => {
            const listener = ev => {
                console.debug('Channel event', ev);
                rerender();
            };
            chatChannel.on(listener);
            return () => chatChannel.off(listener);
        }, [chatChannel]);
        return react__WEBPACK_IMPORTED_MODULE_0___default().createElement(Component, Object.assign({}, props));
    };
}


/***/ }),

/***/ "./lib/hooks/ai-sort.js":
/*!******************************!*\
  !*** ./lib/hooks/ai-sort.js ***!
  \******************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "useComlexitySort": () => (/* binding */ useComlexitySort),
/* harmony export */   "useSimilaritySort": () => (/* binding */ useSimilaritySort)
/* harmony export */ });
/* harmony import */ var _mantine_hooks__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @mantine/hooks */ "webpack/sharing/consume/default/@mantine/hooks/@mantine/hooks?7129");
/* harmony import */ var _mantine_hooks__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_mantine_hooks__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! react */ "webpack/sharing/consume/default/react");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(react__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var zod__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! zod */ "webpack/sharing/consume/default/zod/zod");
/* harmony import */ var zod__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(zod__WEBPACK_IMPORTED_MODULE_2__);
/* harmony import */ var _chat_completion__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! ./chat-completion */ "./lib/hooks/chat-completion.js");




const useAiSort = (props) => {
    const { systemPrompt, userPrompt, codeList, cacheKey } = props;
    const { result, isLoading, isFulfilled, start } = (0,_chat_completion__WEBPACK_IMPORTED_MODULE_3__.useChatCompletion)({
        systemPrompt: systemPrompt,
        userPrompt: userPrompt + codeList.map((c, i) => `[${i}] ${c.code}\n`).join('\n')
    });
    const [sortingCache, setSortingCache] = (0,_mantine_hooks__WEBPACK_IMPORTED_MODULE_0__.useLocalStorage)({
        key: cacheKey,
        deserialize: parseSortCache,
        getInitialValueInEffect: false
    });
    const cachedResult = (0,react__WEBPACK_IMPORTED_MODULE_1__.useMemo)(() => {
        if (!sortingCache || !isCacheHit(codeList, sortingCache)) {
            return undefined;
        }
        return sortingCache.map(id => codeList.findIndex(c => c.id === id));
    }, [sortingCache, codeList]);
    const parseResult = () => {
        if (isLoading || !isFulfilled) {
            return undefined;
        }
        const regex = new RegExp(`\\[\\d+(,\\W*\\d+){${Math.max(codeList.length - 1, 0)}}\\]`);
        const sortedIndexMatch = result.match(regex);
        if (!sortedIndexMatch) {
            console.warn('Invalid output format: ' + result);
            return undefined;
        }
        const parsedObj = JSON.parse(sortedIndexMatch[0]);
        const sortedIndex = zod__WEBPACK_IMPORTED_MODULE_2__.z.array(zod__WEBPACK_IMPORTED_MODULE_2__.z.number()).parse(parsedObj);
        setSortingCache(sortedIndex.map(i => codeList[i].id));
        return sortedIndex;
    };
    return {
        isLoading: !cachedResult && isLoading,
        sortedIndex: cachedResult || parseResult(),
        start: (0,react__WEBPACK_IMPORTED_MODULE_1__.useCallback)(() => {
            if (cachedResult) {
                return;
            }
            start();
        }, [cachedResult, start])
    };
};
const useComlexitySort = (codeList) => {
    const { sortedIndex, start, isLoading } = useAiSort({
        systemPrompt: 'You are an intelligent Coding Assistant that can read and analyse code in terms of algorithm complexity. ' +
            'You are given a list of code snippets that implements the same algorithm and you need to sort them by time complexity.',
        userPrompt: 'Please help me analyse time complexity for a series of code snippets written in Python. ' +
            'Each snippet has a format of `[<order_number>] <multiline_code>\\n`, ' +
            'and you are supposed to output ONLY a permutation of order numbers of the given snippets ' +
            'in ascending order of the time complexity of the corresponding code snippet in the format of JSON number array, e.g. [1,0,2] (no spaces in between). ' +
            'Therefore, the code snippets are sorted from the fastest to the slowest in terms of the big-O notation. ' +
            'If you find two snippets have the same time complexity, you can output either one of them first.\n' +
            'Please be reminded that, you MUST ONLY output ONE number array and NO MORE.\n' +
            'For example, if the input is "[0] {...some code...}\\n[1] {...some code...}\\n[2] {...some code...}\\n[3] {...some code...}\\n", ' +
            'in your unspoken mind, you can analyse each of them and the algorithms they contain,' +
            'then you find that their time complexity are [0]:"O(n^2)", [1]:"O(n)", [2]:"O(n^3)", [3]:"O(n)", ' +
            'as you already know that O(n) is smaller than O(n^2), and O(n^2) is smaller than O(n^3) in big-O notation, ' +
            'therefore, the answer should be either [1,3,0,2] or [3,1,0,2]\n' +
            'Now, given the following code snippets, please give me the FINAL answer without any explanation:\n',
        codeList,
        cacheKey: 'complexity-sort'
    });
    (0,react__WEBPACK_IMPORTED_MODULE_1__.useEffect)(() => {
        if (codeList.length > 0) {
            start();
        }
    }, [JSON.stringify(codeList)]);
    return {
        isLoading,
        sortedIndex
    };
};
const useSimilaritySort = (myCode, othersCodeList) => {
    const { sortedIndex, start, isLoading } = useAiSort({
        systemPrompt: 'You are an intelligent Coding Assistant that can read and analyse code in terms of logical similarity. ' +
            'You are given a list of code snippets that implements the same algorithm and you need to analyse how similar they are in terms of the essential logic.',
        userPrompt: 'Please help me analyse logical similarity for a series of code snippets written in Python in contrast of my own implementation. ' +
            'I will provide you my implementation first, with the format of `[my_code] <multiline_code>\\n`. ' +
            'Then I will give you a series of candidate code snippets, and each snippet has a format of `[<order_number>] <multiline_code>\\n`, ' +
            'and you are supposed to output ONLY a permutation of order numbers of the candidate snippets ' +
            'in descending order of logical similarity to my implementation of the corresponding code snippet in the format of JSON number array, e.g. [1,0,2] (no spaces in between). ' +
            'Therefore, candidate code snippets can be sorted from the most similar to mine to the most different logically. ' +
            'If you find two snippets that you think equally similar to mine, you can output either one of them first.\n' +
            `For example, if the input is "[my_code] ${'def foo(n):\\n' + '    return bool(n % 2)\\n'}\\n[0] ${'def is_odd(x):\\n' + '    return math.fmod(x, 2) > 0\\n'}\\n[1] ${'def bar(a):\\n' + '    return a > (2 * math.floor(a/2))\\n'}\\n", ` +
            'you can analyse each of them and the algorithms they contain at first.' +
            'In this case, my code and candidate code [0] are logically identical since we both used modulo operation to check if a number is odd, ' +
            'in spite of different function names, arguments, and what specific modulo calculation we used. ' +
            'but candidate code [1] is different since it checked if a number is odd by comparing it with the result of the nearest even number. ' +
            'As the result, candidate code 0 is the most similar to mine, and candidate code 1 is the most different logically, ' +
            'so the output should be [0,1].\n' +
            'You can assume all inputs are invalid. You should NOT output any explanations, or natural language content other than a number array.\n\n' +
            'Now, please analyse the following code snippets and output the any one of the viable permutations of their order number:\n' +
            `[my_code] ${myCode}\n`,
        codeList: othersCodeList,
        cacheKey: 'similarity-sort'
    });
    (0,react__WEBPACK_IMPORTED_MODULE_1__.useEffect)(() => {
        if (othersCodeList.length > 0) {
            start();
        }
    }, [myCode, JSON.stringify(othersCodeList)]);
    return {
        isLoading,
        sortedIndex
    };
};
const parseSortCache = (s) => {
    const valueSchema = zod__WEBPACK_IMPORTED_MODULE_2__.z.array(zod__WEBPACK_IMPORTED_MODULE_2__.z.string());
    try {
        return valueSchema.parse(JSON.parse(s));
    }
    catch (e) {
        return undefined;
    }
};
const isCacheHit = (codeList, cache) => {
    if (cache.length !== codeList.length) {
        return false;
    }
    const codeIdSet = new Set(codeList.map(c => c.id));
    return cache.every(id => codeIdSet.has(id));
};


/***/ }),

/***/ "./lib/hooks/chaining.js":
/*!*******************************!*\
  !*** ./lib/hooks/chaining.js ***!
  \*******************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "makeAsyncChainingHook": () => (/* binding */ makeAsyncChainingHook),
/* harmony export */   "makeChainingHook": () => (/* binding */ makeChainingHook)
/* harmony export */ });
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! react */ "webpack/sharing/consume/default/react");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(react__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _types__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ../types */ "./lib/types/maybe.js");
/* harmony import */ var _state__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ./state */ "./lib/hooks/state.js");



const makeChainingHook = () => (chain) => {
    const wrappedChain = (val) => _types__WEBPACK_IMPORTED_MODULE_1__.Maybe.from(chain(val));
    return (mt) => {
        const lastMt = (0,react__WEBPACK_IMPORTED_MODULE_0__.useRef)(mt);
        const [mu, setMu] = (0,react__WEBPACK_IMPORTED_MODULE_0__.useState)(_types__WEBPACK_IMPORTED_MODULE_1__.Maybe.nothing());
        (0,react__WEBPACK_IMPORTED_MODULE_0__.useEffect)(() => {
            if (mt.isNothing() && mu.isJust()) {
                setMu(_types__WEBPACK_IMPORTED_MODULE_1__.Maybe.nothing());
            }
            else if (mt.isJust() &&
                (mu.isNothing() || _types__WEBPACK_IMPORTED_MODULE_1__.Maybe.equals(mt, lastMt.current))) {
                setMu(mt.chain(wrappedChain));
            }
            lastMt.current = mt;
        }, [mt, setMu]);
        return mu;
    };
};
const makeAsyncChainingHook = (chain, cleanup) => {
    const wrappedChain = (val) => chain(val).then(data => _types__WEBPACK_IMPORTED_MODULE_1__.Maybe.from(data));
    const disposeMaybe = (mu) => {
        if (mu.isJust()) {
            cleanup === null || cleanup === void 0 ? void 0 : cleanup(mu.unwrap());
        }
    };
    return (mt) => {
        const lastMt = (0,react__WEBPACK_IMPORTED_MODULE_0__.useRef)(mt);
        // TODO: handle with concurrent updates and cleanup for async chaining
        const [mu, setMu] = (0,_state__WEBPACK_IMPORTED_MODULE_2__.useDisposibleState)(_types__WEBPACK_IMPORTED_MODULE_1__.Maybe.nothing(), disposeMaybe);
        (0,react__WEBPACK_IMPORTED_MODULE_0__.useEffect)(() => {
            if (mt.isNothing() && mu.isJust()) {
                setMu(_types__WEBPACK_IMPORTED_MODULE_1__.Maybe.nothing());
            }
            else if (mt.isJust() &&
                (mu.isNothing() || !_types__WEBPACK_IMPORTED_MODULE_1__.Maybe.equals(mt, lastMt.current))) {
                mt.asyncChain(wrappedChain).then(setMu);
            }
            lastMt.current = mt;
        }, [mt, setMu]);
        return mu;
    };
};


/***/ }),

/***/ "./lib/hooks/chat-completion.js":
/*!**************************************!*\
  !*** ./lib/hooks/chat-completion.js ***!
  \**************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "useChatCompletion": () => (/* binding */ useChatCompletion)
/* harmony export */ });
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! react */ "webpack/sharing/consume/default/react");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(react__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var react_async__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! react-async */ "webpack/sharing/consume/default/react-async/react-async");
/* harmony import */ var react_async__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(react_async__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _api_openai_chat__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ../api/openai-chat */ "./lib/api/openai-chat.js");



// import { useDynamicCompletionNotification } from './chat-notifications';
// Supports chat completion models (gpt-3.5-turbo) and stream decoding
const useChatCompletion = (prompt) => {
    const [result, setResult] = (0,react__WEBPACK_IMPORTED_MODULE_0__.useState)('');
    const formattedPrompt = (0,react__WEBPACK_IMPORTED_MODULE_0__.useMemo)(() => {
        if (typeof prompt === 'string') {
            return [{ role: 'user', content: prompt }];
        }
        return [
            { role: 'system', content: prompt.systemPrompt },
            { role: 'user', content: prompt.userPrompt }
        ];
    }, [JSON.stringify(prompt)]);
    const fetchCompletion = (0,react__WEBPACK_IMPORTED_MODULE_0__.useCallback)(() => (0,_api_openai_chat__WEBPACK_IMPORTED_MODULE_2__.fetchStreamingCompletion)(formattedPrompt, newData => setResult(res => res + newData)), [formattedPrompt]);
    // Clear result when prompt changes
    (0,react__WEBPACK_IMPORTED_MODULE_0__.useEffect)(() => {
        return () => setResult('');
    }, [formattedPrompt]);
    // useDynamicCompletionNotification(prompt, result);
    const { isLoading, isFulfilled, run } = (0,react_async__WEBPACK_IMPORTED_MODULE_1__.useAsync)({
        deferFn: fetchCompletion
    });
    return { isLoading, result, isFulfilled, start: run };
};


/***/ }),

/***/ "./lib/hooks/rerender.js":
/*!*******************************!*\
  !*** ./lib/hooks/rerender.js ***!
  \*******************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "useRerender": () => (/* binding */ useRerender)
/* harmony export */ });
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! react */ "webpack/sharing/consume/default/react");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(react__WEBPACK_IMPORTED_MODULE_0__);

const useRerender = () => {
    const [, setCount] = (0,react__WEBPACK_IMPORTED_MODULE_0__.useState)(0);
    return (0,react__WEBPACK_IMPORTED_MODULE_0__.useCallback)(() => setCount(c => c + 1), []);
};


/***/ }),

/***/ "./lib/hooks/state.js":
/*!****************************!*\
  !*** ./lib/hooks/state.js ***!
  \****************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "useDisposibleState": () => (/* binding */ useDisposibleState)
/* harmony export */ });
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! react */ "webpack/sharing/consume/default/react");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(react__WEBPACK_IMPORTED_MODULE_0__);

const useDisposibleState = (initialState, dispose) => {
    const [state, setState] = (0,react__WEBPACK_IMPORTED_MODULE_0__.useState)(initialState);
    (0,react__WEBPACK_IMPORTED_MODULE_0__.useEffect)(() => {
        return () => dispose(state);
    }, [state, dispose]);
    return [state, setState];
};


/***/ }),

/***/ "./lib/hooks/stream-chat.js":
/*!**********************************!*\
  !*** ./lib/hooks/stream-chat.js ***!
  \**********************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "useChannelAutoRefresh": () => (/* binding */ useChannelAutoRefresh),
/* harmony export */   "useStreamChat": () => (/* binding */ useStreamChat)
/* harmony export */ });
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! react */ "webpack/sharing/consume/default/react");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(react__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var stream_chat__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! stream-chat */ "webpack/sharing/consume/default/stream-chat/stream-chat?e0f2");
/* harmony import */ var stream_chat__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(stream_chat__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _constants__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ../constants */ "./lib/constants.js");
/* harmony import */ var _types__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! ../types */ "./lib/types/maybe.js");
/* harmony import */ var _chaining__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! ./chaining */ "./lib/hooks/chaining.js");
/* harmony import */ var _rerender__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! ./rerender */ "./lib/hooks/rerender.js");






const createStreamChatClient = async ({ apiKey = _constants__WEBPACK_IMPORTED_MODULE_2__.GETSTREAM_API_KEY, userData, token }) => {
    const client = new stream_chat__WEBPACK_IMPORTED_MODULE_1__.StreamChat(apiKey);
    // TODO: add token auth
    await client.connectUser(userData, token !== null && token !== void 0 ? token : client.devToken(userData.id));
    return client;
};
const useStreamChatClient = (0,_chaining__WEBPACK_IMPORTED_MODULE_3__.makeAsyncChainingHook)(createStreamChatClient, client => {
    console.debug('user disconnected');
    client.disconnectUser();
});
const useStreamChatChannel = (0,_chaining__WEBPACK_IMPORTED_MODULE_3__.makeAsyncChainingHook)(async ({ chatClient, channelId }) => {
    const channel = chatClient.channel('livestream', channelId, {
        // add as many custom fields as you'd like
        image: 'https://www.drupal.org/files/project-images/react.png',
        name: channelId
    });
    await channel.watch();
    return channel;
}, channel => {
    console.debug('channel closed');
    channel.clean();
});
const useStreamChat = ({ channelId, credentials }) => {
    const chatClient = useStreamChatClient((0,react__WEBPACK_IMPORTED_MODULE_0__.useMemo)(() => _types__WEBPACK_IMPORTED_MODULE_4__.Maybe.from(credentials).map(creds => ({
        userData: creds.userData,
        token: creds.token
    })), [credentials]));
    const chatChannel = useStreamChatChannel((0,react__WEBPACK_IMPORTED_MODULE_0__.useMemo)(() => chatClient.map(chatClient => ({ chatClient, channelId })), [chatClient, channelId]));
    return chatChannel.chain(channel => chatClient.map(client => ({ chatChannel: channel, chatClient: client })));
};
const useChannelAutoRefresh = (channel) => {
    const rerender = (0,_rerender__WEBPACK_IMPORTED_MODULE_5__.useRerender)();
    (0,react__WEBPACK_IMPORTED_MODULE_0__.useEffect)(() => {
        channel.on(event => {
            console.debug('channel event: ', event);
            rerender();
        });
    }, [channel, rerender]);
};


/***/ }),

/***/ "./lib/hooks/user-data.js":
/*!********************************!*\
  !*** ./lib/hooks/user-data.js ***!
  \********************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "useChatUserCredentials": () => (/* binding */ useChatUserCredentials)
/* harmony export */ });
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! react */ "webpack/sharing/consume/default/react");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(react__WEBPACK_IMPORTED_MODULE_0__);

const useChatUserCredentials = ({ userName, userId }) => {
    const memoizedCredentials = (0,react__WEBPACK_IMPORTED_MODULE_0__.useMemo)(() => ({
        userData: {
            id: userId,
            name: userName,
            image: `https://getstream.io/random_png/?id=${userId}&name=${userName}`
        },
        token: undefined
    }), [userName, userId]);
    return memoizedCredentials;
};


/***/ }),

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
/* harmony import */ var _jupyterlab_cell_toolbar__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @jupyterlab/cell-toolbar */ "webpack/sharing/consume/default/@jupyterlab/cell-toolbar");
/* harmony import */ var _jupyterlab_cell_toolbar__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_cell_toolbar__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! @jupyterlab/notebook */ "webpack/sharing/consume/default/@jupyterlab/notebook");
/* harmony import */ var _jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_2__);
/* harmony import */ var _jupyterlab_settingregistry__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! @jupyterlab/settingregistry */ "webpack/sharing/consume/default/@jupyterlab/settingregistry");
/* harmony import */ var _jupyterlab_settingregistry__WEBPACK_IMPORTED_MODULE_3___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_settingregistry__WEBPACK_IMPORTED_MODULE_3__);
/* harmony import */ var _jupyterlab_translation__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! @jupyterlab/translation */ "webpack/sharing/consume/default/@jupyterlab/translation");
/* harmony import */ var _jupyterlab_translation__WEBPACK_IMPORTED_MODULE_4___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_translation__WEBPACK_IMPORTED_MODULE_4__);
/* harmony import */ var _command__WEBPACK_IMPORTED_MODULE_6__ = __webpack_require__(/*! ./command */ "./lib/command.js");
/* harmony import */ var _components_icons__WEBPACK_IMPORTED_MODULE_7__ = __webpack_require__(/*! ./components/icons */ "./lib/components/icons.js");
/* harmony import */ var _constants__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! ./constants */ "./lib/constants.js");








// Get the current widget and activate unless the args specify otherwise.
function getCurrentWidget(tracker, shell, args) {
    const widget = tracker.currentWidget;
    const activate = args['activate'] !== false;
    if (activate && widget) {
        shell.activateById(widget.id);
    }
    return widget;
}
const codePeersPlugin = {
    id: _constants__WEBPACK_IMPORTED_MODULE_5__.PLUGIN_ID,
    autoStart: true,
    requires: [_jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_2__.INotebookTracker],
    optional: [_jupyterlab_settingregistry__WEBPACK_IMPORTED_MODULE_3__.ISettingRegistry, _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__.IToolbarWidgetRegistry, _jupyterlab_translation__WEBPACK_IMPORTED_MODULE_4__.ITranslator],
    activate: (app, tracker, settingRegistry, toolbarRegistry, translator) => {
        const toolbarItems = settingRegistry && toolbarRegistry
            ? (0,_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__.createToolbarFactory)(toolbarRegistry, settingRegistry, _jupyterlab_cell_toolbar__WEBPACK_IMPORTED_MODULE_1__.CellBarExtension.FACTORY_NAME, codePeersPlugin.id, translator !== null && translator !== void 0 ? translator : _jupyterlab_translation__WEBPACK_IMPORTED_MODULE_4__.nullTranslator)
            : undefined;
        app.docRegistry.addWidgetExtension('Notebook', new _jupyterlab_cell_toolbar__WEBPACK_IMPORTED_MODULE_1__.CellBarExtension(app.commands, toolbarItems));
        app.commands.addCommand(_constants__WEBPACK_IMPORTED_MODULE_5__.COMMAND_CODE_REVIEW, (0,_command__WEBPACK_IMPORTED_MODULE_6__.makeTriggerFrameCommand)('Codepeers: Review', args => getCurrentWidget(tracker, app.shell, args), _command__WEBPACK_IMPORTED_MODULE_6__.makeCodeReviewElement));
        app.commands.addCommand(_constants__WEBPACK_IMPORTED_MODULE_5__.COMMAND_CODE_IDEAS, (0,_command__WEBPACK_IMPORTED_MODULE_6__.makeTriggerFrameCommand)('Codepeers: Ideas', args => getCurrentWidget(tracker, app.shell, args), _command__WEBPACK_IMPORTED_MODULE_6__.makeAskHelpElement));
        (0,_components_icons__WEBPACK_IMPORTED_MODULE_7__.registerCustomIcons)();
    }
};
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (codePeersPlugin);


/***/ }),

/***/ "./lib/types/index.js":
/*!****************************!*\
  !*** ./lib/types/index.js ***!
  \****************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "CellAppMetadataSchema": () => (/* binding */ CellAppMetadataSchema),
/* harmony export */   "ChatCompletionChoiceSchema": () => (/* binding */ ChatCompletionChoiceSchema),
/* harmony export */   "ChatCompletionResponseSchema": () => (/* binding */ ChatCompletionResponseSchema),
/* harmony export */   "Maybe": () => (/* reexport safe */ _maybe__WEBPACK_IMPORTED_MODULE_1__.Maybe),
/* harmony export */   "NotebookAppMetadataSchema": () => (/* binding */ NotebookAppMetadataSchema)
/* harmony export */ });
/* harmony import */ var zod__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! zod */ "webpack/sharing/consume/default/zod/zod");
/* harmony import */ var zod__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(zod__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _maybe__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ./maybe */ "./lib/types/maybe.js");

/** Embedded in notebook metadata */
const NotebookAppMetadataSchema = zod__WEBPACK_IMPORTED_MODULE_0__.z.object({
    document_id: zod__WEBPACK_IMPORTED_MODULE_0__.z.string(),
    user_id: zod__WEBPACK_IMPORTED_MODULE_0__.z.string(),
    user_name: zod__WEBPACK_IMPORTED_MODULE_0__.z.string(),
    admin_view: zod__WEBPACK_IMPORTED_MODULE_0__.z.boolean().optional()
});
/** Embedded in notebook cell metadata */
const CellAppMetadataSchema = zod__WEBPACK_IMPORTED_MODULE_0__.z.object({
    topic_id: zod__WEBPACK_IMPORTED_MODULE_0__.z.string(),
    submission_id: zod__WEBPACK_IMPORTED_MODULE_0__.z.string().optional()
});
const ChatCompletionChoiceSchema = zod__WEBPACK_IMPORTED_MODULE_0__.z.object({
    delta: zod__WEBPACK_IMPORTED_MODULE_0__.z.object({
        content: zod__WEBPACK_IMPORTED_MODULE_0__.z.string().optional(),
        role: zod__WEBPACK_IMPORTED_MODULE_0__.z.string().optional()
    }),
    finish_reason: zod__WEBPACK_IMPORTED_MODULE_0__.z.string().nullable(),
    index: zod__WEBPACK_IMPORTED_MODULE_0__.z.number()
});
const ChatCompletionResponseSchema = zod__WEBPACK_IMPORTED_MODULE_0__.z.object({
    choices: zod__WEBPACK_IMPORTED_MODULE_0__.z.array(ChatCompletionChoiceSchema)
});



/***/ }),

/***/ "./lib/types/maybe.js":
/*!****************************!*\
  !*** ./lib/types/maybe.js ***!
  \****************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "Maybe": () => (/* binding */ Maybe)
/* harmony export */ });
class Maybe {
    constructor(value) {
        this.value = value;
    }
    static from(value) {
        return new Maybe(value);
    }
    static of(value) {
        return new Maybe(value);
    }
    static nothing() {
        return new Maybe();
    }
    static equals(lhv, rhv) {
        return lhv.inner() === rhv.inner();
    }
    isJust() {
        return !this.isNothing();
    }
    isNothing() {
        return this.value === undefined;
    }
    map(fn) {
        if (this.isNothing()) {
            return new Maybe();
        }
        return new Maybe(fn(this.value));
    }
    chain(fn) {
        if (this.isNothing()) {
            return new Maybe();
        }
        return fn(this.value);
    }
    asyncChain(fn) {
        if (this.isNothing()) {
            return Promise.resolve(new Maybe());
        }
        return fn(this.value);
    }
    unwrap() {
        if (this.isNothing()) {
            throw new Error('Nothing to unwrap');
        }
        return this.value;
    }
    inner() {
        return this.value;
    }
}


/***/ }),

/***/ "./lib/utils/index.js":
/*!****************************!*\
  !*** ./lib/utils/index.js ***!
  \****************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "filterMap": () => (/* binding */ filterMap),
/* harmony export */   "unwrapped": () => (/* binding */ unwrapped),
/* harmony export */   "uuidv4": () => (/* binding */ uuidv4),
/* harmony export */   "withDefaultProps": () => (/* reexport safe */ _props__WEBPACK_IMPORTED_MODULE_1__.withDefaultProps)
/* harmony export */ });
/* harmony import */ var tiny_invariant__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! tiny-invariant */ "webpack/sharing/consume/default/tiny-invariant/tiny-invariant");
/* harmony import */ var tiny_invariant__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(tiny_invariant__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _props__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ./props */ "./lib/utils/props.js");

const filterMap = (arr, trans) => arr.flatMap(t => {
    const maybeU = trans(t);
    return maybeU ? [maybeU] : [];
});
const unwrapped = (maybeT) => {
    tiny_invariant__WEBPACK_IMPORTED_MODULE_0___default()(maybeT !== undefined);
    return maybeT;
};
const uuidv4 = () => {
    const uuid = new Array(36);
    for (let i = 0; i < 36; i++) {
        uuid[i] = Math.floor(Math.random() * 16);
    }
    uuid[14] = 4; // set bits 12-15 of time-high-and-version to 0100
    uuid[19] = uuid[19] &= ~(1 << 2); // set bit 6 of clock-seq-and-reserved to zero
    uuid[19] = uuid[19] |= 1 << 3; // set bit 7 of clock-seq-and-reserved to one
    uuid[8] = uuid[13] = uuid[18] = uuid[23] = '-';
    return uuid.map(x => x.toString(16)).join('');
};



/***/ }),

/***/ "./lib/utils/props.js":
/*!****************************!*\
  !*** ./lib/utils/props.js ***!
  \****************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "withDefaultProps": () => (/* binding */ withDefaultProps)
/* harmony export */ });
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! react */ "webpack/sharing/consume/default/react");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(react__WEBPACK_IMPORTED_MODULE_0__);

const withDefaultProps = (Component, defaultProps) => {
    return (props) => react__WEBPACK_IMPORTED_MODULE_0___default().createElement(Component, Object.assign({}, defaultProps, props));
};


/***/ }),

/***/ "./lib/views/code-list.js":
/*!********************************!*\
  !*** ./lib/views/code-list.js ***!
  \********************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "PeerCodeView": () => (/* binding */ PeerCodeView)
/* harmony export */ });
/* harmony import */ var _emotion_react__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @emotion/react */ "webpack/sharing/consume/default/@emotion/react/@emotion/react?185d");
/* harmony import */ var _emotion_react__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_emotion_react__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _emotion_css__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @emotion/css */ "webpack/sharing/consume/default/@emotion/css/@emotion/css");
/* harmony import */ var _emotion_css__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_emotion_css__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _mantine_core__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! @mantine/core */ "webpack/sharing/consume/default/@mantine/core/@mantine/core?2426");
/* harmony import */ var _mantine_core__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(_mantine_core__WEBPACK_IMPORTED_MODULE_2__);
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! react */ "webpack/sharing/consume/default/react");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_3___default = /*#__PURE__*/__webpack_require__.n(react__WEBPACK_IMPORTED_MODULE_3__);
/* harmony import */ var react_async__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! react-async */ "webpack/sharing/consume/default/react-async/react-async");
/* harmony import */ var react_async__WEBPACK_IMPORTED_MODULE_4___default = /*#__PURE__*/__webpack_require__.n(react_async__WEBPACK_IMPORTED_MODULE_4__);
/* harmony import */ var stream_chat_react__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! stream-chat-react */ "webpack/sharing/consume/default/stream-chat-react/stream-chat-react");
/* harmony import */ var stream_chat_react__WEBPACK_IMPORTED_MODULE_5___default = /*#__PURE__*/__webpack_require__.n(stream_chat_react__WEBPACK_IMPORTED_MODULE_5__);
/* harmony import */ var stream_chat_react_dist_css_index_css__WEBPACK_IMPORTED_MODULE_6__ = __webpack_require__(/*! stream-chat-react/dist/css/index.css */ "./node_modules/stream-chat-react/dist/css/index.css");
/* harmony import */ var tiny_invariant__WEBPACK_IMPORTED_MODULE_7__ = __webpack_require__(/*! tiny-invariant */ "webpack/sharing/consume/default/tiny-invariant/tiny-invariant");
/* harmony import */ var tiny_invariant__WEBPACK_IMPORTED_MODULE_7___default = /*#__PURE__*/__webpack_require__.n(tiny_invariant__WEBPACK_IMPORTED_MODULE_7__);
/* harmony import */ var _components_app_container__WEBPACK_IMPORTED_MODULE_19__ = __webpack_require__(/*! ../components/app-container */ "./lib/components/app-container.js");
/* harmony import */ var _components_base__WEBPACK_IMPORTED_MODULE_13__ = __webpack_require__(/*! ../components/base */ "./lib/components/base.js");
/* harmony import */ var _components_code_block__WEBPACK_IMPORTED_MODULE_12__ = __webpack_require__(/*! ../components/code-block */ "./lib/components/code-block.js");
/* harmony import */ var _components_customized_chat__WEBPACK_IMPORTED_MODULE_10__ = __webpack_require__(/*! ../components/customized-chat/code-message */ "./lib/components/customized-chat/code-message.js");
/* harmony import */ var _components_customized_chat__WEBPACK_IMPORTED_MODULE_11__ = __webpack_require__(/*! ../components/customized-chat */ "./lib/components/customized-chat/thread-header.js");
/* harmony import */ var _hocs_check_props__WEBPACK_IMPORTED_MODULE_14__ = __webpack_require__(/*! ../hocs/check-props */ "./lib/hocs/check-props.js");
/* harmony import */ var _hocs_refresh_chat__WEBPACK_IMPORTED_MODULE_15__ = __webpack_require__(/*! ../hocs/refresh-chat */ "./lib/hocs/refresh-chat.js");
/* harmony import */ var _hooks_ai_sort__WEBPACK_IMPORTED_MODULE_9__ = __webpack_require__(/*! ../hooks/ai-sort */ "./lib/hooks/ai-sort.js");
/* harmony import */ var _hooks_stream_chat__WEBPACK_IMPORTED_MODULE_17__ = __webpack_require__(/*! ../hooks/stream-chat */ "./lib/hooks/stream-chat.js");
/* harmony import */ var _hooks_user_data__WEBPACK_IMPORTED_MODULE_16__ = __webpack_require__(/*! ../hooks/user-data */ "./lib/hooks/user-data.js");
/* harmony import */ var _utils__WEBPACK_IMPORTED_MODULE_8__ = __webpack_require__(/*! ../utils */ "./lib/utils/index.js");
/* harmony import */ var _context_user_code__WEBPACK_IMPORTED_MODULE_18__ = __webpack_require__(/*! ../context/user-code */ "./lib/context/user-code.js");
/** @jsx jsx */




















const StreamChatCodeChannelView = ({ chatClient, chatChannel, myCode }) => {
    const [sortKind, setSortKind] = react__WEBPACK_IMPORTED_MODULE_3___default().useState('likes');
    const messages = chatChannel.state.messages.filter(m => !m.deleted_at);
    const submittedCodeList = (0,react__WEBPACK_IMPORTED_MODULE_3__.useMemo)(() => (0,_utils__WEBPACK_IMPORTED_MODULE_8__.filterMap)(messages, ({ text, codeMetadata, id }) => {
        var _a;
        return text && codeMetadata
            ? // TODO: remove this patch in dev, since early submission has no submission_id
                { id: (_a = codeMetadata.submission_id) !== null && _a !== void 0 ? _a : id, code: text }
            : undefined;
    }), [messages]);
    const { sortedIndex: complexitySortedIndex, isLoading: isComplexitySortLoading } = (0,_hooks_ai_sort__WEBPACK_IMPORTED_MODULE_9__.useComlexitySort)(submittedCodeList);
    const { sortedIndex: similaritySortedIndex, isLoading: isSimilaritySortLoading } = (0,_hooks_ai_sort__WEBPACK_IMPORTED_MODULE_9__.useSimilaritySort)(myCode.code, submittedCodeList);
    const sortedMessages = (() => {
        switch (sortKind) {
            case 'likes':
                return messages.sort((ma, mb) => { var _a, _b, _c, _d; return (_b = (_a = mb.reaction_counts) === null || _a === void 0 ? void 0 : _a.like) !== null && _b !== void 0 ? _b : 0 - ((_d = (_c = ma.reaction_counts) === null || _c === void 0 ? void 0 : _c.like) !== null && _d !== void 0 ? _d : 0); });
            case 'comments':
                return messages.sort((ma, mb) => { var _a, _b; return (_a = mb.reply_count) !== null && _a !== void 0 ? _a : 0 - ((_b = ma.reply_count) !== null && _b !== void 0 ? _b : 0); });
            case 'copies':
                return messages.sort((ma, mb) => { var _a, _b, _c, _d; return (_b = (_a = mb.reaction_counts) === null || _a === void 0 ? void 0 : _a.love) !== null && _b !== void 0 ? _b : 0 - ((_d = (_c = ma.reaction_counts) === null || _c === void 0 ? void 0 : _c.love) !== null && _d !== void 0 ? _d : 0); });
            case 'similarity':
                tiny_invariant__WEBPACK_IMPORTED_MODULE_7___default()(!!similaritySortedIndex);
                return similaritySortedIndex.map(i => messages[i]);
            case 'complexity':
                tiny_invariant__WEBPACK_IMPORTED_MODULE_7___default()(!!complexitySortedIndex);
                return complexitySortedIndex.map(i => messages[i]);
            case 'lines-fewest':
                return messages.sort((ma, mb) => {
                    var _a, _b, _c, _d;
                    return ((_b = (_a = ma.text) === null || _a === void 0 ? void 0 : _a.split('\n').length) !== null && _b !== void 0 ? _b : 0) -
                        ((_d = (_c = mb.text) === null || _c === void 0 ? void 0 : _c.split('\n').length) !== null && _d !== void 0 ? _d : 0);
                });
            case 'lines-most':
                return messages.sort((ma, mb) => {
                    var _a, _b, _c, _d;
                    return ((_b = (_a = mb.text) === null || _a === void 0 ? void 0 : _a.split('\n').length) !== null && _b !== void 0 ? _b : 0) -
                        ((_d = (_c = ma.text) === null || _c === void 0 ? void 0 : _c.split('\n').length) !== null && _d !== void 0 ? _d : 0);
                });
        }
    })();
    const submittedCode = sortedMessages.find(message => { var _a; return ((_a = message.codeMetadata) === null || _a === void 0 ? void 0 : _a.user_id) === myCode.user_id; });
    const isCodeSynced = (submittedCode === null || submittedCode === void 0 ? void 0 : submittedCode.text) === myCode.code;
    const { run: handleSubmit } = (0,react_async__WEBPACK_IMPORTED_MODULE_4__.useAsync)({
        deferFn: (0,react__WEBPACK_IMPORTED_MODULE_3__.useCallback)(() => {
            const { code, ...meta } = myCode;
            const codeMessage = { text: code, codeMetadata: meta };
            return submittedCode
                ? chatClient.updateMessage({ ...codeMessage, id: submittedCode.id })
                : chatChannel.sendMessage({ ...codeMessage, id: meta.submission_id });
        }, [chatChannel, chatClient, submittedCode, myCode])
    });
    const chatElement = ((0,_emotion_react__WEBPACK_IMPORTED_MODULE_0__.jsx)(stream_chat_react__WEBPACK_IMPORTED_MODULE_5__.Chat, { client: chatClient, theme: "str-chat__theme-light", customClasses: {
            chat: _emotion_css__WEBPACK_IMPORTED_MODULE_1__.css `
          height: 100%;
          .str-chat__send-button {
            display: block !important;
          }
        `
        } },
        (0,_emotion_react__WEBPACK_IMPORTED_MODULE_0__.jsx)(stream_chat_react__WEBPACK_IMPORTED_MODULE_5__.Channel, { channel: chatChannel, Message: _components_customized_chat__WEBPACK_IMPORTED_MODULE_10__.CodeMessage, ThreadStart: VoidComponent, ThreadHeader: _components_customized_chat__WEBPACK_IMPORTED_MODULE_11__.SimpleReturnThreadHeader },
            (0,_emotion_react__WEBPACK_IMPORTED_MODULE_0__.jsx)(stream_chat_react__WEBPACK_IMPORTED_MODULE_5__.Window, null,
                (0,_emotion_react__WEBPACK_IMPORTED_MODULE_0__.jsx)(_mantine_core__WEBPACK_IMPORTED_MODULE_2__.Flex, { direction: "row", align: "center", justify: "space-between", p: "md" },
                    (0,_emotion_react__WEBPACK_IMPORTED_MODULE_0__.jsx)(_mantine_core__WEBPACK_IMPORTED_MODULE_2__.Text, null,
                        "Total Code Submissions: ",
                        sortedMessages.length),
                    (0,_emotion_react__WEBPACK_IMPORTED_MODULE_0__.jsx)(_mantine_core__WEBPACK_IMPORTED_MODULE_2__.Select, { label: "Sort By", value: sortKind, data: [
                            { label: 'Most Likes', value: 'likes' },
                            { label: 'Most Comments', value: 'comments' },
                            { label: 'Most Copies', value: 'copies' },
                            {
                                label: 'Most Similar 🤖',
                                value: 'similarity',
                                disabled: isSimilaritySortLoading || !similaritySortedIndex
                            },
                            {
                                label: 'Fastest 🤖',
                                value: 'complexity',
                                disabled: isComplexitySortLoading || !complexitySortedIndex
                            },
                            { label: 'Longest', value: 'lines-most' },
                            { label: 'Shortest', value: 'lines-fewest' }
                        ], onChange: newValue => setSortKind(newValue) })),
                (0,_emotion_react__WEBPACK_IMPORTED_MODULE_0__.jsx)(stream_chat_react__WEBPACK_IMPORTED_MODULE_5__.MessageList, { messages: sortedMessages, disableDateSeparator: true })),
            (0,_emotion_react__WEBPACK_IMPORTED_MODULE_0__.jsx)(WrappedThread, { Message: _components_customized_chat__WEBPACK_IMPORTED_MODULE_10__.ThreadMessage }))));
    if (isCodeSynced) {
        return chatElement;
    }
    return ((0,_emotion_react__WEBPACK_IMPORTED_MODULE_0__.jsx)(_mantine_core__WEBPACK_IMPORTED_MODULE_2__.Flex, { direction: "column", h: "100%", align: "stretch" },
        (0,_emotion_react__WEBPACK_IMPORTED_MODULE_0__.jsx)(_mantine_core__WEBPACK_IMPORTED_MODULE_2__.Box, { style: { flexGrow: 1 } }, chatElement),
        (0,_emotion_react__WEBPACK_IMPORTED_MODULE_0__.jsx)(_mantine_core__WEBPACK_IMPORTED_MODULE_2__.Box, { style: { flexGrow: 0 } },
            (0,_emotion_react__WEBPACK_IMPORTED_MODULE_0__.jsx)(SyncCodeView, { myCode: myCode, handleSubmit: handleSubmit, isUpdate: !!submittedCode }))));
};
const SyncCodeView = ({ myCode, handleSubmit, isUpdate }) => {
    const action = isUpdate ? 'update' : 'submit';
    return ((0,_emotion_react__WEBPACK_IMPORTED_MODULE_0__.jsx)(react__WEBPACK_IMPORTED_MODULE_3__.Fragment, null,
        (0,_emotion_react__WEBPACK_IMPORTED_MODULE_0__.jsx)(_mantine_core__WEBPACK_IMPORTED_MODULE_2__.Divider, { my: "sm" }),
        (0,_emotion_react__WEBPACK_IMPORTED_MODULE_0__.jsx)(_mantine_core__WEBPACK_IMPORTED_MODULE_2__.Text, { color: "gray.500", size: "sm" },
            "Do you want to ",
            action,
            " your code?"),
        (0,_emotion_react__WEBPACK_IMPORTED_MODULE_0__.jsx)(_mantine_core__WEBPACK_IMPORTED_MODULE_2__.Flex, { direction: "row", align: "flex-end" },
            (0,_emotion_react__WEBPACK_IMPORTED_MODULE_0__.jsx)(_mantine_core__WEBPACK_IMPORTED_MODULE_2__.Box, { style: { flex: 1 } },
                (0,_emotion_react__WEBPACK_IMPORTED_MODULE_0__.jsx)(_components_code_block__WEBPACK_IMPORTED_MODULE_12__.PyCodeBlock, { code: myCode.code })),
            (0,_emotion_react__WEBPACK_IMPORTED_MODULE_0__.jsx)(_components_base__WEBPACK_IMPORTED_MODULE_13__.ClearButton, { onClick: handleSubmit, title: action.toUpperCase(), css: _emotion_react__WEBPACK_IMPORTED_MODULE_0__.css `
            svg path {
              fill: #006cff;
            }
          ` },
                (0,_emotion_react__WEBPACK_IMPORTED_MODULE_0__.jsx)(stream_chat_react__WEBPACK_IMPORTED_MODULE_5__.SendIconV2, null)))));
};
const InnerView = (0,_hocs_check_props__WEBPACK_IMPORTED_MODULE_14__.withPropsCheckDefined)((0,_hocs_refresh_chat__WEBPACK_IMPORTED_MODULE_15__.withChannelAutoRefresh)(StreamChatCodeChannelView));
const PeerCodeView = ({ codeBlock }) => {
    const { topic_id: topicId, user_id: userId, user_name: userName } = codeBlock;
    const credentials = (0,_hooks_user_data__WEBPACK_IMPORTED_MODULE_16__.useChatUserCredentials)({ userId, userName });
    const chatResources = (0,_hooks_stream_chat__WEBPACK_IMPORTED_MODULE_17__.useStreamChat)({
        channelId: `review-${topicId}`,
        credentials
    }).inner();
    return ((0,_emotion_react__WEBPACK_IMPORTED_MODULE_0__.jsx)(_context_user_code__WEBPACK_IMPORTED_MODULE_18__.UserCodeProvider, { code: codeBlock },
        (0,_emotion_react__WEBPACK_IMPORTED_MODULE_0__.jsx)(_components_app_container__WEBPACK_IMPORTED_MODULE_19__.FramedAppContainer, null,
            (0,_emotion_react__WEBPACK_IMPORTED_MODULE_0__.jsx)(InnerView, { chatChannel: chatResources === null || chatResources === void 0 ? void 0 : chatResources.chatChannel, chatClient: chatResources === null || chatResources === void 0 ? void 0 : chatResources.chatClient, myCode: codeBlock }))));
};
const VoidComponent = () => null;
const WrappedThread = props => ((0,_emotion_react__WEBPACK_IMPORTED_MODULE_0__.jsx)("div", { style: {
        position: 'relative',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'stretch'
    } },
    (0,_emotion_react__WEBPACK_IMPORTED_MODULE_0__.jsx)(stream_chat_react__WEBPACK_IMPORTED_MODULE_5__.Thread, Object.assign({}, props))));


/***/ }),

/***/ "./lib/views/regular-chat.js":
/*!***********************************!*\
  !*** ./lib/views/regular-chat.js ***!
  \***********************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "RegularChatView": () => (/* binding */ RegularChatView)
/* harmony export */ });
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! react */ "webpack/sharing/consume/default/react");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(react__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _components_app_container__WEBPACK_IMPORTED_MODULE_6__ = __webpack_require__(/*! ../components/app-container */ "./lib/components/app-container.js");
/* harmony import */ var _components_stream_chat__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! ../components/stream-chat */ "./lib/components/stream-chat.js");
/* harmony import */ var _hocs_check_props__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ../hocs/check-props */ "./lib/hocs/check-props.js");
/* harmony import */ var _hooks_stream_chat__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! ../hooks/stream-chat */ "./lib/hooks/stream-chat.js");
/* harmony import */ var _hooks_user_data__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! ../hooks/user-data */ "./lib/hooks/user-data.js");
/* harmony import */ var _hocs_refresh_chat__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ../hocs/refresh-chat */ "./lib/hocs/refresh-chat.js");







const InnerView = (0,_hocs_check_props__WEBPACK_IMPORTED_MODULE_1__.withPropsCheckDefined)((0,_hocs_refresh_chat__WEBPACK_IMPORTED_MODULE_2__.withChannelAutoRefresh)(_components_stream_chat__WEBPACK_IMPORTED_MODULE_3__.StreamChatChannelView));
const RegularChatView = ({ codeBlock, channelId }) => {
    const { user_id: userId, user_name: userName } = codeBlock;
    const credentials = (0,_hooks_user_data__WEBPACK_IMPORTED_MODULE_4__.useChatUserCredentials)({ userId, userName });
    const userChatData = (0,_hooks_stream_chat__WEBPACK_IMPORTED_MODULE_5__.useStreamChat)({
        channelId,
        credentials
    }).inner();
    return (react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_components_app_container__WEBPACK_IMPORTED_MODULE_6__.FramedAppContainer, null,
        react__WEBPACK_IMPORTED_MODULE_0___default().createElement(InnerView, Object.assign({}, userChatData))));
};


/***/ })

}]);
//# sourceMappingURL=lib_index_js.073ed8ebe366c0649971.js.map