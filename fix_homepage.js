// Fix the homepage JavaScript functions
function openLoginModal() {
    console.log('Opening login modal...');
    // Create login modal if it doesn't exist
    if (!document.getElementById('loginModal')) {
        const modal = document.createElement('div');
        modal.id = 'loginModal';
        modal.className = 'modal';
        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h3>Login</h3>
                    <button class="close-btn" onclick="closeModal('loginModal')">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
                <div class="modal-body">
                    <form id="loginForm">
                        <div class="form-group">
                            <label for="loginEmail">Email</label>
                            <input type="email" id="loginEmail" name="email" required>
                        </div>
                        <div class="form-group">
                            <label for="loginPassword">Password</label>
                            <input type="password" id="loginPassword" name="password" required>
                        </div>
                        <div class="form-actions">
                            <button type="submit" class="btn-primary">Login</button>
                            <button type="button" class="btn-secondary" onclick="closeModal('loginModal')">Cancel</button>
                        </div>
                    </form>
                </div>
            </div>
        `;
        document.body.appendChild(modal);
    }
    document.getElementById('loginModal').style.display = 'block';
}

function openSignupModal() {
    console.log('Opening signup modal...');
    // Create signup modal if it doesn't exist
    if (!document.getElementById('signupModal')) {
        const modal = document.createElement('div');
        modal.id = 'signupModal';
        modal.className = 'modal';
        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h3>Sign Up</h3>
                    <button class="close-btn" onclick="closeModal('signupModal')">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
                <div class="modal-body">
                    <form id="signupForm">
                        <div class="form-group">
                            <label for="signupName">Full Name</label>
                            <input type="text" id="signupName" name="name" required>
                        </div>
                        <div class="form-group">
                            <label for="signupEmail">Email</label>
                            <input type="email" id="signupEmail" name="email" required>
                        </div>
                        <div class="form-group">
                            <label for="signupPassword">Password</label>
                            <input type="password" id="signupPassword" name="password" required>
                        </div>
                        <div class="form-group">
                            <label for="signupConfirmPassword">Confirm Password</label>
                            <input type="password" id="signupConfirmPassword" name="confirmPassword" required>
                        </div>
                        <div class="form-actions">
                            <button type="submit" class="btn-primary">Sign Up</button>
                            <button type="button" class="btn-secondary" onclick="closeModal('signupModal')">Cancel</button>
                        </div>
                    </form>
                </div>
            </div>
        `;
        document.body.appendChild(modal);
    }
    document.getElementById('signupModal').style.display = 'block';
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'none';
    }
}

// Add modal styles if they don't exist
if (!document.getElementById('modal-styles')) {
    const styleElement = document.createElement('style');
    styleElement.id = 'modal-styles';
    styleElement.textContent = `
        .modal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.8);
            z-index: 1000;
        }
        .modal-content {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: #1a1a1a;
            border-radius: 8px;
            border: 1px solid #333;
            min-width: 400px;
            max-width: 500px;
            max-height: 80vh;
            overflow-y: auto;
        }
        .modal-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 20px;
            border-bottom: 1px solid #333;
        }
        .modal-header h3 {
            color: #00ff85;
            font-size: 18px;
            margin: 0;
        }
        .close-btn {
            background: none;
            border: none;
            color: #ccc;
            font-size: 20px;
            cursor: pointer;
            padding: 5px;
        }
        .close-btn:hover {
            color: #fff;
        }
        .modal-body {
            padding: 20px;
        }
        .form-group {
            margin-bottom: 15px;
        }
        .form-group label {
            display: block;
            color: #cccccc;
            font-weight: bold;
            margin-bottom: 5px;
            text-transform: uppercase;
            letter-spacing: 1px;
            font-size: 12px;
        }
        .form-group input {
            width: 100%;
            padding: 12px 15px;
            background: #222;
            border: 1px solid #444;
            border-radius: 4px;
            color: #ffffff;
            font-size: 14px;
            box-sizing: border-box;
        }
        .form-group input:focus {
            outline: none;
            border-color: #00ff85;
            box-shadow: 0 0 5px rgba(0, 255, 133, 0.3);
        }
        .form-actions {
            display: flex;
            gap: 15px;
            justify-content: flex-end;
            margin-top: 20px;
        }
        .btn-primary, .btn-secondary {
            padding: 10px 20px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
            font-weight: bold;
            text-transform: uppercase;
            letter-spacing: 1px;
            transition: all 0.3s ease;
        }
        .btn-primary {
            background: #00ff85;
            color: #000;
        }
        .btn-primary:hover {
            background: #00cc6a;
        }
        .btn-secondary {
            background: #333;
            color: #fff;
            border: 1px solid #555;
        }
        .btn-secondary:hover {
            background: #444;
        }
    `;
    document.head.appendChild(styleElement);
}

// Make functions globally available
window.openLoginModal = openLoginModal;
window.openSignupModal = openSignupModal;
window.closeModal = closeModal;

console.log('Login and Signup functions loaded successfully');
