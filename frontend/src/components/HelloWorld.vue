<template>
  <div class="hello">
    <h1>{{ msg }}</h1>
  </div>
</template>

<script>
const component = {
  name: "HelloWorld",
  props: {
    msg: String,
  },
};

module.exports = component;
</script>
