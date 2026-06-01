document.addEventListener('DOMContentLoaded', () => {
    // Inject Cropper.js CSS and JS safely
    const cropperCss = document.createElement('link');
    cropperCss.rel = 'stylesheet';
    cropperCss.href = 'https://cdnjs.cloudflare.com/ajax/libs/cropperjs/1.5.13/cropper.min.css';
    document.head.appendChild(cropperCss);

    const cropperJs = document.createElement('script');
    cropperJs.src = 'https://cdnjs.cloudflare.com/ajax/libs/cropperjs/1.5.13/cropper.min.js';
    document.head.appendChild(cropperJs);

    // Inject Modal HTML
    const modalHtml = `
    <div id="profile-modal" style="display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; z-index: 9999; background: rgba(0,0,0,0.7); backdrop-filter: blur(10px); align-items: center; justify-content: center;">
        <div style="background: rgba(4,6,4,0.85); border: 1px solid rgba(140,196,96,0.3); border-radius: 20px; padding: 40px; width: 400px; position: relative; color: #fff; box-shadow: 0 20px 40px rgba(0,0,0,0.5);">
            <i class="ri-close-line" id="close-profile-btn" style="position: absolute; top: 20px; right: 20px; font-size: 24px; cursor: pointer; color: #9ca3af;"></i>
            <h2 style="margin-bottom: 25px; font-weight: 500; text-align: center;">Edit Profile</h2>
            
            <div style="display: flex; flex-direction: column; align-items: center; margin-bottom: 30px;">
                <div id="profile-pic-wrapper" style="width: 120px; height: 120px; border-radius: 50%; border: 2px dashed rgba(140,196,96,0.5); display: flex; align-items: center; justify-content: center; overflow: hidden; cursor: pointer; position: relative; background: rgba(255,255,255,0.05); margin-bottom: 10px; transition: all 0.2s;">
                    <img id="profile-modal-img" src="" style="width: 100%; height: 100%; object-fit: cover; display: none;">
                    <span id="profile-modal-initials" style="font-size: 36px; color: #e0e0e0; font-weight: 500;"></span>
                    <div style="position: absolute; bottom: 0; left: 0; right: 0; background: rgba(0,0,0,0.6); padding: 5px 0; text-align: center; font-size: 11px; color: #8cc460; font-weight: 500;"><i class="ri-camera-fill"></i> Change</div>
                </div>
                <input type="file" id="profile-pic-upload" accept="image/*" style="display: none;">
                <p style="font-size: 12px; color: #9ca3af;">Click to upload a new photo</p>
            </div>

            <div style="margin-bottom: 25px;">
                <label style="display: block; margin-bottom: 8px; font-size: 13px; color: #9ca3af;">Full Name</label>
                <input type="text" id="profile-name-input" style="width: 100%; background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); color: #fff; padding: 12px 15px; border-radius: 10px; outline: none; font-size: 14px; transition: border-color 0.2s;">
            </div>
            
            <button id="save-profile-btn" style="width: 100%; background: linear-gradient(135deg, #44612a 0%, #5d813b 100%); color: #fff; border: 1px solid rgba(140,196,96,0.3); padding: 14px; border-radius: 10px; font-size: 14px; cursor: pointer; font-weight: 500; transition: all 0.2s;">Save Changes</button>
        </div>
    </div>
    
    <!-- Cropper Modal -->
    <div id="cropper-modal" style="display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; z-index: 10000; background: rgba(0,0,0,0.9); align-items: center; justify-content: center;">
        <div style="background: #111; padding: 20px; border-radius: 12px; max-width: 600px; width: 100%;">
            <div style="height: 400px; width: 100%; background: #000; margin-bottom: 20px; position: relative;">
                <img id="cropper-image" style="max-width: 100%; max-height: 100%; display: block;">
            </div>
            <div style="display: flex; justify-content: flex-end; gap: 15px;">
                <button id="cancel-crop-btn" style="background: rgba(255,255,255,0.1); color: #fff; border: none; padding: 10px 20px; border-radius: 8px; cursor: pointer;">Cancel</button>
                <button id="apply-crop-btn" style="background: #8cc460; color: #000; border: none; padding: 10px 20px; border-radius: 8px; cursor: pointer; font-weight: 600;">Crop & Apply</button>
            </div>
        </div>
    </div>
    `;

    document.body.insertAdjacentHTML('beforeend', modalHtml);

    const profileModal = document.getElementById('profile-modal');
    const cropperModal = document.getElementById('cropper-modal');
    const closeProfileBtn = document.getElementById('close-profile-btn');
    const saveProfileBtn = document.getElementById('save-profile-btn');
    
    const picWrapper = document.getElementById('profile-pic-wrapper');
    const picUpload = document.getElementById('profile-pic-upload');
    const nameInput = document.getElementById('profile-name-input');
    const modalImg = document.getElementById('profile-modal-img');
    const modalInitials = document.getElementById('profile-modal-initials');
    
    let cropper = null;
    let newAvatarBase64 = null;

    // Attach click to the sidebar profile section
    document.querySelectorAll('.user-profile').forEach(btn => {
        btn.style.cursor = 'pointer';
        btn.title = 'Edit Profile';
        btn.addEventListener('click', () => {
            const currentUser = JSON.parse(localStorage.getItem('currentUser')) || {};
            nameInput.value = currentUser.fullname || 'Likhith Gowda M A';
            
            if (currentUser.avatarData) {
                modalImg.src = currentUser.avatarData;
                modalImg.style.display = 'block';
                modalInitials.style.display = 'none';
            } else {
                const parts = nameInput.value.split(' ');
                modalInitials.textContent = (parts[0][0] + (parts.length > 1 ? parts[parts.length-1][0] : '')).toUpperCase();
                modalImg.style.display = 'none';
                modalInitials.style.display = 'block';
            }
            
            profileModal.style.display = 'flex';
        });
    });

    closeProfileBtn.addEventListener('click', () => {
        profileModal.style.display = 'none';
    });

    // Picture Upload
    picWrapper.addEventListener('click', () => {
        picUpload.click();
    });

    picWrapper.addEventListener('mouseover', () => picWrapper.style.borderColor = '#8cc460');
    picWrapper.addEventListener('mouseout', () => picWrapper.style.borderColor = 'rgba(140,196,96,0.5)');
    nameInput.addEventListener('focus', () => nameInput.style.borderColor = 'rgba(140,196,96,0.5)');
    nameInput.addEventListener('blur', () => nameInput.style.borderColor = 'rgba(255,255,255,0.1)');

    picUpload.addEventListener('change', (e) => {
        if (e.target.files && e.target.files[0]) {
            const reader = new FileReader();
            reader.onload = (e) => {
                document.getElementById('cropper-image').src = e.target.result;
                profileModal.style.display = 'none';
                cropperModal.style.display = 'flex';
                
                if (cropper) { cropper.destroy(); }
                
                let checkCropper = setInterval(() => {
                    if (window.Cropper) {
                        clearInterval(checkCropper);
                        cropper = new Cropper(document.getElementById('cropper-image'), {
                            aspectRatio: 1,
                            viewMode: 1,
                            dragMode: 'move',
                            background: false,
                            autoCropArea: 0.8
                        });
                    }
                }, 100);
            };
            reader.readAsDataURL(e.target.files[0]);
        }
    });

    document.getElementById('cancel-crop-btn').addEventListener('click', () => {
        cropperModal.style.display = 'none';
        profileModal.style.display = 'flex';
        if (cropper) cropper.destroy();
        picUpload.value = '';
    });

    document.getElementById('apply-crop-btn').addEventListener('click', () => {
        if (cropper) {
            const canvas = cropper.getCroppedCanvas({
                width: 250,
                height: 250,
                fillColor: '#fff'
            });
            newAvatarBase64 = canvas.toDataURL('image/jpeg', 0.8);
            
            modalImg.src = newAvatarBase64;
            modalImg.style.display = 'block';
            modalInitials.style.display = 'none';
            
            cropper.destroy();
        }
        cropperModal.style.display = 'none';
        profileModal.style.display = 'flex';
    });

    saveProfileBtn.addEventListener('click', () => {
        const currentUser = JSON.parse(localStorage.getItem('currentUser')) || {};
        currentUser.fullname = nameInput.value.trim();
        if (newAvatarBase64) {
            currentUser.avatarData = newAvatarBase64;
        }
        localStorage.setItem('currentUser', JSON.stringify(currentUser));
        
        updateGlobalUI(currentUser);
        profileModal.style.display = 'none';
    });

    function updateGlobalUI(user) {
        document.querySelectorAll('#nav-name').forEach(el => el.textContent = user.fullname);
        
        const parts = user.fullname.split(' ');
        const initials = (parts[0][0] + (parts.length > 1 ? parts[parts.length-1][0] : '')).toUpperCase();
        
        document.querySelectorAll('.avatar').forEach(el => {
            el.style.padding = '0'; // reset padding if image is used
            if (user.avatarData) {
                el.innerHTML = `<img src="${user.avatarData}" style="width:100%;height:100%;border-radius:50%;object-fit:cover;">`;
            } else {
                el.innerHTML = initials;
            }
        });
        
        // Update main welcome heading
        const welcomeText = document.getElementById('welcome-text');
        if (welcomeText) {
            welcomeText.innerHTML = `Welcome back, ${parts[0]} <img src="assets/app_logo.jpg" alt="Logo" style="width: 1.4em; height: 1.4em; mix-blend-mode: screen; filter: contrast(1.5) brightness(1.2); -webkit-mask-image: radial-gradient(circle at center, black 65%, transparent 85%); mask-image: radial-gradient(circle at center, black 65%, transparent 85%);">`;
        }
    }

    // Auto-load avatar on page boot
    setTimeout(() => {
        const user = JSON.parse(localStorage.getItem('currentUser'));
        if (user && user.avatarData) {
            updateGlobalUI(user);
        }
    }, 300);
});
