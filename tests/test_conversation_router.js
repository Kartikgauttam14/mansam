const assert = require('node:assert/strict');
const { route } = require('../js/conversation-router.js');
for (const step of [1, 2, 'gender', 'usage', 3, 'size']) {
  for (const text of ['What is an attar?', 'How much is GHUMUD?', 'Do you deliver to Dubai?', 'What sizes does this perfume have?', 'What is the difference between oud and musk?', 'هل لديكم توصيل؟', 'Compare rose and oud', 'Show me two similar perfumes']) {
    const result = route(text, step, { notes: 'rose' });
    assert.equal(result.kind, 'question', text);
    assert.equal(result.next, step);
    assert.deepEqual(result.patch, {});
  }
}
const full = route('I need a 100 ml unisex rose perfume for a wedding', 'gender');
assert.equal(full.kind, 'recommend');
assert.equal(full.patch.gender, 'unisex');
assert.equal(full.patch.usage, 'occasion');
assert.equal(full.patch.sizeMl, 100);
const saved = { gender: 'unisex', usage: 'daily', notes: 'rose but not oud', sizeMl: 100 };
const update = route('Actually, make it 50 ml', 'complete', saved);
assert.equal(update.kind, 'recommend');
assert.deepEqual(update.patch, { sizeMl: 50 });
assert.equal(saved.sizeMl, 100);
assert.equal(route('Woman', 'gender').next, 'usage');
assert.equal(route('Daily use', 'usage', { gender: 'female' }).next, 3);
assert.equal(route('musk', 3, { gender: 'female', usage: 'daily' }).next, 'size');
assert.equal(route('١٠٠ مل', 'size', saved).patch.sizeMl, 100);
assert.equal(route('عطر للجنسين ورد ١٠٠ مل لمناسبة خاصة', 1).kind, 'recommend');
console.log('Conversation routing checks passed.');
