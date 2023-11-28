module.exports = {
  transform: { "^.+\\.ts?$": "ts-jest" },
  testEnvironment: "node",
  testRegex: "/.*\\.(test|spec)?\\.(ts|tsx|js)$",
  moduleFileExtensions: ["ts", "tsx", "js", "jsx", "json", "node"],
  moduleNameMapper: {
    "^d3$": "<rootDir>/node_modules/d3/dist/d3.min.js",
  },
};
