// Staff registration handler - integrates with main.js apiCall function
async function submitNewStaff() {
    const username = document.getElementById('staffUsername')?.value.trim();
    const password = document.getElementById('staffPassword')?.value.trim();
    const passwordConfirm = document.getElementById('staffPasswordConfirm')?.value.trim();
    const role = document.getElementById('staffRole')?.value || 'viewer';

    if (!username || !password || !passwordConfirm) {
        showAlert('يرجى ملء جميع الحقول!');
        return;
    }

    if (password !== passwordConfirm) {
        showAlert('كلمات المرور غير متطابقة!');
        return;
    }

    if (password.length < 6) {
        showAlert('كلمة المرور يجب أن تكون على الأقل 6 أحرف!');
        return;
    }

    // Use apiCall from main.js
    const data = await apiCall('/register-staff', 'POST', { username, password, role });
    if (data && data.status === 'success') {
        const modal = bootstrap.Modal.getInstance(document.getElementById('addStaffModal'));
        if (modal) modal.hide();
        const form = document.getElementById('addStaffForm');
        if (form) form.reset();
        showAlert('✅ ' + data.message, 'success');
        // Refresh staff list if needed
        if (typeof loadStaff === 'function') {
            loadStaff();
        }
    } else {
        showAlert('❌ خطأ: ' + (data ? data.message : 'تعذر تسجيل الموظف.'));
    }
}

// Initialize staff modal and event listeners
document.addEventListener('DOMContentLoaded', function() {
    const btnAddStaff = document.getElementById('btnAddStaff');
    const btnAddStaffProfile = document.getElementById('btnAddStaffProfile');
    const btnSaveStaff = document.getElementById('btn-save-staff');
    const addStaffForm = document.getElementById('addStaffForm');

    function openStaffModal() {
        if (addStaffForm) addStaffForm.reset();
        const modal = bootstrap.Modal.getOrCreateInstance(document.getElementById('addStaffModal'));
        if (modal) modal.show();
    }
    
    if (btnAddStaff) {
        btnAddStaff.addEventListener('click', openStaffModal);
    }

    if (btnAddStaffProfile) {
        btnAddStaffProfile.addEventListener('click', openStaffModal);
    }
    
    if (btnSaveStaff) {
        btnSaveStaff.addEventListener('click', submitNewStaff);
    }
    
    // Optional: Submit form with Enter key
    if (addStaffForm) {
        addStaffForm.addEventListener('keypress', function(event) {
            if (event.key === 'Enter') {
                event.preventDefault();
                submitNewStaff();
            }
        });
    }
});
