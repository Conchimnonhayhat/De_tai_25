/**
 * Workshop UI Main JavaScript File
 */

document.addEventListener('DOMContentLoaded', () => {
    const assignmentRows = document.getElementById('assignment-user-rows');
    const addAssignmentUser = document.getElementById('add-assignment-user');
    if (assignmentRows && addAssignmentUser) {
        addAssignmentUser.addEventListener('click', () => {
            if (assignmentRows.children.length >= 30) return;
            const row = assignmentRows.firstElementChild.cloneNode(true);
            const select = row.querySelector('select');
            select.removeAttribute('id');
            select.value = '';
            assignmentRows.appendChild(row);
            select.focus();
            addAssignmentUser.disabled = assignmentRows.children.length >= 30;
        });
        assignmentRows.addEventListener('click', event => {
            const removeButton = event.target.closest('[data-remove-assignee]');
            if (!removeButton || assignmentRows.children.length === 1) return;
            removeButton.closest('.assignment-user-row').remove();
            addAssignmentUser.disabled = false;
        });
        assignmentRows.closest('form').addEventListener('submit', event => {
            const selected = [...assignmentRows.querySelectorAll('select')].map(select => select.value);
            if (new Set(selected).size !== selected.length) {
                event.preventDefault();
                window.alert('Mỗi nhân viên chỉ được chọn một lần.');
            }
        });
    }
    document.querySelectorAll('form[data-confirm]').forEach(form => {
        form.addEventListener('submit', event => {
            if (!window.confirm(form.dataset.confirm)) event.preventDefault();
        });
    });
    // Auto-dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            alert.style.transition = 'opacity 0.5s ease';
            setTimeout(() => alert.remove(), 500);
        }, 5000);
    });

    // Theme Toggle Functionality (Dark / Light Mode)
    initThemeToggle();
});

function initThemeToggle() {
    const toggleBtn = document.getElementById('themeToggleBtn');
    const toggleIcon = document.getElementById('themeToggleIcon');
    if (!toggleBtn) return;

    function updateThemeUI(theme) {
        if (!toggleIcon) return;
        if (theme === 'dark') {
            toggleIcon.className = 'fa-solid fa-sun theme-toggle-icon';
            toggleBtn.title = 'Chuyển sang Chế độ Sáng';
            toggleBtn.setAttribute('aria-label', 'Chuyển sang Chế độ Sáng');
        } else {
            toggleIcon.className = 'fa-solid fa-moon theme-toggle-icon';
            toggleBtn.title = 'Chuyển sang Chế độ Tối';
            toggleBtn.setAttribute('aria-label', 'Chuyển sang Chế độ Tối');
        }
    }

    const currentTheme = document.documentElement.getAttribute('data-theme') || 'light';
    updateThemeUI(currentTheme);

    toggleBtn.addEventListener('click', () => {
        toggleBtn.classList.add('animating');
        setTimeout(() => toggleBtn.classList.remove('animating'), 500);

        const current = document.documentElement.getAttribute('data-theme');
        const nextTheme = current === 'dark' ? 'light' : 'dark';

        document.documentElement.setAttribute('data-theme', nextTheme);
        localStorage.setItem('theme', nextTheme);
        updateThemeUI(nextTheme);
    });
}
