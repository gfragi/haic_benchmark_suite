const { shallowMount } = require("@vue/test-utils");
const HelloWorld = require("../../src/components/HelloWorld.vue");

describe("HelloWorld.vue", () => {
  it("renders props.msg when passed", () => {
    const msg = "new message";
    const wrapper = shallowMount(HelloWorld, {
      props: { msg },
    });
    expect(wrapper.text()).toMatch(msg);
  });
});
