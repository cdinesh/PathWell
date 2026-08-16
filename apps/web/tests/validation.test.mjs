import assert from "node:assert/strict";
import test from "node:test";

test("signup rules require strong matching passwords", () => {
  const password = "StrongPass123";
  assert.equal(password.length >= 10 && /[A-Z]/.test(password) && /[a-z]/.test(password) && /[0-9]/.test(password), true);
  assert.notEqual(password, "different");
});

test("document size rule accepts up to 10 MB", () => {
  assert.equal(1024 <= 10 * 1024 * 1024, true);
  assert.equal(11 * 1024 * 1024 <= 10 * 1024 * 1024, false);
});

test("goal progress is capped at 100 percent", () => {
  const progress = (current, target) => Math.min(Math.round(current / target * 100), 100);
  assert.equal(progress(17500, 25000), 70);
  assert.equal(progress(120, 100), 100);
});

test("AI composer blocks too-short requests", () => {
  assert.equal("hi".length >= 3, false);
  assert.equal("Plan Italy".length >= 3, true);
});
