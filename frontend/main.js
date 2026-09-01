// -------------------------
// Global Variables
// -------------------------
const API_URL = (() => {
    if (window.location.protocol.startsWith('http')) {
        const host = window.location.hostname;
        const port = window.location.port ? `:${window.location.port}` : '';
        return `${window.location.protocol}//${host}${port}/api`;
    }
    return 'http://127.0.0.1:5000/api';
})();

let actionModal;
let addSubModal;
let addAreaModal;
let addStaffModal;
let logFilterModal;
let selectedSubscriberId = null;
let selectedSubscriberData = null;
let isInlineEditingSubscriber = false;
let allSubscribers = [];
let totalSubscribersOverall = 0;
let totalDebtOverall = 0;
let subscribersRequestId = 0;
let allLogs = [];
let allAreas = [];
let currentSubscriberDebt = 0;
let currentSubscriberPage = 1;
let totalSubscriberPages = 1;
let currentLogsPage = 1;
let totalLogsPages = 1;
let currentLogFilter = 'الكل';
let logFilterStartDate = '';
let logFilterEndDate = '';
let activeLogSubscriberId = null;
let isActionSubmitting = false;
let subscriberFilters = {
    search: '',
    debtOnly: false,
    renewalFrom: '',
    renewalTo: ''
};
const subscribersPerPage = 50;
const logsPerPage = 100;

const dom = {
    loginPage: document.getElementById('loginPage'),
    appContainer: document.getElementById('appContainer'),
    loginForm: document.getElementById('loginForm'),
    loginUsername: document.getElementById('loginUsername'),
    loginPassword: document.getElementById('loginPassword'),
    loginMessage: document.getElementById('loginMessage'),
    btnLogout: document.getElementById('btnLogout'),
    btnProfileInfo: document.getElementById('btnProfileInfo'),
    profileInfoCard: document.getElementById('profileInfoCard'),
    profileUsername: document.getElementById('profileUsername'),
    profileRole: document.getElementById('profileRole'),
    profileAreasCount: document.getElementById('profileAreasCount'),
    btnProfileAreas: document.getElementById('btnProfileAreas'),
    btnMyTeam: document.getElementById('btnMyTeam'),
    btnAddStaffProfile: document.getElementById('btnAddStaffProfile'),
    teamAddStaffWrapper: document.getElementById('teamAddStaffWrapper'),
    totalSubscribers: document.getElementById('total-subscribers'),
    todayIncome: document.getElementById('today-income'),
    totalDebt: document.getElementById('total-debt'),
    searchInput: document.getElementById('searchInput'),
    debtOnlyFilter: document.getElementById('debtOnlyFilter'),
    renewalFromFilter: document.getElementById('renewalFromFilter'),
    renewalToFilter: document.getElementById('renewalToFilter'),
    btnApplySubscriberFilters: document.getElementById('btnApplySubscriberFilters'),
    btnResetSubscriberFilters: document.getElementById('btnResetSubscriberFilters'),
    subscriberFiltersSummary: document.getElementById('subscriberFiltersSummary'),
    subscribersTableBody: document.getElementById('subscribers-table-body'),
    logsTableBody: document.getElementById('logs-table-body'),
    tabDashboard: document.getElementById('tab-dashboard'),
    tabSubscribers: document.getElementById('tab-subscribers'),
    tabLogs: document.getElementById('tab-logs'),
    tabMonthlyReport: document.getElementById('tab-monthly-report'),
    dashboardSection: document.getElementById('dashboard'),
    subscribersSection: document.getElementById('subscribers'),
    areasSection: document.getElementById('areas'),
    logsSection: document.getElementById('logs'),
    monthlyReportPeriod: document.getElementById('monthlyReportPeriod'),
    btnLoadMonthlyReport: document.getElementById('btnLoadMonthlyReport'),
    monthlyReportMessage: document.getElementById('monthlyReportMessage'),
    monthlyReportTableBody: document.getElementById('monthlyReportTableBody'),
    monthlyTotalCollected: document.getElementById('monthlyTotalCollected'),
    monthlyCashReceived: document.getElementById('monthlyCashReceived'),
    monthlyElectronicReceived: document.getElementById('monthlyElectronicReceived'),
    monthlyRenewalsAmount: document.getElementById('monthlyRenewalsAmount'),
    monthlyPaymentsCount: document.getElementById('monthlyPaymentsCount'),
    monthlyRenewalsCount: document.getElementById('monthlyRenewalsCount'),
    monthlyActiveDaysCount: document.getElementById('monthlyActiveDaysCount'),
    btnTodayPromises: document.getElementById('btn-today-promises'),
    btnAddSubscriber: document.getElementById('btn-add-subscriber'),
    btnAddArea: document.getElementById('btn-add-area'),
    btnSaveArea: document.getElementById('btn-save-area'),
    newAreaName: document.getElementById('newAreaName'),
    todayPayments: document.getElementById('today-payments'),
    todayRenewals: document.getElementById('today-renewals'),
    reportStatusBadge: document.getElementById('report-status-badge'),
    reportStatusMessage: document.getElementById('report-status-msg'),
    btnOpenLogFilter: document.getElementById('btn-open-log-filter'),
    btnApplyLogFilter: document.getElementById('btnApplyLogFilter'),
    btnClearLogFilter: document.getElementById('btnClearLogFilter'),
    logFilterSubscriberId: document.getElementById('logFilterSubscriberId'),
    btnCopyDetails: document.getElementById('btn-copy-details'),
    btnDeleteSub: document.getElementById('btn-delete-sub'),
    btnViewSubscriberLogs: document.getElementById('btn-view-subscriber-logs'),
    btnEditSub: document.getElementById('btn-edit-sub'),
    btnCloseDetails: document.getElementById('btn-close-details'),
    btnCancelInlineEdit: document.getElementById('btn-cancel-inline-edit'),
    btnSaveEdit: document.getElementById('btn-save-edit'),
    btnSaveNew: document.getElementById('btn-save-new'),
    confirmBtn: document.getElementById('confirmBtn'),
    quickPromiseInput: document.getElementById('quick-detail-promise'),
    amountInput: document.getElementById('amountInput'),
    fullDebtBtn: document.getElementById('fullDebtBtn'),
    isCashCheckbox: document.getElementById('isCashCheckbox'),
    cashPaymentDiv: document.getElementById('cashPaymentDiv'),
    paymentMethodDiv: document.getElementById('paymentMethodDiv'),
    paymentMethod: document.getElementById('paymentMethod'),
    promiseDateInput: document.getElementById('promiseDate'),
    addSubscriberForm: document.getElementById('addSubscriberForm'),
    editSubscriberForm: document.getElementById('editSubscriberForm'),
    addAreaId: document.getElementById('addAreaId'),
    editAreaId: document.getElementById('editAreaId'),
    subscriberDetailView: document.getElementById('subscriberDetailView'),
    detailModalTitle: document.getElementById('detailModalTitle'),
    detailsModalContent: document.querySelector('#detailsModal .modal-content'),
    detailName: document.getElementById('detail-name'),
    detailId: document.getElementById('detail-id'),
    detailArea: document.getElementById('detail-area'),
    detailPhone: document.getElementById('detail-phone'),
    detailBalance: document.getElementById('detail-balance'),
    detailNotes: document.getElementById('detail-notes'),
    areasTableBody: document.getElementById('areas-table-body'),
    subscriberPageInfo: document.getElementById('subscriberPageInfo'),
    btnPrevPage: document.getElementById('btn-prev-page'),
    btnNextPage: document.getElementById('btn-next-page'),
    logsPageInfo: document.getElementById('logsPageInfo'),
    btnPrevLogsPage: document.getElementById('btn-prev-logs-page'),
    btnNextLogsPage: document.getElementById('btn-next-logs-page')
};

function buildUrl(endpoint) {
    const trimmed = endpoint.trim();
    const normalized = trimmed.startsWith('/api') ? trimmed.slice(4) : trimmed;
    return normalized.startsWith('/') ? `${API_URL}${normalized}` : `${API_URL}/${normalized}`;
}

function normalizeSubscriber(sub) {
    if (!sub || typeof sub !== 'object') return sub;

    return {
        ...sub,
        phone_number: sub.phone_number ?? sub.phone ?? '',
        phone: sub.phone ?? sub.phone_number ?? '',
        area_name: sub.area_name ?? sub.area ?? '',
        area: sub.area ?? sub.area_name ?? '',
        last_renewal_date: sub.last_renewal_date ?? '',
        promise_date: sub.promise_date ?? '',
        notes: sub.notes ?? ''
    };
}

function normalizeLog(log) {
    if (!log || typeof log !== 'object') return null;

    const rawType = String(log.type ?? log.transaction_type ?? '').toLowerCase();
    const normalizedType = rawType === 'payment' || rawType === 'تسديد'
        ? 'تسديد'
        : rawType === 'renewal' || rawType === 'تجديد'
            ? 'تجديد'
            : (log.type || 'غير معروف');

    const amountValue = Number(log.amount ?? log.value ?? 0);

    return {
        type: normalizedType,
        subscriber_id: log.subscriber_id ?? log.subscriberId ?? null,
        subscriber_name: log.subscriber_name ?? log.subscriber ?? log.name ?? 'غير معروف',
        processed_by: log.processed_by ?? log.processed_by_name ?? log.user_name ?? log.actor_name ?? 'غير معروف',
        amount: Number.isFinite(amountValue) ? amountValue : 0,
        date: log.date ?? log.transaction_date ?? ''
    };
}

function getBaghdadYearMonth() {
    const baghdadParts = new Intl.DateTimeFormat('en-CA', {
        timeZone: 'Asia/Baghdad',
        year: 'numeric',
        month: '2-digit'
    }).formatToParts(new Date());
    const values = Object.fromEntries(
        baghdadParts
            .filter(({ type }) => type !== 'literal')
            .map(({ type, value }) => [type, value])
    );

    return `${values.year}-${values.month}`;
}

function formatBaghdadDateTime(value) {
    const dateText = String(value || '').trim();
    if (!dateText) return '';

    // Naive values are already Baghdad wall-clock times from the API.
    if (!/[zZ]$|[+-]\d{2}:?\d{2}$/.test(dateText)) {
        return dateText.replace('T', ' ').slice(0, 19);
    }

    const date = new Date(dateText);
    if (Number.isNaN(date.getTime())) return dateText.replace('T', ' ').slice(0, 19);

    return new Intl.DateTimeFormat('en-CA', {
        timeZone: 'Asia/Baghdad',
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        hourCycle: 'h23'
    }).format(date).replace(',', '');
}

function requestOptions(method = 'GET', body = null) {
    const headers = { 'Content-Type': 'application/json' };
    const token = localStorage.getItem('token');
    if (token) {
        headers.Authorization = `Bearer ${token}`;
    }
    const options = { method, headers };
    if (body !== null) {
        options.body = JSON.stringify(body);
    }
    return options;
}

async function apiCall(endpoint, method = 'GET', body = null) {
    try {
        const response = await fetch(buildUrl(endpoint), requestOptions(method, body));
        if (response.status === 401) {
            localStorage.removeItem('token');
            showLogin();
            showAlert('لا تملك صلاحية للوصول! يرجى تسجيل الدخول أولاً.');
            return null;
        }
        const data = await response.json().catch(() => null);
        if (!response.ok) {
            showAlert(data?.message || `فشل الطلب (${response.status})`, 'danger');
            return data || { status: 'error', message: `فشل الطلب (${response.status})` };
        }
        return data;
    } catch (error) {
        console.error('Network Error:', error);
        return {
            status: 'error',
            message: 'تعذر الاتصال بالخادم. تأكد من تشغيل الباك اند وفتح الصفحة من عنوان الخادم.'
        };
    }
}

function ensureToastContainer() {
    let container = document.getElementById('appToastContainer');
    if (container) return container;

    container = document.createElement('div');
    container.id = 'appToastContainer';
    container.className = 'toast-container position-fixed top-0 start-50 translate-middle-x p-3';
    container.style.zIndex = '2000';
    document.body.appendChild(container);
    return container;
}

function restoreModalFocus() {
    const activeModal = document.querySelector('.modal.show');
    if (!activeModal) return;

    const firstInput = activeModal.querySelector('input, select, textarea, button');
    if (firstInput && typeof firstInput.focus === 'function') {
        firstInput.focus({ preventScroll: true });
    }
}

function showAlert(message, type = 'danger') {
    const container = ensureToastContainer();
    const tone = ['success', 'warning', 'info', 'danger'].includes(type) ? type : 'danger';
    const toastEl = document.createElement('div');

    toastEl.className = `toast align-items-center text-bg-${tone} border-0`;
    toastEl.setAttribute('role', 'alert');
    toastEl.setAttribute('aria-live', 'assertive');
    toastEl.setAttribute('aria-atomic', 'true');
    toastEl.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">${message}</div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
    `;

    container.appendChild(toastEl);
    const toast = new bootstrap.Toast(toastEl, { delay: 3500 });

    toastEl.addEventListener('hidden.bs.toast', () => {
        toastEl.remove();
    }, { once: true });

    toast.show();
    setTimeout(restoreModalFocus, 30);
}

function normalizeRole(role) {
    return typeof role === 'string' ? role.trim().toLowerCase() : '';
}

function getRoleLabel(role) {
    const normalizedRole = normalizeRole(role);

    if (normalizedRole === 'super_admin') return 'مدير عام';
    if (normalizedRole === 'admin') return 'مدير';
    if (normalizedRole === 'editor') return 'محرر';
    if (normalizedRole === 'commenter') return 'معلق';
    if (normalizedRole === 'viewer') return 'مشاهد';
    return 'موظف';
}

function canManageStaff(role) {
    const normalizedRole = normalizeRole(role);
    return normalizedRole === 'admin';
}

function canManageContent(role) {
    const normalizedRole = normalizeRole(role);
    return normalizedRole === 'admin' || normalizedRole === 'editor' || normalizedRole === 'super_admin';
}

function canProcessTransactions(role) {
    const normalizedRole = normalizeRole(role);
    return normalizedRole === 'admin' || normalizedRole === 'editor';
}

function canEditSubscribers(role) {
    const normalizedRole = normalizeRole(role);
    return normalizedRole === 'admin' || normalizedRole === 'editor' || normalizedRole === 'commenter';
}

function canViewAuditLog(role) {
    const normalizedRole = normalizeRole(role);
    return normalizedRole === 'admin' || normalizedRole === 'editor';
}

async function copyPhoneToClipboard(phone) {
    if (!phone || phone === 'لا يوجد رقم') return false;

    const cleanPhone = String(phone).trim();

    try {
        if (navigator.clipboard && window.isSecureContext) {
            await navigator.clipboard.writeText(cleanPhone);
        } else {
            const tempInput = document.createElement('textarea');
            tempInput.value = cleanPhone;
            tempInput.setAttribute('readonly', '');
            tempInput.style.position = 'fixed';
            tempInput.style.left = '-9999px';
            document.body.appendChild(tempInput);
            tempInput.select();
            document.execCommand('copy');
            document.body.removeChild(tempInput);
        }

        if (window.matchMedia('(pointer: coarse)').matches) {
            window.location.href = `tel:${cleanPhone}`;
        }
        return true;
    } catch (error) {
        console.error('Copy phone failed:', error);
        return false;
    }
}

function decodeJwtRole(token) {
    if (!token) return '';
    try {
        const payload = token.split('.')[1];
        if (!payload) return '';
        const normalized = payload.replace(/-/g, '+').replace(/_/g, '/');
        const padded = normalized + '='.repeat((4 - (normalized.length % 4)) % 4);
        return JSON.parse(atob(padded))?.role || '';
    } catch (error) {
        console.warn('Unable to decode JWT role:', error);
        return '';
    }
}

function getCurrentRole() {
    const storedRole = localStorage.getItem('userRole');
    const token = localStorage.getItem('token');
    const decodedRole = decodeJwtRole(token);
    return normalizeRole(decodedRole || storedRole || 'viewer');
}

function redirectForRole(role) {
    const normalizedRole = normalizeRole(role);
    if (normalizedRole === 'super_admin') {
        window.location.href = './super_dashboard.html';
        return true;
    }
    return false;
}

function showLogin() {
    dom.loginPage.classList.remove('d-none');
    dom.appContainer.classList.add('d-none');
    dom.btnProfileInfo.classList.add('d-none');
    dom.profileInfoCard.classList.add('d-none');
    dom.btnLogout.classList.add('d-none');
    dom.loginMessage.innerText = '';
    dom.loginForm.reset();
}

function showApp() {
    dom.loginPage.classList.add('d-none');
    dom.appContainer.classList.remove('d-none');
    dom.btnProfileInfo.classList.remove('d-none');
    dom.btnLogout.classList.remove('d-none');

    const userRole = getCurrentRole();
    localStorage.setItem('userRole', userRole);
    const username = localStorage.getItem('username') || 'غير معروف';
    dom.profileUsername.innerText = username;
    dom.profileRole.innerText = getRoleLabel(userRole);
    dom.profileAreasCount.innerText = Array.isArray(allAreas) ? allAreas.length : 0;

    const canManageStaffOnly = canManageStaff(userRole);
    const canManageContentOnly = canManageContent(userRole);
    const canViewAuditLogOnly = canViewAuditLog(userRole);

    if (dom.btnAddStaff) {
        dom.btnAddStaff.classList.toggle('d-none', !canManageStaffOnly);
    }

    if (dom.teamAddStaffWrapper) {
        dom.teamAddStaffWrapper.classList.toggle('d-none', !canManageStaffOnly);
    }

    if (dom.btnAddSubscriber) {
        dom.btnAddSubscriber.classList.toggle('d-none', !canManageContentOnly);
    }

    if (dom.btnAddArea) {
        dom.btnAddArea.classList.toggle('d-none', !canManageContentOnly);
    }

    if (dom.tabLogs) {
        dom.tabLogs.classList.toggle('d-none', !canViewAuditLogOnly);
    }

    if (dom.tabMonthlyReport) {
        dom.tabMonthlyReport.classList.toggle('d-none', !canViewAuditLogOnly);
    }

    if (dom.btnViewSubscriberLogs) {
        dom.btnViewSubscriberLogs.classList.toggle('d-none', !canViewAuditLogOnly);
    }

    if (dom.btnSaveNew) {
        dom.btnSaveNew.disabled = !canManageContentOnly;
    }

    if (dom.btnSaveEdit) {
        dom.btnSaveEdit.disabled = !canManageContentOnly;
    }

    if (dom.btnDeleteSub) {
        dom.btnDeleteSub.disabled = !canManageContentOnly;
    }
}

function initPage() {
    actionModal = new bootstrap.Modal(document.getElementById('actionModal'));
    addSubModal = new bootstrap.Modal(document.getElementById('addSubscriberModal'));
    addAreaModal = new bootstrap.Modal(document.getElementById('addAreaModal'));
    addStaffModal = new bootstrap.Modal(document.getElementById('addStaffModal'));
    logFilterModal = new bootstrap.Modal(document.getElementById('logFilterModal'));
    if (dom.monthlyReportPeriod) {
        dom.monthlyReportPeriod.value = getBaghdadYearMonth();
    }
    registerEventListeners();
    loadInitialState();
}

function setDetailsModalMode(isEditing) {
    if (dom.detailsModalContent) {
        dom.detailsModalContent.classList.toggle('is-editing', Boolean(isEditing));
    }

    if (dom.detailModalTitle) {
        dom.detailModalTitle.innerHTML = isEditing
            ? '<i class="fa-solid fa-pen-to-square text-primary"></i> تعديل بيانات المشترك'
            : '<i class="fa-solid fa-id-card text-primary"></i> بطاقة المشترك';
    }
}

function syncSubscriberFiltersFromDom() {
    subscriberFilters = {
        search: dom.searchInput?.value.trim() || '',
        debtOnly: Boolean(dom.debtOnlyFilter?.checked),
        renewalFrom: dom.renewalFromFilter?.value || '',
        renewalTo: dom.renewalToFilter?.value || ''
    };
}

function updateSubscriberFilterSummary() {
    if (!dom.subscriberFiltersSummary) return;

    const summaryParts = [];

    if (subscriberFilters.search) {
        summaryParts.push(`بحث: ${subscriberFilters.search}`);
    }

    if (subscriberFilters.debtOnly) {
        summaryParts.push('المديونون فقط');
    }

    if (subscriberFilters.renewalFrom || subscriberFilters.renewalTo) {
        const fromLabel = subscriberFilters.renewalFrom || 'البداية';
        const toLabel = subscriberFilters.renewalTo || 'الآن';
        summaryParts.push(`آخر اشتراك من ${fromLabel} إلى ${toLabel}`);
    }

    dom.subscriberFiltersSummary.innerText = summaryParts.length
        ? `الفلاتر الحالية: ${summaryParts.join(' | ')}`
        : 'الفلاتر الحالية: الكل';
}

function hasValidSubscriberDateRange() {
    const { renewalFrom, renewalTo } = subscriberFilters;
    if (renewalFrom && renewalTo && renewalFrom > renewalTo) {
        showAlert('تاريخ البداية يجب أن يكون أقدم أو يساوي تاريخ النهاية.', 'warning');
        return false;
    }
    return true;
}

function buildSubscriberQueryParams(page = 1) {
    const params = new URLSearchParams({
        page: String(page),
        per_page: String(subscribersPerPage)
    });

    if (subscriberFilters.search) {
        params.set('search', subscriberFilters.search);
    }

    if (subscriberFilters.debtOnly) {
        params.set('debt_only', 'true');
    }

    if (subscriberFilters.renewalFrom) {
        params.set('renewal_from', subscriberFilters.renewalFrom);
    }

    if (subscriberFilters.renewalTo) {
        params.set('renewal_to', subscriberFilters.renewalTo);
    }

    return params;
}

function registerEventListeners() {
    dom.loginForm.addEventListener('submit', handleLogin);
    document.getElementById('editStaffForm')?.addEventListener('submit', submitStaffUpdate);
    document.addEventListener('click', (event) => {
        const editButton = event.target.closest('.edit-staff-btn');
        if (editButton) openEditStaffModal(editButton);
    });
    dom.btnProfileInfo.addEventListener('click', (event) => {
        event.stopPropagation();
        dom.profileInfoCard.classList.toggle('d-none');
    });
    document.addEventListener('click', (event) => {
        const clickedInsideProfile = dom.profileInfoCard.contains(event.target) || dom.btnProfileInfo.contains(event.target);
        if (!clickedInsideProfile) {
            dom.profileInfoCard.classList.add('d-none');
        }
    });
    dom.btnProfileAreas.addEventListener('click', () => {
        dom.profileInfoCard.classList.add('d-none');
        switchSection('areas');
        if (addAreaModal) addAreaModal.show();
    });
    if (dom.btnMyTeam) {
        dom.btnMyTeam.addEventListener('click', (event) => {
            event.stopPropagation();
            openTeamModal();
        });
    }
    dom.btnLogout.addEventListener('click', logoutUser);
    dom.tabDashboard.addEventListener('click', () => switchSection('dashboard'));
    dom.tabSubscribers.addEventListener('click', () => {
        switchSection('subscribers');
        loadSubscribers(1);
    });
    dom.tabLogs.addEventListener('click', () => {
        if (canViewAuditLog(getCurrentRole())) {
            switchSection('logs');
        }
    });
    if (dom.tabMonthlyReport) {
        dom.tabMonthlyReport.addEventListener('click', () => {
            if (canViewAuditLog(getCurrentRole())) {
                switchSection('monthly-report');
                loadMonthlyReport();
            }
        });
    }
    if (dom.btnLoadMonthlyReport) {
        dom.btnLoadMonthlyReport.addEventListener('click', loadMonthlyReport);
    }
    dom.searchInput.addEventListener('input', filterSubscribers);
    if (dom.debtOnlyFilter) {
        dom.debtOnlyFilter.addEventListener('change', filterSubscribers);
    }
    if (dom.btnApplySubscriberFilters) {
        dom.btnApplySubscriberFilters.addEventListener('click', filterSubscribers);
    }
    if (dom.btnResetSubscriberFilters) {
        dom.btnResetSubscriberFilters.addEventListener('click', resetSubscriberFilters);
    }
    if (dom.btnTodayPromises) {
        dom.btnTodayPromises.addEventListener('click', loadPromisesToday);
    }
    dom.btnAddSubscriber.addEventListener('click', openAddSubscriberModal);
    dom.btnAddArea.addEventListener('click', () => addAreaModal.show());
    dom.btnSaveArea.addEventListener('click', submitNewArea);
    document.addEventListener('click', async (event) => {
        const editButton = event.target.closest('.edit-area-btn');
        if (!editButton) return;

        const areaId = Number(editButton.dataset.areaId);
        const currentName = editButton.dataset.areaName || '';
        const newName = window.prompt('اكتب الاسم الجديد للمنطقة:', currentName);

        if (newName === null) return;

        const trimmedName = newName.trim();
        if (!trimmedName) {
            showAlert('يرجى إدخال اسم المنطقة.', 'warning');
            return;
        }

        const data = await apiCall(`/areas/${areaId}`, 'PUT', { name: trimmedName });
        if (data && data.status === 'success') {
            showAlert(data.message || 'تم تحديث اسم المنطقة بنجاح.', 'success');
            loadAreas();
        } else {
            showAlert(data?.message || 'فشل تحديث اسم المنطقة.', 'danger');
        }
    });
    if (dom.btnOpenLogFilter) {
        dom.btnOpenLogFilter.addEventListener('click', () => logFilterModal.show());
    }
    if (dom.btnApplyLogFilter) {
        dom.btnApplyLogFilter.addEventListener('click', () => {
            const startDate = document.getElementById('logFilterStartDate').value;
            const endDate = document.getElementById('logFilterEndDate').value;
            const subscriberIdInput = document.getElementById('logFilterSubscriberId').value.trim();
            logFilterStartDate = startDate;
            logFilterEndDate = endDate;
            activeLogSubscriberId = subscriberIdInput ? Number(subscriberIdInput) : null;

            if (!validateLogDateRange()) {
                return;
            }

            if (activeLogSubscriberId) {
                loadLogs(1, activeLogSubscriberId);
            } else {
                filterLogs(currentLogFilter);
            }
            logFilterModal.hide();
        });
    }
    if (dom.btnClearLogFilter) {
        dom.btnClearLogFilter.addEventListener('click', () => {
            logFilterStartDate = '';
            logFilterEndDate = '';
            activeLogSubscriberId = null;
            const subscriberIdInput = document.getElementById('logFilterSubscriberId');
            if (subscriberIdInput) subscriberIdInput.value = '';
            document.getElementById('logFilterStartDate').value = '';
            document.getElementById('logFilterEndDate').value = '';
            currentLogFilter = 'الكل';
            updateLogFilterButtonLabel();
            loadLogs(1);
            logFilterModal.hide();
        });
    }
    document.querySelectorAll('[data-log-filter]').forEach((button) => {
        button.addEventListener('click', () => {
            const filterType = button.dataset.logFilter;
            const startDate = document.getElementById('logFilterStartDate').value;
            const endDate = document.getElementById('logFilterEndDate').value;
            const subscriberIdInput = document.getElementById('logFilterSubscriberId').value.trim();
            logFilterStartDate = startDate;
            logFilterEndDate = endDate;
            activeLogSubscriberId = subscriberIdInput ? Number(subscriberIdInput) : null;

            if (!validateLogDateRange()) {
                return;
            }

            if (activeLogSubscriberId) {
                loadLogs(1, activeLogSubscriberId);
            } else {
                filterLogs(filterType);
            }
            logFilterModal.hide();
        });
    });
    dom.btnCopyDetails.addEventListener('click', copySubscriberDetails);
    dom.btnDeleteSub.addEventListener('click', () => {
        if (selectedSubscriberId !== null) deleteSubscriber(selectedSubscriberId);
    });
    if (dom.btnViewSubscriberLogs) {
        dom.btnViewSubscriberLogs.addEventListener('click', () => {
            if (selectedSubscriberId !== null) {
                const subscriberIdInput = document.getElementById('logFilterSubscriberId');
                if (subscriberIdInput) {
                    subscriberIdInput.value = selectedSubscriberId;
                }
                activeLogSubscriberId = selectedSubscriberId;
                const detailsModal = bootstrap.Modal.getInstance(document.getElementById('detailsModal'));
                if (detailsModal) detailsModal.hide();
                switchSection('logs');
                loadLogs(1, selectedSubscriberId);
            }
        });
    }
    dom.btnEditSub.addEventListener('click', () => {
        if (selectedSubscriberData) {
            enterInlineEditMode(selectedSubscriberData);
        }
    });
    if (dom.btnCancelInlineEdit) {
        dom.btnCancelInlineEdit.addEventListener('click', exitInlineEditMode);
    }
    const detailsModalEl = document.getElementById('detailsModal');
    if (detailsModalEl) {
        detailsModalEl.addEventListener('hidden.bs.modal', () => exitInlineEditMode({ preserveSelection: true }));
    }
    dom.btnSaveEdit.addEventListener('click', submitEditSubscriber);
    dom.btnSaveNew.addEventListener('click', submitNewSubscriber);
    dom.confirmBtn.addEventListener('click', submitAction);
    dom.quickPromiseInput.addEventListener('change', quickUpdatePromise);
    if (dom.fullDebtBtn) {
        dom.fullDebtBtn.addEventListener('click', setFullDebtAmount);
    }
    dom.btnPrevPage.addEventListener('click', () => {
        if (currentSubscriberPage > 1) loadSubscribers(currentSubscriberPage - 1);
    });
    dom.btnNextPage.addEventListener('click', () => {
        if (currentSubscriberPage < totalSubscriberPages) loadSubscribers(currentSubscriberPage + 1);
    });
    if (dom.btnPrevLogsPage) {
        dom.btnPrevLogsPage.addEventListener('click', () => {
            if (currentLogsPage > 1) loadLogs(currentLogsPage - 1);
        });
    }
    if (dom.btnNextLogsPage) {
        dom.btnNextLogsPage.addEventListener('click', () => {
            if (currentLogsPage < totalLogsPages) loadLogs(currentLogsPage + 1);
        });
    }
    document.querySelectorAll('[data-quick-amount]').forEach((button) => {
        button.addEventListener('click', () => setQuickAmount(parseInt(button.dataset.quickAmount, 10)));
    });
}

function loadInitialState() {
    const token = localStorage.getItem('token');
    if (token) {
        const role = getCurrentRole();
        if (redirectForRole(role)) {
            return;
        }
        showApp();
        loadPageData();
    } else {
        showLogin();
    }
}

async function handleLogin(event) {
    event.preventDefault();
    const username = dom.loginUsername.value.trim();
    const password = dom.loginPassword.value.trim();

    localStorage.removeItem('token');
    localStorage.removeItem('userRole');
    localStorage.removeItem('username');

    if (!username || !password) {
        dom.loginMessage.innerText = 'يرجى إدخال اسم المستخدم وكلمة المرور.';
        return;
    }

    const response = await apiCall('/login', 'POST', { username, password });
    if (response && response.token) {
        const resolvedRole = normalizeRole(response.role || decodeJwtRole(response.token) || 'viewer');
        localStorage.setItem('token', response.token);
        localStorage.setItem('userRole', resolvedRole);
        localStorage.setItem('username', response.username || username);
        dom.loginMessage.innerText = '';
        if (redirectForRole(resolvedRole)) {
            return;
        }
        showApp();
        loadPageData();
    } else {
        dom.loginMessage.innerText = response?.message || 'فشل تسجيل الدخول. حاول مرة أخرى.';
    }
}

function logoutUser() {
    localStorage.removeItem('token');
    localStorage.removeItem('userRole');
    localStorage.removeItem('username');
    dom.profileInfoCard.classList.add('d-none');
    showLogin();
}

function loadPageData() {
    loadSubscribers();
    loadTotalSubscribersCount();
    loadAreas();
    if (canViewAuditLog(getCurrentRole())) {
        loadLogs();
        loadDailyReport();
    }
}

async function loadTotalSubscribersCount() {
    const data = await apiCall('/subscribers?page=1&per_page=1');
    if (!data || data.status !== 'success') return;
    totalSubscribersOverall = data.pagination?.total_subscribers || 0;
    if (dom.totalSubscribers) {
        dom.totalSubscribers.innerText = totalSubscribersOverall.toLocaleString();
        dom.totalSubscribers.dataset.total = totalSubscribersOverall;
    }
}

async function loadAreas() {
    try {
        const data = await apiCall('/areas');
        if (!data || data.status !== 'success') return;
        allAreas = data.areas;
        renderAreaOptions(allAreas);
        renderAreasTable(allAreas);
        if (dom.profileAreasCount) {
            dom.profileAreasCount.innerText = Array.isArray(allAreas) ? allAreas.length : 0;
        }
        updateDashboardSummary();
    } catch (error) {
        console.error('خطأ في جلب المناطق:', error);
    }
}

function renderAreaOptions(areas) {
    let optionsHTML = '<option value="" disabled selected>اختر المنطقة...</option>';
    areas.forEach((area) => {
        optionsHTML += `<option value="${area.id}">${area.name}</option>`;
    });
    dom.addAreaId.innerHTML = optionsHTML;
    dom.editAreaId.innerHTML = optionsHTML;
}

function renderAreasTable(areas) {
    dom.areasTableBody.innerHTML = '';
    const canEditArea = canManageContent(getCurrentRole());

    if (!areas.length) {
        dom.areasTableBody.innerHTML = `<tr><td colspan="${canEditArea ? 3 : 2}" class="text-muted p-4">لا توجد مناطق مسجلة بعد.</td></tr>`;
        return;
    }

    areas.forEach((area, index) => {
        const editButton = canEditArea
            ? `<button type="button" class="btn btn-sm btn-outline-primary edit-area-btn" data-area-id="${area.id}" data-area-name="${area.name}"><i class="fa-solid fa-pen"></i> تعديل</button>`
            : '';

        dom.areasTableBody.innerHTML += `
            <tr>
                <td>${index + 1}</td>
                <td>${area.name}</td>
                <td>${editButton}</td>
            </tr>
        `;
    });
}

async function submitNewArea() {
    const name = dom.newAreaName.value.trim();
    if (!name) {
        showAlert('يرجى إدخال اسم المنطقة.');
        return;
    }
    const data = await apiCall('/areas', 'POST', { name });
    if (data && data.status === 'success') {
        addAreaModal.hide();
        dom.newAreaName.value = '';
        showAlert(data.message, 'success');
        loadAreas();
    } else {
        showAlert(data?.message || 'فشل إنشاء المنطقة.');
    }
}

async function loadSubscribers(page = 1) {
    try {
        if (!dom.subscribersTableBody) return;
        const requestId = ++subscribersRequestId;
        dom.subscribersTableBody.innerHTML = '<div class="col-12 text-muted p-4 text-center">جاري تحميل المشتركين...</div>';
        updateSubscriberFilterSummary();
        const params = buildSubscriberQueryParams(page);

        const data = await apiCall(`/subscribers?${params.toString()}`);
        if (requestId !== subscribersRequestId) return;
        if (!data || data.status !== 'success') {
            dom.subscribersTableBody.innerHTML = `<div class="col-12 text-danger p-4 text-center">${data?.message || 'تعذر تحميل قائمة المشتركين.'}</div>`;
            return;
        }
        const subscribersList = (Array.isArray(data.subscribers) ? data.subscribers : [])
            .filter((subscriber) => subscriber && typeof subscriber === 'object')
            .map(normalizeSubscriber);
        allSubscribers = subscribersList;
        currentSubscriberPage = page;
        totalSubscriberPages = data.pagination?.total_pages || 1;
        totalDebtOverall = Number(data.pagination?.total_debt || 0);
        dom.subscriberPageInfo.innerText = `صفحة ${currentSubscriberPage} من ${totalSubscriberPages}`;
        dom.btnPrevPage.disabled = currentSubscriberPage <= 1;
        dom.btnNextPage.disabled = currentSubscriberPage >= totalSubscriberPages;
        renderTable(allSubscribers);
        updateDashboardSummary();
    } catch (error) {
        console.error('خطأ في تحميل المشتركين:', error);
        if (dom.subscribersTableBody) {
            dom.subscribersTableBody.innerHTML = '<div class="col-12 text-danger p-4 text-center">حدث خطأ أثناء تحميل قائمة المشتركين.</div>';
        }
    }
}

function filterSubscribers() {
    syncSubscriberFiltersFromDom();
    if (!hasValidSubscriberDateRange()) return;
    loadSubscribers(1);
}

function resetSubscriberFilters() {
    subscriberFilters = {
        search: '',
        debtOnly: false,
        renewalFrom: '',
        renewalTo: ''
    };

    if (dom.searchInput) dom.searchInput.value = '';
    if (dom.debtOnlyFilter) dom.debtOnlyFilter.checked = false;
    if (dom.renewalFromFilter) dom.renewalFromFilter.value = '';
    if (dom.renewalToFilter) dom.renewalToFilter.value = '';

    updateSubscriberFilterSummary();
    loadSubscribers(1);
}

function createSubscriberRow(sub) {
    const card = document.createElement('div');
    card.className = 'col-lg-6 col-xl-4';

    const balanceValue = Number(sub.balance || 0);
    const isDebt = balanceValue < 0;
    const phone = sub.phone_number || sub.phone || 'لا يوجد رقم';
    const area = sub.area_name || sub.area_id || 'غير محدد';
    const promiseText = sub.promise_date && sub.promise_date !== 'None' ? `موعد السداد: ${sub.promise_date}` : 'لا يوجد وعد';
    const lastRenewalText = sub.last_renewal_date ? `آخر اشتراك: ${sub.last_renewal_date}` : 'آخر اشتراك: لا يوجد تجديد';
    const notes = sub.notes && String(sub.notes).trim() ? String(sub.notes).trim() : 'لا توجد ملاحظات';
    const canProcess = canProcessTransactions(getCurrentRole());

    card.innerHTML = `
        <div class="card h-100 shadow-sm border-0 rounded-4">
            <div class="card-body p-3">
                <div class="d-flex justify-content-between align-items-start mb-3">
                    <div>
                        <div class="text-primary fw-bold subscriber-name" style="cursor: pointer; font-size: 1.05rem;"></div>
                        <small class="text-primary subscriber-phone d-block mt-1"></small>
                    </div>
                    <span class="badge rounded-pill balance-badge px-2 py-2"></span>
                </div>

                <div class="small text-dark mb-2">
                    <i class="fa-solid fa-location-dot me-1"></i>
                    <span class="area-name"></span>
                </div>

                <div class="small text-dark mb-2 last-renewal-date"></div>
                <div class="small text-dark mb-2 promise-date"></div>
                <div class="small text-dark mb-3 subscriber-notes"></div>

                ${canProcess ? `
                    <div class="d-flex gap-2">
                        <button type="button" class="btn btn-sm btn-outline-success flex-fill fw-bold renew-btn">تجديد</button>
                        <button type="button" class="btn btn-sm btn-outline-primary flex-fill fw-bold payment-btn">تسديد</button>
                    </div>
                ` : ''}
            </div>
        </div>
    `;

    const phoneEl = card.querySelector('.subscriber-phone');
    phoneEl.textContent = `الهاتف: ${phone}`;
    phoneEl.style.cursor = 'pointer';
    phoneEl.style.fontWeight = '600';
    phoneEl.title = 'انقر لنسخ الرقم';
    phoneEl.addEventListener('click', async () => {
        const copied = await copyPhoneToClipboard(phone);
        showAlert(copied ? 'تم نسخ رقم الهاتف بنجاح' : 'لا يمكن نسخ الرقم الآن', copied ? 'success' : 'warning');
    });

    const subscriberNameEl = card.querySelector('.subscriber-name');
    subscriberNameEl.textContent = sub.name || '-';
    subscriberNameEl.title = 'انقر لعرض بطاقة المشترك';
    subscriberNameEl.addEventListener('click', () => showSubscriberDetails(sub.id));
    card.querySelector('.area-name').textContent = area;
    card.querySelector('.last-renewal-date').textContent = lastRenewalText;

    const balanceBadge = card.querySelector('.balance-badge');
    balanceBadge.textContent = isDebt ? `دين ${Math.abs(balanceValue).toLocaleString()}` : `رصيد ${balanceValue.toLocaleString()}`;
    balanceBadge.classList.add(isDebt ? 'bg-danger' : 'bg-success');

    card.querySelector('.promise-date').textContent = promiseText;
    card.querySelector('.subscriber-notes').textContent = `ملاحظات: ${notes}`;
    const renewButton = card.querySelector('.renew-btn');
    const paymentButton = card.querySelector('.payment-btn');
    if (renewButton) {
        renewButton.addEventListener('click', () => openModal(sub.id, sub.name, 'renewal', sub.balance));
    }
    if (paymentButton) {
        paymentButton.addEventListener('click', () => openModal(sub.id, sub.name, 'payment', sub.balance));
    }
    return card;
}

function renderTable(list) {
    dom.subscribersTableBody.innerHTML = '';
    if (!list.length) {
        dom.subscribersTableBody.innerHTML = '<div class="col-12 text-muted p-4 text-center">لا توجد بيانات للعرض</div>';
        return;
    }
    list.forEach((sub) => {
        try {
            dom.subscribersTableBody.appendChild(createSubscriberRow(sub));
        } catch (error) {
            console.error('خطأ في رسم بيانات المشترك:', sub, error);
        }
    });

    if (!dom.subscribersTableBody.children.length) {
        dom.subscribersTableBody.innerHTML = '<div class="col-12 text-danger p-4 text-center">تعذر عرض بيانات المشتركين.</div>';
    }
}

function openAddSubscriberModal() {
    dom.addSubscriberForm.reset();
    addSubModal.show();
}

async function openTeamModal() {
    dom.profileInfoCard.classList.add('d-none');
    const teamModalEl = document.getElementById('teamModal');
    const teamModalBody = document.getElementById('teamModalBody');
    if (!teamModalEl || !teamModalBody) return;

    teamModalBody.innerHTML = '<div class="text-center text-muted">جاري التحميل...</div>';
    const modal = bootstrap.Modal.getOrCreateInstance(teamModalEl);
    modal.show();

    try {
        const data = await apiCall('/staff');
        if (!data || data.status !== 'success') {
            teamModalBody.innerHTML = '<div class="text-danger">تعذر جلب بيانات الفريق.</div>';
            return;
        }

        const manager = data.manager || {};
        const members = Array.isArray(data.members) ? data.members : [];
        const roleLabel = (role) => getRoleLabel(role);
        const userRole = localStorage.getItem('userRole');
        if (dom.teamAddStaffWrapper) {
            dom.teamAddStaffWrapper.classList.toggle('d-none', userRole !== 'admin');
        }

        teamModalBody.innerHTML = `
            <div class="mb-3">
                <div class="fw-bold text-primary mb-2"><i class="fa-solid fa-user-shield"></i> المدير</div>
                <div class="border rounded p-2 bg-light">
                    <div class="fw-semibold">${manager.username || '—'}</div>
                    <div class="small text-muted">${roleLabel(manager.role || 'admin')}</div>
                </div>
            </div>
            <div>
                <div class="fw-bold text-secondary mb-2"><i class="fa-solid fa-users"></i> الموظفون</div>
                ${members.length ? members.map((member) => `
                    <div class="border rounded p-2 mb-2">
                        <div class="d-flex justify-content-between align-items-center gap-2">
                            <div>
                                <div class="fw-semibold">${member.username || '—'}</div>
                                <div class="small text-muted">${roleLabel(member.role || 'viewer')}</div>
                            </div>
                            ${userRole === 'admin' ? `<button type="button" class="btn btn-sm btn-outline-primary edit-staff-btn" data-staff-id="${member.id}" data-staff-username="${member.username || ''}" data-staff-role="${member.role || 'viewer'}" data-staff-active="${member.is_active !== false}"><i class="fa-solid fa-pen"></i> تعديل</button>` : ''}
                        </div>
                    </div>
                `).join('') : '<div class="text-muted">لا يوجد موظفون مسجلون حتى الآن.</div>'}
            </div>
        `;
    } catch (error) {
        console.error('خطأ في تحميل فريق العمل:', error);
        teamModalBody.innerHTML = '<div class="text-danger">حدث خطأ أثناء تحميل بيانات الفريق.</div>';
    }
}

function openEditStaffModal(button) {
    document.getElementById('editStaffId').value = button.dataset.staffId || '';
    document.getElementById('editStaffUsername').value = button.dataset.staffUsername || '';
    document.getElementById('editStaffPassword').value = '';
    document.getElementById('editStaffRole').value = button.dataset.staffRole || 'viewer';
    document.getElementById('editStaffActive').checked = button.dataset.staffActive !== 'false';
    bootstrap.Modal.getOrCreateInstance(document.getElementById('editStaffModal')).show();
}

async function submitStaffUpdate(event) {
    event.preventDefault();
    const staffId = document.getElementById('editStaffId').value;
    const username = document.getElementById('editStaffUsername').value.trim();
    const password = document.getElementById('editStaffPassword').value;
    const role = document.getElementById('editStaffRole').value;
    if (!username) {
        showAlert('اسم المستخدم مطلوب', 'warning');
        return;
    }

    const payload = { username, role, is_active: document.getElementById('editStaffActive').checked };
    if (password) payload.password = password;
    const data = await apiCall(`/my-team/${staffId}`, 'PUT', payload);
    if (data?.status === 'success') {
        bootstrap.Modal.getInstance(document.getElementById('editStaffModal'))?.hide();
        showAlert(data.message, 'success');
        openTeamModal();
    }
}

async function submitNewSubscriber() {
    const name = document.getElementById('addName').value.trim();
    const phone = document.getElementById('addPhone').value.trim();
    const areaId = dom.addAreaId.value;
    const notes = document.getElementById('addNotes').value.trim();
    if (!name || !phone || !areaId) {
        showAlert('يرجى تعبئة الحقول الإجبارية (الاسم، الهاتف، المنطقة)!');
        return;
    }
    const newSubscriberData = {
        name,
        phone_number: phone,
        area_id: parseInt(areaId, 10),
        notes
    };
    try {
        const data = await apiCall('/subscribers', 'POST', newSubscriberData);
        if (data && data.status === 'success') {
            addSubModal.hide();
            showAlert(data.message, 'success');
            loadSubscribers();
            loadTotalSubscribersCount();
            loadDailyReport();
        } else {
            showAlert(`❌ خطأ: ${data ? data.message : 'تعذر حفظ المشترك.'}`);
        }
    } catch (error) {
        showAlert('❌ حدث خطأ في الاتصال بالسيرفر!');
        console.error('Error:', error);
    }
}

async function showSubscriberDetails(subscriberId) {
    selectedSubscriberId = subscriberId;
    selectedSubscriberData = null;
    exitInlineEditMode({ preserveSelection: true });
    dom.detailName.innerText = 'جاري التحميل...';
    dom.detailId.innerText = `ID: ${subscriberId}`;
    dom.detailArea.innerText = '-';
    dom.detailPhone.innerText = '-';
    dom.detailBalance.innerText = '-';
    dom.quickPromiseInput.value = '';
    dom.detailNotes.innerText = 'جاري جلب الملاحظات...';
    dom.detailNotes.className = 'm-0 text-muted small fst-italic';
    const detailsModal = bootstrap.Modal.getOrCreateInstance(document.getElementById('detailsModal'));
    detailsModal.show();
    try {
        const data = await apiCall(`/subscribers/${subscriberId}`);
        if (!data || data.status !== 'success') {
            dom.detailName.innerText = '❌ حدث خطأ!';
            showAlert(data ? data.message : 'تعذر جلب تفاصيل المشترك.');
            return;
        }
        const sub = normalizeSubscriber(data.subscriber);
        selectedSubscriberData = sub;
        const canEdit = canEditSubscribers(getCurrentRole());
        dom.detailName.innerText = sub.name;
        dom.detailArea.innerText = sub.area_name || sub.area || '-';
        dom.detailBalance.innerText = `${sub.balance.toLocaleString()} د.ع`;
        dom.detailBalance.className = sub.balance < 0 ? 'fw-bold fs-5 text-danger' : 'fw-bold fs-5 text-success';
        dom.quickPromiseInput.value = sub.promise_date && sub.promise_date !== 'None' ? sub.promise_date.substring(0, 10) : '';
        if (!sub.phone || sub.phone === 'لا يوجد رقم مسجل') {
            dom.detailPhone.innerHTML = '<span class="text-danger small">لا يوجد رقم مسجل</span>';
        } else {
            dom.detailPhone.innerText = sub.phone;
            dom.detailPhone.className = 'fw-bold text-dark';
        }
        if (sub.notes && sub.notes.trim() !== '' && sub.notes !== 'None') {
            dom.detailNotes.innerText = sub.notes;
            dom.detailNotes.className = 'm-0 text-dark small fw-semibold';
        } else {
            dom.detailNotes.innerText = 'لا توجد ملاحظات مسجلة لهذا المشترك.';
            dom.detailNotes.className = 'm-0 text-muted small fst-italic';
        }
        if (dom.btnEditSub) dom.btnEditSub.classList.toggle('d-none', !canEdit);
        if (dom.btnDeleteSub) dom.btnDeleteSub.classList.toggle('d-none', !canEdit);
        if (dom.quickPromiseInput) dom.quickPromiseInput.disabled = !canEdit;
    } catch (error) {
        console.error('خطأ:', error);
        dom.detailName.innerText = '❌ خطأ في الاتصال';
    }
}

async function openSubscriberEditor(subscriberId, fallbackSub = null) {
    const fallbackNormalized = fallbackSub ? normalizeSubscriber(fallbackSub) : null;
    if (fallbackNormalized) {
        selectedSubscriberId = fallbackNormalized.id;
        selectedSubscriberData = fallbackNormalized;
        enterInlineEditMode(fallbackNormalized);
        return;
    }

    if (subscriberId) {
        await showSubscriberDetails(subscriberId);
        if (selectedSubscriberData) {
            enterInlineEditMode(selectedSubscriberData);
        }
    }
}

function enterInlineEditMode(sub) {
    const normalizedSub = normalizeSubscriber(sub);
    if (!canEditSubscribers(getCurrentRole())) {
        showAlert('المشاهد يستطيع العرض فقط ولا يمكنه تعديل بيانات المشترك.', 'warning');
        return;
    }
    isInlineEditingSubscriber = true;

    if (dom.subscriberDetailView) dom.subscriberDetailView.classList.add('d-none');
    if (dom.editSubscriberForm) dom.editSubscriberForm.classList.remove('d-none');
    if (dom.btnEditSub) dom.btnEditSub.classList.add('d-none');
    if (dom.btnCopyDetails) dom.btnCopyDetails.classList.add('d-none');
    if (dom.btnCloseDetails) dom.btnCloseDetails.classList.add('d-none');
    if (dom.btnViewSubscriberLogs) dom.btnViewSubscriberLogs.classList.add('d-none');
    if (dom.btnCancelInlineEdit) dom.btnCancelInlineEdit.classList.remove('d-none');
    if (dom.btnSaveEdit) dom.btnSaveEdit.classList.remove('d-none');
    setDetailsModalMode(true);

    const editSubId = document.getElementById('editSubId');
    const editName = document.getElementById('editName');
    const editPhone = document.getElementById('editPhone');
    const editNotes = document.getElementById('editNotes');
    const editPromiseDate = document.getElementById('editPromiseDate');

    if (editSubId) editSubId.value = normalizedSub.id;
    if (editName) editName.value = normalizedSub.name || '';
    if (editPhone) editPhone.value = normalizedSub.phone === 'لا يوجد رقم مسجل' ? '' : normalizedSub.phone || '';
    if (dom.editAreaId) dom.editAreaId.value = normalizedSub.area_id || '';
    if (editNotes) editNotes.value = normalizedSub.notes || '';
    if (editPromiseDate) {
        editPromiseDate.value = normalizedSub.promise_date && normalizedSub.promise_date !== 'None' && normalizedSub.promise_date !== 'لا يوجد وعد مسجل' ? normalizedSub.promise_date : '';
    }
}

function exitInlineEditMode(options = {}) {
    const preserveSelection = Boolean(options.preserveSelection);
    isInlineEditingSubscriber = false;

    if (dom.subscriberDetailView) dom.subscriberDetailView.classList.remove('d-none');
    if (dom.editSubscriberForm) dom.editSubscriberForm.classList.add('d-none');
    if (dom.btnEditSub) dom.btnEditSub.classList.remove('d-none');
    if (dom.btnCopyDetails) dom.btnCopyDetails.classList.remove('d-none');
    if (dom.btnCloseDetails) dom.btnCloseDetails.classList.remove('d-none');
    if (dom.btnViewSubscriberLogs) dom.btnViewSubscriberLogs.classList.toggle('d-none', !canViewAuditLog(getCurrentRole()));
    if (dom.btnCancelInlineEdit) dom.btnCancelInlineEdit.classList.add('d-none');
    if (dom.btnSaveEdit) dom.btnSaveEdit.classList.add('d-none');
    setDetailsModalMode(false);

    if (!preserveSelection && dom.editSubscriberForm) {
        dom.editSubscriberForm.reset();
    }
}

async function submitEditSubscriber() {
    const subId = document.getElementById('editSubId').value;
    const updatedData = {
        name: document.getElementById('editName').value.trim(),
        phone_number: document.getElementById('editPhone').value.trim(),
        area_id: parseInt(dom.editAreaId.value, 10),
        notes: document.getElementById('editNotes').value.trim(),
        promise_date: document.getElementById('editPromiseDate').value || null
    };
    try {
        const data = await apiCall(`/subscribers/${subId}`, 'PUT', updatedData);
        if (data && data.status === 'success') {
            showAlert(`✅ ${data.message}`, 'success');
            await showSubscriberDetails(Number(subId));
            loadSubscribers();
        } else {
            showAlert(`❌ خطأ: ${data ? data.message : 'تعذر حفظ التعديلات.'}`);
        }
    } catch (error) {
        showAlert('❌ حدث خطأ في الاتصال بالسيرفر!');
        console.error('Error:', error);
    }
}

async function deleteSubscriber(subId) {
    if (!confirm('⚠️ تحذير: هل أنت متأكد أنك تريد حذف هذا المشترك نهائياً؟ لا يمكن التراجع عن هذا الإجراء!')) return;
    try {
        const data = await apiCall(`/subscribers/${subId}`, 'DELETE');
        if (data && data.status === 'success') {
            const detailsModal = bootstrap.Modal.getInstance(document.getElementById('detailsModal'));
            if (detailsModal) detailsModal.hide();
            showAlert(`🗑️ ${data.message}`, 'success');
            loadSubscribers();
            loadTotalSubscribersCount();
        } else {
            showAlert(`❌ خطأ: ${data ? data.message : 'تعذر حذف المشترك.'}`);
        }
    } catch (error) {
        showAlert('❌ حدث خطأ في الاتصال بالسيرفر!');
        console.error('Error:', error);
    }
}

async function loadPromisesToday() {
    try {
        const data = await apiCall('/promises_today');
        if (!data) return;
        if (data.status === 'success') {
            if (data.count === 0) {
                showAlert('لا توجد وعود مستحقة لهذا اليوم! 🎉', 'success');
                loadSubscribers();
            } else {
                renderTable(data.subscribers);
                showAlert(`تم العثور على ${data.count} وعود مستحقة اليوم!`, 'info');
            }
        }
    } catch (error) {
        showAlert('❌ حدث خطأ في جلب الوعود من السيرفر!');
        console.error(error);
    }
}

async function loadLogs(page = 1, subscriberId = activeLogSubscriberId) {
    try {
        const params = new URLSearchParams({
            page: String(page),
            per_page: String(logsPerPage)
        });
        if (subscriberId) {
            params.set('subscriber_id', String(subscriberId));
        }

        const data = await apiCall(`/logs?${params.toString()}`);
        if (!data) return;
        if (data.status === 'success') {
            const rawLogs = Array.isArray(data.logs)
                ? data.logs
                : (Array.isArray(data.items) ? data.items : []);

            allLogs = rawLogs
                .map(normalizeLog)
                .filter((log) => log !== null);

            currentLogsPage = data.pagination?.current_page || page;
            totalLogsPages = data.pagination?.total_pages || 1;
            if (dom.logsPageInfo) {
                dom.logsPageInfo.innerText = `صفحة ${currentLogsPage} من ${totalLogsPages}`;
            }
            if (dom.btnPrevLogsPage) {
                dom.btnPrevLogsPage.disabled = currentLogsPage <= 1;
            }
            if (dom.btnNextLogsPage) {
                dom.btnNextLogsPage.disabled = currentLogsPage >= totalLogsPages;
            }

            currentLogFilter = 'الكل';
            updateLogFilterButtonLabel();
            renderLogsTable(allLogs);
            updateDashboardSummary();
        }
    } catch (error) {
        console.error('Error loading logs:', error);
        dom.logsTableBody.innerHTML = '<tr><td colspan="5" class="text-danger p-4">❌ خطأ في الاتصال وجلب السجل</td></tr>';
    }
}

function renderLogsTable(logsArray) {
    dom.logsTableBody.innerHTML = '';
    if (!logsArray.length) {
        dom.logsTableBody.innerHTML = '<tr><td colspan="5" class="text-muted p-4">لا توجد عمليات مطابقة للعرض.</td></tr>';
        return;
    }
    logsArray.forEach((log) => {
        const badgeClass = log.type === 'تسديد' ? 'bg-primary' : (log.type === 'تجديد' ? 'bg-success' : 'bg-secondary');
        const icon = log.type === 'تسديد' ? 'fa-hand-holding-dollar' : (log.type === 'تجديد' ? 'fa-wifi' : 'fa-circle-info');
        const displayDate = formatBaghdadDateTime(log.date);
        dom.logsTableBody.innerHTML += `
            <tr>
                <td dir="ltr" class="text-muted small">${displayDate}</td>
                <td class="fw-bold text-dark">${log.subscriber_name}</td>
                <td class="small text-secondary">${log.processed_by || 'غير معروف'}</td>
                <td><span class="badge ${badgeClass} fs-6"><i class="fa-solid ${icon}"></i> ${log.type}</span></td>
                <td class="fw-bold fs-6">${Number(log.amount || 0).toLocaleString()} د.ع</td>
            </tr>
        `;
    });
}

function updateLogFilterButtonLabel() {
    if (dom.btnOpenLogFilter) {
        dom.btnOpenLogFilter.innerText = currentLogFilter === 'الكل' ? 'تصفية' : `تصفية: ${currentLogFilter}`;
    }
}

function validateLogDateRange() {
    if (!logFilterStartDate || !logFilterEndDate) {
        return true;
    }

    if (logFilterStartDate > logFilterEndDate) {
        showAlert('تاريخ البداية يجب أن يكون أقدم أو يساوي تاريخ النهاية');
        return false;
    }

    return true;
}

function filterLogs(filterType) {
    currentLogFilter = filterType;
    updateLogFilterButtonLabel();

    if (!validateLogDateRange()) {
        return;
    }

    const filteredLogs = allLogs.filter((log) => {
        const dateText = String(log.date || '');
        const logDate = dateText.includes('T') ? dateText.split('T')[0] : dateText.split(' ')[0];
        const matchesType = filterType === 'الكل' || log.type === filterType;
        const matchesStart = !logFilterStartDate || logDate >= logFilterStartDate;
        const matchesEnd = !logFilterEndDate || logDate <= logFilterEndDate;
        const matchesSubscriber = !activeLogSubscriberId || Number(log.subscriber_id) === Number(activeLogSubscriberId);
        return matchesType && matchesStart && matchesEnd && matchesSubscriber;
    });

    renderLogsTable(filteredLogs);
}

async function loadDailyReport() {
    if (!canViewAuditLog(getCurrentRole())) return;
    const data = await apiCall('/daily_report');
    if (!data || data.status !== 'success') return;

    const summary = data.summary || {};
    if (dom.todayPayments) {
        dom.todayPayments.innerText = `${Number(summary.total_payments_collected || 0).toLocaleString()} د.ع`;
    }
    if (dom.todayRenewals) {
        dom.todayRenewals.innerText = `${Number(summary.total_renewals_value || 0).toLocaleString()} د.ع`;
    }
}

function formatIraqiDinar(value) {
    return `${Number(value || 0).toLocaleString()} د.ع`;
}

function renderMonthlyReport(data) {
    const totals = data.totals || {};
    const days = Array.isArray(data.days) ? data.days : [];

    dom.monthlyTotalCollected.innerText = formatIraqiDinar(totals.grand_total_collected);
    dom.monthlyCashReceived.innerText = formatIraqiDinar(totals.total_cash_received);
    dom.monthlyElectronicReceived.innerText = formatIraqiDinar(totals.total_electronic_received);
    dom.monthlyRenewalsAmount.innerText = formatIraqiDinar(totals.total_renewals_amount);
    dom.monthlyPaymentsCount.innerText = Number(totals.total_payments_count || 0).toLocaleString();
    dom.monthlyRenewalsCount.innerText = Number(totals.total_renewals_count || 0).toLocaleString();
    dom.monthlyActiveDaysCount.innerText = Number(totals.active_days_count || 0).toLocaleString();
    dom.monthlyReportMessage.className = 'small text-muted mb-3';
    dom.monthlyReportMessage.innerText = `ملخص شهر ${data.month}/${data.year}`;

    if (!days.length) {
        dom.monthlyReportTableBody.innerHTML = '<tr><td colspan="6" class="text-muted p-4">لا توجد عمليات مسجلة في هذا الشهر.</td></tr>';
        return;
    }

    dom.monthlyReportTableBody.innerHTML = days.map((day) => `
        <tr>
            <td dir="ltr" class="text-muted">${day.summary_date || '-'}</td>
            <td>${Number(day.payments_count || 0).toLocaleString()}</td>
            <td>${Number(day.renewals_count || 0).toLocaleString()}</td>
            <td>${formatIraqiDinar(day.cash_received)}</td>
            <td>${formatIraqiDinar(day.electronic_received)}</td>
            <td class="fw-bold">${formatIraqiDinar(day.total_collected)}</td>
        </tr>
    `).join('');
}

async function loadMonthlyReport() {
    if (!canViewAuditLog(getCurrentRole()) || !dom.monthlyReportPeriod?.value) return;

    const [year, month] = dom.monthlyReportPeriod.value.split('-');
    dom.monthlyReportMessage.className = 'small text-muted mb-3';
    dom.monthlyReportMessage.innerText = 'جاري تحميل التقرير...';

    const data = await apiCall(`/monthly-summary?year=${encodeURIComponent(year)}&month=${encodeURIComponent(month)}`);
    if (!data || !data.success) {
        dom.monthlyReportMessage.className = 'small text-danger mb-3';
        dom.monthlyReportMessage.innerText = data?.error || data?.message || 'تعذر تحميل التقرير الشهري.';
        return;
    }

    renderMonthlyReport(data);
}

function updateDashboardSummary() {
    const totalSubscribersCount = Number(dom.totalSubscribers?.dataset?.total || totalSubscribersOverall || 0);
    const totalAreasCount = Array.isArray(allAreas) ? allAreas.length : 0;

    if (dom.totalSubscribers) {
        dom.totalSubscribers.innerText = totalSubscribersCount.toLocaleString();
    }
    if (dom.profileAreasCount) {
        dom.profileAreasCount.innerText = totalAreasCount.toLocaleString();
    }
    if (dom.totalDebt) {
        dom.totalDebt.innerText = `${totalDebtOverall.toLocaleString()} د.ع`;
    }
}

async function submitAction() {
    if (isActionSubmitting) return;

    const subscriberId = document.getElementById('modal-subscriber-id').value;
    const actionType = document.getElementById('modal-action-type').value;
    const amount = dom.amountInput.value;
    const promiseDate = dom.promiseDateInput.value;
    const isCash = dom.isCashCheckbox.checked;
    const paymentMethod = dom.paymentMethod?.value || 'cash';

    if (!amount || Number(amount) <= 0) {
        return showAlert('يرجى إدخال مبلغ صحيح!');
    }

    isActionSubmitting = true;
    const confirmBtn = dom.confirmBtn;
    const originalButtonText = confirmBtn.innerHTML;
    confirmBtn.disabled = true;
    confirmBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span> جاري التنفيذ...';

    const endpoint = actionType === 'payment' ? '/transactions/payment' : '/transactions/renewal';
    const requestData = {
        subscriber_id: parseInt(subscriberId, 10),
        amount: parseInt(amount, 10),
        promise_date: promiseDate,
        is_cash: isCash
    };
    if (actionType === 'payment') {
        requestData.payment_type = paymentMethod;
    }

    try {
        const data = await apiCall(endpoint, 'POST', requestData);
        if (data && data.status === 'success') {
            actionModal.hide();
            showAlert(data.message || 'تم تنفيذ العملية بنجاح.', 'success');
            loadSubscribers();
            loadLogs();
            loadDailyReport();
        } else {
            showAlert(`❌ تنبيه: ${data ? data.message : 'تعذر تنفيذ العملية.'}`);
        }
    } catch (error) {
        showAlert('❌ خطأ في الاتصال بالسيرفر!');
    } finally {
        isActionSubmitting = false;
        confirmBtn.disabled = false;
        confirmBtn.innerHTML = originalButtonText;
    }
}

function switchSection(sectionName) {
    document.querySelectorAll('.section-content').forEach((el) => el.classList.remove('active'));
    document.querySelectorAll('.nav-tabs .nav-link').forEach((el) => el.classList.remove('active'));
    document.getElementById(sectionName).classList.add('active');
    document.getElementById(`tab-${sectionName}`).classList.add('active');
}

function openModal(subscriberId, subscriberName, actionType, currentBalance) {
    currentSubscriberDebt = currentBalance < 0 ? Math.abs(currentBalance) : 0;
    const titleLabel = document.getElementById('actionModalLabel');
    const confirmBtn = dom.confirmBtn;
    if (actionType === 'payment') {
        titleLabel.innerHTML = '<i class="fa-solid fa-hand-holding-dollar text-primary"></i> تسديد مبلغ';
        confirmBtn.className = 'btn btn-primary w-100 py-2 fw-bold fs-5';
        dom.cashPaymentDiv.style.display = 'none';
        dom.paymentMethodDiv.style.display = 'block';
        dom.paymentMethod.value = 'cash';
        if (dom.fullDebtBtn) dom.fullDebtBtn.classList.remove('d-none');
    } else {
        titleLabel.innerHTML = '<i class="fa-solid fa-wifi text-success"></i> تجديد اشتراك';
        confirmBtn.className = 'btn btn-success w-100 py-2 fw-bold fs-5';
        dom.cashPaymentDiv.style.display = 'block';
        dom.paymentMethodDiv.style.display = 'none';
        dom.isCashCheckbox.checked = false;
        if (dom.fullDebtBtn) dom.fullDebtBtn.classList.add('d-none');
    }
    document.getElementById('modal-subscriber-name').innerText = subscriberName;
    dom.amountInput.value = '';
    dom.promiseDateInput.value = '';
    document.getElementById('modal-subscriber-id').value = subscriberId;
    document.getElementById('modal-action-type').value = actionType;
    actionModal.show();
}

function setQuickAmount(amount) {
    dom.amountInput.value = amount;
}

function setFullDebtAmount() {
    if (currentSubscriberDebt > 0) {
        dom.amountInput.value = currentSubscriberDebt;
    } else {
        showAlert('هذا المشترك ليس عليه دين ليتم تسديده!');
    }
}

async function quickUpdatePromise() {
    if (!selectedSubscriberId) return;
    if (!canEditSubscribers(getCurrentRole())) {
        showAlert('المشاهد يستطيع العرض فقط ولا يمكنه تعديل بيانات المشترك.', 'warning');
        return;
    }
    const updatedData = { promise_date: dom.quickPromiseInput.value || null };
    try {
        const data = await apiCall(`/subscribers/${selectedSubscriberId}`, 'PUT', updatedData);
        if (data && data.status === 'success') {
            loadSubscribers();
        } else {
            console.error('خطأ في تحديث الوعد:', data ? data.message : 'No response');
        }
    } catch (error) {
        console.error('حدث خطأ في الاتصال أثناء تحديث الوعد:', error);
    }
}

function copySubscriberDetails() {
    const id = dom.detailId.innerText.replace('ID: ', '').trim();
    const name = dom.detailName.innerText;
    const area = dom.detailArea.innerText;
    const phone = dom.detailPhone.innerText;
    const balance = dom.detailBalance.innerText;
    const promiseDate = dom.quickPromiseInput.value || 'لا يوجد';
    const notes = dom.detailNotes.innerText;
    const textToCopy = `ID: ${id}\nالاسم: ${name}\nالمنطقة: ${area}\nرقم الهاتف: ${phone}\nالرصيد الحالي: ${balance}\nوعد التسديد: ${promiseDate}\nملاحظات: ${notes}`;
    navigator.clipboard.writeText(textToCopy)
        .then(() => showAlert('تم نسخ معلومات المشترك إلى الحافظة.', 'success'))
        .catch((error) => {
            console.error('خطأ في نسخ المعلومات:', error);
            showAlert('تعذر نسخ المعلومات. الرجاء المحاولة مرة أخرى.');
        });
}

window.addEventListener('DOMContentLoaded', initPage);
