import Keycloak from "keycloak-js";

const keycloak = new Keycloak({
  url: "https://keycloak.humaine-horizon.eu/",
  realm: "humaine",
  clientId: "minio",
});

export default keycloak;
