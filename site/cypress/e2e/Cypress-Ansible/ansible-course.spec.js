describe('Testing Ansible Scripts', () => {

    it('should work', () => {
        cy.login('instructor');
        cy.visit('term', 'course');
    });
});