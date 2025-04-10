import Keycloak from "keycloak-js";

const keycloak = new Keycloak({
  url: "https://idp.studyingreece.edu.gr/",
  realm: "hua",
  clientId: "benchmark",
});

export default keycloak;
