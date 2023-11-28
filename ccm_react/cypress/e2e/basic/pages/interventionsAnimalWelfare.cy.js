describe("Animal welfare interventions page tests", function () {
  beforeEach(function () {
    cy.visit("http://localhost:5173/interventions/animal-welfare");
  });

  it("displays basic info", function () {
    cy.get("body").should("contain.text", "Cross-Cause Cost-Effectiveness");
  });
});
