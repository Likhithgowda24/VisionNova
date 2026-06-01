function initTheme() {
    const isLight = localStorage.getItem('theme') === 'light';
    if (isLight) {
        document.body.classList.add('light-theme');
    }
    
    // Find theme buttons by checking their innerHTML for the sun/moon icon
    document.querySelectorAll('.icon-btn').forEach(btn => {
        if(btn.innerHTML.includes('ri-sun-line') || btn.innerHTML.includes('ri-moon-line')) {
            const icon = btn.querySelector('i');
            if (icon) {
                // If Light theme, show Sun. If Dark theme, show Moon.
                icon.className = isLight ? 'ri-sun-line' : 'ri-moon-line';
            }
            
            // Remove old listeners to prevent duplicates if initTheme runs twice
            const newBtn = btn.cloneNode(true);
            btn.parentNode.replaceChild(newBtn, btn);
            
            newBtn.addEventListener('click', () => {
                document.body.classList.toggle('light-theme');
                const nowLight = document.body.classList.contains('light-theme');
                localStorage.setItem('theme', nowLight ? 'light' : 'dark');
                
                // Update icons
                document.querySelectorAll('.icon-btn i').forEach(i => {
                    if(i.className.includes('ri-sun-line') || i.className.includes('ri-moon-line')) {
                        i.className = nowLight ? 'ri-sun-line' : 'ri-moon-line';
                    }
                });
            });
        }
    });
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initTheme);
} else {
    initTheme();
}
