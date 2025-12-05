// Basic test to verify Jest is working with Vue CLI
const { shallowMount } = require("@vue/test-utils");
const { createApp } = require("vue");

describe("Basic Vue CLI Jest Test", () => {
  it("should run Jest with Vue CLI plugin", () => {
    expect(true).toBe(true);
  });

  it("should be able to import Vue", () => {
    expect(createApp).toBeDefined();
  });

  it("should be able to import Vue Test Utils", () => {
    expect(shallowMount).toBeDefined();
  });
});
