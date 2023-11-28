describe("Projects xrisk page tests", function () {
  beforeEach(function () {
    cy.visit("http://localhost:5173/projects/xrisk");
  });

  it("displays basic info", function () {
    cy.get("body").should("contain.text", "Cross-Cause Cost-Effectiveness");
  });
});
