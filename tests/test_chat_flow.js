const fs = require('node:fs');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const { route } = require('../js/conversation-router');
const source = fs.readFileSync(require.resolve('../js/chatbot.js'), 'utf8').split('  const styles =')[0];
const events = [], requests = [];
const context = {
  window: { MANSAM_CONFIG: {}, MansamConversationRouter: { route } },
  document: { querySelector: () => null },
  localStorage: { setItem() {} }, sessionStorage: { setItem() {} }, console,
  events, requests
};
vm.createContext(context);
vm.runInContext(source + `
  stopRecognition = refreshLanguage = updateSuggestions = setThinking = () => {};
  addMessage = (text, role) => events.push({text, role});
  requestChat = async payload => { requests.push(payload); return {answer: 'Here is the answer.', language: 'en', productIds: []}; };
  state.language = 'en'; state.speakerEnabled = false;
  window.test = {state, send};
})();`, context);
(async () => {
  const { state, send } = context.window.test;
  state.flowStep = 'size'; state.profile.discovery = {gender:'unisex',usage:'daily',notes:'rose'};
  await send('What sizes does this perfume have?');
  assert.equal(requests.length, 1);
  assert.equal(state.flowStep, 'complete');
  assert.equal(state.profile.discovery.notes, 'rose');
  assert.equal(events.at(-1).text, 'Here is the answer.');
  await send('100 ml');
  assert.equal(requests.at(-1).message, '100 ml');
  state.awaitingName = true;
  await send('What is an attar?');
  assert.equal(state.awaitingName, false);
  assert.equal(requests.at(-1).message, 'What is an attar?');
  await send('Kartik');
  assert.equal(requests.at(-1).message, 'Kartik');
  console.log('Chat handler integration checks passed.');
})().catch(error => { console.error(error); process.exitCode = 1; });
