(function() {
    const sessionKey = 'splashPlayed_v6';
    const forceReplay = window.location.search.includes('replaySplash');
    
    if (sessionStorage.getItem(sessionKey) && !forceReplay) return;
    
    const style = document.createElement('style');
    style.innerHTML = `
        html.splash-active body { overflow: hidden !important; }
        #splash-screen {
            position: fixed; inset: 0; background: #000000; z-index: 2147483647; 
            display: flex; align-items: center; justify-content: center; 
            transition: opacity 0.8s ease-in-out, visibility 0.8s;
        }
        
        .splash-content {
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .logo-assembly {
            width: 320px;
            height: 320px;
            position: relative;
            flex-shrink: 0;
            filter: contrast(1.6) brightness(1.1);
        }

        .logo-slice {
            position: absolute;
            inset: 0;
            background-image: url('assets/app_logo.jpg');
            background-size: cover;
            background-position: center;
            mix-blend-mode: screen;
            border-radius: 50%;
        }

        .slice-1 {
            -webkit-mask-image: conic-gradient(from -62deg, black 124deg, transparent 124deg);
            mask-image: conic-gradient(from -62deg, black 124deg, transparent 124deg);
            animation: assembleSlice1 1.8s cubic-bezier(0.2, 0.8, 0.2, 1) forwards;
        }
        .slice-2 {
            -webkit-mask-image: conic-gradient(from 58deg, black 124deg, transparent 124deg);
            mask-image: conic-gradient(from 58deg, black 124deg, transparent 124deg);
            animation: assembleSlice2 1.8s cubic-bezier(0.2, 0.8, 0.2, 1) forwards;
        }
        .slice-3 {
            -webkit-mask-image: conic-gradient(from 178deg, black 124deg, transparent 124deg);
            mask-image: conic-gradient(from 178deg, black 124deg, transparent 124deg);
            animation: assembleSlice3 1.8s cubic-bezier(0.2, 0.8, 0.2, 1) forwards;
        }

        @keyframes assembleSlice1 {
            0% { transform: rotate(-240deg) scale(0); opacity: 0; filter: blur(30px); }
            100% { transform: rotate(0deg) scale(1); opacity: 1; filter: blur(0px); }
        }
        @keyframes assembleSlice2 {
            0% { transform: rotate(240deg) scale(0); opacity: 0; filter: blur(30px); }
            100% { transform: rotate(0deg) scale(1); opacity: 1; filter: blur(0px); }
        }
        @keyframes assembleSlice3 {
            0% { transform: rotate(-360deg) scale(0); opacity: 0; filter: blur(30px); }
            100% { transform: rotate(0deg) scale(1); opacity: 1; filter: blur(0px); }
        }

        .splash-name-container {
            width: 0;
            overflow: hidden;
            display: flex;
            align-items: center;
            animation: openTextContainer 1.2s cubic-bezier(0.25, 1, 0.5, 1) forwards;
            animation-delay: 2.2s;
        }
        
        @keyframes openTextContainer {
            0% { width: 0; margin-left: 0; opacity: 0; }
            100% { width: 720px; margin-left: 40px; opacity: 1; }
        }

        .splash-name {
            color: #fff; font-size: 104px; font-weight: 700; font-family: 'Inter', sans-serif;
            display: flex; gap: 15px;
            white-space: nowrap;
            animation: morphText 1.2s cubic-bezier(0.25, 1, 0.5, 1) forwards;
            animation-delay: 2.3s;
            opacity: 0;
            text-shadow: 0 20px 50px rgba(140,196,96,0.4);
        }

        @keyframes morphText {
            0% { transform: translateX(-60px); opacity: 0; filter: blur(25px); letter-spacing: -20px; }
            100% { transform: translateX(0); opacity: 1; filter: blur(0px); letter-spacing: 0px; }
        }
    `;
    document.head.appendChild(style);

    document.documentElement.classList.add('splash-active');

    const splash = document.createElement('div');
    splash.id = 'splash-screen';
    splash.innerHTML = `
        <div class="splash-content">
            <div class="logo-assembly">
                <div class="logo-slice slice-1"></div>
                <div class="logo-slice slice-2"></div>
                <div class="logo-slice slice-3"></div>
            </div>
            <div class="splash-name-container">
                <div class="splash-name">
                    <span>VisionNova</span> <span style="color:#8cc460;">AI</span>
                </div>
            </div>
        </div>
    `;
    
    document.documentElement.appendChild(splash);

    window.addEventListener('load', () => {
        setTimeout(() => {
            splash.style.opacity = '0';
            splash.style.visibility = 'hidden';
            document.documentElement.classList.remove('splash-active');
            setTimeout(() => {
                splash.remove();
                sessionStorage.setItem(sessionKey, 'true');
            }, 800);
        }, 4500);
    });
})();
