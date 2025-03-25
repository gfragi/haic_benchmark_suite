module.exports = function(RED) {
    function CustomIconNode(config) {
      RED.nodes.createNode(this, config);
    }
    RED.nodes.registerType("custom-icon-node", CustomIconNode);
};
  