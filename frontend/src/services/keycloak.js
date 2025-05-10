import Keycloak from "keycloak-js";

const keycloak = new Keycloak({

  // TODO: Change that.
  // url: "https://keycloak.humaine-horizon.eu/",
  url: "https://idp.studyingreece.edu.gr/",
  realm: "humaine",
  clientId: "benchmarking-suite",
});

export default keycloak;
