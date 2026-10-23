document.addEventListener('submit', async (event) => {
    const form = event.target;
    const panel = form.closest('.structure-panel');

    if (!panel) {
        return;
    }

    event.preventDefault();
    const activeId = document.activeElement?.id;
    const submitter = event.submitter;
    const activeStackTab = panel.dataset.activeStackTab || 'operations';
    if (form.id === 'list-action-form') {
        const target = panel.querySelector('#target-node').value;
        form.querySelector('#list-action-value').value = target;
        form.querySelector('#list-action-target').value = target;
    }
    const formData = submitter
        ? new FormData(form, submitter)
        : new FormData(form);

    try {
        const response = await fetch(form.action || window.location.href, {
            method: form.method || 'POST',
            body: formData,
            headers: { 'X-Requested-With': 'XMLHttpRequest' },
        });

        if (!response.ok) {
            throw new Error(`The server returned HTTP ${response.status}.`);
        }

        const page = new DOMParser().parseFromString(await response.text(), 'text/html');
        const updatedPanel = page.querySelector('.structure-panel');

        if (!updatedPanel) {
            throw new Error('The server response did not include the updated structure.');
        }

        panel.replaceWith(updatedPanel);
        if (updatedPanel.classList.contains('stack-ui-panel')) {
            setStackTab(updatedPanel, activeStackTab);
        }
        if (activeId) {
            updatedPanel.querySelector(`#${CSS.escape(activeId)}`)?.focus({ preventScroll: true });
        }
    } catch (error) {
        let status = panel.querySelector('.form-status');
        if (!status) {
            status = document.createElement('p');
            status.className = 'form-status error';
            status.setAttribute('role', 'status');
            panel.prepend(status);
        }
        status.className = 'form-status error';
        status.textContent = `Could not update the result. ${error.message}`;
    }
});

document.addEventListener('click', (event) => {
    const exampleButton = event.target.closest('[data-random-infix-example]');
    if (exampleButton) {
        const infixPanel = exampleButton.closest('#infix-panel');
        const expressionInput = infixPanel?.querySelector('#infix-expression');
        const examples = [
            '(1 / 2) * 4',
            '3 + 4 * 2',
            '(8 - 3) * 2',
            '12 / (2 + 4)',
            '2 ^ 3 ^ 2',
            '(a + b) * c',
            '10 + 6 / 2',
            '5 * (3 + 2) - 4',
        ];

        if (expressionInput) {
            const availableExamples = examples.filter((example) => example !== expressionInput.value);
            const choices = availableExamples.length ? availableExamples : examples;
            expressionInput.value = choices[Math.floor(Math.random() * choices.length)];
            expressionInput.focus();
        }
        return;
    }

    const tab = event.target.closest('[data-stack-tab]');
    if (!tab) {
        return;
    }

    const panel = tab.closest('.stack-ui-panel');
    if (panel) {
        setStackTab(panel, tab.dataset.stackTab);
    }
});

function setStackTab(panel, selectedTab) {
    panel.dataset.activeStackTab = selectedTab;
    panel.querySelectorAll('[data-stack-tab]').forEach((tab) => {
        const isSelected = tab.dataset.stackTab === selectedTab;
        tab.setAttribute('aria-selected', String(isSelected));
        tab.tabIndex = isSelected ? 0 : -1;
    });
    panel.querySelectorAll('[data-stack-panel]').forEach((tabPanel) => {
        tabPanel.hidden = tabPanel.dataset.stackPanel !== selectedTab;
    });
}
