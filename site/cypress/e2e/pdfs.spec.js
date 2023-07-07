Cypress.Commands.add('switch_settings', (gradeable_id) => {
    cy.visit(['sample', 'gradeable', gradeable_id, 'update']);
    cy.get('#page_3_nav').click();
    // Save the previous settings to revert after. 
    cy.get('#minimum_grading_group option:selected').invoke('text').as(gradeable_id.concat('_selected'));
    cy.get('input[name="grader_assignment_method"]:checked').as(gradeable_id.concat('_checked'));
    
    cy.get('[data-testid="minimum_grading_group"]').select('Limited Access Grader');
    cy.get('input[data-testname="grader_assignment_method"][value="1"]').check();
});

Cypress.Commands.add('revert_settings', (gradeable_id) => {
    cy.visit(['sample', 'gradeable', gradeable_id, 'update']);
    cy.get('#page_3_nav').click();
    cy.get('@'.concat(gradeable_id, '_selected')).then(setting => {
        cy.get('#minimum_grading_group').select(setting);
        cy.get('#minimum_grading_group option:selected').should('have.text', setting);
    });
    cy.get('@'.concat(gradeable_id, '_checked')).check();
});

Cypress.Commands.add('pdf_access', (user_id, gradeable_id) => {
    cy.visit('/');
    cy.login(user_id);

    cy.visit(['sample', 'gradeable', gradeable_id, 'grading', 'details']);
    cy.get('#agree-button').click({ force: true });
    cy.get('[data-testid="details-table"]').should('be.visible');
    if (user_id !== 'grader') {
            cy.get('[data-testid="view-sections"').then(($button) =>{
                if($button.text().includes('View All')){
                    $button.click();
                }
            });
        
    }
    // This gets a gradeable that has been graded already, so there are submissions available. 
    cy.get('[data-testid="grade-table"]').contains('/ 12').click({ force: true });
    // This is because some of the gradeables have the submission tab open
    cy.get('[data-testid="show-submission"]').then($element => {
        console.log($element.className);
        if($element.hasClass('active')){
            // do nothing
        } else {
            $element.click();
        }
    });

    cy.get('[data-testid="folders"]').contains('submissions').click();
    cy.get('#div_viewer_sd1').contains('words_').click();
    cy.get('#pageContainer1').should('be.visible');
    cy.logout();
}
);

const types = ['grading_homework_pdf', 'grading_homework_team_pdf', 'grading_pdf_peer_homework', 'grading_pdf_peer_team_homework'];

describe('Test cases for PDFs access', () => {
    before(() => {
        // cy.visit('/');
        // cy.login('instructor');
        // types.forEach((gradeable_id) => {
        //     cy.switch_settings(gradeable_id);
        // });
        // cy.logout();
    });

    after(() => {
        cy.visit('/');
        cy.login('instructor');
        types.forEach((gradeable_id) => {
            cy.revert_settings(gradeable_id);
        });
        cy.logout();
    });

    ['grader', 'ta', 'instructor'].forEach((user) => {
        it(`${user} should have access to pdfs`, () => {
            types.forEach((gradeable_id) => {
                cy.pdf_access(user, gradeable_id);
            });
            cy.login('student');
        });
    });
});
