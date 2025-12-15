// // Jest setup file for Vue 3 tests
// import { config } from "@vue/test-utils";

// // Configure Vue Test Utils globally
// config.global.mocks = {
//   $t: (key) => key, // Mock i18n
// };

// // Mock window.matchMedia for Vuetify
// Object.defineProperty(window, "matchMedia", {
//   writable: true,
//   value: jest.fn().mockImplementation((query) => ({
//     matches: false,
//     media: query,
//     onchange: null,
//     addListener: jest.fn(), // deprecated
//     removeListener: jest.fn(), // deprecated
//     addEventListener: jest.fn(),
//     removeEventListener: jest.fn(),
//     dispatchEvent: jest.fn(),
//   })),
// });

// // Mock IntersectionObserver
// global.IntersectionObserver = class IntersectionObserver {
//   constructor() {}
//   observe() {
//     return null;
//   }
//   disconnect() {
//     return null;
//   }
//   unobserve() {
//     return null;
//   }
// };
