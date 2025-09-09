/**
 * Project Management JavaScript for DBGear Editor
 */

// Toggle project dropdown
function toggleProjectDropdown() {
    console.log('toggleProjectDropdown called');
    const dropdown = document.getElementById('projectDropdownMenu');
    const button = document.getElementById('projectDropdownBtn');
    
    console.log('dropdown:', dropdown);
    console.log('button:', button);
    
    if (dropdown && button) {
        console.log('Toggling dropdown visibility');
        dropdown.classList.toggle('hidden');
        
        // Close dropdown when clicking outside
        if (!dropdown.classList.contains('hidden')) {
            document.addEventListener('click', closeDropdownOnClickOutside);
        } else {
            document.removeEventListener('click', closeDropdownOnClickOutside);
        }
    }
}

// Close dropdown when clicking outside
function closeDropdownOnClickOutside(event) {
    const dropdown = document.getElementById('projectDropdownMenu');
    const button = document.getElementById('projectDropdownBtn');
    
    if (dropdown && button && 
        !dropdown.contains(event.target) && 
        !button.contains(event.target)) {
        dropdown.classList.add('hidden');
        document.removeEventListener('click', closeDropdownOnClickOutside);
    }
}

// Switch to a different project
async function switchProject(projectPath) {
    try {
        const response = await fetch('/api/projects/switch', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                project_path: projectPath
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            // Reload the page to update the UI
            window.location.reload();
        } else {
            alert('Failed to switch project: ' + result.error);
        }
    } catch (error) {
        alert('Error switching project: ' + error.message);
    }
}

// Open project modal
function openProjectModal() {
    console.log('openProjectModal called');
    // Close dropdown first
    const dropdown = document.getElementById('projectDropdownMenu');
    if (dropdown) {
        dropdown.classList.add('hidden');
    }
    
    console.log('Fetching modal content...');
    // Load and show modal
    fetch('/projects/modal')
        .then(response => response.text())
        .then(html => {
            const modalContainer = document.getElementById('projectModalContainer') || 
                                 document.createElement('div');
            modalContainer.id = 'projectModalContainer';
            modalContainer.innerHTML = html;
            
            if (!document.getElementById('projectModalContainer')) {
                document.body.appendChild(modalContainer);
            }
        })
        .catch(error => {
            alert('Error loading project modal: ' + error.message);
        });
}

// Close project modal
function closeProjectModal() {
    const modal = document.getElementById('projectModal');
    if (modal) {
        modal.remove();
    }
}

// Close modal when clicking backdrop
function closeProjectModalOnBackdrop(event) {
    if (event.target.id === 'projectModal') {
        closeProjectModal();
    }
}

// Browse for project path (placeholder - requires file system access)
function browseProjectPath() {
    // For now, just focus on the input field
    // In a real implementation, this would open a file browser
    const input = document.getElementById('newProjectPath');
    if (input) {
        input.focus();
    }
    
    alert('Please enter the project directory path manually. File browser integration requires additional setup.');
}

// Add new project
async function addNewProject() {
    const pathInput = document.getElementById('newProjectPath');
    const switchCheckbox = document.getElementById('switchToNew');
    
    if (!pathInput || !pathInput.value.trim()) {
        alert('Please enter a project path');
        return;
    }
    
    const projectPath = pathInput.value.trim();
    const shouldSwitch = switchCheckbox ? switchCheckbox.checked : true;
    
    try {
        const response = await fetch('/api/projects/add', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                project_path: projectPath,
                switch: shouldSwitch
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            if (shouldSwitch) {
                // Reload the page to update the UI
                window.location.reload();
            } else {
                // Close modal and refresh dropdown
                closeProjectModal();
                // Optionally refresh the header dropdown
                location.reload();
            }
        } else {
            alert('Failed to add project: ' + result.error);
        }
    } catch (error) {
        alert('Error adding project: ' + error.message);
    }
}

// Remove project from recent list
async function removeProject(projectPath) {
    if (!confirm('Remove this project from recent projects?')) {
        return;
    }
    
    try {
        const response = await fetch('/api/projects/remove', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                project_path: projectPath
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            // Reload the modal content
            openProjectModal();
        } else {
            alert('Failed to remove project: ' + result.error);
        }
    } catch (error) {
        alert('Error removing project: ' + error.message);
    }
}

// Handle keyboard shortcuts
document.addEventListener('keydown', function(event) {
    // Ctrl/Cmd + Shift + P to open project modal
    if ((event.ctrlKey || event.metaKey) && event.shiftKey && event.key === 'P') {
        event.preventDefault();
        openProjectModal();
    }
    
    // Escape to close modal
    if (event.key === 'Escape') {
        closeProjectModal();
    }
});